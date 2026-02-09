from pathlib import Path
from typing import Dict, Tuple

from mdw.downloader_akmk.commons import Point

Setup = str
WindowsPlacement = str
Browser = str

ColorType = Tuple[int, int, int]

download_dir_repo: Dict[Setup, Path] = {
    'priv-pk' : Path(r"/home/pawel/Downloads/"),
    'work': Path(r"C:\Users\pkleczek\Downloads"),
}

repo_root_dir_repo:  Dict[Setup, Path] = {
    'priv-pk' : Path(r"/home/pawel/Downloads/CAAK"),
    'work': Path(r"D:\! KleczekPawel\Mszana\AOff_AAdm"),
}

address_bar_coords_repo: Dict[Setup, Dict[WindowsPlacement, Dict[Browser, Point]]] = {
    'priv-pk' : {
        'fullscreen': {
            'chrome': Point(x=210, y=65),
            'firefox': Point(x=430, y=65),
        }
    },
    'priv-ak': {
        'side-by-side': Point(x=1250, y=90),
        # 'fullscreen':,
    },
    'work': {
        # 'side-by-side': Point(1250, 90),
        'fullscreen': {
            'chrome': Point(x=210, y=65),
            'firefox': Point(x=430, y=65),
        }
    },
}

download_button_coords_repo: Dict[Setup, Dict[WindowsPlacement, Dict[Browser, Point]]] = {
    'priv-pk': {
        'fullscreen': {
            'chrome': Point(x=1390, y=355),
            'firefox': Point(x=1330, y=350),
        }
    },
    'priv-ak': {
        'side-by-side': Point(x=1250, y=90),
        # 'fullscreen':,
    },
    'work': {
        # 'side-by-side': Point(1250, 90),
        'fullscreen': {
            'chrome': Point(x=1390, y=355),
            'firefox': Point(x=1400, y=350),
        }
    },
}

download_list_background_color_repo: Dict[Browser, ColorType] = {
    'chrome': (253, 251, 255),
    'firefox': (255, 255, 255),
}

download_list_sample_location_repo: Dict[Browser, Point] = {
    'chrome': Point(x=1315, y=340),
    'firefox': Point(x=1400, y=630),
}

safe_point_location_repo: Dict[Browser, Point] = {
    'chrome': Point(x=150, y=500),
    'firefox': Point(x=150, y=500),
}
