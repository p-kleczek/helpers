from dataclasses import dataclass, field
from typing import List, Optional, TypeVar


@dataclass
class Icon:
    href: str


@dataclass
class HotSpot:
    x: int
    xunits: str
    y: int
    yunits: str


@dataclass
class IconStyle:
    color: str
    scale: float
    icon: Icon
    hotSpot: Optional[HotSpot] = None


@dataclass
class LineStyle:
    color: str
    width: float


@dataclass
class LabelStyle:
    scale: float


@dataclass
class BalloonStyle:
    text: str


@dataclass
class Style:
    id_: str
    icon_style: Optional[IconStyle] = None
    line_style: Optional[LineStyle] = None
    label_style: Optional[LabelStyle] = None
    balloon_style: Optional[BalloonStyle] = None


@dataclass
class StyleMap:
    id_: str
    normal: Style
    highlight: Style


@dataclass
class Coordinate:
    x: float
    y: float
    z: float


@dataclass
class Data:
    gx_media_links: str


@dataclass
class ExtendedData:
    data: Data


@dataclass
class Placemark:
    name: str
    stylemap: StyleMap
    coordinates: List[Coordinate]
    description: Optional[str] = None
    extended_data: Optional[ExtendedData] = None


PlacemarkType = TypeVar('PlacemarkType', bound=Placemark)


@dataclass
class Point(Placemark):
    pass


@dataclass
class Line(Placemark):
    tessellate: Optional[bool] = None


@dataclass
class Folder:
    name: str
    placemarks: List[Placemark] = field(default_factory=list)


@dataclass
class Document:
    name: str
    description: str = ""
    # styles: List[Style]
    style_maps: List[StyleMap] = field(default_factory=list)
    folders: List[Folder] = field(default_factory=list)
