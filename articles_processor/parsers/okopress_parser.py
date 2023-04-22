import json
import logging
import re
from abc import ABC
from datetime import datetime
from typing import ClassVar, List

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData


class OKOPressHTMLParser(ArticleHTMLParser, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'class' in tag_data.attrs
                and 'mt-16' in tag_data.attrs['class'])

    @staticmethod
    def is_article_lead(tag_data: TagData) -> bool:
        return tag_data.tag == 'div' and tag_data.attrs.get('class', None) == 'cg_article_lead'

    @staticmethod
    def is_text_paragraph(tag_data: TagData) -> bool:
        return (tag_data.tag == 'p'
                and 'class' in tag_data.attrs
                and not any(chunk in tag_data.attrs['class']
                            for chunk in ['mt-1', 'lg:mr-2']))

    @staticmethod
    def is_block_quote(tag_data: TagData) -> bool:
        return (tag_data.tag == 'blockquote'
                and 'class' in tag_data.attrs
                and 'typography__blockquote' in tag_data.attrs['class'])

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
        return re.fullmatch(r"h[1-2]", tag_data.tag) is not None
        # and not('class' in tag_data.attrs
        #         and 'mt-3' in tag_data.attrs['class']))

    @staticmethod
    def is_link_to_another_article(tag_data: TagData) -> bool:
        return tag_data.tag == 'a'

    def process_starttag(self):
        current_tag = self.tag_hierarchy[-1].td

        if current_tag.tag == "meta":
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

        is_social_media_link: bool = self.is_embedded_text() and current_tag.tag == 'a' and 'href' in current_tag.attrs
        if is_social_media_link:
            self.output.content += f"EMBED:\n{current_tag.attrs['href']}\n\n"

        # if self.is_question(current_tag):
        #     self.output.content += "Q: "

    def process_endtag(self):
        last_tag = self.tag_hierarchy[-1].td
        if self.is_content():
            if self.is_text_paragraph(last_tag) or self.is_article_lead(last_tag):
                self.output.content += '\n\n'
            # if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
            #     self.output.content += '\n\n'
            # if self.is_block_quote(last_tag):
            #     self.output.content += '\n'

    tags_to_ignore_recursively: ClassVar[List[TagData]] = [
        TagData(tag='div', attrs={'class': {'uppercase', 'items-center'}}),
        TagData(tag='div', attrs={'class': 'mt-4'}),
        TagData(tag='span', attrs={'class': 'sr-only'}),
        TagData(tag='div', attrs={'class': 'hidden'}),
        TagData(tag='div', attrs={'class': 'flex flex-col md:flex-row'}),
        TagData(tag='p', attrs={'class': {'uppercase', 'leading-4', 'text-right'}}),
    ]

    tags_to_ignore_individually: ClassVar[List[TagData]] = [
        TagData(tag='h3', attrs={}),
        TagData(tag='p', attrs={'class': 'mt-1'}),
        TagData(tag='p', attrs={'class': 'lg:mr-2'}),
        TagData(tag='div', attrs={'class': 'm-auto'}),
        TagData(tag='div', attrs={'class': {'footer-group__header', 'mb-6'}}),
        TagData(tag='span', attrs={'class': 'ml-3.5'}),
        TagData(tag='div', attrs={'class': {'mt-16', 'text-center'}}),
        TagData(tag='div', attrs={'class': {'flex', 'flex-row', 'flex-wrap'}}),
        TagData(tag='div', attrs={'class': {'ml-4', 'flex', 'flex-col'}}),
        TagData(tag='div', attrs={'class': {'mt-7', 'xl:mt-10'}}),
        TagData(tag='p', attrs={'class': 'hidden'}),
        TagData(tag='style', attrs={}),
        TagData(tag='div', attrs={'style': ''}),
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return (super().get_tags_to_ignore()
                + OKOPressHTMLParser.tags_to_ignore_recursively
                + OKOPressHTMLParser.tags_to_ignore_individually)

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={'class': 'mt-16'}),
        ]

    def process_data(self):
        last_tag = self.tag_hierarchy[-1].td

        if last_tag.tag == "title":
            self.output.title += last_tag.cleaned_data
            return
        # if last_tag.tag == "script" and 'application/ld+json' == last_tag.attrs.get('type', None):
        #     self.output.metadata.update(json.loads(last_tag.data))
        #     return

        if last_tag.tag == 'p':
            x = 1

        if self.is_content():
            if self.is_text_paragraph(last_tag) or self.is_article_lead(last_tag):
                if (self.output.content[-1] != '\n'
                        and not self.output.content.endswith(" ")):
                    self.output.content += " "
                self.output.content += last_tag.cleaned_data
                return

            if last_tag.tag == 'div' and last_tag.attrs.get('type') == 'button':
                self.output.content += f"[BUTTON] {last_tag.cleaned_data}\n"
                return

            if self.is_block_quote(last_tag):
                self.output.content += re.sub(r"^\n\s+", "", last_tag.cleaned_data)
                return

            if self.is_header(last_tag):
                if 'Przeczytaj także:' in last_tag.data:
                    # self.stop_processing = True
                    return

                if self.output.content and self.output.content[-1] != '\n':
                    self.output.content += "\n\n"

                self.output.content += f"{self.header_marker}{last_tag.cleaned_data.rstrip()}\n\n"
                return

            if last_tag.tag == 'a':
                if self.is_link_to_another_article(last_tag):
                    href: str = last_tag.attrs['href']
                    self.output.links.append(re.sub("#.*$", "", href))
                    self.output.content += f"{last_tag.cleaned_data}[L{len(self.output.links)}]"
                else:
                    self.output.content += last_tag.cleaned_data
                return

            if (last_tag.tag == 'span' and 'class' in last_tag.attrs
                    and not any(chunk in last_tag.attrs['class']
                                for chunk in ['sr-only', 'select-none',
                                              'ml-3.5'])):
                self.output.content += last_tag.cleaned_data
                logging.warning(f'span: {last_tag.data}')
                return

            # italics
            if last_tag.tag == 'i':
                self.output.content += f"//{last_tag.cleaned_data}//"
                return

            # bold
            if last_tag.tag == 'strong':
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

            self.check_ignored_tag(last_tag, last_tag.data)

    def should_stop_processing(self) -> bool:
        last_tag = self.tag_hierarchy[-1].td
        return (last_tag.tag == 'p' and 'class' in last_tag.attrs
                and 'lg:mr-2' in last_tag.attrs['class'])

    def feed(self, data: str) -> None:
        super().feed(data)

    def postprocess_metadata(self) -> None:
        super().postprocess_metadata()
        # self.output.author = self.output.metadata['author']['name']
        # self.output.title = self.output.metadata['headline']

    def remove_extra_metadata(self):
        pass
        # for tag in ['url', 'description', '@id', '@type']:
        #     if tag in self.output.metadata['author']:
        #         self.output.metadata['author'].pop(tag)
