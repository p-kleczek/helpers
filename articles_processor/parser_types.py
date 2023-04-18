from dataclasses import dataclass, field
from datetime import datetime
from typing import List


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
    content: str = ""
    "Content of the article"
    metadata: dict = field(default_factory=dict)
    url: str = ""
    "Article's URL."
    links: List[str] = field(default_factory=list)

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
            "",
            f"CHARSET: {self.charset}" if full else "",
            f"DESCRIPTION: {self.description}",
            f"METADATA:\n{pprint.pformat(self.metadata)}" if full else "",
            "",
            f"CONTENT:\n\n{self.content}",
            "",
            f"LINKS: \n{links_str}",
        ])

    def __str__(self):
        return self.print(full=True)
