import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Final

from google_my_maps.kml_types import Document, Point, Folder, Line, Placemark, Style, Text, StyleId, StyleTypes, \
    LineStyle, BalloonStyle, StyleMap, get_stylemap_id_line, get_style_id_line
from google_my_maps.my_parser import MyParser, create_placemark_style_id, \
    Folders
from google_my_maps.marking import StatusColors, Icons, line_width_normal
import lxml.etree
from lxml.etree import CDATA


def get_placemark_id(folder: Folder, placemark: Placemark) -> str:
    return f"{folder.name} / {str(placemark.name).strip()} [t={type(placemark).__name__}]"


def is_route_directions(folder: Folder) -> bool:
    MIN_NUM_OF_PLACEMARKS: Final = 3  # At least a line and its two endpoints.
    return (len(folder.placemarks) >= MIN_NUM_OF_PLACEMARKS and isinstance(folder.placemarks[0], Line)
            and all(isinstance(p, Point) for p in folder.placemarks[1:]))


def add_predefined_line_styles(map: Document) -> None:
    """
    Add all needed line styles (based on statuses) to <Style> and <StyleMap>.

    :param map: The document processed.
    """
    status_color: StatusColors
    for status_color in StatusColors:
        style_type: StyleTypes
        for style_type in StyleTypes:
            style_id = get_style_id_line(status_color=status_color, style_type=style_type)
            if style_id not in map.styles:
                def get_color(status: StatusColors) -> str:
                    color_rrggbb = status.lower()
                    rr = color_rrggbb[:2]
                    gg = color_rrggbb[2:4]
                    bb = color_rrggbb[4:]
                    return f"ff{bb}{gg}{rr}"

                map.styles[style_id] = Style(
                    id_=style_id,
                    line_style=LineStyle(
                        color=get_color(status=status_color),
                        width=line_width_normal,
                    ),
                    balloon_style=BalloonStyle(
                        text=Text("<h3>$[name]</h3>"),
                    )
                )
                map.styles_ordering.append(style_id)
        stylemap_id = get_stylemap_id_line(status_color=status_color)
        if stylemap_id not in map.style_maps:
            map.style_maps[stylemap_id] = StyleMap(
                id_=stylemap_id,
                normal=map.styles[get_style_id_line(status_color=status_color, style_type=StyleTypes.normal)],
                highlight=map.styles[get_style_id_line(status_color=status_color, style_type=StyleTypes.highlight)],
            )
            map.styles_ordering.append(stylemap_id)


def verify_and_fix_map(map: Document) -> None:
    print(f"[START] Fixing and verifying : \"{map.name}\" ...")

    add_predefined_line_styles(map)

    for folder_name, folder in map.folders.items():
        if 'Directions from' in folder_name:
            print(f"Skipping: {folder_name}")
            continue

        if m := re.match(r"\[.*] Dzień #(?P<day_no>\d+).*", folder_name):
            if is_route_directions(folder):
                print(f"Fixing route directions: {folder_name}")
                line = folder.placemarks[0]
                line.coordinates = line.coordinates[::2]  # Reduce the number of nodes.
                folder.placemarks = [line]  # Remove all waypoints; retain only the line.
                day_no = int(m.group('day_no'))
                line.style = None
                status = StatusColors.VISITED_AP if day_no % 2 == 1 else StatusColors.VISITED_AP_ROUTES_EVEN
                line.stylemap = map.style_maps[get_stylemap_id_line(status_color=status)]
                continue

        for placemark in folder.placemarks:
            status = None
            icon = None

            def current_placemark() -> str:
                return get_placemark_id(folder=folder, placemark=placemark)

            try:
                status = placemark.status
            except ValueError as e:
                print(f"{current_placemark()} : {e}")

            if isinstance(placemark, Point):
                try:
                    icon = placemark.icon
                except ValueError as e:
                    print(f"{current_placemark()} : {e}")

                if status is None or icon is None:
                    continue

                if (icon in [Icons.TRAIN]
                        and status != StatusColors.TRANSPORTATION):
                    print(f"{current_placemark()} : Invalid status for transportation!")

                if icon == Icons.DOWNTOWN:
                    new_style_id = create_placemark_style_id(
                        icon=Icons.CITY, status=status
                    )
                    if placemark.stylemap is not None:
                        placemark.stylemap.id_ = new_style_id
                    else:
                        placemark.style.id_ = new_style_id
            elif isinstance(placemark, Line):
                # FIXME: Make line widths consistent.
                pass


def refactor_map(root_doc: Document):
    print(f"[START] Refactoring : \"{root_doc.name}\" ...")

    folder_names = [Folders.POIS,
                    Folders.TRANSPORTATION,
                    Folders.ACCOMMODATION,
                    Folders.TRIPS,
                    Folders.AUXILIARY]
    new_folders: Dict[str, Folder] = {name: Folder(name=name) for name in folder_names}

    folder_filters: Dict[str, Set[Icons]] = {
        Folders.POIS: {
            Icons.DEFAULT,
            Icons.CIRCLE,
            Icons.STAR,
            Icons.CYCLING,
            Icons.KAYAKING,
            Icons.SKIING_DOWNHILL,
            Icons.SKIING_CROSS_COUNTRY,
            Icons.SWIMMING,
            Icons.BEACH,
            Icons.TREE_CONIFER,
            Icons.TREE_DECIDUOUS,
            Icons.MOUNTAIN,
            Icons.HIKING,
            Icons.VIEWPOINT,
            Icons.RESTAURANT,
            Icons.CAFE,
            Icons.SHOPPING_CART,
            Icons.TICKET_STAR,
            Icons.PARKING,
            Icons.PARK,
            Icons.LOOKOUT_TOWER,
            Icons.MONUMENT,
            Icons.MUSEUM,
            Icons.HISTORIC_BUILDING,
            Icons.VISTA_PARTIAL,
            Icons.CITY,
            Icons.HARDWARE,
            Icons.PLACE_OF_WORSHIP,
            Icons.INFORMATION,
            Icons.WALKING,
            Icons.DEATH,
            Icons.TRAIN_STEAM,
            Icons.LAKE,
        },
        Folders.TRANSPORTATION: {
            Icons.BUS,
            Icons.TRAIN,
            Icons.VEHICLE_FERRY,
            Icons.AIRPORT,
        },
        Folders.ACCOMMODATION: {
            Icons.CAMPING,
            Icons.HOTEL,
        },
        # Folders.TRIPS
        Folders.AUXILIARY: {
            Icons.HOUSE,
        },
    }

    for folder_name, folder in root_doc.folders.items():
        if 'Directions from' in folder_name:
            print(f"Skipping: {folder_name}")
            continue

        for placemark in folder.placemarks:
            style_id = (placemark.stylemap.id_ if placemark.stylemap is not None
                        else placemark.style.id_)

            placemark_name_str = str(placemark.name).strip()

            def current_placemark() -> str:
                return get_placemark_id(folder=folder, placemark=placemark)

            target_folder_name: Optional[str] = None
            if isinstance(placemark, Point):
                try:
                    icon = placemark.icon
                except ValueError as e:
                    print(f"{folder.name} / {placemark.name} : {e}")
                    continue

                skipped_icons = {
                    Icons.DIAMOND,
                    Icons.CURRENCY_EXCHANGE,
                    Icons.GAS_STATION,
                    Icons.WATER,
                    Icons.X,
                    Icons.PICNIC,
                    Icons.RENTAL_CAR,
                }

                if icon in skipped_icons:
                    print(f"Skipped : {current_placemark()}")
                    continue

                for folder_name, icons in folder_filters.items():
                    if icon in icons:
                        target_folder_name = folder_name
                        break

                if (icon == Icons.RESTAURANT
                        and re.match(r"\[.*\] ", placemark_name_str)):
                    target_folder_name = Folders.TRIPS

            elif isinstance(placemark, Line):
                if placemark_name_str.startswith('#LK#'):
                    # Linia kolejowa
                    target_folder_name = Folders.TRANSPORTATION
                elif any(placemark_name_str.startswith(f'[{tag}]')
                         for tag in {'buty', 'rower', 'kolej', 'auto'}):
                    target_folder_name = Folders.POIS
                elif (re.fullmatch(r"\[.*\] Dzień #\d+.*", placemark_name_str)
                      or re.fullmatch(r"\[.*\] Trasa", placemark_name_str)
                      or "[Trasa]" in placemark_name_str):
                    # FIXME: Include also routes tagged with "Dzień #..."
                    target_folder_name = Folders.TRIPS
                    # FIXME: Set the proper status based on object's name:
                    # StatusColors.VISITED_AP,
                    # StatusColors.VISITED_AP_TREKS,
                    # StatusColors.VISITED_AP_ROUTES_EVEN,
            else:
                raise NotImplementedError(f"Placemark type: {type(placemark)}")

            if target_folder_name is None:
                print(f"Unhandled placemark: {current_placemark()}")
                continue

            new_folders[target_folder_name].placemarks.append(placemark)

    root_doc.clear_folders()
    for folder_name in folder_names:
        root_doc.add_folder(new_folders[folder_name])


def get_trip_name(map: Document) -> str:
    raw_name = map.name
    trip_name = raw_name.replace(" - mapa", "")
    return trip_name


def add_visited_note(placemark: Placemark, trip_name: str):
    # TODO: Test if works correctly with CDATA!
    description = placemark.description.text if placemark.description else ""

    visited_header: Final[str] = "Odwiedzone przy okazji:"
    if not description:
        description = f"{visited_header}\n- {trip_name}"
    else:
        if isinstance(description, CDATA):
            description = str(placemark.description)

        if visited_header in description:
            description += f"\n- {trip_name}"
        else:
            if not description.endswith('<br><br>'):
                description += "\n\n"
            description += f"{visited_header}\n- {trip_name}"
    description = re.sub("\n", "<br>", description)

    placemark.description = Text(description)


def merge_maps(root_map_path: Path, added_maps_paths: List[Path]) -> Document:
    parser = MyParser()

    root_doc = parser.parse_kml(root_map_path)

    verify_and_fix_map(root_doc)
    refactor_map(root_doc)

    added_docs: List[Document] = [parser.parse_kml(p) for p in added_maps_paths]

    for doc in added_docs:
        verify_and_fix_map(doc)
        refactor_map(doc)

    item: Document
    for item in added_docs:
        folder: Folder
        for folder_name, folder in item.folders.items():
            placemark: Placemark
            for placemark in folder.placemarks:
                if placemark.status in [
                    StatusColors.VISITED_P_ONLY,
                    StatusColors.VISITED_A_ONLY,
                    StatusColors.VISITED_AP,
                    StatusColors.VISITED_AP_TREKS,
                    StatusColors.VISITED_AP_ROUTES_EVEN,
                ]:
                    add_visited_note(placemark=placemark, trip_name=get_trip_name(item))
                root_doc.folders[folder_name].placemarks.append(placemark)

        for style_id in item.styles_ordering:
            if style_id in root_doc.styles_ordering:
                continue

            if style_id in item.styles:
                root_doc.add_style(item.styles[style_id])

            if style_id in item.style_maps:
                root_doc.add_stylemap(item.style_maps[style_id])

    return root_doc
