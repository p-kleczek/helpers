
import re
import shutil
import time
from os import walk
import os.path
from pathlib import Path
from typing import List, Tuple

from PIL import Image, UnidentifiedImageError


if __name__ == "__main__":
    in_dir_path: Path = Path(r'/media/pawel/Samsung_T5/Multimedia/Muzyka/~ All-in-one/Autor-utwor/')

    make_copy: bool = True
    "If True, a (renamed) copy of a photo will be made."

    out_dir_path: Path = in_dir_path / "_RENAMED_" if make_copy else in_dir_path
    if not os.path.isdir(out_dir_path):
        os.mkdir(out_dir_path)

    DEBUG_ON: bool = True
    do_rename: bool = True

    if not DEBUG_ON:
        print('Are you sure you want to rename files? [y/N]')
        answer = input()
        if answer == 'y':
            do_rename = True
        else:
            print('Files not renamed.')

    if not do_rename:
        print("NOTE: Files will not be renamed.")

    change_list: List[Tuple[str, str]] = []  # Old -> New

    (_, _, filenames) = next(walk(in_dir_path))
    for old_filename in filenames:
        old_path: Path = in_dir_path / old_filename

        new_stem: str

        # Replace [] with {}
        # new_stem = old_path.stem.replace("[", "{").replace("]", "}")

        # Replace "Artist - Title" with "Title {Artist}"
        chunks = old_path.stem.split(" - ")
        new_stem = f"{chunks[1]} {{{chunks[0]}}}"

        new_filename = new_stem + old_path.suffix
        new_path = out_dir_path / new_filename

        if DEBUG_ON:
            print(f'{old_path} -> {new_path}')

        if make_copy:
            shutil.copyfile(old_path, new_path)
        else:
            if do_rename:
                os.rename(old_path, new_path)

        change_list.append((old_filename, new_filename))

    print('Done! :)')

    current_dir = Path(__file__).parent
    out_list_dir = current_dir / "out"
    if not os.path.isdir(out_list_dir):
        os.mkdir(out_list_dir)

    with open(out_list_dir / "list.txt", "w") as out_file:
        out_file.write("\n".join(f"{old}\t{new}" for old, new in change_list))
