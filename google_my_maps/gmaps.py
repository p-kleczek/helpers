# FIXME: Make sure input files are FRESH (e.g., downloaded on the same day when merging takes place)
#  - Google often changes the location of images on the server, so that using stalled data might result in
#  gray images being displayed instead of the original ones.

# NOTES:
# *) After uploading the new map to Google MyMaps, ALWAYS check whether the result has correct image URLs.

from pathlib import Path

from lxml import etree

from google_my_maps.kml_types import Document
from google_my_maps.my_parser import MyParser
from google_my_maps.merger import verify_and_fix_map, merge_maps, refactor_map


def export_document(document: Document, output_path: Path) -> None:
    parser = MyParser()
    kml = parser.save_kml(document)

    et = etree.ElementTree(kml)
    etree.indent(et, space="  ")
    # et.write('output.kml', pretty_print=True, xml_declaration=True, encoding='UTF-8')
    xml_out = etree.tostring(et, pretty_print=True, xml_declaration=False, encoding='UTF-8',
                             doctype='<?xml version="1.0" encoding="UTF-8"?>')

    with open(output_path, 'wb') as f:
        f.write(xml_out)


warto_zobaczyc_path = Path("./input/") / "Warto zobaczyć - wersja nowa.kml"


def test_merge():
    alpy2023_path = Path("./input/") / "Alpy 2023 - mapa.kml"

    merged_map = merge_maps(root_map_path=warto_zobaczyc_path,
                            added_maps_paths=[alpy2023_path])

    export_document(merged_map, output_path=Path('output/merged.kml'))


def test_merge_2():
    alpy2023_path = Path("/home/pawel/Downloads/Alpy 2023 - mapa(1).kml")
    warto_zobaczyc_path = Path("/home/pawel/Downloads/Warto zobaczyć - wersja nowa.kml")

    merged_map = merge_maps(root_map_path=warto_zobaczyc_path,
                            added_maps_paths=[alpy2023_path])

    export_document(merged_map, output_path=Path('output/merged.kml'))


def test_reexport(input_path: Path):
    parser = MyParser()
    parsed_document = parser.parse_kml(input_path)
    # parsed_document = parser.parse_kml(Path("./tests/") / "sample.kml")
    # parsed_document = parser.parse_kml(Path("/home/pawel/Downloads/") / "Podlasie 2023.kml")
    # parsed_document = parser.parse_kml(Path("/home/pawel/Downloads/") / "Warto zobaczyć - wersja nowa.kml")

    verify_and_fix_map(parsed_document)
    refactor_map(parsed_document)

    export_document(parsed_document, output_path=Path('output.kml'))


# test_reexport(input_path=Path("/home/pawel/Downloads/Warto zobaczyć - wersja nowa(1).kml"))
# test_reexport(input_path=Path("/home/pawel/Downloads/Alpy 2023 - mapa.kml"))
# test_reexport(input_path=Path("./input/Bałkany 2022 [mapa].kml"))
# test_reexport(input_path=Path("./input/Barcelona 2022 [mapa].kml"))
# test_reexport(input_path=Path("./input/Listopadówka 2023-10_11 - mapa.kml"))
# test_reexport(input_path=Path("./input/Majówka 2023 - Beskid Niski (rowerowo).kml"))
# test_reexport(input_path=Path("./input/Podlasie 2023.kml"))
test_reexport(input_path=Path("./input/Słowacja 2022-06.kml"))
# test_merge()
# test_merge_2()
