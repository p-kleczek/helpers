from pathlib import Path

from lxml import etree

from google_my_maps.my_parser import MyParser

parser = MyParser()
parsed_document = parser.parse_kml(Path("./tests/") / "sample.kml")
# parsed_document = parser.parse_kml(Path("/home/pawel/Downloads/") / "Podlasie 2023.kml")
# parsed_document = parser.parse_kml(Path("/home/pawel/Downloads/") / "Warto zobaczyć - wersja nowa.kml")

# print(parsed_document)
kml = parser.save_kml(parsed_document)

et = etree.ElementTree(kml)
etree.indent(et, space="  ")
et.write('output.kml', pretty_print=True, xml_declaration=True, encoding='UTF-8')
