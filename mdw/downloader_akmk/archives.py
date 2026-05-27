from dataclasses import dataclass, field
from enum import Enum, auto, StrEnum
from typing import Dict, List, Optional

ArchiveBookId = str


class ArchiveId(Enum):
    SDM = auto()
    CAAK = auto()


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
class IndexRange:
    start_inx: PageIndex
    end_inx: PageIndex
    year: int
    note: Optional[str] = None


@dataclass
class ArchiveBookData:
    archive_id: ArchiveId
    url_id: str
    num_pages: int
    current_page_numbering: PageNumeringType
    first_notes_page_inx: PageIndex
    "Index of the first page with notes (i.e., actual archival content)."
    indexes: List[IndexRange]
    "Index of the first page with the list of cases (usually at the end of the book)."
    last_notes_page_inx: PageIndex
    "Index of the last page with notes (i.e., actual archival content)."
    broken_file_indexes: List[PageIndex] = field(default_factory=list)
    "Indexes for which downloading the preview stucks."
    has_narrow_pages: bool = False
    "True w przypadku tzw. 'języczków' - a nie stronic normalnej szerokości."

    # 'AEp NNN': ArchiveBookData(archive_id=ArchiveId.CAAK,
    #                             url_id='URL_ID',
    #                             num_pages=NUM_PAGES,
    #                             current_page_numbering=PageNumeringType.TYPE,
    #                             first_notes_page_inx=INX,
    #                             indexes = [IndexRange(INX1, INX2, year=YYYY)],
    #                             last_notes_page_inx=INX),


archive_books: Dict[ArchiveBookId, ArchiveBookData] = {
    'AEp 34': ArchiveBookData(archive_id=ArchiveId.SDM,
                              url_id='volumen-iii-actorum-radziwill-cardinalis-et-perpetui-administratoris-dioecesis'
                                     '-cracoviensis-ducis-severiae-negotia-causas-lites-obligationes-et-alias-ad-form'
                                     '-saeculare-pertinenria-et-ducatus-severiae-continens-stante-eiusdem'
                                     '-administratore-conscriptorum-per-martinum-ciesielski-notarium',
                              num_pages=656,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,  # FIXME: Chodzi o wartość "Strona"
                              indexes=[IndexRange(638, 639, year=1592), IndexRange(640, 640, year=1593),
                                       IndexRange(640, 643, year=1594), IndexRange(643, 644, year=1595),
                                       IndexRange(644, 645, year=1596), IndexRange(645, 646, year=1597),
                                       IndexRange(646, 647, year=1598), IndexRange(647, 649, year=1599),
                                       IndexRange(649, 649, year=1600)],
                              last_notes_page_inx=649),

    'AEp 35': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5fd9f6cea84a183c3fbab9e2',
                              num_pages=1114,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=8,
                              indexes=[IndexRange(1092, 1093, year=1600), IndexRange(1093, 1099, year=1601),
                                       IndexRange(1099, 1111, year=1601)],
                              last_notes_page_inx=1111),

    'AEp 80': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e4a845085925c58390ac555',
                              num_pages=814,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=1,
                              indexes=[IndexRange(787, 793, year=1728), IndexRange(793, 799, year=1729),
                                       IndexRange(799, 805, year=1730)],
                              last_notes_page_inx=805),

    'AEp 81': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f0d7c6565285c0903339d18',
                              num_pages=464,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[IndexRange(449, 455, year=1731), IndexRange(455, 458, year=1732)],
                              last_notes_page_inx=458),

    'AEp 82': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f1a71493f5f2408d94abee2',
                              num_pages=1248,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=12,
                              indexes=[IndexRange(1206, 1207, year=1734), IndexRange(1207, 1209, year=1735),
                                       IndexRange(1210, 1221, year=1736), IndexRange(1221, 1238, year=1737)],
                              last_notes_page_inx=1238),

    'AEp 90': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='60a51addfcb1be07f560bfc1',
                              num_pages=684,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[IndexRange(334, 343, year=1749), IndexRange(664, 678, year=1750)],
                              last_notes_page_inx=678),

    'AEp 91': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='60a62c36fdeed9095ec0e990',
                              num_pages=492,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=5,
                              indexes=[IndexRange(467, 478, year=1751), IndexRange(479, 486, year=1752)],
                              last_notes_page_inx=486),

    'AEp 92': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f1031d578bbb208d7defdc7',
                              num_pages=466,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[IndexRange(444, 452, year=1753), IndexRange(454, 463, year=1754)],
                              last_notes_page_inx=463),

    'AEp 93': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f2d40953ce7600867e3d3de',
                              num_pages=358,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=6,
                              indexes=[IndexRange(144, 148, year=1755), IndexRange(348, 352, year=1756)],
                              last_notes_page_inx=352),

    'AEp 94': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f4f8e2f99b1ae0d2c1df953',
                              num_pages=680,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[IndexRange(476, 482, year=1757), IndexRange(672, 675, year=1758)],
                              last_notes_page_inx=675),

    'AEp 95': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f105ad278bbb208d7df052b',
                              num_pages=374,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=0,
                              indexes=[IndexRange(366, 369, year=1757), IndexRange(369, 370, year=1758)],
                              last_notes_page_inx=370),

    'AEp 96': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f0d8c7b3f5f2408d9485fec',
                              num_pages=424,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=7,
                              indexes=[IndexRange(417, 419, year=1758)],
                              last_notes_page_inx=419),

    'AEp 97': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f0da2961536770904bff132',
                              num_pages=404,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[IndexRange(392, 396, year=1758)],
                              last_notes_page_inx=396),

    'AEp 98': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5f2bd0e3c7b200083bbe31a6',
                              num_pages=708,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=8,
                              indexes=[IndexRange(688, 689, year=1759), IndexRange(689, 692, year=1760),
                                       IndexRange(692, 694, year=1761), IndexRange(694, 694, year=1762),
                                       IndexRange(695, 697, year=1763), IndexRange(697, 697, year=1764),
                                       IndexRange(697, 699, year=1765), IndexRange(699, 700, year=1766),
                                       IndexRange(700, 701, year=1767), IndexRange(701, 701, year=1768),
                                       IndexRange(701, 702, year=1769), IndexRange(702, 702, year=1770),
                                       IndexRange(702, 703, year=1771), IndexRange(703, 703, year=1772)],
                              last_notes_page_inx=703),

    # NOTE: 1773-02 - 1782
    # 'AEp 99': ArchiveBookData(archive_id=ArchiveId.CAAK,
    #                             url_id='5f2bf33b5ec1890890969da6',
    #                             num_pages=1348,
    #                             current_page_numbering=PageNumeringType.TYPE,
    #                             first_notes_page_inx=6,
    #                             indexes = [IndexRange(INX1, INX2, year=YYYY)],
    #                             last_notes_page_inx=INX),

    'AEp 102': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5f59eb1c4dbce3082cec6dfd',
                               num_pages=794,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=6,
                               indexes=[IndexRange(254, 259, year=1759), IndexRange(782, 791, year=1760)],
                               last_notes_page_inx=791),

    'AEp 103': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5f633200b4f16a0a7d276396',
                               num_pages=908,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=6,
                               indexes=[IndexRange(366, 376, year=1761), IndexRange(894, 905, year=1762)],
                               last_notes_page_inx=905),

    'AEp 104': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='60a658d9d821e409356456cc',
                               num_pages=994,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=5,
                               indexes=[IndexRange(988, 988, year=1763)],
                               last_notes_page_inx=988),

    'AEp 105': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='60a6593a18cc195ab86fc5f5',
                               num_pages=614,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[IndexRange(606, 611, year=1764)],
                               last_notes_page_inx=611),

    'AEp 106': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='60a659de18cc195ab86fc5fa',
                               num_pages=824,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[IndexRange(486, 491, year=1765, note='pt. 1 (I-XI)'),
                                        IndexRange(820, 820, year=1765, note='pt. 2 (XII)'),
                                        IndexRange(812, 819, year=1766)],
                               last_notes_page_inx=820),

    'AEp 107': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='60a65a66a0b2f25ee8c0d0d6',
                               num_pages=884,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],
                               # [IndexRange(INX1, INX2, year=1767), IndexRange(INX1, INX2, year=1768), IndexRange(
                               # INX1, INX2, year=1769)],  # FIXME: Uzupełnić - zob. poniżej.
                               # r. 1767: 190r-194r
                               # r. 1768: 335r-336v
                               # r. 1769: 431v-434r
                               last_notes_page_inx=878),

    'AEp 108': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='60e6d4a459a8ad5e381eb4eb',
                               num_pages=950,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],
                               # FIXME: Uzupełnić: [IndexRange(INX1, INX2, year=1770), IndexRange(INX1, INX2,
                               #  year=1771), IndexRange(INX1, INX2, year=1772), IndexRange(INX1, INX2, year=1773),
                               #  IndexRange(INX1, INX2, year=1774), IndexRange(942, 944, year=1775)],
                               # r. 1770: 90r-92v
                               # r. 1771: 160r-161v
                               # r. 1772: 238v-239v
                               last_notes_page_inx=944),

    # ===============================================================
    # Acta Officialia
    # ===============================================================

    'AOff 9': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e43b48629fd527f362855b6',
                              num_pages=1049,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=8,
                              indexes=[],
                              last_notes_page_inx=1047,
                              has_narrow_pages=True),

    'AOff 110': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5fd9f58f31bdef3c5713d51e',
                                num_pages=674,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[],
                                last_notes_page_inx=669),

    # AOff 111 - brak w CAAK

    'AOff 112': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5fd9f6aaf0570e3c6e4bc0e7',
                                num_pages=1496,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=5,
                                indexes=[],
                                last_notes_page_inx=1488),

    'AOff 113': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5fd9f6b6a84a183c3fbab96e',
                                num_pages=1410,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1407),

    'AOff 115': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5fd9f6bd268b8c3c51fdf67f',
                                num_pages=1239,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1235),

    'AOff 120': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f075c815c491007c27786e8',
                                num_pages=1024,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1021),

    'AOff 121': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f2000988498b808336227ec',
                                num_pages=1830,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1826),

    'AOff 122': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f1ca96ad6e76107f43f6ef5',
                                num_pages=510,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=1,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=505),

    'AOff 123': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f43e8b2b593ba085fead762',
                                num_pages=1624,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1619),

    'AOff 124': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f43e780f8838408962ff1a9',
                                num_pages=1596,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1593),

    'AOff 125': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f1ca8e3ad85ed0855298bc7',
                                num_pages=460,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=454),

    'AOff 126': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f3ea7464d06ac088a8aae3b',
                                num_pages=1514,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1511),

    'AOff 127': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f50c9576734500d230b7b90',
                                num_pages=2028,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=6,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=2027),

    'AOff 128': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f200088cfeb640819f319d5',
                                num_pages=1367,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=4,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1365),

    'AOff 129': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f4621d2e8bed008530af24f',
                                num_pages=1968,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=14,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1965),

    'AOff 130': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f468403a9811f4424676610',
                                num_pages=1834,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1821),

    'AOff 131': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f4920bb0a187b0fabb11ed8',
                                num_pages=1934,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=10,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1930),

    'AOff 132': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f2d568742fc9508a631d244',
                                num_pages=1242,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=8,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1239),

    'AOff 133': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f6b219c57a0ea49780437cc',
                                num_pages=1390,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=8,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1386),

    'AOff 134': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f58e5c1a7a6cc085b4dc540',
                                num_pages=1190,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=10,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1187),
    # spisy: od #1180

    'AOff 135': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f2183f5c45a5507fae22d3d',
                                num_pages=1212,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=12,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1208),

    'AOff 136': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50fd75274e4697fdf082d',
                                num_pages=1926,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[],  # FIXME: Check it.
                                last_notes_page_inx=1923),

    'AOff 137': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50fa9b93d6c0967278531',
                                num_pages=1680,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[],
                                last_notes_page_inx=1676),

    # TODO: Other AOff ...

    'AOff 140': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50f2114b3e109568e5dda',
                                num_pages=2060,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(2024, 2057, year=1661)],
                                last_notes_page_inx=2057),

    'AOff 141': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50ede5274e4697fdf0701',
                                num_pages=1286,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=8,
                                indexes=[IndexRange(1242, 1282, year=1663)],
                                last_notes_page_inx=1282),

    'AOff 142': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50e9c3892654460a1ac44',
                                num_pages=1612,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(1555, 1607, year=1664)],
                                last_notes_page_inx=1607),

    'AOff 143': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50e713892654460a1ac14',
                                num_pages=1242,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=5,
                                indexes=[IndexRange(1223, 1239, year=1665)],
                                last_notes_page_inx=1239),

    'AOff 144': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50e30b93d6c096727839c',
                                num_pages=1318,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(1294, 1314, year=1666)],
                                last_notes_page_inx=1314),

    'AOff 145': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50dae0c7cc246cf5b93e1',
                                num_pages=2572,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(2542, 2565, year=1667)],
                                last_notes_page_inx=2565),

    'AOff 146': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50d7841f35c3242b3fd80',
                                num_pages=1446,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=8,
                                indexes=[IndexRange(1410, 1439, year=1669)],
                                last_notes_page_inx=1439),

    'AOff 147': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50d43fdeed9095ec0a8f6',
                                num_pages=2004,
                                current_page_numbering=PageNumeringType.Foliation,
                                # r. 1670
                                first_notes_page_inx=6,
                                indexes=[IndexRange(1964, 1998, year=1670)],
                                last_notes_page_inx=1998),

    # TODO: Other AOff ...

    'AOff 149': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='60a50cd3437c01093e9f6159',
                                num_pages=1380,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=5,
                                indexes=[IndexRange(1353, 1377, year=1672)],
                                last_notes_page_inx=1377),

    # TODO: Other AOff ...

    'AOff 151': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='6006b12f9fb09a28639f19d6',
                                num_pages=1290,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=5,
                                indexes=[IndexRange(1266, 1287, year=1674)],
                                last_notes_page_inx=1287),

    'AOff 152': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f1a6b32c2c918091b45b7c0',
                                num_pages=1038,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=2,
                                indexes=[IndexRange(1012, 1034, year=1675)],
                                last_notes_page_inx=1034),

    'AOff 153': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f1a6974abc17909014217f8',
                                num_pages=934,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(916, 931, year=1676)],
                                last_notes_page_inx=931),

    'AOff 154': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f084fccceca5f092857b668',
                                num_pages=402,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(392, 395, year=1677)],
                                last_notes_page_inx=395),

    'AOff 155': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f58a16b1a771a08293cb92e',
                                num_pages=1100,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=5,
                                indexes=[IndexRange(367, 373, year=1678), IndexRange(1083, 1097, year=1679)],
                                last_notes_page_inx=1097),

    'AOff 156': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f58d753d71fa1085963164f',
                                num_pages=1848,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(512, 524, year=1683), IndexRange(1090, 1104, year=1684),
                                         IndexRange(1826, 1844, year=1685)],
                                last_notes_page_inx=1844),

    'AOff 157': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='6006b0d7b4a0126bb5b11446',
                                num_pages=2258,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(704, 724, year=1686), IndexRange(1266, 1279, year=1687),
                                         IndexRange(2236, 2250, year=1688), IndexRange(2250, 2253, year=1689)],
                                last_notes_page_inx=2253),

    # TODO: Other AOff ...

    'AOff 158': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f1a6ef4ceca5f09285c6658',
                                num_pages=576,
                                current_page_numbering=PageNumeringType.Pagination,
                                first_notes_page_inx=10,
                                indexes=[],
                                last_notes_page_inx=572,
                                broken_file_indexes=[128, 152]),
    # TODO: AOff 159-164

    'AOff 165': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5ffc1f73301dd32857d16f82',
                                num_pages=1522,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(1486, 1486, year=1710), IndexRange(1486, 1494, year=1711),
                                         IndexRange(1494, 1502, year=1712), IndexRange(1502, 1510, year=1713),
                                         IndexRange(1510, 1516, year=1714)],
                                last_notes_page_inx=1516),

    'AOff 166': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5ff851ad619442067bf760d8', num_pages=1430,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=8,
                                indexes=[IndexRange(1412, 1413, year=1714), IndexRange(1413, 1417, year=1715),
                                         # NOTE: Brakuje końca indeksu dla r. 1715 oraz początku dla r. 1716,
                                         # jako że zmiana daty jest: 26 VIII (#1417) -> 6 VI (#1418) mimo ciągłości
                                         # kart.
                                         IndexRange(1417, 1419, year=1716), IndexRange(1419, 1420, year=1717),
                                         # NOTE: Brak nagłówka między r. 1717 a 1718, ale zmiana daty: 19 X -> 15 I
                                         IndexRange(1420, 1422, year=1718),
                                         # FIXME: Sprwdzić do którego roku odnoszą się spisy ujęte wyżej jako r. 1718.
                                         IndexRange(1420, 1422, year=1719),
                                         # FIXME: Sprwdzić do którego roku odnoszą się spisy ujęte wyżej jako r. 1719.
                                         ],
                                last_notes_page_inx=1422),

    'AOff 167': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5ff85173619442067bf760d3', num_pages=2102,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(2070, 2072, year=1720), IndexRange(2072, 2080, year=1721),
                                         IndexRange(2080, 2088, year=1722), IndexRange(2088, 2095, year=1723)],
                                last_notes_page_inx=2095),

    'AOff 168': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5ff85133619442067bf760ce', num_pages=1415,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(1389, 1395, year=1724), IndexRange(1395, 1401, year=1725),
                                         IndexRange(1401, 1407, year=1726)],
                                last_notes_page_inx=1407),

    'AOff 169': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5ff850f3f235eb285e81d2fb',
                                num_pages=876,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=4,
                                indexes=[IndexRange(862, 870, year=1727), IndexRange(870, 871, year=1728)],
                                last_notes_page_inx=873),

    # 'AOff NNN': ArchiveBookData(archive_id=ArchiveId.CAAK,
    #                             url_id='URL_ID',
    #                             num_pages=NUM_PAGES,
    #                             current_page_numbering=PageNumeringType.TYPE,
    #                             first_notes_page_inx=INX,
    #                             indexes = [IndexRange(INX1, INX2, year=YYYY)],
    #                             last_notes_page_inx=INX),

    'AOff 178': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f575c6e52f8d9501c58a419',
                                num_pages=506,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(484, 498, year=1743)],
                                last_notes_page_inx=498),

    'AOff 179': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f575be05aa4a6504cbe3918',
                                num_pages=478,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(458, 468, year=1744)],
                                last_notes_page_inx=468),

    'AOff 180': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f575b7bd26cda5071a3a19b',
                                num_pages=886,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(854, 867, year=1745), IndexRange(868, 869, year=1746)],
                                last_notes_page_inx=873),

    'AOff 181': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f575b04f1eea150470098bd',
                                num_pages=1214,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(672, 677, year=1747),
                                         IndexRange(1198, 1203, year=1748, note='pt. 1 (I-IX)')],
                                last_notes_page_inx=1203),

    'AOff 182': ArchiveBookData(archive_id=ArchiveId.CAAK,
                                url_id='5f575a9c3c9fd5353b10319f',
                                num_pages=860,
                                current_page_numbering=PageNumeringType.Foliation,
                                first_notes_page_inx=6,
                                indexes=[IndexRange(834, 837, year=1758, note='pt. 2 (X-XII)'),
                                         IndexRange(838, 853, year=1749)],
                                last_notes_page_inx=853),

    # ===============================================================
    # Acta Administratorialia
    # ===============================================================

    # 'AAdm 6': ArchiveBookData(archive_id=ArchiveId.CAAK,
    #                           url_id='5e4a5ea813e0af5864a7da2a', num_pages=508),

    # 'AAdm NN': ArchiveBookData(archive_id=ArchiveId.CAAK,
    #                             url_id='URL_ID',
    #                             num_pages=0,
    #                             current_page_numbering=PageNumeringType.,
    #                             first_notes_page_inx=,
    #                             last_notes_page_inx=),

    'AAdm 1': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e42838133a040386152a9bb',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=617),

    'AAdm 2': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e3c241d445e795858225922',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=8,
                              indexes=[],  # FIXME: Check it.
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

    'AAdm 3': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e42a30cd3b9d61aece6cd64',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=636),

    'AAdm 4': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e43dfe55fbac11dd7389319',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=726),

    'AAdm 5': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e43ef3c1b28b362770dec86',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=679),

    'AAdm 6': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e4a5ea813e0af5864a7da2a',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=235),

    'AAdm 7': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e4a719f13e0af5864a7e2d5',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Pagination,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=294),

    'AAdm 9': ArchiveBookData(archive_id=ArchiveId.CAAK,
                              url_id='5e564c6ae4b4d569f5565374',
                              num_pages=0,
                              current_page_numbering=PageNumeringType.Foliation,
                              first_notes_page_inx=4,
                              indexes=[],  # FIXME: Check it.
                              last_notes_page_inx=292),

    'AAdm 9a': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5e5657dbf0c25e79af5dbeb1',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=58),

    'AAdm 10': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5e5666414a1503583a3e1941',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=448),

    'AAdm 11': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5e661cc45979be05a78a46b3',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=3,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=1153),

    'AAdm 12': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ea14e2e60d3281d8c66973b',
                               num_pages=1538,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=1530),

    'AAdm 13': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ea16bfd7346f71db9d74b48',
                               num_pages=970,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=4,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=966),

    'AAdm 14': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ea2abdfb3c7261dcd211de5',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Foliation,
                               first_notes_page_inx=6,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=1428),

    'AAdm 15': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ea2b62eb3c7261dcd211e28',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=6,
                               indexes=[],  # FIXME: Check it.
                               last_notes_page_inx=1491),

    'AAdm 22': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ec4f3c5f8027a0b2d623396',
                               num_pages=0,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=4,
                               indexes=[],
                               last_notes_page_inx=763),

    'AAdm 23': ArchiveBookData(archive_id=ArchiveId.CAAK,
                               url_id='5ec4fa34b970c20a0546014e',
                               num_pages=168,
                               current_page_numbering=PageNumeringType.Pagination,
                               first_notes_page_inx=4,
                               indexes=[],
                               last_notes_page_inx=165),
}
