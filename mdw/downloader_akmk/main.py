import datetime
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

from archives import *

import _tkinter
import pyautogui
import tkinter

# FIXME: These settings are OS-dependent!
download_dir: Path = Path(r"C:\Users\pkleczek\Downloads")
repo_root_dir: Path = Path(r"D:\! KleczekPawel\Mszana\AOff_AAdm")

# queue: List[ArchiveBookId] = ['AAdm 13', 'AAdm 14', 'AAdm 15', 'AAdm 22']
queue: List[ArchiveBookId] = ['AOff 165', 'AOff 169',
                              'AAdm 10', 'AAdm 11', 'AAdm 12', 'AAdm 13', 'AAdm 14', 'AAdm 15', 'AAdm 22']
# FIXME: Verify:
# 'AOff 166','AOff 167', 'AOff 168',

@dataclass
class Point:
    x: int
    y: int


Setup = str
WindowsPlacement = str
Browser = str

address_bar_coords_repo: Dict[Setup, Dict[WindowsPlacement, Dict[Browser, Point]]] = {
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

setup = 'work'
windows_placement = 'fullscreen'
browser = 'chrome'
address_bar_coords = address_bar_coords_repo[setup][windows_placement][browser]
download_button_coords = download_button_coords_repo[setup][windows_placement][browser]

# Idle time between clicking "Download" button and proceeding to the next page.
download_interval_secs: float = 1.0

class AKMKColors:
    preview_background = (89, 89, 89)
    title_bar_background = (0, 77, 130)


def get_book_file_id(book_id: ArchiveBookId) -> str:
    return book_id.replace(' ', '_')


def get_missing_pages_indexes(book_id: ArchiveBookId, download_dir: Path) -> Set[int]:
    book_file_id = get_book_file_id(book_id)

    expected_pages: Dict[str, PageIndex] = {}
    page_number: int = 1
    page_side: PageSide = PageSide.r
    book: ArchiveBookData = archive_books[book_id]
    for page_index in range(book.first_notes_page_inx, book.last_notes_page_inx + 1):
        page_id = f"AKMKr_{book_file_id}#{page_number:04d}_{page_side}"
        expected_pages[page_id] = page_index
        if book.current_page_numbering == PageNumeringType.Pagination or page_side == PageSide.v:
            page_number += 1
        page_side = PageSide.v if page_side == PageSide.r else PageSide.r

        if book_id == 'AAdm 13' and page_number == 11 and page_side == PageSide.v:
            # NOTE: CAAK has incorrect numbering of pages for this book, after 11r goes 12v.
            page_number = 12

    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        for filename in filenames:
            if book_file_id not in filename or not filename.endswith('.jpg'):
                continue
            page_id = filename.split('.')[0]
            try:
                expected_pages.pop(page_id)
            except KeyError as e:
                print(f"Key not found: {page_id}")
        break  # Do not visit directories recursively.

    return set(expected_pages.values())

def build_caak_url(page_no: int) -> str:
    return f"https://caak.upjp2.edu.pl/j/{archival_entry.url_id}/s/{page_no - 1}/f"


def get_url_content() -> str:
    pyautogui.moveTo(address_bar_coords.x, address_bar_coords.y)
    pyautogui.click(clicks=2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')

    while True:
        try:
            clipboard_content = tkinter.Tk().clipboard_get()
            break
        except _tkinter.TclError:
            time.sleep(1)
    return clipboard_content

def abort_if_not_on_akmk_webpage():
    if browser != 'chrome':
        print('Not implemented - missing coordinates')
        return

    title_bar_background_color_sample_locations = [
        Point(x=190, y=220),
        Point(x=1000, y=300),
        Point(x=1700, y=250),
    ]

    for point in title_bar_background_color_sample_locations:
        sampled_color = pyautogui.pixel(point.x, point.y)
        if sampled_color != AKMKColors.title_bar_background:
            print("Likely not on AKMK website.")
            exit(1)

    preview_background_sample_locations = [
        Point(x=650, y=450),
        Point(x=1250, y=450),
        Point(x=650, y=900),
        Point(x=1250, y=900),
    ]

    for point in preview_background_sample_locations:
        sampled_color = pyautogui.pixel(point.x, point.y)
        if sampled_color != AKMKColors.preview_background:
            print("Likely not on AKMK website.")
            exit(1)

def put_url_to_clipboard(url: str):
    while True:
        try:
            r = tkinter.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(url)
            r.update()  # Now it stays on the clipboard after the window is closed.
            r.destroy()
            break
        except _tkinter.TclError:
            time.sleep(1)

def paste_url_from_clipboard():
    pyautogui.moveTo(address_bar_coords.x, address_bar_coords.y)
    pyautogui.click(clicks=2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'v')

def visit_webpage(url: str):
    print(f"Visiting: {url}")

    while True:
        # NOTE: New way of inserting the address (needs to be refined).
        # pyautogui.moveTo(address_bar_coords.x, address_bar_coords.y)
        # pyautogui.click(clicks=2)
        # pyautogui.hotkey('ctrl', 'a')
        # abort_if_not_on_akmk_webpage()
        # put_url_to_clipboard(url)
        # paste_url_from_clipboard()

        # NOTE: Old way of inserting the address.
        pyautogui.moveTo(address_bar_coords.x, address_bar_coords.y)
        pyautogui.click(clicks=2)
        pyautogui.hotkey('ctrl', 'a')
        # abort_if_not_on_akmk_webpage()
        # pyautogui.press('del')
        # abort_if_not_on_akmk_webpage()
        pyautogui.write(url, interval=0.025)

        url_content = get_url_content()
        if url_content == url:
            break

        print(f"ULR: expected = {url}, actual = {url_content}")
        print("Retrying...")

    pyautogui.press('enter')


def reload_webpage():
    pyautogui.hotkey('ctrl', 'f5')


def wait_until_loaded():
    initial_timeout_secs = 1.5
    subsequent_timeout_secs = 0.5
    max_waiting_time_secs = 30

    time.sleep(initial_timeout_secs)
    n_retries = 0
    download_start = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        if (download_start - now).seconds > max_waiting_time_secs:
            n_retries = 0
            reload_webpage()
            time.sleep(initial_timeout_secs)
        # DEBUG: Take a screenshot.
        # from PIL import ImageGrab
        # image = ImageGrab.grab()
        # sampled_color = image.getpixel((sample_location.x, sample_location.y))
        # image.save("screenshot.png")

        sample_location = Point(x=950, y=960)
        sampled_color = pyautogui.pixel(sample_location.x, sample_location.y)

        # if pyautogui.pixelMatchesColor(sample_location.x, sample_location.y, preview_background_color)
        if sampled_color != AKMKColors.preview_background:
            break
        print("Waiting for full preview...")
        n_retries += 1
        time.sleep(subsequent_timeout_secs)

def is_download_list_opened():
    if browser == 'chrome':
        download_list_background_color = (253, 251, 255)
    elif browser == 'firefox':
        download_list_background_color = (255, 255, 255)
    else:
        raise NotImplemented

    if browser == 'chrome':
        sample_location = Point(x=1315, y=340)
    elif browser == 'firefox':
        sample_location = Point(x=1400, y=630)
    else:
        raise NotImplemented

    sampled_color = pyautogui.pixel(sample_location.x, sample_location.y)
    return sampled_color == download_list_background_color

def click_download():
    pyautogui.click(download_button_coords.x, download_button_coords.y)

def move_downloaded_files(book_id: ArchiveBookId, repo_dir: Path):
    book_file_id = get_book_file_id(book_id)
    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        for filename in filenames:
            if book_file_id not in filename or not filename.endswith('.jpg'):
                continue
            try:
                shutil.move(download_dir / filename, repo_dir / filename)
            except Exception as e:
                print(f"Error while moving file {book_id}/{filename}: {e}")
        break  # Do not visit directories recursively.

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    num_downloaded_pages = 0

    for archive_signature in queue:
        book_file_id = get_book_file_id(archive_signature)
        repo_dir: Path = repo_root_dir / book_file_id
        move_downloaded_files(archive_signature, repo_dir)

    for archive_signature in queue:
        print(f"Processing archive: {archive_signature}")
        archival_entry = archive_books[archive_signature]

        book_file_id = get_book_file_id(archive_signature)
        repo_dir: Path = repo_root_dir / book_file_id

        # move_downloaded_files(archive_signature, repo_dir)
        expected_pages = get_missing_pages_indexes(archive_signature, repo_dir)
        print(f"\tPage indexes to download: {sorted(expected_pages)}")
        print()

        for page_inx in sorted(expected_pages):
            page_no = page_inx + 1
            caak_url = build_caak_url(page_no)

            # # FIXME: Click on task bar.
            # upper_row_y: int = 1035
            # # pyautogui.click(500, 1065)
            # pyautogui.click(600, upper_row_y)
            # time.sleep(1)
            # # pyautogui.click(600, 1065)
            # pyautogui.click(765, upper_row_y)
            # time.sleep(1)

            visit_webpage(caak_url)
            wait_until_loaded()

            # NONTE: In case of the list of downloaded file being visible, click in "safe area" to close it.
            safe_point = Point(x=150, y=500)
            pyautogui.click(safe_point.x, safe_point.y)
            time.sleep(0.2)
            # if is_download_list_opened():
            #     # NONTE: If the list of downloaded file is visible, click in "safe area" to close it.
            #     safe_point = Point(x=150, y=500)
            #     pyautogui.click(safe_point.x, safe_point.y)
            click_download()
            num_downloaded_pages += 1

            now = datetime.datetime.now()
            total_time = (now - start_time).seconds
            print(f"Downloaded at: {now} \t (avg. speed: {total_time / num_downloaded_pages:.1f} p./sec.)")

            time.sleep(download_interval_secs)

    print("All downloads completed.")
