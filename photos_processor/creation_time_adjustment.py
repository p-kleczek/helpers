# EXIF key:
# - Karolina Gajczak: 306
# 36867
# Image.open(path).getexif()[]
import os
import shutil
from datetime import datetime, timedelta
from os import walk
from pathlib import Path
from typing import List, Tuple

from PIL import UnidentifiedImageError

from photos_processor.photos_creation_time import create_date_taken_prefix, get_datetime_taken

if __name__ == "__main__":
    actual_datetime = datetime(year=2012, month=7, day=19, hour=9, minute=27, second=48)
    datetime_to_be_fixed = datetime(year=2008, month=6, day=6, hour=21, minute=46, second=56)
    time_offset = actual_datetime - datetime_to_be_fixed
    time_offset = timedelta(0)

    in_dir_path: Path = Path(
        r'/media/pawel/Samsung_T5/Multimedia/Zdjęcia/2012-07 - Rowery Podlasie-Litwa-Łotwa {rower}/Zdjęcia Adama/')

    make_copy: bool = True
    """If True, a (renamed) copy of a photo will be made."""

    out_dir_path: Path = in_dir_path / "_RENAMED_" if make_copy else in_dir_path

    if not make_copy:
        assert str(in_dir_path).endswith('Rename'), "The input path must end with `Rename.`"

    DEBUG_ON: bool = False
    do_rename: bool = False

    if not DEBUG_ON:
        if do_rename:
            print('Are you sure you want to rename files? [y/N]')
            answer = input()
            if answer == 'y':
                do_rename = True
        if not do_rename:
            print('Files will NOT be renamed.')

    print(f"dt={time_offset}")

    change_list: List[Tuple[str, str]] = []  # Old -> New

    (_, _, filenames) = next(walk(in_dir_path))
    for old_filename in filenames:
        old_path: Path = in_dir_path / old_filename
        try:
            take_datetime = get_datetime_taken(old_path)
            corrected_take_datetime = take_datetime + time_offset
            prefix = create_date_taken_prefix(taken_datetime=corrected_take_datetime, is_short=False)
        except (KeyError, UnidentifiedImageError, ValueError):
            continue
        new_filename: str = f'{prefix}_{old_filename}'
        new_path = out_dir_path / new_filename

        if DEBUG_ON:
            print(f'{old_path} -> {new_path}')

        if do_rename:
            os.rename(old_path, new_path)
        else:
            if not out_dir_path.exists():
                os.makedirs(out_dir_path)
            shutil.copy(old_path, new_path)

        change_list.append((old_filename, new_filename))

    print('Done! :)')

    with open(Path("out/list.txt"), "w") as out_file:
        out_file.write("\n".join(f"{old}\t{new}" for old, new in change_list))

# FIXME: How to modify EXIF tags...
#  https://stackoverflow.com/a/71732863/492221
# https://pypi.org/project/pyexiv2/
