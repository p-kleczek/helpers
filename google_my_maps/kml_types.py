import re
from dataclasses import dataclass, field
from enum import auto, Enum, StrEnum
from typing import List, Optional, TypeVar, Dict
import lxml.etree
from lxml.etree import CDATA

from google_my_maps.marking import StatusColors, Icons, line_width_normal

StyleId = str
Name = str


class StyleTypes(StrEnum):
    normal = "normal"
    highlight = "highlight"


class Text:
    def __init__(self, text=""):
        self.text: Optional[str | CDATA] = None

        if text:
            if not any(isinstance(text, t) for t in [str, CDATA]):
                raise TypeError(f"text is of type: {type(text)}")
            if isinstance(text, str) and any(c in text for c in "&<>\'\""):
                text = CDATA(text)
            self.text = text

    def __eq__(self, other):
        return (isinstance(other, type(self))
                and isinstance(self.text, type(other.text))
                and str(other) == str(self))

    # def __repr__(self):
    #     return str(self.text)

    # def __hash__(self):
    #     return hash(str(self.text))

    def __str__(self):
        if isinstance(self.text, CDATA):
            el = lxml.etree.Element('e')
            el.text = self.text
            s = lxml.etree.tostring(el, encoding="unicode")
            if m := re.match(r'<e><!\[CDATA\[(?P<text>.*)]]></e>', s):
                t = m.group('text')
            else:
                t = s
                t = re.sub(r'<e><!\[CDATA\[', "", t)
                t = re.sub(r']]></e>', "", t)
                t = t.strip()
            return t
        return str(self.text)


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
    text: Text


@dataclass
class Style:
    id_: StyleId
    icon_style: Optional[IconStyle] = None
    line_style: Optional[LineStyle] = None
    label_style: Optional[LabelStyle] = None
    balloon_style: Optional[BalloonStyle] = None


@dataclass
class StyleMap:
    id_: StyleId
    normal: Style
    highlight: Style


@dataclass
class Coordinate:
    x: float
    y: float
    z: float


MAX_COORDINATE_DIGITS: int = 6


@dataclass
class Data:
    gx_media_links: Text


@dataclass
class ExtendedData:
    data: Data


def get_stylemap_id_line(status_color: StatusColors) -> StyleId:
    line_width: int = int(line_width_normal * 1000)
    return f"line-{status_color}-{line_width}-nodesc"


def get_style_id_line(status_color: StatusColors, style_type: StyleTypes) -> StyleId:
    return f"{get_stylemap_id_line(status_color=status_color)}-{style_type}"


@dataclass
class Placemark:
    name: Text
    style: Optional[Style]
    stylemap: Optional[StyleMap]
    coordinates: List[Coordinate]
    description: Optional[Text] = None
    extended_data: Optional[ExtendedData] = None

    @property
    def style_id(self) -> str:
        return self.stylemap.id_ if self.stylemap is not None else self.style.id_

    @property
    def status(self) -> StatusColors:
        if 'icon' in self.style_id:
            m = re.match(r"#?icon-\d+-(?P<color>[0-9A-F]{6})", self.style_id)
        elif 'line' in self.style_id:
            m = re.match(r"#?line-(?P<color>[0-9A-F]{6})", self.style_id)
        else:
            raise NotImplementedError(f"Unknown styleUrl: {self.style_id}")
        color = m.group('color')
        return StatusColors(color)

    @property
    def icon(self) -> Icons:
        m = re.match(r"#?icon-(?P<iconcode>\d+)-", self.style_id)
        icon_code = m.group('iconcode')
        return Icons(int(icon_code))


PlacemarkType = TypeVar('PlacemarkType', bound=Placemark)


@dataclass
class Point(Placemark):
    pass


@dataclass
class Line(Placemark):
    tessellate: Optional[bool] = None


@dataclass
class Folder:
    name: Name
    placemarks: List[Placemark] = field(default_factory=list)


@dataclass
class Document:
    name: Name
    description: Text = None
    styles: Dict[StyleId, Style] = field(default_factory=dict)
    style_maps: Dict[StyleId, StyleMap] = field(default_factory=dict)
    folders: Dict[Name, Folder] = field(default_factory=dict)
    folders_ordering: List[Name] = field(default_factory=list)
    styles_ordering: List[StyleId] = field(default_factory=list)

    def __post_init__(self):
        self.description = self.description or Text()

    def clear_folders(self) -> None:
        self.folders = {}
        self.folders_ordering = []

    def add_folder(self, folder: Folder) -> None:
        if folder.name in self.folders:
            raise Exception(f"A folder named `{folder.name}` already exists.")
        self.folders[folder.name] = folder
        self.folders_ordering.append(folder.name)

    def remove_folder(self, folder_name: Name) -> None:
        if folder_name in self.folders:
            del self.folders[folder_name]
            self.folders_ordering.remove(folder_name)

    def clear_styles(self) -> None:
        for style_id in self.styles:
            self.styles_ordering.remove(style_id)
        self.styles = {}

    def add_style(self, style: Style) -> None:
        if style.id_ in self.styles:
            raise Exception(f"A style named `{style.id_}` already exists.")
        self.styles[style.id_] = style
        self.styles_ordering.append(style.id_)

    def remove_style(self, style_id: str) -> None:
        if style_id in self.styles:
            del self.styles[style_id]
            self.styles_ordering.remove(style_id)

    def clear_stylemaps(self) -> None:
        for stylemap_id in self.style_maps:
            self.styles_ordering.remove(stylemap_id)
        self.style_maps = {}

    def add_stylemap(self, style_map: StyleMap) -> None:
        if style_map.id_ in self.style_maps:
            raise Exception(f"A style map named `{style_map.id_}` already exists.")
        self.style_maps[style_map.id_] = style_map
        self.styles_ordering.append(style_map.id_)

    def remove_stylemap(self, stylemap_id: str) -> None:
        if stylemap_id in self.style_maps:
            del self.style_maps[stylemap_id]
            self.styles_ordering.remove(stylemap_id)
