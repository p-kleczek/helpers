from dataclasses import dataclass, field
from enum import Enum, auto, StrEnum
from typing import Dict, Optional, List

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
    index_start_inx: Optional[PageIndex]
    "Index of the first page with the list of cases (usually at the end of the book)."
    last_notes_page_inx: PageIndex
    "Index of the last page with notes (i.e., actual archival content)."
    broken_file_indexes: List[PageIndex] = field(default_factory=list)
    "Indexes for which downloading the preview stucks."

    # 'AOff NNN': ArchiveBookData(url_id='URL_ID',
    #                             num_pages=NUM_PAGES,
    #                             current_page_numbering=PageNumeringType.TYPE,
    #                             first_notes_page_inx=INX,
    #                             last_notes_page_inx=INX),
archive_books: Dict[ArchiveBookId, ArchiveBookData] = {
    'AOff 113': ArchiveBookData(url_id='5fd9f6b6a84a183c3fbab96e',
                                num_pages=1410,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1407),

    'AOff 115': ArchiveBookData(url_id='5fd9f6bd268b8c3c51fdf67f',
                                num_pages=1239,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1235),

    'AOff 120': ArchiveBookData(url_id='5f075c815c491007c27786e8',
                                num_pages=1024,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1021),

    'AOff 121': ArchiveBookData(url_id='5f2000988498b808336227ec',
                                num_pages=1830,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1826),

    'AOff 122': ArchiveBookData(url_id='5f1ca96ad6e76107f43f6ef5',
                                num_pages=510,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=1,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=505),

    'AOff 123': ArchiveBookData(url_id='5f43e8b2b593ba085fead762',
                                num_pages=1624,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1619),

    'AOff 124': ArchiveBookData(url_id='5f43e780f8838408962ff1a9',
                                num_pages=1596,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1593),

    'AOff 125': ArchiveBookData(url_id='5f1ca8e3ad85ed0855298bc7',
                                num_pages=460,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=454),

    'AOff 126': ArchiveBookData(url_id='5f3ea7464d06ac088a8aae3b',
                                num_pages=1514,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1511),

    'AOff 127': ArchiveBookData(url_id='5f50c9576734500d230b7b90',
                                num_pages=2028,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=6,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=2027),

    'AOff 128': ArchiveBookData(url_id='5f200088cfeb640819f319d5',
                                num_pages=1367,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1365),

    'AOff 129': ArchiveBookData(url_id='5f4621d2e8bed008530af24f',
                                num_pages=1968,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=14,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1965),

    'AOff 130': ArchiveBookData(url_id='5f468403a9811f4424676610',
                                num_pages=1834,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1821),

    'AOff 131': ArchiveBookData(url_id='5f4920bb0a187b0fabb11ed8',
                                num_pages=1934,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=10,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1930),

    'AOff 132': ArchiveBookData(url_id='5f2d568742fc9508a631d244',
                                num_pages=1242,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=8,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1239),

    'AOff 133': ArchiveBookData(url_id='5f6b219c57a0ea49780437cc',
                                num_pages=1390,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=8,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1386),

    'AOff 134': ArchiveBookData(url_id='5f58e5c1a7a6cc085b4dc540',
                                num_pages=1190,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=10,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1187),
    # spisy: od #1180

    # TODO: Other AOff ...

    'AOff 149': ArchiveBookData(url_id='60a50cd3437c01093e9f6159',
                                num_pages=1380,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=5,
                                index_start_inx=1353,
                                last_notes_page_inx=1377),

    # TODO: Other AOff ...

    'AOff 158': ArchiveBookData(url_id='5f1a6ef4ceca5f09285c6658',
                                num_pages=576,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=10,
                                index_start_inx=None,
                                last_notes_page_inx=572,
                                broken_file_indexes=[128, 152]),
    # TODO: AOff 159-164

    'AOff 165': ArchiveBookData(url_id='5ffc1f73301dd32857d16f82',
                                num_pages=1522,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1519),
    'AOff 166': ArchiveBookData(url_id='5ff851ad619442067bf760d8', num_pages=1430,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=8,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1422),
    'AOff 167': ArchiveBookData(url_id='5ff85173619442067bf760d3', num_pages=2102,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=2095),
    'AOff 168': ArchiveBookData(url_id='5ff85133619442067bf760ce', num_pages=1415,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=1407),
    'AOff 169': ArchiveBookData(url_id='5ff850f3f235eb285e81d2fb',
                                num_pages=876,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                index_start_inx=None,  # FIXME: Check it.
                                last_notes_page_inx=873),

    # 'AAdm 6': ArchiveBookData(url_id='5e4a5ea813e0af5864a7da2a', num_pages=508),

    # 'AAdm NN': ArchiveBookData(url_id='URL_ID',
    #                             num_pages=0,
    #                             current_page_numbering=PageNumeringType.,
    #                             first_notes_page_inx=,
    #                             last_notes_page_inx=),

    'AAdm 1': ArchiveBookData(url_id='5e42838133a040386152a9bb',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=617),

    'AAdm 2': ArchiveBookData(url_id='5e3c241d445e795858225922',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=8,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=692),

    # FIXME: Ustawić odpowiednie przeskoki - por. poniżej.
    # 'AAdm_2#0331_r': 668
    # #667 = 330r
    # #668 = 330v
    # #669 = 331r
    #
    # 'AAdm_2#0332_v': 671
    # #671 = 332r
    # #672 = 332v
    #
    # 'AAdm_2#0336_r': 678
    # #678 = 335v
    # #679 = 336v

    'AAdm 3': ArchiveBookData(url_id='5e42a30cd3b9d61aece6cd64',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=636),

    'AAdm 4': ArchiveBookData(url_id='5e43dfe55fbac11dd7389319',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=726),

    'AAdm 5': ArchiveBookData(url_id='5e43ef3c1b28b362770dec86',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=679),

    'AAdm 6': ArchiveBookData(url_id='5e4a5ea813e0af5864a7da2a',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=235),

    'AAdm 7': ArchiveBookData(url_id='5e4a719f13e0af5864a7e2d5',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Pagination,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=294),

    'AAdm 9': ArchiveBookData(url_id='5e564c6ae4b4d569f5565374',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              index_start_inx=None,  # FIXME: Check it.
                              last_notes_page_inx=292),

    'AAdm 9a': ArchiveBookData(url_id='5e5657dbf0c25e79af5dbeb1',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=58),

    'AAdm 10': ArchiveBookData(url_id='5e5666414a1503583a3e1941',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=448),

    'AAdm 11': ArchiveBookData(url_id='5e661cc45979be05a78a46b3',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=3,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=1153),

    'AAdm 12': ArchiveBookData(url_id='5ea14e2e60d3281d8c66973b',
                               num_pages=1538,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=1530),

    'AAdm 13': ArchiveBookData(url_id='5ea16bfd7346f71db9d74b48',
                               num_pages=970,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=966),

    'AAdm 14': ArchiveBookData(url_id='5ea2abdfb3c7261dcd211de5',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=6,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=1428),

    'AAdm 15': ArchiveBookData(url_id='5ea2b62eb3c7261dcd211e28',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=6,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=1491),

    'AAdm 22': ArchiveBookData(url_id='5ec4f3c5f8027a0b2d623396',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=4,
                               index_start_inx=None,  # FIXME: Check it.
                               last_notes_page_inx=763),
}
