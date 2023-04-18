import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from html.parser import HTMLParser
from typing import List, Dict, Tuple, Optional, ClassVar

from articles_processor.parser_types import OutputData


# from articles_processor.proc_logger import logger

def clean_text(s: str) -> str:
    s = s.replace(chr(0xa0), " ")
    return s


@dataclass
class TagData:
    tag: str
    attrs: Optional[dict]
    data: Optional[str] = None

    @property
    def cleaned_data(self) -> str:
        return clean_text(self.data) if self.data else ""


class TagStatus(Enum):
    IGNORED = auto()
    PROCESSED = auto()


@dataclass
class TagEntry:
    td: TagData
    status: TagStatus


class ArticleHTMLParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.output = OutputData()
        self.level: int = 0
        self.tag_hierarchy: List[TagEntry] = []
        self.stop_processing: bool = False
        "No further tags should be (actively) processed."

    header_marker: ClassVar[str] = '[H] '
    quote_marker: ClassVar[str] = '[Q] '
    italics_marker: ClassVar[str] = '//'

    def get_tags_to_ignore(self) -> List[TagData]:
        return [
            TagData(tag='img', attrs={}),
            TagData(tag='button', attrs={}),
            TagData(tag='figcaption', attrs={}),
            TagData(tag='script', attrs={'type': 'text/javascript'}),
            TagData(tag='script', attrs=None),
        ]

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        """Tags for which no 'unhandled' error should be issued."""
        return [
            TagData(tag='i', attrs={}),
        ]

    @staticmethod
    def parse_attrs(attrs_as_list: List[Tuple]) -> Dict[str, str]:
        return {k: v for k, v in attrs_as_list}

    @staticmethod
    @abstractmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        raise NotImplementedError

    def is_content(self) -> bool:
        """Check whether the currently processed tag belongs to the article's content."""
        return any(self.is_contnet_tag(te.td) for te in self.tag_hierarchy)

    def try_extract_charset(self, tag: str, attrs: Dict):
        if tag == "meta":
            if charset := attrs.get('charset'):
                self.output.charset = charset.lower()

    def handle_startendtag(self, tag, attrs):
        attrs_dict = self.parse_attrs(attrs)
        if tag == 'link' and attrs_dict.get('rel') == 'canonical':
            self.output.url = attrs_dict['href']
        self.try_extract_charset(tag, attrs_dict)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)

        if self.tag_hierarchy and self.tag_hierarchy[-1].td.tag == "img":
            logging.warning("Closing tag: img")
            self.tag_hierarchy.pop()
            self.level -= 1

        current_tag: TagData = TagData(tag=tag, attrs=self.parse_attrs(attrs))
        status: TagStatus = TagStatus.IGNORED if self.is_ignored_tag(current_tag) else TagStatus.PROCESSED
        tabs: str = "".join(self.level * ['  '])
        status_str: str = f"{'I' if status == TagStatus.IGNORED else 'P'}{'+R' if self.is_ignored_in_hierarchy() else ''}"

        if not status_str:
            x = 1

        logging.debug(f"{tabs}{tag} <{status_str}> {attrs}")

        self.tag_hierarchy.append(TagEntry(td=current_tag,
                                           status=status))
        self.level += 1

        if self.should_stop_processing():
            logging.warning("Processing stopped!")
            self.stop_processing = True

        if self.stop_processing:
            return

        if current_tag.tag == 'div' and 'class' in current_tag.attrs and 'flex-row' in current_tag.attrs['class']:
            x = 1

        if self.is_ignored_in_hierarchy():
            # if current_tag.td.tag == 'div' and current_tag.td.attrs.get('class') == 'single__post__content':
            #     x = 1
            # logging.warning(f"Ignored: {current_tag}")
            return
        # logging.warning(f"Processed: {current_tag}")

        self.try_extract_charset(tag, current_tag.attrs)

        if self.is_content():
            # italics
            if current_tag.tag == 'i':
                self.output.content += self.italics_marker

        self.process_starttag()

    @abstractmethod
    def process_starttag(self):
        raise NotImplementedError

    def should_stop_processing(self) -> bool:
        return False

    def handle_endtag(self, tag):
        self.process_endtag()

        if not self.stop_processing and self.is_content():
            # italics
            if tag == 'i':
                self.output.content += self.italics_marker

        self.level -= 1
        tabs: str = "".join(self.level * ['  '])
        logging.debug(f"{tabs}/{tag} {self.tag_hierarchy[-1].td.attrs}")
        self.tag_hierarchy.pop()

    @abstractmethod
    def process_endtag(self):
        raise NotImplementedError

    def handle_data(self, data):
        super().handle_data(data)
        if not self.tag_hierarchy:
            return
        self.tag_hierarchy[-1].td.data = data

        if self.is_ignored_in_hierarchy():
            return

        # Handle some standard tags.
        last_tag = self.tag_hierarchy[-1].td
        if self.is_content():
            # if self.is_text_paragraph(last_tag) or self.is_article_lead(last_tag):
            #     self.output.content += last_tag.cleaned_data
            #     return
            #
            # if self.is_block_quote(last_tag):
            #     self.output.content += re.sub(r"^\n\s+", "", last_tag.cleaned_data)
            #     return
            #
            # if self.is_header(last_tag):
            #     if 'Przeczytaj także:' in last_tag.data:
            #         # self.stop_processing = True
            #         return
            #
            #     self.output.content += f"{self.header_marker}{last_tag.cleaned_data.rstrip()}\n\n"
            #     return
            #
            # if last_tag.tag == 'a':
            #     if self.is_link_to_another_article(last_tag):
            #         href: str = last_tag.attrs['href']
            #         self.output.links.append(re.sub("#.*$", "", href))
            #         self.output.content += f"{last_tag.cleaned_data}[L{len(self.output.links)}]"
            #     else:
            #         self.output.content += last_tag.cleaned_data
            #     return

            # italics
            if last_tag.tag == 'i':
                # self.output.content += f"//{last_tag.cleaned_data}//"
                self.output.content += last_tag.cleaned_data
                return

            # bold
            if last_tag.tag in {'strong', 'b'}:
                self.output.content += last_tag.cleaned_data
                return

            # list item
            if last_tag.tag == 'li':
                self.output.content += f"  * {last_tag.cleaned_data}"
                if last_tag.cleaned_data.rstrip().endswith(';'):
                    self.output.content += '\n'
                if last_tag.cleaned_data.rstrip().endswith('.'):
                    self.output.content += '\n\n'
                return

        self.process_data()

    @abstractmethod
    def process_data(self):
        raise NotImplementedError

    def check_ignored_tag(self, last_tag: TagData, data: str) -> None:
        if self.is_tag_match(last_tag, self.get_tags_to_ignore() + self.get_tags_with_suppressed_validation()):
            return
        raise ValueError(f"Unknown tag: {last_tag.tag} {last_tag.attrs} D=`{data}`")

    @staticmethod
    def is_tag_match(td: TagData, td_list: List[TagData]) -> bool:
        for ignored_tag_data in td_list:
            is_same_tag: bool = (td.tag == ignored_tag_data.tag)
            has_same_attrs: bool = True
            if ignored_tag_data.attrs is None:
                has_same_attrs = not td.attrs
            else:
                for attr, val in ignored_tag_data.attrs.items():
                    if attr not in td.attrs:
                        has_same_attrs = False
                        break
                    if isinstance(val, str):
                        has_same_attrs = has_same_attrs and val in td.attrs[attr]
                    elif isinstance(val, set):
                        has_same_attrs = has_same_attrs and all(v in td.attrs[attr] for v in val)
                    else:
                        raise ValueError(f'Invalid attr value: {attr} -> {val}')
            if is_same_tag and has_same_attrs:
                return True
        return False

    def is_ignored_tag(self, td: TagData = None) -> bool:
        return self.is_tag_match(td, self.get_tags_to_ignore())

    def is_ignored_in_hierarchy(self) -> bool:
        return any(te.status == TagStatus.IGNORED for te in self.tag_hierarchy)

    def is_embedded_text(self) -> bool:
        return any(
            te.td.tag == 'div' and 'class' in te.td.attrs and 'text--embed' in te.td.attrs['class']
            for te in self.tag_hierarchy
        )

    def feed(self, data: str) -> None:
        super().feed(data)
        self.postprocess_metadata()

        assert self.output.url, "No URL was assigned to the article!"
        assert self.output.author, 'Unknown author!'
        assert self.output.author, 'Unknown headline!'

        self.output.title = self.output.title.strip()

        if 'datePublished' in self.output.metadata:
            pub_date_meta_str = self.output.metadata['datePublished']
            pub_date_meta = datetime.fromisoformat(pub_date_meta_str)
            # if self.output.pub_date:
            #     assert self.output.pub_date.date() == pub_date_meta.date()
            # else:
            self.output.pub_date = pub_date_meta

        if 'dateModified' in self.output.metadata:
            mod_date_meta_str = self.output.metadata['dateModified']
            mod_date_meta = datetime.fromisoformat(mod_date_meta_str)
            # if self.output.last_updated:
            #     assert self.output.last_updated.date() == mod_date_meta.date()
            # else:
            self.output.last_updated = mod_date_meta

        def remove_nbsps(s: str) -> str:
            return s.replace("\u00a0", " ")

        self.output.content = remove_nbsps(self.output.content)
        self.output.content = self.output.content.rstrip()
        self.output.content = self.output.content.replace("„", '"')
        self.output.content = self.output.content.replace("”", '"')
        self.remove_extra_metadata()

    def postprocess_metadata(self) -> None:
        return

    def remove_extra_metadata(self):
        for tag in ['@context', '@type', 'articleSection', 'hasPart',
                    'image', 'publisher', 'isAccessibleForFree',
                    'mainEntityOfPage'] + ['itemListElement', 'keywords']:
            if tag in self.output.metadata:
                self.output.metadata.pop(tag)
