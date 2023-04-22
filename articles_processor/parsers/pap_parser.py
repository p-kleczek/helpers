import re
from abc import ABC
from datetime import datetime
from typing import ClassVar, List

from articles_processor.parsers.base_parser import ArticleHTMLParser, TagData


class PapHTMLParser(ArticleHTMLParser, ABC):
    @staticmethod
    def is_contnet_tag(tag_data: TagData) -> bool:
        return ((tag_data.tag == 'article'
                 and 'role' in tag_data.attrs
                 and 'article' in tag_data.attrs['role'])
                or (tag_data.tag == 'div'
                    and 'class' in tag_data.attrs
                    and 'cg_article_printed_info' in tag_data.attrs['class']))

    @staticmethod
    def is_article_lead(tag_data: TagData) -> bool:
        return (tag_data.tag == 'div'
                and 'class' in tag_data.attrs
                and 'field--name-field-lead' in tag_data.attrs['class'])

    @staticmethod
    def is_text_paragraph(tag_data: TagData) -> bool:
        return tag_data.tag == 'p'

    def is_block_quote(self, tag_data: TagData) -> bool:
        return tag_data.tag == 'blockquote'

    @staticmethod
    def is_header(tag_data: TagData) -> bool:
        return re.fullmatch(r"h\d", tag_data.tag) is not None

    @staticmethod
    def is_link_to_another_article(tag_data: TagData) -> bool:
        return tag_data.tag == 'a'

    def process_startendtag(self, tag: TagData) -> None:
        if tag.tag == 'meta' and tag.attrs.get('property') == "og:title":
            self.output.title = tag.attrs['content']

    def process_starttag(self):
        pass
        # current_tag = self.tag_hierarchy[-1].td

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
    ]

    def get_tags_to_ignore(self) -> List[TagData]:
        return super().get_tags_to_ignore() + self.tags_to_ignore

    def get_tags_with_suppressed_validation(self) -> List[TagData]:
        return super().get_tags_with_suppressed_validation() + [
            TagData(tag='div', attrs={}),
        ]

    def handle_data(self, data):
        if m := re.fullmatch(r'\s*(?P<timestamp>\d{4}-\d{2}-\d{2} \d{1,2}:\d{2})\s*', data):
            self.output.pub_date = datetime.strptime(m.group('timestamp'), "%Y-%m-%d %H:%M")

        if m := re.fullmatch(r'aktualizacja: \s*(?P<timestamp>\d{4}-\d{2}-\d{2}, \d{1,2}:\d{2})\s*', data):
            fixed_timestamp = m.group('timestamp').replace(",", "")
            self.output.last_updated = datetime.strptime(fixed_timestamp, "%Y-%m-%d %H:%M")

        super().handle_data(data)

    def process_data(self):
        last_tag = self.tag_hierarchy[-1].td

        if self.is_content():
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
                if last_tag.data.startswith('Autor:'):
                    self.output.author = last_tag.data.replace("Autor: ", "")
                    return

                self.output.content += last_tag.cleaned_data
                return

            if self.is_block_quote(last_tag):
                self.output.content += re.sub(r"^\n\s+", "", last_tag.cleaned_data)
                return

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
                and ('field--name-field-tags' in last_tag.attrs['class']))

    def postprocess_metadata(self) -> None:
        super().postprocess_metadata()
        if not self.output.author:
            self.output.author = "(PAP)"
