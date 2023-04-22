import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum, auto
from html.parser import HTMLParser
from typing import List, Dict, Tuple, Optional, ClassVar, Pattern, Union

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
    tag_no: int
    level: int


class ListType(Enum):
    ORDERED = auto()
    UNORDERED = auto()


def get_individual_attr_pattern(s: str):
    return re.compile(f"(?:^| ){s}(?: |$)")


class ArticleHTMLParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.output = OutputData()
        self.level: int = 0
        self.tag_no = 0
        self.tag_hierarchy: List[TagEntry] = []
        self.stop_processing: bool = False
        "No further tags should be (actively) processed."
        self.list_type: Optional[ListType] = None

    header_marker: ClassVar[str] = '[HEADER] '
    quote_marker: ClassVar[str] = '[QUOTE] '
    italics_marker: ClassVar[str] = '//'
    list_markers: ClassVar[Dict[ListType, str]] = {
        ListType.ORDERED: '-',
        ListType.UNORDERED: '*',
    }

    def get_tags_to_ignore(self) -> List[TagData]:
        return [
            TagData(tag='img', attrs={}),
            TagData(tag='button', attrs={}),
            TagData(tag='figcaption', attrs={}),
            TagData(tag='script', attrs={'type': 'text/javascript'}),
            TagData(tag='script', attrs=None),
            TagData(tag='picture', attrs=None),
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
        self.tag_no += 1

        tabs: str = "".join(self.level * ['  '])
        status_str: str = "P"
        logging.debug(f"{tabs}{tag}(/) <{status_str}> {self.parse_attrs(attrs)}")

        current_tag = TagData(tag=tag, attrs=self.parse_attrs(attrs))
        if tag == 'link' and current_tag.attrs.get('rel') == 'canonical':
            self.output.url = current_tag.attrs['href']
        self.try_extract_charset(tag, current_tag.attrs)

        if tag == 'br':
            self.output.content += '\n'
            return

        self.process_startendtag(current_tag)

    def process_startendtag(self, tag: TagData) -> None:
        pass

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

        logging.debug(f"{tabs}{tag} <{status_str}> {attrs}")

        level = self.tag_hierarchy[-1].level + 1 if self.tag_hierarchy else 0
        self.tag_no += 1
        self.tag_hierarchy.append(TagEntry(td=current_tag,
                                           status=status,
                                           tag_no=self.tag_no,
                                           level=level
                                           ))
        self.level += 1

        if current_tag.tag == 'link' and current_tag.attrs.get('rel') == 'canonical':
            self.output.url = current_tag.attrs['href']

        if self.should_stop_processing():
            logging.warning("Processing stopped!")
            self.stop_processing = True

        if self.stop_processing:
            return

        # if current_tag.tag == 'div' and 'class' in current_tag.attrs and 'flex-row' in current_tag.attrs['class']:
        #     x = 1

        if self.is_ignored_in_hierarchy():
            # if current_tag.td.tag == 'div' and current_tag.td.attrs.get('class') == 'single__post__content':
            #     x = 1
            # logging.warning(f"Ignored: {current_tag}")
            return
        # logging.warning(f"Processed: {current_tag}")

        self.try_extract_charset(tag, current_tag.attrs)

        if self.is_content():
            if current_tag.tag == 'ol':
                self.list_type = ListType.ORDERED
                return
            if current_tag.tag == 'ul':
                self.list_type = ListType.UNORDERED
                return

            # italics
            if current_tag.tag in {'i', 'em'}:
                self.output.content += self.italics_marker

            # list item
            if current_tag.tag == 'li':
                if self.output.content and self.output.content[-1] != '\n':
                    self.output.content += '\n'
                self.output.content += f"  {self.list_markers[self.list_type]} "

        self.process_starttag()

    @abstractmethod
    def process_starttag(self):
        raise NotImplementedError

    def should_stop_processing(self) -> bool:
        return False

    def handle_endtag(self, tag):
        if not (self.stop_processing or self.is_ignored_in_hierarchy()):
            self.process_endtag()

        if not self.stop_processing and self.is_content():
            # italics
            if tag in {'i', 'em'}:
                self.output.content += self.italics_marker

            if tag in {'ul', 'ol'}:
                self.list_type = None
                self.output.content += "\n"

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

        if self.stop_processing or self.is_ignored_in_hierarchy():
            return

        # Handle some standard tags.
        last_tag = self.tag_hierarchy[-1].td

        if last_tag.tag == "script" and 'application/ld+json' == last_tag.attrs.get('type'):
            meta = json.loads(last_tag.data)
            data_to_insert: Dict[str, dict] = {}
            if key := meta.get('@type'):
                data_to_insert[key] = meta
            elif graph := meta.get('@graph'):
                for item in graph:
                    data_to_insert[item['@type']] = item
            else:
                raise NotImplementedError(f"Unknown meta format: {meta}")

            for key, value in data_to_insert.items():
                if key in self.output.metadata:
                    logging.error(f'Duplicated <script type="application/ld+json"> key: {key}')
                self.output.metadata[key] = value

        # if (last_tag.tag == 'div' and 'class' in last_tag.attrs and 'cg_article_printed_info_details' in last_tag.attrs['class']):
        #     x = 1

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

            if last_tag.tag in {'ol', 'ul'}:
                return

                # italics
            if last_tag.tag in {'i', 'em'}:
                # self.output.content += f"//{last_tag.cleaned_data}//"
                # self.output.content += last_tag.cleaned_data
                self.process_italics_data(last_tag)
                return

            # bold
            if last_tag.tag in {'strong', 'b'}:
                self.output.content += last_tag.cleaned_data
                return

            # list item
            if last_tag.tag == 'li':
                # if self.output.content[-1] != '\n':
                #     self.output.content += '\n'
                # self.output.content += f"  * {last_tag.cleaned_data}"
                self.output.content += last_tag.cleaned_data
                if last_tag.cleaned_data.rstrip().endswith((';', '.')):
                    self.output.content += '\n'
                return

            # new line
            if last_tag.tag == 'br':
                self.output.content += '\n'
                return

        self.process_data()

    def process_italics_data(self, tag_data: TagData) -> None:
        self.output.content += tag_data.cleaned_data

    @abstractmethod
    def process_data(self):
        raise NotImplementedError

    def check_ignored_tag(self, last_tag: TagData, data: str) -> None:
        if self.is_tag_match(last_tag, self.get_tags_to_ignore() + self.get_tags_with_suppressed_validation()):
            return
        raise ValueError(f"Unknown tag: {last_tag.tag} {last_tag.attrs} D=`{data}`")

    @staticmethod
    def is_tag_match(td: TagData, td_list: List[TagData]) -> bool:
        x = 1
        for ignored_tag_data in td_list:
            is_same_tag: bool = (td.tag == ignored_tag_data.tag)
            if not is_same_tag:
                continue

            has_same_attrs: bool = True
            if ignored_tag_data.attrs is None:
                has_same_attrs = not td.attrs
            else:
                for attr, val in ignored_tag_data.attrs.items():
                    if attr not in td.attrs:
                        has_same_attrs = False
                        break

                    def verify_chunk(v: Union[str, Pattern], td: TagData) -> bool:
                        v_target = td.attrs[attr]
                        if isinstance(v, str):
                            return v in v_target
                        elif isinstance(v, Pattern):
                            return v.search(v_target) is not None
                        else:
                            raise TypeError(f"type(v): {type(v)}")

                    if isinstance(val, str) or isinstance(val, Pattern):
                        has_same_attrs = has_same_attrs and verify_chunk(val, td)
                    elif isinstance(val, set):
                        has_same_attrs = has_same_attrs and all(verify_chunk(v, td) for v in val)
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

        self.output.verify_data()

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

        self.remove_extra_metadata()

        def remove_nbsps(s: str) -> str:
            return s.replace("\u00a0", " ")

        self.output.content = remove_nbsps(self.output.content)
        self.output.content = self.output.content.rstrip()
        self.output.content = self.output.content.replace("„", '"')
        self.output.content = self.output.content.replace("”", '"')
        # Remove "orphaned" italics markers.
        self.output.content = re.sub(r"////", "", self.output.content)
        # Remove excessive newlines.
        self.output.content = re.sub(r"\n{2,}", "\n\n", self.output.content)
        # Fix multiple consecutive spaces (unless at the beginning of a line - as part of DokuWiki list syntax).
        self.output.content = re.sub(r"(?<!\n) {2,}", " ", self.output.content)
        # Remove spaces before punctuation.
        self.output.content = re.sub(r" (?=[,\.;])", "", self.output.content)
        # Remove newlines before lowercase latters.
        self.output.content = re.sub(r"\n+(?=[a-z])", "", self.output.content)
        # Remove newlines between list and preceeding paragraph.
        self.output.content = re.sub(r"\n+(?= {2}\*)", "\n", self.output.content)

    def postprocess_metadata(self) -> None:

        def get_headline(entry: dict):
            if headline := entry.get('headline'):
                headline = re.sub("&quot;", "``", headline, count=1)
                headline = re.sub("&quot;", "''", headline, count=1)
                self.output.title = headline

        def get_pub_date(entry: dict):
            if pub_date := entry.get('datePublished'):
                try:
                    self.output.pub_date = datetime.fromisoformat(pub_date)
                except ValueError as e:
                    logging.error(str(e))

        def get_mod_date(entry: dict):
            if mod_date := entry.get('dateModified'):
                try:
                    self.output.last_updated = datetime.fromisoformat(mod_date)
                except ValueError as e:
                    logging.error(str(e))

        def get_author(entry: dict):
            # if author_element := entry.get('author'):
            if isinstance(entry, dict):
                self.output.author = entry['name']
            elif isinstance(entry, list):
                self.output.author = " and ".join(author['name'] for author in entry)
            else:
                raise NotImplementedError(f"author of type `{type(entry)}` not (yet) supported.")

        # if '@graph' in self.output.metadata:
        #     for item in self.output.metadata['@graph']:
        #         if item['@type'] == 'Person':
        #             self.output.author = item['name']
        #         if item['@type'] == 'BlogPosting':
        #             self.output.title = item['headline']
        #             self.output.pub_date = datetime.fromisoformat(item['datePublished'])
        #             self.output.last_updated = datetime.fromisoformat(item['dateModified'])

        if person := self.output.metadata.get('Person'):
            get_author(person)

        if blog_posting := self.output.metadata.get('BlogPosting'):
            get_headline(blog_posting)
            get_pub_date(blog_posting)
            get_mod_date(blog_posting)

        if news := self.output.metadata.get('NewsArticle'):
            if author := news.get('author'):
                get_author(author)
            get_headline(news)
            get_pub_date(news)
            get_mod_date(news)

            if url := news.get('url'):
                self.output.url = url
            elif mainEntityOfPage := news.get('mainEntityOfPage'):
                if isinstance(mainEntityOfPage, str) and 'http' in mainEntityOfPage:
                    self.output.url = mainEntityOfPage
                elif url := mainEntityOfPage.get('url'):
                    self.output.url = url

    def remove_extra_metadata(self):
        for tag in ['@context', '@type', 'articleSection', 'hasPart',
                    'image', 'publisher', 'isAccessibleForFree',
                    'mainEntityOfPage'] + ['itemListElement', 'keywords']:
            if tag in self.output.metadata:
                self.output.metadata.pop(tag)
