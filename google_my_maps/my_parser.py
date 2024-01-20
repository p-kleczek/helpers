import re
from enum import Enum, auto
from pathlib import Path
from typing import List, Dict, Optional, Type, Set

import lxml.etree
from lxml import etree
from lxml.etree import CDATA

import xml.etree.ElementTree as ET

from google_my_maps.kml_types import Document, Style, IconStyle, Icon, LabelStyle, BalloonStyle, StyleMap, LineStyle, \
    Coordinate, Point, Line, Folder, PlacemarkType, Data, ExtendedData, HotSpot


class XmlEngine(Enum):
    XML = auto()
    LXML = auto()


xml_engine: XmlEngine = XmlEngine.LXML

NodeType: Type = {
    XmlEngine.XML: ET.Element,
    XmlEngine.LXML: lxml.etree.Element
}[xml_engine]


class MyParser:
    INDENT: str = " " * 2

    def __init__(self):
        self.styles: Dict[str, Style] = {}
        self.style_maps: Dict[str, StyleMap] = {}

    def parse_style(self, node: NodeType) -> Style:
        style: Style = Style(id_=node.attrib['id'])
        for child in node:
            match tag := child.tag:
                # FIXME: Check for other elements in children (other than handled below).
                case 'IconStyle':
                    hot_spot: Optional[HotSpot] = None
                    if (hs := child.find('hotSpot')) is not None:
                        hot_spot = HotSpot(x=int(hs.attrib['x']),
                                           xunits=hs.attrib['xunits'],
                                           y=int(hs.attrib['y']),
                                           yunits=hs.attrib['yunits']
                                           )

                    style.icon_style = IconStyle(
                        color=child.find('color').text,
                        scale=float(child.find('scale').text),
                        icon=Icon(href=child.find('Icon/href').text),
                        hotSpot=hot_spot,
                    )
                case 'LineStyle':
                    style.line_style = LineStyle(
                        color=child.find('color').text,
                        width=float(child.find('width').text),
                    )
                case 'LabelStyle':
                    style.label_style = LabelStyle(
                        scale=float(child.find('scale').text),
                    )
                case 'BalloonStyle':
                    text = child.find('text').text
                    style.balloon_style = BalloonStyle(
                        text=self.get_cdata_text(text)
                    )
                case _:
                    raise NotImplementedError(tag)

        return style

    @staticmethod
    def get_cdata_text(text: str | lxml.etree.CDATA) -> str | lxml.etree.CDATA:
        if isinstance(text, lxml.etree.CDATA):
            return text

        if not isinstance(text, str):
            raise TypeError(f"text is of type: {type(text)}")

        if any(c in text for c in "&<>\'\""):
            return CDATA(text)
        return text

    def parse_stylemap(self, node: NodeType) -> StyleMap:
        normal: Optional[Style] = None
        highlight: Optional[Style] = None

        for child in node:
            # FIXME: Check for other elements in children (other than handled below).
            style = self.styles[child.find('styleUrl').text[1:]]
            match (key := child.find('key').text):
                case 'normal':
                    normal = style
                case 'highlight':
                    highlight = style
                case _:
                    raise NotImplementedError(key)

        return StyleMap(
            id_=node.attrib['id'],
            normal=normal,
            highlight=highlight,
        )

    def parse_placemark(self, node: NodeType) -> PlacemarkType:
        kwargs = {}
        class_: Optional[Type] = None

        def parse_coordinates(crd_node: NodeType) -> List[Coordinate]:
            coordinates: List[Coordinate] = []
            text = crd_node.text.strip()
            for coord_txt in text.split("\n"):
                coords = [float(c) for c in coord_txt.split(',')]
                coordinates.append(Coordinate(*coords))
            return coordinates

        for child in node:
            match tag := child.tag:
                # FIXME: Check for other elements in children (other than handled below).
                case 'name':
                    kwargs['name'] = child.text
                case 'description':
                    kwargs['description'] = child.text
                case 'styleUrl':
                    kwargs['stylemap'] = self.style_maps[child.text[1:]]
                case 'Point':
                    class_ = Point
                    kwargs['coordinates'] = parse_coordinates(child.find('coordinates'))
                case 'LineString':
                    class_ = Line
                    kwargs['tessellate'] = bool(child.find('tessellate').text)
                    kwargs['coordinates'] = parse_coordinates(child.find('coordinates'))
                case 'ExtendedData':
                    kwargs['extended_data'] = ExtendedData(
                        data=Data(gx_media_links=self.get_cdata_text(child.find('.//value').text)),
                    )
                    #         <ExtendedData>
                    #           <Data name="gx_media_links">
                    #             <value><![CDATA[https://doc-10-bc-mymaps.googleusercontent.com/untrusted/hostedimage/4jdncotf9bbp7kl0o8t3rde974/am1l9t4bcu7i2itrhtrkqgpgmg/1693645807750/vzuLRJTzg-tN72CLOAmh_KUis8ReF4jF/16193039080792181271/5ACnmet7YZorIObWl_5n8rBKE8vhMELII0IJ5ZYLDU6KtMDruM6s9zsyZLZ2IZm-vKB5qnG4EDVZBFV_mNM7d2bPZrcBla-YQJxoL3nu5o5iaYZqmWXawPQb6Jz3w2vuTfQml8EXGGYoUOyztel-NiPXMAvtL5js6WHZbI5ZahgXXhI9ZMzPMqFj5ivX_gn1bn9zUUT67w8xol1_T7sj1SyDfg-l2TT4fCamXn2KUfguu1Xv-8zU?session=0&fife]]></value>
                    #           </Data>
                    #         </ExtendedData>
                case _:
                    raise NotImplementedError(tag)

        return class_(**kwargs)

    def parse_folder(self, node: NodeType) -> Folder:
        folder: Folder = Folder(name=node.find('name').text)

        for child in node:
            match (tag := child.tag):
                case 'name':
                    pass
                case 'Placemark':
                    folder.placemarks.append(self.parse_placemark(child))
                case _:
                    raise NotImplementedError(tag)

        return folder

    def parse_document(self, node: NodeType) -> Document:
        document: Document = Document(name=node.find('name').text)

        for child in node:
            match (tag := child.tag):
                case 'name':
                    pass
                case 'description':
                    document.description = self.get_cdata_text(child.text)
                case 'Style':
                    style = self.parse_style(child)
                    self.styles[style.id_] = style
                case 'StyleMap':
                    stylemap = self.parse_stylemap(child)
                    self.style_maps[stylemap.id_] = stylemap
                    document.style_maps.append(stylemap)
                case 'Folder':
                    document.folders.append(self.parse_folder(child))
                case _:
                    raise NotImplementedError(tag)

        return document

    def parse_kml(self, filepath: Path) -> Document:
        if xml_engine == XmlEngine.LXML:
            # parser = etree.XMLParser(strip_cdata=False)

            tree = etree.parse(filepath)
            root = tree.getroot()
            # root = etree.XML('<root><![CDATA[test]]></root>', parser)

            for elem in root.getiterator():
                # Skip comments and processing instructions,
                # because they do not have names
                if not (
                        isinstance(elem, etree._Comment)
                        or isinstance(elem, etree._ProcessingInstruction)
                ):
                    # Remove a namespace URI in the element's name
                    elem.tag = lxml.etree.QName(elem).localname

            ns = root.nsmap[None]
        elif xml_engine == XmlEngine.XML:
            tree = ET.parse(filepath)
            root = tree.getroot()

            uri_pattern = re.compile(r"\{http://.*?}")

            def remove_uri_from_tags(node: NodeType):
                node.tag = uri_pattern.sub("", node.tag)
                for elem in node:
                    remove_uri_from_tags(elem)

            remove_uri_from_tags(root)
        else:
            raise NotImplementedError(f"The given engine ({xml_engine}) is not (yet?) supported.")

        return self.parse_document(root.find('Document'))

        # >>> print(tree.docinfo.xml_version)
        # >>> print(tree.docinfo.doctype)

    @staticmethod
    def float_to_str(f: float) -> str:
        return re.sub(r"\.0$", "", str(f))

    def save_kml(self, document: Document, level: int = 1) -> etree.Element:

        kml = etree.Element('kml')
        kml.set('xmlns', "http://www.opengis.net/kml/2.2")

        document_elem = etree.SubElement(kml, 'Document')
        document_name = etree.SubElement(document_elem, 'name')
        document_name.text = document.name

        document_description = etree.SubElement(document_elem, 'description')
        if document.description:
            document_description.text = self.get_cdata_text(document.description)

        saved_styles: Set[str] = set()
        # FIXME: Avoid duplicates of Styles.

        for stylemap in document.style_maps:
            style_elem = etree.SubElement(document_elem, 'Style')
            self.save_style(stylemap.normal, style_elem)
            style_elem = etree.SubElement(document_elem, 'Style')
            self.save_style(stylemap.highlight, style_elem)
            stylemap_elem = etree.SubElement(document_elem, 'StyleMap')
            self.save_stylemap(stylemap, stylemap_elem)

        for folder in document.folders:
            self.save_folder(folder=folder, elem=document_elem, level=level + 1)

        print(etree.tostring(kml, pretty_print=True))

        return kml

    def save_placemark(self, placemark: PlacemarkType, elem: NodeType, level: int) -> None:
        placemark_elem = etree.SubElement(elem, 'Placemark')
        level += 1

        placemark_name = etree.SubElement(placemark_elem, 'name')
        placemark_name.text = self.get_cdata_text(placemark.name)

        if placemark.description:
            placemark_description = etree.SubElement(placemark_elem, 'description')
            placemark_description.text = self.get_cdata_text(placemark.description)

        placemark_styleurl = etree.SubElement(placemark_elem, 'styleUrl')
        placemark_styleurl.text = "#" + placemark.stylemap.id_

        if (extData := placemark.extended_data) is not None:
            placemark_extdata = etree.SubElement(placemark_elem, 'ExtendedData')
            extdata_data = etree.SubElement(placemark_extdata, 'Data')
            extdata_data.attrib['name'] = 'gx_media_links'
            extdata_data_value = etree.SubElement(extdata_data, 'value')
            extdata_data_value.text = extData.data.gx_media_links

        tag: str
        if isinstance(placemark, Point):
            tag = 'Point'
        elif isinstance(placemark, Line):
            tag = 'LineString'
        else:
            raise NotImplementedError(type(placemark))
        placemark_class_elem = etree.SubElement(placemark_elem, tag)
        level += 1

        if isinstance(placemark, Line):
            tessellate_elem = etree.SubElement(placemark_class_elem, 'tessellate')
            tessellate_elem.text = str(int(placemark.tessellate))

        if any(isinstance(placemark, c) for c in [Point, Line]):
            coordinates_elem = etree.SubElement(placemark_class_elem, 'coordinates')
            level += 1
            # FIXME: Prepend enough tabs.
            coordinates_elem.text = "\n" + "\n".join(
                f"{self.INDENT * level}{self.float_to_str(c.x)},{self.float_to_str(c.y)},{self.float_to_str(c.z)}"
                for c in placemark.coordinates) + "\n" + self.INDENT * (level - 1)

    def save_folder(self, folder: Folder, elem: NodeType, level: int) -> None:
        folder_elem = etree.SubElement(elem, 'Folder')
        folder_name = etree.SubElement(folder_elem, 'name')
        folder_name.text = folder.name

        for placemark in folder.placemarks:
            self.save_placemark(placemark=placemark, elem=folder_elem, level=level + 1)

    def save_style(self, style: Style, elem: NodeType) -> None:
        elem.set('id', style.id_)

        if style.icon_style is not None:
            icon_style = etree.SubElement(elem, 'IconStyle')
            icon_style_color = etree.SubElement(icon_style, 'color')
            icon_style_color.text = style.icon_style.color
            icon_style_scale = etree.SubElement(icon_style, 'scale')
            icon_style_scale.text = self.float_to_str(style.icon_style.scale)
            icon_style_icon = etree.SubElement(icon_style, 'Icon')
            icon_style_icon_href = etree.SubElement(icon_style_icon, 'href')
            icon_style_icon_href.text = style.icon_style.icon.href
            if style.icon_style.hotSpot is not None:
                icon_style_hotspot = etree.SubElement(icon_style, 'hotSpot')
                icon_style_hotspot.attrib['x'] = str(style.icon_style.hotSpot.x)
                icon_style_hotspot.attrib['xunits'] = style.icon_style.hotSpot.xunits
                icon_style_hotspot.attrib['y'] = str(style.icon_style.hotSpot.y)
                icon_style_hotspot.attrib['yunits'] = style.icon_style.hotSpot.yunits

        if style.line_style is not None:
            line_style = etree.SubElement(elem, 'LineStyle')
            line_style_color = etree.SubElement(line_style, 'color')
            line_style_color.text = style.line_style.color
            line_style_width = etree.SubElement(line_style, 'width')
            line_style_width.text = self.float_to_str(style.line_style.width)

        if style.label_style is not None:
            label_style = etree.SubElement(elem, 'LabelStyle')
            label_style_scale = etree.SubElement(label_style, 'scale')
            label_style_scale.text = self.float_to_str(style.label_style.scale)

        if style.balloon_style is not None:
            balloon_style = etree.SubElement(elem, 'BalloonStyle')
            balloon_style_text = etree.SubElement(balloon_style, 'text')
            balloon_style_text.text = self.get_cdata_text(style.balloon_style.text)

    def save_stylemap(self, stylemap: StyleMap, elem: NodeType) -> None:
        elem.set('id', stylemap.id_)

        pair = etree.SubElement(elem, 'Pair')
        key = etree.SubElement(pair, 'key')
        key.text = 'normal'
        style_url = etree.SubElement(pair, 'styleUrl')
        style_url.text = f"#{stylemap.normal.id_}"

        pair = etree.SubElement(elem, 'Pair')
        key = etree.SubElement(pair, 'key')
        key.text = 'highlight'
        style_url = etree.SubElement(pair, 'styleUrl')
        style_url.text = f"#{stylemap.highlight.id_}"
