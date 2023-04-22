import json
import re
from abc import ABC
from datetime import datetime
from typing import ClassVar, List

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData


# FIXME: work in progress...
class OnetHTMLParser(ArticleHTMLParser, ABC):
    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'class' in tag_data.attrs
                and 'whitelistPremium' in tag_data.attrs['class'])

    @staticmethod
    def is_article_lead(tag_data: TagData) -> bool:
        return tag_data.tag == 'div' and tag_data.attrs.get('id') == 'lead'

    @staticmethod
    def is_text_paragraph(tag_data: TagData) -> bool:
        return tag_data.tag == 'p'

    # @staticmethod
    # @abstractmethod
    # def get_block_quote_class():
    #     raise NotImplementedError
    #
    # def is_block_quote(self, tag_data: TagData) -> bool:
    #     return (tag_data.tag == 'blockquote'
    #             and 'class' in tag_data.attrs
    #             and self.get_block_quote_class() in tag_data.attrs['class'])
    #
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
        return re.fullmatch(r"h\d", tag_data.tag) is not None

    @staticmethod
    def is_link_to_another_article(tag_data: TagData) -> bool:
        return tag_data.tag == 'a'

    def process_starttag(self):
        current_tag = self.tag_hierarchy[-1].td

        # if current_tag.tag == "meta":
        #     if charset := current_tag.attrs.get('charset', None):
        #         self.output.charset = charset
        #     if 'pubdate' == current_tag.attrs.get('name', None):
        #         date = current_tag.attrs.get('content', None)
        #         self.output.pub_date = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
        #     if 'lastupdated' == current_tag.attrs.get('name', None):
        #         date = current_tag.attrs.get('content', None)
        #         self.output.last_updated = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
        #     if 'Description' == current_tag.attrs.get('name', None):
        #         desc = current_tag.attrs.get('content', None)
        #         self.output.description = desc

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

    tags_to_ignore: ClassVar[List[TagData]] = [
        TagData(tag='figure', attrs={'class': 'mainPhoto'}),
        TagData(tag='aside', attrs={'class': 'extraList'}),
        TagData(tag='div', attrs={'class': 'contentShareLeft'}),
        TagData(tag='div', attrs={'class': 'pulsevideo'}),
        TagData(tag='div', attrs={'class': {'placeholder', 'embed'}}),
        TagData(tag='ul', attrs={'class': 'narrow', 'data-scroll': 'bullet'}),
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return super().get_tags_to_ignore() + self.tags_to_ignore

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={'id': 'leadContainer'}),
            TagData(tag='div', attrs={'class': 'detailContentWrapper'}),
            TagData(tag='div', attrs={'class': 'detailContent'}),
            TagData(tag='div', attrs={'class': 'articleBody'}),
            # TagData(tag='div', attrs={'class': 'cg_article_side-audio-wrapper'}),
            # TagData(tag='div', attrs={'class': 'cg_article_printed_info'}),
        ]

    def process_italics_data(self, tag_data: TagData) -> None:
        if 'Dalsza część artykułu pod materiałem wideo' in tag_data.data:
            return
        super().process_italics_data(tag_data)

    def process_data(self):
        last_tag = self.tag_hierarchy[-1].td

        # if last_tag.tag == "title":
        #     self.output.title += last_tag.cleaned_data

        if self.is_content():

            if last_tag.tag == 'em' and last_tag.data.startswith('Źródło:'):
                self.output.source = last_tag.data.replace('Źródło: ', "")
                return

            if self.is_contnet_tag(last_tag):
                if last_tag.data.strip():
                    data = last_tag.cleaned_data
                    data = re.sub("\n", " ", data)
                    data = re.sub(" +", " ", data)
                    self.output.content += data
                return

            if self.is_article_lead(last_tag):
                last_tag.data = last_tag.data.rstrip()

            if any(te.td.tag == 'em' and 'Czytaj też:' in te.td.data for te in self.tag_hierarchy):
                return

            if self.is_text_paragraph(last_tag) or self.is_article_lead(last_tag):
                self.output.content += last_tag.cleaned_data
                return

            # if self.is_block_quote(last_tag):
            #     self.output.content += re.sub(r"^\n\s+", "", data)
            #     return

            if self.is_header(last_tag):
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

            self.check_ignored_tag(last_tag, last_tag.data)

    def should_stop_processing(self) -> bool:
        last_tag = self.tag_hierarchy[-1].td
        return (last_tag.tag == 'div'
                and 'class' in last_tag.attrs
                and (last_tag.attrs['class'] == 'afterDetailModules'))

    def postprocess_metadata(self) -> None:
        super().postprocess_metadata()
        if 'Onet' in self.output.author:
            self.output.author = f"({self.output.author})"
