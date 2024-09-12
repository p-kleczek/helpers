# EXIF key:
# - Karolina Gajczak: 306
# 36867
# Image.open(path).getexif()[]
import os
import shutil
from os import walk
from pathlib import Path
from typing import List, Tuple

from PIL import UnidentifiedImageError

from photos_processor.photos_creation_time import create_date_taken_prefix, get_datetime_taken, NotCameraImageException

# '2014:07:27 00:33:11'

make_copy: bool = True
"If True, a (renamed) copy of a photo will be made."
DEBUG_ON: bool = True
do_rename: bool = True
"Should the rename be actually performed?"

if __name__ == "__main__":
    # Bałkany
    # in_dir_path: Path = Path(r'/media/pawel/Samsung_T5/Multimedia/Zdjęcia/2022-08-13_28 - Bałkany 2022 {VARIA}/Ania&Rafal/')
    # in_dir_path: Path = Path(r'/media/pawel/Samsung_T5/Multimedia/Zdjęcia/2022-08-13_28 - Bałkany 2022 {VARIA}/Redmi 4A/')
    # in_dir_path: Path = Path(r'/media/pawel/Samsung_T5/Multimedia/Zdjęcia/2022-08-13_28 - Bałkany 2022 {VARIA}/Samsung/')

    # Podróż poślubna
    # in_dir_path: Path = Path(r'/media/pawel/data/My Pictures/2023-06-08_25 - Podróż poślubna/')
    # in_dir_path: Path = Path(r'/media/pawel/data/My Pictures/2023-06-08_25 - Podróż poślubna/iPhone_PK/')
    # in_dir_path: Path = Path(r'/media/pawel/data/My Pictures/2023-06-08_25 - Podróż poślubna/iPhone_AK/')
    # in_dir_path: Path = Path(r'/media/pawel/data/My Pictures/2023-06-08_25 - Podróż poślubna/MOV_test/')

    # Podlasie 2023
    # in_dir_path: Path = Path(r'/home/pawel/Pictures/Podlasie 2023/AK/')
    # in_dir_path: Path = Path(r'/home/pawel/Pictures/Podlasie 2023/Nikon/')
    # in_dir_path: Path = Path(r'/home/pawel/Pictures/Podlasie 2023/PK/')

    in_dir_path: Path = Path(r'/home/pawel/Pictures/Beskid Żywiecki 2023/Pawel_Rename/')
    # in_dir_path: Path = Path(r'/home/pawel/Pictures/Beskid Żywiecki 2023/Aneta_Rename/')
    in_dir_path: Path = Path(r'/home/pawel/Pictures/Majówka 2024/')

    # ---

    out_dir_path: Path = in_dir_path / "_RENAMED_" if make_copy else in_dir_path

    if do_rename and not make_copy:
        assert str(in_dir_path).endswith('Rename'), "The input path must end with `Rename.`"

    if not DEBUG_ON:
        if do_rename:
            print('Are you sure you want to rename files? [y/N]')
            answer = input()
            if answer == 'y':
                do_rename = True
        if not do_rename:
            print('Files will NOT be renamed.')

    change_list: List[Tuple[str, str]] = []  # Old -> New

    if make_copy and do_rename and not out_dir_path.exists():
        os.makedirs(out_dir_path)

    (_, _, filenames) = next(walk(in_dir_path))
    for old_filename in filenames:
        old_path: Path = in_dir_path / old_filename
        try:
            take_datetime = get_datetime_taken(old_path)
            prefix = create_date_taken_prefix(taken_datetime=take_datetime, is_short=False)
            # prefix = filename[:-4].replace('.', '-').replace(' ', '_')
        except NotCameraImageException as e:
            print(f"{e} -- skipping")
            continue
        except (KeyError, UnidentifiedImageError, ValueError) as e:
            print(f"Error ({type(e)}) `{e}` while processing {old_path}")
            continue
        new_filename: str = f'{prefix}_{old_filename}'
        new_path = out_dir_path / new_filename

        if DEBUG_ON:
            print(f'{old_path} -> {new_path}')

        if do_rename:
            if make_copy:
                shutil.copy2(old_path, new_path)
            else:
                os.rename(old_path, new_path)

        # change_list.append((old_filename, new_filename))
        change_list.append((old_filename, new_filename))

    print('Done! :)')

    with open(Path("out/list.txt"), "w") as out_file:
        out_file.write("\n".join(f"{old}\t{new}" for old, new in change_list))
