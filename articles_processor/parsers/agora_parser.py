import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import ClassVar, List

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData, TagStatus


class AgoraHTMLParser(ArticleHTMLParser, ABC):
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

    def process_starttag(self):
        current_tag = self.tag_hierarchy[-1].td

        if current_tag.tag == "meta":
            if 'pubdate' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                self.output.pub_date = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'lastupdated' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                self.output.last_updated = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'Description' == current_tag.attrs.get('name', None):
                desc = current_tag.attrs.get('content', None)
                self.output.description = desc

        is_social_media_link: bool = (self.is_embedded_text()
                                      and current_tag.tag == 'a' and 'href' in current_tag.attrs)
        if is_social_media_link:
            self.output.content += f"EMBED:\n{current_tag.attrs['href']}\n\n"

        if self.is_question(current_tag):
            self.output.content += self.quote_marker

    def process_endtag(self):
        last_tag = self.tag_hierarchy[-1].td
        if self.is_content():
            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                self.output.content += '\n\n'
            if self.is_block_quote(last_tag):
                self.output.content += '\n'

    def process_data(self):
        last_tag = self.tag_hierarchy[-1].td
        if last_tag.tag == "title":
            self.output.title += last_tag.cleaned_data

        if self.is_content():
            if any(last_tag.data.startswith(s) for s in ['CZTAJ TAKŻE:', 'POLECAMY']):
                self.tag_hierarchy[-1].status = TagStatus.IGNORED
                return

            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                self.output.content += last_tag.cleaned_data
                return

            if self.is_block_quote(last_tag):
                self.output.content += re.sub(r"^\n\s+", "", last_tag.cleaned_data)
                return

            if self.is_header(last_tag):
                # is_isolated_header: bool = last_tag.cleaned_data[-1] in ".?!"
                # if is_isolated_header:
                #     self.output.content += self.header_marker
                self.output.content += self.header_marker
                self.output.content += last_tag.cleaned_data.rstrip()
                self.output.content += "\n\n"  # if is_isolated_header else " "
                return

            if last_tag.tag == 'a':
                if self.is_link_to_another_article(last_tag):
                    href: str = last_tag.attrs['href']
                    self.output.links.append(re.sub("#.*$", "", href))
                    self.output.content += f"{last_tag.cleaned_data}[L{len(self.output.links)}]"
                else:
                    self.output.content += last_tag.cleaned_data
                return

            self.check_ignored_tag(last_tag, last_tag.data)

    tags_to_ignore_recursively: ClassVar[List[TagData]] = [
        TagData(tag='span', attrs={'class': 'banLabel'}),
        TagData(tag='div', attrs={'id': '-ADBOARD-'}),
    ]

    tags_to_ignore_individually: ClassVar[List[TagData]] = [
        # TagData(tag='h2', attrs={}),
        # TagData(tag='div', attrs={'class': 'quote-socials'}),
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return (super().get_tags_to_ignore()
                + AgoraHTMLParser.tags_to_ignore_recursively
                + AgoraHTMLParser.tags_to_ignore_individually)

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={'class': 'article--content'}),
            TagData(tag='div', attrs={'class': 'paywall'}),
        ]

    def feed(self, data: str) -> None:
        super().feed(data)

    def postprocess_metadata(self) -> None:
        super().postprocess_metadata()
        # self.output.author = " and ".join(author['name'] for author in self.output.metadata['author'])
        # self.output.url = self.output.metadata['mainEntityOfPage']['url']

    def remove_extra_metadata(self):
        pass
        # for author in self.output.metadata['author']:
        #     for tag in ['url', 'description']:
        #         if tag in author:
        #             author.pop(tag)


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
        return 'art_interview_question'

    @staticmethod
    def get_header_class() -> str:
        raise NotImplementedError
        # return 'text--title'

    @staticmethod
    def get_text_link_class() -> str:
        return 'art_link'

    tags_to_ignore: ClassVar[List[TagData]] = [
        TagData(tag='div', attrs={'id': 'adUnit-'}),
        TagData(tag='div', attrs={'class': 'art_embed'}),
        TagData(tag='span', attrs={'class': 'imageUOM'}),
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return super().get_tags_to_ignore() + WysokieObcasyHTMLParser.tags_to_ignore

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={'id': 'wo_article_body'}),
            TagData(tag='div', attrs={'class': 'paywall'}),
            TagData(tag='section', attrs={'class': 'art_content', 'itemprop': 'articleSection'}),
        ]

    def should_stop_processing(self) -> bool:
        last_tag = self.tag_hierarchy[-1].td
        return (last_tag.tag == 'section'
                and 'class' in last_tag.attrs
                and (last_tag.attrs['class'] == 'article-publio'))


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

    tags_to_ignore_recursively: ClassVar[List[TagData]] = [
        TagData(tag='div', attrs={'class': 'adview'}),
        TagData(tag='div', attrs={'class': 'text--embed'}),
        # TagData(tag='div', attrs={'class': 'text--photo'}),
        TagData(tag='div', attrs={'class': 'container mt+++'}),
    ]

    tags_to_ignore_individually: ClassVar[List[TagData]] = [
        # TagData(tag='h2', attrs={}),
        # TagData(tag='div', attrs={'class': 'quote-socials'}),
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return (super().get_tags_to_ignore()
                + WyborczaHTMLParser.tags_to_ignore_recursively
                + WyborczaHTMLParser.tags_to_ignore_individually)

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={'class': 'text--photo'}),
            TagData(tag='figure', attrs={'class': 'a-image'}),
            TagData(tag='span', attrs={'class': 'text--photo-title'}),
            TagData(tag='span', attrs={'class': 'text--photo-author'}),
        ]

    def should_stop_processing(self) -> bool:
        last_tag = self.tag_hierarchy[-1].td
        return (last_tag.tag == 'div'
                and 'class' in last_tag.attrs
                and (last_tag.attrs['class'] == 'article--postcontent'))
