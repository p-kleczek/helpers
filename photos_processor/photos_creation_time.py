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
from enum import IntEnum
from pathlib import Path

from PIL import Image

# In order to install 'pyexiv2', first install:
#   sudo apt install exiv2
#   sudo apt install python3-dev
#   sudo apt install libexiv2-dev
#   sudo apt install libboost-python-dev
# import pyexiv2

# Installation:
# pip install PyExifTool
import exiftool

img_datetime_filename_chunk_pattern = re.compile(
    r'(?P<full>(?P<Y>\d{4})(?P<m>\d{2})(?P<d>\d{2})_(?P<H>\d{2})(?P<M>\d{2})(?P<S>\d{2}))')
"YYYYmmdd_MMHHSS (np. IMG_20201005_071043.JPG)"

exif_datetime_pattern = re.compile(
    r'.*(?P<Y>\d{4}):(?P<m>\d{2}):(?P<d>\d{2}) (?P<H>\d{2}):(?P<M>\d{2}):(?P<S>\d{2})')


class ExifTag(IntEnum):
    """See: https://www.awaresystems.be/imaging/tiff/tifftags/search.html"""
    Make = 271
    "The scanner manufacturer."
    DateTime = 306
    "Date and time of image creation."
    DateTimeOriginal = 36867
    "The date and time when the original image data was generated."


class NotCameraImageException(Exception):
    pass


def get_datetime_taken(path: Path) -> datetime:
    file_extension: str = str(path.suffix).lower()

    if (m := img_datetime_filename_chunk_pattern.search(str(path))) is not None:
        t = datetime.strptime(m.group('full'), "%Y%m%d_%H%M%S")
    elif file_extension in ('.jpeg', '.jpg'):
        # EXIF tags: https://exiv2.org/tags.html
        exif = Image.open(path).getexif()._get_merged_dict()
        if ExifTag.Make.value not in exif:
            raise NotCameraImageException(f"{path} was NOT created using a camera"
                                          f" (it does not contain EXIF scanner manufacturer tag).")
        date_taken_str: str = exif[ExifTag.DateTimeOriginal.value]
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
