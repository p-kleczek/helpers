from pathlib import Path
from typing import List, re, Dict, Optional

tex_in_path: Path = Path(
    '/mnt/data/My Documents/AnetKa/Samochód (nowy)/Skoda Octavia IV Scout/Scout_IV_manual/Scout_IV_manual_RAW.tex')
tex_out_path: Path = Path('Scout_IV_manual_OUT.tex')

with open(tex_in_path) as f:
    lines_in = f.readlines()

lines_out: List[str] = []

Marker = str

itemize_map: Dict[Marker, str] = {
    '▶': 'Triangle',
    '›': 'Arrow',
    '✓': 'Tick',
}

current_itemize_markers: List[Marker] = []
"""Przechowuje hierarchię znaczników użytych w aktualnie przetwarzanym konspekcie wypunktowanym."""


def extract_marker(line: str) -> Optional[Marker]:
    stripped_line = line.lstrip()
    for marker in itemize_map.keys():
        if stripped_line.startswith(marker):
            return marker
    return None


# Sytuacje do rozpatrzenia:
# (1) W ogóle pierwsze itemize (po zwykłym akapicie) -> dodać BEGIN \itemize
# (2) Zagnieżdżone itemize (zmiana znacznika na nowy typ) -> dodać BEGIN \itemize
# (3) Zagnieżdżone itemize (zmiana znacznika na jeden z poprzednich typów występujących w hierarchii) -> dodać odpowiednią liczbę END \itemize (żeby zamknąć wszystkie otwarte znaczniki do pożądanego miejsca)
# (4) Koniec zagnieżdżonego itemize -> dodać odpowiednią liczbę END \itemize (żeby zamknąć wszystkie otwarte znaczniki)

# def insert_item(line_in: str, marker: Marker) -> None:
#     codename = itemize_map[marker]
#     lines_out.append("\t" + line_in.replace(marker, f"\\item{codename}"))

def end_itemize() -> None:
    tabs = "\t" * (len(current_itemize_markers) - 1)
    lines_out.append(tabs + f'\\end{{itemize{itemize_map[current_itemize_markers[-1]]}}}\n')
    current_itemize_markers.pop(-1)


for line_in_inx, line_in in enumerate(lines_in):
    line_in = line_in.replace('»', r'\guillemotright')

    marker = extract_marker(line_in)

    if marker is None:
        while current_itemize_markers:
            end_itemize()
        lines_out.append(line_in)
    else:
        codename = itemize_map[marker]
        previous_in_line = lines_in[line_in_inx - 1]
        curent_marker = current_itemize_markers[-1] if current_itemize_markers else None

        if curent_marker != marker:
            if marker in current_itemize_markers:
                # Przypadek (3)
                while current_itemize_markers[-1] != marker:
                    end_itemize()
            else:
                # Przypadek (1) albo (2)
                tabs = "\t" * len(current_itemize_markers)
                lines_out.append(tabs + f'\\begin{{itemize{codename}}}\n')
                current_itemize_markers.append(marker)

        tabs = "\t" * len(current_itemize_markers)
        lines_out.append(tabs + line_in.replace(marker, f"\\item{codename}"))

with open(tex_out_path, 'w', encoding='utf-8') as f:
    f.writelines(lines_out)
