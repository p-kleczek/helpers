import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import auto, Enum
from html.parser import HTMLParser
from typing import List, Optional, Tuple, Dict, Union, Pattern


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


class BasicHTMLParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.level: int = 0
        self.tag_no = 0
        self.tag_hierarchy: List[TagEntry] = []
        self.stop_processing: bool = False
        "No further tags should be (actively) processed."

    @property
    def current_tag(self) -> Optional[TagEntry]:
        return self.tag_hierarchy[-1] if self.tag_hierarchy else None

    @staticmethod
    def get_tags_to_ignore() -> List[TagData]:
        return [
            TagData(tag='img', attrs={}),
            TagData(tag='button', attrs={}),
            TagData(tag='figcaption', attrs={}),
            TagData(tag='script', attrs={'type': 'text/javascript'}),
            TagData(tag='script', attrs=None),
            TagData(tag='picture', attrs=None),
        ]

    @staticmethod
    def get_tags_with_suppressed_validation() -> List[TagData]:
        """Tags for which no 'unhandled' error should be issued."""
        return [
            TagData(tag='i', attrs={}),
        ]

    @staticmethod
    def parse_attrs(attrs_as_list: List[Tuple]) -> Dict[str, str]:
        return {k: v for k, v in attrs_as_list}

    def handle_startendtag(self, tag, attrs):
        self.tag_no += 1

        tabs: str = "".join(self.level * ['  '])
        status_str: str = "P"
        logging.debug(f"{tabs}{tag}(/) <{status_str}> {self.parse_attrs(attrs)}")

        current_tag = TagData(tag=tag, attrs=self.parse_attrs(attrs))

        self.process_startendtag(current_tag)

    def process_startendtag(self, tag: TagData) -> None:
        pass

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)

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

        if self.is_ignored_in_hierarchy():
            return

        self.process_starttag()

    def process_starttag(self):
        """Implements custom logic related to processing the start tag."""
        pass

    def handle_endtag(self, tag):
        if not (self.stop_processing or self.is_ignored_in_hierarchy()):
            self.process_endtag()

        self.level -= 1
        tabs: str = "".join(self.level * ['  '])
        logging.debug(f"{tabs}/{tag} {self.tag_hierarchy[-1].td.attrs}")
        self.tag_hierarchy.pop()

    def process_endtag(self):
        pass

    def handle_data(self, data):
        super().handle_data(data)
        if not self.tag_hierarchy:
            return
        self.tag_hierarchy[-1].td.data = data

        self.process_data()

    def process_data(self):
        pass

    def check_ignored_tag(self, last_tag: TagData, data: str) -> None:
        if self.is_tag_match(last_tag, self.get_tags_to_ignore() + self.get_tags_with_suppressed_validation()):
            return
        raise ValueError(f"Unknown tag: {last_tag.tag} {last_tag.attrs} D=`{data}`")

    @staticmethod
    def is_tag_match(td: TagData, td_list: List[TagData]) -> bool:
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

    def feed(self, data: str) -> None:
        super().feed(data)
        self.postprocess_metadata()

    def postprocess_metadata(self) -> None:
        pass
