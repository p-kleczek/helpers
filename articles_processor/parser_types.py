import logging
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum, auto
from typing import List, Dict, Set

dummy_date = date(9999, 1, 1)


class DataError(Enum):
    NO_URL = auto()
    NO_TITLE = auto()
    NO_AUTHOR = auto()
    NO_PUB_DATE = auto()


@dataclass
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
    source: str = None
    "Kto jest autorem oryginalnej informacji?"
    content: str = ""
    "Content of the article"
    metadata: Dict[str, dict] = field(default_factory=dict)
    """A dictionary of <script type="application/ld+json"> tags.
    `@type` value is a key and the whole dictionary is the value.
    """
    url: str = ""
    "Article's URL."
    links: List[str] = field(default_factory=list)
    errors: Set[DataError] = field(default_factory=set)

    def print(self, full: bool) -> str:
        links_str: str = ''.join(
            f"L{inx + 1} \t{link}\n" for inx, link in enumerate(self.links)) if self.links else "--"
        was_updated: bool = (self.last_updated.strftime('%Y-%m-%d') != self.pub_date.strftime('%Y-%m-%d')
                             if self.last_updated and self.pub_date else False)

        pub_date = self.pub_date.strftime('%Y-%m-%d') if self.pub_date else "?"
        last_update = (self.last_updated.strftime('%Y-%m-%d') if was_updated else '--') if self.last_updated else "?"

        import pprint

        return "\n".join([
            f"TITLE: {self.title}",
            f"URL: {self.url}",
            f"AUTHOR(s): {self.author}",
            f"PUB_DATE: {pub_date}",
            f"LAST_UPDATE: {last_update}",
            f"SOURCE: {self.source or '--'}",
            "",
            f"CHARSET: {self.charset}" if full else "",
            f"DESCRIPTION: {self.description}" if full else "",
            f"METADATA:\n{pprint.pformat(self.metadata)}" if full else "",
            "",
            f"CONTENT:\n\n{self.content}",
            "",
            f"LINKS: \n{links_str}",
        ])

    def __str__(self):
        return self.print(full=True)

    def verify_data(self):
        if not self.url:
            logging.error("No URL was assigned to the article!")
            self.url = "URL"
            self.errors.add(DataError.NO_URL)

        if not self.author:
            logging.error("Unknown author!")
            self.author = "AUTHOR"
            self.errors.add(DataError.NO_AUTHOR)

        if not self.title:
            logging.error("Unknown title!")
            self.title = "TITLE"
            self.errors.add(DataError.NO_TITLE)

        if not self.pub_date:
            logging.error("Unknown publication date!")
            self.pub_date = datetime(year=dummy_date.year, month=dummy_date.month, day=dummy_date.day)
            self.errors.add(DataError.NO_PUB_DATE)
