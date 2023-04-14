# EXIF key:
# - Karolina Gajczak: 306
# 36867
# Image.open(path).getexif()[]
import os
from os import walk
from pathlib import Path
from typing import List, Tuple

from PIL import UnidentifiedImageError

from photos_processor.photos_creation_time import create_date_taken_prefix, get_datetime_taken

# '2014:07:27 00:33:11'

if __name__ == "__main__":
    # dir_path = r'I:\DATA\Multimedia\Zdjęcia\2020-08-08_16 - Rumunia\Rumunia - MT\fix'
    # dir_path = r'C:\Users\Pawel\Downloads\Zdjęcia\2021-07-23_08-01 - Mazury [z Anetą]'
    # dir_path = r'C:\Users\Pawel\Downloads\Zdjęcia\2021-07-23_08-01 - Mazury [z Anetą]\rename'
    # dir_path: Path = Path(r'H:\DATA\Multimedia\Zdjęcia prywatne\2022-04-29_05-05 - Barcelona, Katalonia, Andora\Rename')
    in_dir_path: Path = Path(r'D:\! TEMP\test_images')
    in_dir_path: Path = Path(r'H:\Multimedia\Zdjęcia\2022-08-13_28 - Bałkany 2022\ALL_Nikon')

    make_copy: bool = True
    """If True, a (renamed) copy of a photo will be made."""

    out_dir_path: Path = in_dir_path / "_RENAMED_" if make_copy else in_dir_path

    if not make_copy:
        assert str(in_dir_path).endswith('Rename'), "The input path must end with `Rename.`"

    DEBUG_ON: bool = True
    do_rename: bool = False

    if not DEBUG_ON:
        if do_rename:
            print('Are you sure you want to rename files? [y/N]')
            answer = input()
            if answer == 'y':
                do_rename = True
        if not do_rename:
            print('Files will NOT be renamed.')

    change_list: List[Tuple[str, str]] = []  # Old -> New

    (_, _, filenames) = next(walk(in_dir_path))
    for old_filename in filenames:
        old_path: Path = in_dir_path / old_filename
        try:
            take_datetime = get_datetime_taken(old_path)
            prefix = create_date_taken_prefix(taken_datetime=take_datetime, is_short=False)
            # prefix = filename[:-4].replace('.', '-').replace(' ', '_')
        except (KeyError, UnidentifiedImageError, ValueError):
            continue
        new_filename: str = f'{prefix}_{old_filename}'
        new_path = out_dir_path / new_filename

        if DEBUG_ON:
            print(f'{old_path} -> {new_path}')

        if do_rename:
            os.rename(old_path, new_path)

        change_list.append((old_filename, new_filename))

    print('Done! :)')

    with open(Path("out/list.txt"), "w") as out_file:
        out_file.write("\n".join(f"{old}\t{new}" for old, new in change_list))
