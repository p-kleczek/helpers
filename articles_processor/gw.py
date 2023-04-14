import json
import os
import pprint
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, StrEnum
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Dict

from bibtex.bibtex_key_generator import generate_bibtex_key

# ============================================================================

input_dir: Path = Path('input/')
input_dir: Path = Path('/media/pawel/data/My Downloads/~ DOŚĆ Milczenia/')
input_file_path: Path = input_dir / "gw2.html"
input_file_path: Path = input_dir / "Czy mnie dziwi, że na rekolekcjach w Toruniu gość jak patostreamer bije kobietę Ani trochę.html"


# ============================================================================

class OutputData:
    title: str = ""
    author: str = ""
    pub_date: datetime = None
    "Publication date"
    last_updated: datetime = None
    "Last update date"
    charset: str = None
    description: str = ""
    "Article description/subtitle"
    content: str = ""
    "Content of the article"
    metadata: dict = ""
    url: str = ""
    "Article's URL."
    links: List[str] = []

    def __str__(self):
        links_str: str = ''.join(
            f"L{inx + 1} \t{link}\n" for inx, link in enumerate(self.links)) if self.links else "--"
        was_updated: bool = (self.last_updated.strftime('%Y-%m-%d') != self.pub_date.strftime('%Y-%m-%d')
                             if self.last_updated and self.pub_date else False)

        pub_date = self.pub_date.strftime('%Y-%m-%d') if self.pub_date else "?"
        last_update = (self.last_updated.strftime('%Y-%m-%d') if was_updated else '--') if self.last_updated else "?"

        return "\n".join([
            f"TITLE: {self.title}",
            f"URL: {self.url}",
            f"AUTHOR(s): {self.author}",
            f"PUB_DATE: {pub_date}",
            f"LAST_UPDATE: {last_update}",
            "",
            f"CHARSET: {self.charset}",
            f"DESCRIPTION: {self.description}",
            f"METADATA:\n{pprint.pformat(self.metadata)}",
            "",
            f"CONTENT:\n\n{self.content}",
            "",
            f"LINKS: \n{links_str}",
        ])


output: OutputData = OutputData()


@dataclass
class TagData:
    tag: str
    attrs: dict


tag_hierarchy: List[TagData] = []


def is_content() -> bool:
    return any(td.tag == 'div' and 'class' in td.attrs
               and (td.attrs['class'] == 'paywall' or 'article--content' in td.attrs['class'])
               for td in tag_hierarchy)


def is_embedded_text() -> bool:
    return any(td.tag == 'div' and 'class' in td.attrs and 'text--embed' in td.attrs['class'] for td in tag_hierarchy)


def remove_nbsps(s: str) -> str:
    return s.replace("\u00a0", " ")


class MyHTMLParser(HTMLParser):
    @staticmethod
    def is_text_paragraph(tag_data: TagData) -> bool:
        return tag_data.tag == 'p' and tag_data.attrs.get('class', None) == 'text--paragraph'

    @staticmethod
    def is_block_quote(tag_data: TagData) -> bool:
        return tag_data.tag == 'blockquote' and 'class' in tag_data.attrs and 'text--quote' in tag_data.attrs['class']

    @staticmethod
    def is_question(tag_data: TagData) -> bool:
        return tag_data.tag == 'h4' and 'class' in tag_data.attrs and 'text--question' in tag_data.attrs['class']

    @staticmethod
    def is_header(tag_data: TagData) -> bool:
        return (re.fullmatch(r"h\d", tag_data.tag)
                and 'class' in tag_data.attrs
                and 'text--title' in tag_data.attrs['class'])

    def handle_starttag(self, tag, attrs):
        current_tag: TagData = TagData(tag=tag, attrs={k: v for k, v in attrs})
        tag_hierarchy.append(current_tag)

        if tag == "meta":
            if charset := current_tag.attrs.get('charset', None):
                output.charset = charset
            if 'pubdate' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                output.pub_date = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'lastupdated' == current_tag.attrs.get('name', None):
                date = current_tag.attrs.get('content', None)
                output.last_updated = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            if 'Description' == current_tag.attrs.get('name', None):
                desc = current_tag.attrs.get('content', None)
                output.description = desc

        is_social_media_link: bool = is_embedded_text() and tag == 'a' and 'href' in current_tag.attrs
        if is_social_media_link:
            output.content += f"EMBED:\n{current_tag.attrs['href']}\n\n"

        if self.is_question(current_tag):
            output.content += "Q: "

    def handle_endtag(self, tag):
        last_tag = tag_hierarchy[-1]
        if is_content():
            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                output.content += '\n\n'
            if self.is_block_quote(last_tag):
                output.content += '\n'

        tag_hierarchy.pop()

    def handle_data(self, data):
        if not tag_hierarchy:
            return
        last_tag = tag_hierarchy[-1]
        if last_tag.tag == "title":
            output.title += data
        if last_tag.tag == "script" and 'application/ld+json' == last_tag.attrs.get('type', None):
            output.metadata = json.loads(data)

        if is_content():
            if self.is_text_paragraph(last_tag) or self.is_question(last_tag):
                output.content += data

            if self.is_block_quote(last_tag):
                output.content += re.sub(r"^\n\s+", "", data)

            if self.is_header(last_tag):
                is_isolated_header: bool = data[-1] in ".?!"
                if is_isolated_header:
                    output.content += "H: "
                output.content += data.rstrip()
                output.content += "\n\n" if is_isolated_header else " "

            is_link_to_another_article: bool = (last_tag.tag == 'a'
                                                and 'class' in last_tag.attrs
                                                and 'text--link' in last_tag.attrs['class'])
            if is_link_to_another_article:
                href: str = last_tag.attrs['href']
                output.links.append(re.sub("#.*$", "", href))
                output.content += f"{data}[L{len(output.links)}]"


charsets = ["UTF-8", "ISO-8859-2"]

for charset in charsets:
    try:
        with open(input_file_path, encoding=charset) as f:
            file_content = f.readlines()
    except UnicodeDecodeError:
        continue


def remove_extra_metadata():
    for tag in ['@context', '@type', 'articleSection', 'hasPart',
                'image', 'publisher', 'isAccessibleForFree',
                'mainEntityOfPage']:
        output.metadata.pop(tag)

    for author in output.metadata['author']:
        author.pop('url')


parser = MyHTMLParser()
parser.feed(''.join(file_content))

output.title = output.title.strip()
output.author = ", ".join(author['name'] for author in output.metadata['author'])
output.url = output.metadata['mainEntityOfPage']['url']

pub_date_meta_str = output.metadata['datePublished']
pub_date_meta = datetime.fromisoformat(pub_date_meta_str)
if output.pub_date:
    assert output.pub_date.date() == pub_date_meta.date()
else:
    output.pub_date = pub_date_meta

mod_date_meta_str = output.metadata['dateModified']
mod_date_meta = datetime.fromisoformat(mod_date_meta_str)
if output.last_updated:
    assert output.last_updated.date() == mod_date_meta.date()
else:
    output.last_updated = mod_date_meta

remove_extra_metadata()

print(output)

output.content = remove_nbsps(output.content)
output.content = output.content.replace("„", '"')
output.content = output.content.rstrip()


class Publishers(StrEnum):
    WYBORCZA = "Gazeta Wyborcza"


def get_publisher(url: str) -> str:
    publisher: str = ""
    if 'wyborcza.pl' in url:
        publisher = Publishers.WYBORCZA

        subtypes: Dict[str, str] = {
            'duzyformat': "Duży Format",
            'torun': "Toruń",
        }

        for url_chunk, subtype in subtypes.items():
            if f"/{url_chunk}/" in url:
                return f"{publisher} ({subtype})"
        return publisher

    if 'wysokieobcasy.pl' in url:
        return f"{Publishers.WYBORCZA} (Wysokie Obcasy)"

    raise ValueError(f"Undefined publisher for URL: {url}")


with open("misc_template.txt") as f:
    template = "".join(f.readlines())

output_filepath = Path("output") / f"{input_file_path.stem}.txt"
with open(output_filepath, "w", encoding="UTF-8") as f:
    publisher_id = 'gw'
    f.write(template.format(
        label=f"{generate_bibtex_key(output.title)}_{publisher_id}_{output.pub_date.strftime('%Y_%m_%d')}",
        author=output.author,
        publisher=get_publisher(output.url),
        title=output.title,
        pubdate=output.pub_date.strftime('%Y-%m-%d'),
        url=output.url,
    ))
    f.write("\n------\n")
    f.write(str(output))
