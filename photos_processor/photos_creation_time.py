# ---------------------------------------------------------------------------------------------------------------------
# Q: Jak zmienić datę i godzinę wykonania zdjęcia?
#
# A: Począwszy od Windows 7 nie ma możliwości ręcznej zmiany godziny wykonania zdjęcia
# - można jednak użyć w tym celu programu Irfan View.
# Po otwarciu pliku wybierz: Options > Change JPG EXIF date/time (taken)...
# Aby dokonać zmiany dla potencjalnie wielu plików na raz:
#   - Otwórz: File >  Thumbnails
#   - Zaznacz zdjęcia, których datę wykonania chcesz zmienić.
#   - Wybierz: RMB > JPG Lossless operations > Change JPG EXIF date/time (date taken)...
#
# ---------------------------------------------------------------------------------------------------------------------

import os.path
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image

# In order to install 'pyexiv2', first install:
#   apt install exiv2
#   apt install python3-dev
#   apt install libexiv2-dev
#   apt install libboost-python-dev
# import pyexiv2

# pip install PyExifTool
import exiftool

img_datetime_filename_chunk_pattern = re.compile(
    r'(?P<full>(?P<Y>\d{4})(?P<m>\d{2})(?P<d>\d{2})_(?P<H>\d{2})(?P<M>\d{2})(?P<S>\d{2}))')
"YYYYmmdd_MMHHSS (np. IMG_20201005_071043.JPG)"

exif_datetime_pattern = re.compile(
    r'.*(?P<Y>\d{4}):(?P<m>\d{2}):(?P<d>\d{2}) (?P<H>\d{2}):(?P<M>\d{2}):(?P<S>\d{2})')


def get_datetime_taken(path: Path) -> datetime:
    file_extension: str = str(path.suffix).lower()

    if (m := img_datetime_filename_chunk_pattern.search(str(path))) is not None:
        t = datetime.strptime(m.group('full'), "%Y%m%d_%H%M%S")
    elif file_extension in ('.jpeg', '.jpg'):
        # EXIF tags: https://exiv2.org/tags.html
        # *) 36867 : Exif.Photo.DateTimeOriginal
        exif = Image.open(path).getexif()._get_merged_dict()
        # date_taken_str: str = exif[306]
        date_taken_str: str = exif[36867]
        m = exif_datetime_pattern.fullmatch(date_taken_str)
        assert m is not None, f"The EXIF date taken value (`{date_taken_str}`) does not match the pattern!"
        t = datetime.strptime(date_taken_str, "%Y:%m:%d %H:%M:%S")
    elif file_extension == '.mov':
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata([str(path)])[0]
        t = datetime.strptime(metadata['QuickTime:CreationDate'], "%Y:%m:%d %H:%M:%S%z")  # '2023:06:23 11:56:43+02:00'
    elif file_extension == '.mp4':
        date_taken_struct = time.gmtime(os.path.getmtime(path))
        t = datetime(*date_taken_struct[:6])
        # FIXME: Adjust for timezone.
        t += timedelta(hours=2)
    else:
        raise ValueError("Unsupported file extension.")

    return t


def create_date_taken_prefix(taken_datetime: datetime, is_short: bool = False) -> str:
    """

    :param taken_datetime: datetime at which an image/movie was taken
    :param is_short: Should create a short prefix?
    :return: image's prefix (based on datetime information)
    """
    prefix = taken_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    if is_short:
        prefix = prefix[:prefix.index('_')]

    return prefix
