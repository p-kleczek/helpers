from abc import ABC
from typing import List

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData


class DefaultHTMLParser(ArticleHTMLParser, ABC):
    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return False

    def process_starttag(self):
        pass

    def process_endtag(self):
        pass

    def get_tags_to_ignore(self) -> List[TagData]:
        return []

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + []

    def process_data(self):
        return
