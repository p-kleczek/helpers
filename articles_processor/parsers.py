import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from typing import List

from articles_processor.types import OutputData


@dataclass
class TagData:
    tag: str
    attrs: dict


tag_hierarchy: List[TagData] = []


def is_embedded_text() -> bool:
    return any(td.tag == 'div' and 'class' in td.attrs and 'text--embed' in td.attrs['class'] for td in tag_hierarchy)


class ArticleHTMLParser(HTMLParser, ABC):
    def __init__(self, output: OutputData):
        super().__init__()
        self.output = output


class AgoraHTMLParser(ArticleHTMLParser, ABC):
    @staticmethod
    @abstractmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        raise NotImplementedError

    def is_content(self) -> bool:
        return any(self.is_contnet_tag(td) for td in tag_hierarchy)

    @staticmethod
    @abstractmethod
    def get_text_paragraph_class():
        raise NotImplementedError

    def is_text_paragraph(self, tag_data: TagData) -> bool:
        return tag_data.tag == 'p' and tag_data.attrs.get('class', None) == self.get_text_paragraph_class()

    @staticmethod
    @abstractmethod
    def get_block_quote_class():
        raise NotImplementedError

    def is_block_quote(self, tag_data: TagData) -> bool:
        return (tag_data.tag == 'blockquote'
                and 'class' in tag_data.attrs
                and self.get_block_quote_class() in tag_data.attrs['class'])

    @staticmethod
    @abstractmethod
    def get_question_class():
        raise NotImplementedError

    def is_question(self, tag_data: TagData) -> bool:
        return (tag_data.tag == 'h4'
                and 'class' in tag_data.attrs
                and self.get_question_class() in tag_data.attrs['class'])

    @staticmethod
    @abstractmethod
    def get_header_class():
        raise NotImplementedError

    def is_header(self, tag_data: TagData) -> bool:
        return (re.fullmatch(r"h\d", tag_data.tag)
                and 'class' in tag_data.attrs
                and self.get_header_class() in tag_data.attrs['class'])

    @staticmethod
    @abstractmethod
    def get_text_link_class() -> str:
        raise NotImplementedError

    def is_link_to_another_article(self, tag_data: TagData) -> bool:
        return (tag_data.tag == 'a'
                and 'class' in tag_data.attrs
                and self.get_text_link_class() in tag_data.attrs['class'])

    def handle_starttag(self, tag, attrs):
        current_tag: TagData = TagData(tag=tag, attrs={k: v for k, v in attrs})
        tag_hierarchy.append(current_tag)

        if tag == "meta":
            if charset := current_tag.attrs.get('charset', None):
                self.output.charset = charset
            if 'pubdate' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                self.output.pub_date = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'lastupdated' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                self.output.last_updated = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'Description' == current_tag.attrs.get('name', None):
                desc = current_tag.attrs.get('content', None)
                self.output.description = desc

        is_social_media_link: bool = is_embedded_text() and tag == 'a' and 'href' in current_tag.attrs
        if is_social_media_link:
            self.output.content += f"EMBED:\n{current_tag.attrs['href']}\n\n"

        if self.is_question(current_tag):
            self.output.content += "Q: "

    def handle_endtag(self, tag):
        last_tag = tag_hierarchy[-1]
        if self.is_content():
            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                self.output.content += '\n\n'
            if self.is_block_quote(last_tag):
                self.output.content += '\n'

        tag_hierarchy.pop()

    tags_to_ignore: List[TagData] = [
        TagData(tag='div', attrs={'id': 'wo_article_body'})
    ]

    def handle_data(self, data):
        if not tag_hierarchy:
            return
        last_tag = tag_hierarchy[-1]
        if last_tag.tag == "title":
            self.output.title += data
        if last_tag.tag == "script" and 'application/ld+json' == last_tag.attrs.get('type', None):
            self.output.metadata = json.loads(data)

        if self.is_content():
            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                self.output.content += data
                return

            if self.is_block_quote(last_tag):
                self.output.content += re.sub(r"^\n\s+", "", data)
                return

            if self.is_header(last_tag):
                is_isolated_header: bool = data[-1] in ".?!"
                if is_isolated_header:
                    self.output.content += "H: "
                self.output.content += data.rstrip()
                self.output.content += "\n\n" if is_isolated_header else " "
                return

            if last_tag.tag == 'a':
                if self.is_link_to_another_article(last_tag):
                    href: str = last_tag.attrs['href']
                    self.output.links.append(re.sub("#.*$", "", href))
                    self.output.content += f"{data}[L{len(self.output.links)}]"
                else:
                    self.output.content += data
                return

            for tag_data in self.tags_to_ignore:
                if (last_tag.tag == tag_data.tag
                    and all(attr in last_tag.attrs and val in last_tag.attrs[attr]
                            for attr, val in last_tag.attrs)):
                    return

            raise ValueError(f"Unknown tag: {last_tag.tag} {last_tag.attrs}")


class WysokieObcasyHTMLParser(AgoraHTMLParser):
    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'id' in tag_data.attrs
                and 'wo_article_body' in tag_data.attrs['id'])

    @staticmethod
    def get_contnet_class() -> str:
        return ''

    @staticmethod
    def get_text_paragraph_class() -> str:
        return "art_paragraph"

    @staticmethod
    def get_block_quote_class() -> str:
        return 'art_blockquote'

    @staticmethod
    def get_question_class() -> str:
        raise NotImplementedError
        # return 'text--question'

    @staticmethod
    def get_header_class() -> str:
        raise NotImplementedError
        # return 'text--title'

    @staticmethod
    def get_text_link_class() -> str:
        return 'art_link'


class WyborczaHTMLParser(AgoraHTMLParser):
    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'class' in tag_data.attrs
                and (tag_data.attrs['class'] == 'paywall' or 'article--content' in tag_data.attrs['class']))

    @staticmethod
    def get_text_paragraph_class() -> str:
        return "text--paragraph"

    @staticmethod
    def get_block_quote_class() -> str:
        return 'text--quote'

    @staticmethod
    def get_question_class() -> str:
        return 'text--question'

    @staticmethod
    def get_header_class() -> str:
        return 'text--title'

    @staticmethod
    def get_text_link_class() -> str:
        return 'text--link'
