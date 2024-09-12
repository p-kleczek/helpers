import csv
from enum import Enum, auto
from typing import Optional

class Orientation(Enum):
    Horizontal = auto()
    Landscape = auto()

OWN_SOURCE = "(zdjęcie własne)"
# (źródło: [[URL|SOURCE]])

def gen_desc(figure_id: str, img_path: str, orientation: Orientation, caption: str, source: Optional[str]) -> str:
    width: int = 400 if orientation == Orientation.Landscape else 300
    source_str: str = f" \\\\ [size=80%]{source}[/size]" if source else ""
    return f"""
<WRAP centeralign>
<figure {figure_id}>
{{{{:{img_path}?{width}}}}}
<caption>
{caption}{source_str}
</caption>
</figure>
</WRAP>
/* (Rys. {{{{ref>{figure_id}}}}}) */
    """.strip()


img_path_root: str = "sources:kronika_gssch"
with open('desc.txt', newline='\n') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')

    for inx, row in enumerate(reader):
        if inx == 0:
            continue

        figure_id = row[0]
        orientation = Orientation.Landscape  # FIXME: Check image size.

        print(gen_desc(figure_id=figure_id,
                       img_path=f"{img_path_root}:{figure_id}.jpg",
                       orientation=orientation,
                       caption=row[2],
                       source=None))
        print()
#
# with open("desc.txt") as f:
#     lines = f.readlines()[1:]
#
# for line in lines:
#     tokens = line.split('\t')
#
