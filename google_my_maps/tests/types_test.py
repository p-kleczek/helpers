import unittest
from pathlib import Path

from lxml import etree

from google_my_maps.my_parser import MyParser
from google_my_maps.kml_types import Document, Style, IconStyle, Icon, LabelStyle, BalloonStyle, StyleMap, LineStyle, \
    Folder, Point, Coordinate, Line


class TestStringMethods(unittest.TestCase):

    def test_parse_style(self):
        parser = MyParser()
        xml = """
            <Style id="ID">
      <IconStyle>
        <color>ffb0279c</color>
        <scale>1</scale>
        <Icon>
          <href>https://www.dummy.com</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
      <BalloonStyle>
        <text><![CDATA[txt]]></text>
      </BalloonStyle>
    </Style>
        """
        node = etree.fromstring(xml)

        expected_output = Style(
            id_="ID",
            icon_style=IconStyle(
                color="ffb0279c",
                scale=1.0,
                icon=Icon(
                    href="https://www.dummy.com"
                )
            ),
            label_style=LabelStyle(
                scale=0.0,
            ),
            balloon_style=BalloonStyle(
                text="<![CDATA[txt]]>",
            )
        )

        self.assertEqual(expected_output, parser.parse_style(node))

    def test_parse_stylemap(self):
        style1 = Style(id_="s1")
        style2 = Style(id_="s2")

        parser = MyParser()
        parser.styles = {
            style1.id_: style1,
            style2.id_: style2,
        }

        xml = f"""
    <StyleMap id="ID">
      <Pair>
        <key>normal</key>
        <styleUrl>#{style1.id_}</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#{style2.id_}</styleUrl>
      </Pair>
    </StyleMap>
        """
        node = etree.fromstring(xml)

        expected_output = StyleMap(
            id_="ID",
            normal=style1,
            highlight=style2,
        )

        self.assertEqual(expected_output, parser.parse_stylemap(node))

    def test_parse_placemark_point(self):
        stylemap1 = StyleMap(id_="sm1", normal=Style(id_="s1"), highlight=Style(id_="s2"))

        parser = MyParser()
        parser.style_maps = {
            stylemap1.id_: stylemap1,
        }

        xml = f"""
      <Placemark>
        <name>Point 1</name>
        <styleUrl>#{stylemap1.id_}</styleUrl>
        <Point>
          <coordinates>
            1,2,3
          </coordinates>
        </Point>
      </Placemark>
        """
        node = etree.fromstring(xml)

        expected_output = Point(
            name="Point 1",
            stylemap=stylemap1,
            coordinates=[
                Coordinate(1, 2, 3)
            ],
        )

        self.assertEqual(expected_output, parser.parse_placemark(node))

    def test_parse_placemark_line(self):
        stylemap1 = StyleMap(id_="sm1", normal=Style(id_="s1"), highlight=Style(id_="s2"))

        parser = MyParser()
        parser.style_maps = {
            stylemap1.id_: stylemap1,
        }

        xml = f"""
      <Placemark>
        <name>Line 1</name>
        <styleUrl>#{stylemap1.id_}</styleUrl>
        <LineString>
          <tessellate>1</tessellate>
          <coordinates>
            1,2,3
            4,5,6
          </coordinates>
        </LineString>
      </Placemark>
        """
        node = etree.fromstring(xml)

        expected_output = Line(
            name="Line 1",
            stylemap=stylemap1,
            tessellate=True,
            coordinates=[
                Coordinate(1, 2, 3),
                Coordinate(4, 5, 6),
            ],
        )

        self.assertEqual(expected_output, parser.parse_placemark(node))

    def test_parsing(self):
        style1_normal = Style(
            id_="icon-1502-9C27B0-nodesc-normal",
            icon_style=IconStyle(
                color="ffb0279c",
                scale=1.0,
                icon=Icon(
                    href="https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
                )
            ),
            label_style=LabelStyle(
                scale=0.0,
            ),
            balloon_style=BalloonStyle(
                text="<![CDATA[<h3>$[name]</h3>]]>",
            )
        )

        style1_highlight = Style(
            id_="icon-1502-9C27B0-nodesc-highlight",
            icon_style=IconStyle(
                color="ffb0279c",
                scale=1.0,
                icon=Icon(
                    href="https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
                )
            ),
            label_style=LabelStyle(
                scale=1.0,
            ),
            balloon_style=BalloonStyle(
                text="<![CDATA[<h3>$[name]</h3>]]>",
            ),
        )

        styleMap1 = StyleMap(
            id_="icon-1502-9C27B0-nodesc",
            normal=style1_normal,
            highlight=style1_highlight
        )

        style2_normal = Style(
            id_="line-000000-1200-nodesc-normal",
            line_style=LineStyle(
                color="ff000000",
                width=1.2,
            ),
            balloon_style=BalloonStyle(
                text="<![CDATA[<h3>$[name]</h3>]]>",
            ),
        )

        style2_highlight = Style(
            id_="line-000000-1200-nodesc-highlight",
            line_style=LineStyle(
                color="ff000000",
                width=1.8,
            ),
            balloon_style=BalloonStyle(
                text="<![CDATA[<h3>$[name]</h3>]]>",
            ),
        )

        styleMap2 = StyleMap(
            id_="line-000000-1200-nodesc",
            normal=style2_normal,
            highlight=style2_highlight
        )

        expected_document = Document(
            name="Sample",
            style_maps=[
                styleMap1,
                styleMap2,
            ],
            folders=[
                Folder(
                    name="Punkty",
                    placemarks=[
                        Point(
                            name="Point 1",
                            stylemap=styleMap1,
                            coordinates=[Coordinate(20.4067731, 52.6252736, 0)],
                        ),
                    ],
                ),
                Folder(
                    name="Trasy",
                    placemarks=[
                        Line(
                            name="Line 1",
                            stylemap=styleMap2,
                            tessellate=True,
                            coordinates=[
                                Coordinate(21.8679547, 52.801645, 0),
                                Coordinate(22.0327497, 52.4079948, 0),
                                Coordinate(21.0549665, 52.243489, 0),
                            ],
                        ),
                    ],
                ),
            ]
        )

        parser = MyParser()
        parsed_document = parser.parse_kml(Path("sample.kml"))

        self.assertEqual(expected_document.name, parsed_document.name)
        self.assertEqual(expected_document.style_maps, parsed_document.style_maps)
        self.assertEqual(expected_document.folders, parsed_document.folders)
        self.assertEqual(expected_document, parsed_document)


if __name__ == '__main__':
    unittest.main()
