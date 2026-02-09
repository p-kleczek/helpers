from dataclasses import dataclass
from enum import Enum, auto, StrEnum
from typing import Dict

ArchiveBookId = str

class PageNumeringType(Enum):
    Pagination = auto()
    "s."
    Foliation = auto()
    "k."

class PageSide(StrEnum):
    r = "r"
    v = "v"

PageIndex = int
"Number which appears in URL of the page."

@dataclass
class ArchiveBookData:
    url_id: str
    num_pages: int
    current_page_numbering: PageNumeringType
    first_notes_page_inx: PageIndex
    "Index of the first page with notes (i.e., actual archival content)."
    last_notes_page_inx: PageIndex
    "Index of the last page with notes (i.e., actual archival content)."


archive_books: Dict[ArchiveBookId, ArchiveBookData] = {
    'AOff 165': ArchiveBookData(url_id='5ffc1f73301dd32857d16f82',
                                num_pages=1522,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                last_notes_page_inx=1519),
    # 'AOff 166': ArchiveBookData(url_id='5ff851ad619442067bf760d8', num_pages=1430),
    # 'AOff 167': ArchiveBookData(url_id='5ff85173619442067bf760d3', num_pages=2102),
    # 'AOff 168': ArchiveBookData(url_id='5ff85133619442067bf760ce', num_pages=1415),
    'AOff 169': ArchiveBookData(url_id='5ff850f3f235eb285e81d2fb',
                                num_pages=876,
                                current_page_numbering = PageNumeringType.Foliation,
                                first_notes_page_inx = 4,
                                last_notes_page_inx = 873),

    # 'AAdm 6': ArchiveBookData(url_id='5e4a5ea813e0af5864a7da2a', num_pages=508),

    # 'AAdm NN': ArchiveBookData(url_id='URL_ID',
    #                             num_pages=0,
    #                             current_page_numbering=PageNumeringType.,
    #                             first_notes_page_inx=,
    #                             last_notes_page_inx=),

    'AAdm 10': ArchiveBookData(url_id='66414a15/f',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               last_notes_page_inx=448),

    'AAdm 11': ArchiveBookData(url_id='5e661cc45979be05a78a46b3',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=3,
                               last_notes_page_inx=1153),

    'AAdm 12': ArchiveBookData(url_id='5ea14e2e60d3281d8c66973b',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               last_notes_page_inx=1530),

    'AAdm 13': ArchiveBookData(url_id='5ea16bfd7346f71db9d74b48',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               last_notes_page_inx=966),

    'AAdm 14': ArchiveBookData(url_id='5ea2abdfb3c7261dcd211de5',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=6,
                               last_notes_page_inx=1428),

    'AAdm 15': ArchiveBookData(url_id='5ea2b62eb3c7261dcd211e28',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=6,
                               last_notes_page_inx=1491),

    'AAdm 22': ArchiveBookData(url_id='5ec4f3c5f8027a0b2d623396',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=4,
                               last_notes_page_inx=763),

    # 'AAdm 12': ArchiveBookData(url_id='5ea14e2e60d3281d8c66973b', num_pages=1538),
    # 'AAdm 13': ArchiveBookData(url_id='5ea16bfd7346f71db9d74b48', num_pages=970),
}