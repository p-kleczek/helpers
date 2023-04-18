import json
import re
from abc import ABC
from datetime import datetime
from typing import List, ClassVar

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData


class WiezHTMLParser(ArticleHTMLParser, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curent_blockquote: List[str] = []

    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'class' in tag_data.attrs
                and 'single__post__content' in tag_data.attrs['class'])

    @staticmethod
    def is_text_paragraph(tag_data: TagData) -> bool:
        return tag_data.tag == 'p'

    @staticmethod
    def is_block_quote(tag_data: TagData) -> bool:
        # 'quote-text-box'
        return (tag_data.tag == 'blockquote'
                and 'class' in tag_data.attrs
                and 'quote' in tag_data.attrs['class'])

    # @staticmethod
    # @abstractmethod
    # def get_question_class():
    #     raise NotImplementedError
    #
    # def is_question(self, tag_data: TagData) -> bool:
    #     return (tag_data.tag == 'h4'
    #             and 'class' in tag_data.attrs
    #             and self.get_question_class() in tag_data.attrs['class'])

    @staticmethod
    def is_header(tag_data: TagData) -> bool:
        return re.fullmatch(r"h3", tag_data.tag) is not None and not tag_data.attrs

    @staticmethod
    def is_link_to_another_article(tag_data: TagData) -> bool:
        return tag_data.tag == 'a'

    def process_starttag(self):
        current_tag = self.tag_hierarchy[-1].td

        if current_tag.tag == "meta":
            if charset := current_tag.attrs.get('charset', None):
                self.output.charset = charset.lower()

        is_social_media_link: bool = self.is_embedded_text() and current_tag.tag == 'a' and 'href' in current_tag.attrs
        if is_social_media_link:
            self.output.content += f"EMBED:\n{current_tag.attrs['href']}\n\n"

        # if tag == 'link' and current_tag.attrs.get('rel') == 'canonical':
        #     self.output.url = current_tag.attrs['href']

        # if self.is_question(current_tag):
        #     self.output.content += "Q: "

    def process_endtag(self):
        last_tag = self.tag_hierarchy[-1]

        if (not self.stop_processing
                and not self.is_ignored_in_hierarchy()
                and self.is_content()):
            if self.is_block_quote(last_tag.td):
                self.output.content += f"[Q] {self.curent_blockquote[1]}: {self.curent_blockquote[0]}\n\n"
                self.curent_blockquote = []
            elif self.is_text_paragraph(last_tag.td) and not self.is_part_of_blockquote():
                self.output.content += '\n\n'

    tags_to_ignore_recursively: ClassVar[List[TagData]] = [
        TagData(tag='aside', attrs={}),
        TagData(tag='figure', attrs={}),
    ]

    tags_to_ignore_individually: ClassVar[List[TagData]] = [
        TagData(tag='aside', attrs={}),
        TagData(tag='figure', attrs={}),
        TagData(tag='h2', attrs={}),
        TagData(tag='div', attrs={'class': 'quote-socials'}),
    ]

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='blockquote', attrs={'class': 'quote-box'}),
            TagData(tag='div', attrs={'class': 'quote-content'}),
            TagData(tag='div', attrs={'class': 'quote-text-box'}),
        ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return (super().get_tags_to_ignore()
                + WiezHTMLParser.tags_to_ignore_recursively
                + WiezHTMLParser.tags_to_ignore_individually)

    # def handle_startendtag(self, tag, attrs):
    #     if self.stop_processing:
    #         return
    #
    #     TagData(tag=tag, attrs=self.parse_attrs(attrs))
    #
    #     if self.is_ignored_tag():
    #         return
    #
    #     attrs_dict = self.parse_attrs(attrs)
    #     if tag == 'link' and attrs_dict.get('rel') == 'canonical':
    #         self.output.url = attrs_dict['href']

    def is_part_of_blockquote(self):
        blockquote_tag: TagData = TagData(tag='blockquote', attrs={})
        for th_td in self.tag_hierarchy:
            is_same_tag: bool = (blockquote_tag.tag == th_td.td.tag)
            has_same_attrs: bool = all(attr in th_td.td.attrs and val in th_td.td.attrs[attr]
                                       for attr, val in blockquote_tag.attrs.items())
            if is_same_tag and has_same_attrs:
                return True
        return False

    def process_data(self):
        last_tag = self.tag_hierarchy[-1].td

        if self.stop_processing or self.is_ignored_in_hierarchy():
            return

        if last_tag.tag == "title":
            self.output.title += last_tag.cleaned_data
            return
        if last_tag.tag == "script" and 'application/ld+json' == last_tag.attrs.get('type'):
            self.output.metadata.update(json.loads(last_tag.data))
            return

        if self.is_content():
            if self.is_part_of_blockquote() and last_tag.tag == 'p':
                self.curent_blockquote.append(last_tag.cleaned_data)
                return

            if self.is_text_paragraph(last_tag):
                self.output.content += last_tag.cleaned_data
                return

            if self.is_header(last_tag):
                self.output.content += f"[H] {last_tag.cleaned_data.rstrip()}\n\n"
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

    def check_ignored_tag(self, last_tag: TagData, data: str) -> None:
        if self.is_contnet_tag(last_tag):
            return
        super().check_ignored_tag(last_tag=last_tag, data=data)

    def postprocess_metadata(self) -> None:
        for item in self.output.metadata['@graph']:
            if item['@type'] == 'Person':
                self.output.author = item['name']
            if item['@type'] == 'BlogPosting':
                self.output.title = item['headline']
                self.output.pub_date = datetime.fromisoformat(item['datePublished'])
                self.output.last_updated = datetime.fromisoformat(item['dateModified'])
