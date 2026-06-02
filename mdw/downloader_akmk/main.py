import argparse
import datetime
import os
import re
import shutil
import time
from typing import Set, List

import pyperclip
import requests

from archives import *
from environment_settings import *

import _tkinter
import pyautogui
import tkinter

from mdw.downloader_akmk.environment_settings import repo_root_dir_repo
from mdw.downloader_akmk.sdm_crawler import get_sdm_imgs_urls

queue = list(archive_books.keys())

parser = argparse.ArgumentParser(prog='CAAK Downloader')
parser.add_argument('setup')
parser.add_argument('windows_placement')
parser.add_argument('browser')
parser.add_argument('--queue')
parser.add_argument('--indexes', action='store_true')
parser.add_argument('--screening', type=int, default=1, help="Download only every n-th page.")
args = parser.parse_args()

setup = args.setup
windows_placement = args.windows_placement
browser = args.browser
queue = args.queue.split(';') if args.queue else list(archive_books.keys())
indexes_only = args.indexes
screening_interval = args.screening

address_bar_coords = address_bar_coords_repo[setup][windows_placement][browser]
download_button_coords = download_button_coords_repo[setup][windows_placement][browser]
restart_app_button_coords = restart_app_button_coords_repo[setup][windows_placement]
stop_and_rerun_app_button_coords = stop_and_rerun_app_button_coords_repo[setup][windows_placement]
download_dir = download_dir_repo[setup]
repo_root_dir = repo_root_dir_repo[setup]
left_monitor_width_px = 1920 if setup in ['priv-pk', 'work'] else 0
x_offset = 1920 if setup == 'priv-pk' else 0  # Represents another offset to the right screen.

download_interval_secs_repo: Dict[ArchiveId, float] = {
    ArchiveId.SDM: 1.0,
    ArchiveId.CAAK: 6.0 if browser == 'chrome' else 10.0
}

download_safeguard_interval_secs: float = 1.0
"""Idle time between clicking "Download" button and proceeding to the next page."""

url_clipboard_retry_interval_secs: float = 1.0
"""Idle time before subsequent attempt to access clipboard."""
safe_point_click_timeout: float = 0.2
visiting_webpage_timeout: float = 2.0
timeout_download_button_click_secs: float = 5.0
timeout_download_subsequent_secs: float = 0.5
max_waiting_time_secs: float = 60
get_pixel_error_timeout: float = 5.0
num_downloads_before_reload: int = 50


class AKMKColors:
    preview_background = (89, 89, 89)
    title_bar_background = (0, 77, 130)


def get_book_file_id(book_id: ArchiveBookId) -> str:
    return book_id.replace(' ', '_')


def get_missing_pages_indexes(book_id: ArchiveBookId, download_dir: Path) -> Dict[str, PageIndex]:
    book_file_id = get_book_file_id(book_id)

    expected_pages: Dict[str, PageIndex] = {}
    page_number: int = 1
    page_side: PageSide = PageSide.r
    book: ArchiveBookData = archive_books[book_id]
    for page_index in range(book.first_notes_page_inx, book.last_notes_page_inx + 1):
        page_id_prefix = {
            'AAdm 2': '',
            'AOff 129': 'AKMKR_'
        }.get(book_id, 'AKMKr_')

        page_id = None
        if book_id in ['AOff 113', 'AOff 158']:
            page_id = f"{page_id_prefix}{book_file_id}#{page_number:04d}"
        elif book_id == 'AEp 35' and page_index == 339:
            # NOTE: Brak '_' między numerem karty a oznaczeniem 'r'/'v'.
            page_id = f"{page_id_prefix}{book_file_id}#{page_number:04d}{page_side}"
        else:
            page_id = f"{page_id_prefix}{book_file_id}#{page_number:04d}_{page_side}"

        expected_pages[page_id] = page_index
        if book.current_page_numbering == PageNumeringType.Pagination or page_side == PageSide.v:
            page_number += 1
        page_side = PageSide.v if page_side == PageSide.r else PageSide.r

        if book_id == 'AAdm 9':
            if page_number == 35 and page_side == PageSide.r:
                # NOTE: CAAK has incorrect numbering of pages for this book, after f. 34v goes f. 35v.
                page_side = PageSide.v
            if page_index == 108:
                # NOTE: CAAK has incorrect numbering of pages for this book, f. 53r is scanned twice (#107 and #108).
                page_number, page_side = 53, PageSide.v
        if book_id == 'AAdm 13' and page_number == 11 and page_side == PageSide.v:
            # NOTE: CAAK has incorrect numbering of pages for this book, after f. 11r goes f. 12v.
            page_number = 12
        if book_id == 'AOff 110':
            # 3v (#11) -> 4v (#12) -> 4r (#13) -> 5r (#14)
            if page_index == 11:
                page_number, page_side = 4, PageSide.v
            if page_index == 12:
                page_number, page_side = 4, PageSide.r
            if page_index == 13:
                page_number, page_side = 5, PageSide.r

        if book_id == 'AOff 122':
            if page_index == 2:
                # NOTE: CAAK has incorrect numbering of pages for this book, after f. 1r goes f. Okl_1r.
                page_number, page_side = 1, PageSide.v
            if page_index == 6:
                # NOTE: CAAK has incorrect numbering of pages for this book, after f. 2r goes f. Target_2v.
                page_number, page_side = 2, PageSide.v
        if book_id == 'AOff 153':
            if page_index == 4:
                # NOTE: CAAK has incorrect numbering of pages for this book, f. 611r is scanned twice (#1226 and #1227).
                page_number, page_side = 2, PageSide.v
        if book_id == 'AOff 155':
            if page_index == 5:
                # NOTE: CAAK has incorrect numbering of pages for this book, f. 611r is scanned twice (#1226 and #1227).
                page_number, page_side = 2, PageSide.v
        if book_id == 'AOff 168':
            if page_index == 1227:
                # NOTE: CAAK has incorrect numbering of pages for this book, f. 611r is scanned twice (#1226 and #1227).
                page_number, page_side = 611, PageSide.v

    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        for filename in filenames:
            if (book_file_id not in filename) or not filename.endswith('.jpg'):
                continue
            page_id = filename.split('.')[0]
            try:
                expected_pages.pop(page_id)
            except KeyError as e:
                print(f"Key not found: {page_id}")
        break  # Do not visit directories recursively.

    return expected_pages


def build_caak_url(archival_entry: ArchiveBookData, page_no: int) -> str:
    return f"https://caak.upjp2.edu.pl/j/{archival_entry.url_id}/s/{page_no - 1}/f"


def restart_app():
    x_offset = -left_monitor_width_px if setup == 'work' else 0
    pyautogui.moveTo(restart_app_button_coords.x + x_offset, restart_app_button_coords.y)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(stop_and_rerun_app_button_coords.x + x_offset, stop_and_rerun_app_button_coords.y)
    pyautogui.click()


def get_pixel(x: int, y: int):
    while True:
        try:
            return pyautogui.pixel(x, y)
        except WindowsError as e:
            print(f"Error: {e}")
            print("Restarting the app...")
            restart_app()
        time.sleep(get_pixel_error_timeout)


def get_url_content() -> str:
    pyautogui.moveTo(address_bar_coords.x + x_offset, address_bar_coords.y)
    pyautogui.click(clicks=2)
    time.sleep(0.1)  # allow selection

    last_value = None

    while True:
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)  # allow clipboard to update

        clipboard_content = pyperclip.paste()

        if clipboard_content and clipboard_content != last_value:
            return clipboard_content

        last_value = clipboard_content
        time.sleep(url_clipboard_retry_interval_secs)
        print("Retrying URL copying...")


def abort_if_not_on_caak_webpage():
    if browser != 'chrome':
        print('Not implemented - missing coordinates')
        return

    # FIXME: Set proper coordinates also for Firefox.
    title_bar_background_color_sample_locations = [
        Point(x=190, y=220),
        Point(x=1000, y=300),
        Point(x=1700, y=250),
    ]

    for point in title_bar_background_color_sample_locations:
        sampled_color = get_pixel(point.x + x_offset, point.y)
        if sampled_color != AKMKColors.title_bar_background:
            print("Likely not on AKMK website.")
            exit(1)

    # FIXME: Set proper coordinates also for Firefox.
    preview_background_sample_locations = [
        Point(x=650, y=450),
        Point(x=1250, y=450),
        Point(x=650, y=900),
        Point(x=1250, y=900),
    ]

    for point in preview_background_sample_locations:
        sampled_color = get_pixel(point.x + x_offset, point.y)
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
            time.sleep(url_clipboard_retry_interval_secs)


def paste_url_from_clipboard():
    pyautogui.moveTo(address_bar_coords.x + x_offset, address_bar_coords.y)
    pyautogui.click(clicks=2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'v')


timeout_visit_webpage_initial_secs: float = 3.0
timeout_visit_webpage_decay_secs: float = 0.2
visit_webpage_times: List[float] = []


def visit_webpage(url: str):
    print(f"Visiting: {url}")

    last_n_readings = visit_webpage_times[-5:]
    past_average_timeout = sum(last_n_readings) / len(
        last_n_readings) if last_n_readings else timeout_visit_webpage_initial_secs
    print(f"Past average timeout: {past_average_timeout:.1f} sec.")

    retry_counter: int = 0
    while True:
        # NOTE: New way of inserting the address (needs to be refined).
        # pyautogui.moveTo(address_bar_coords.x + x_offset, address_bar_coords.y)
        # pyautogui.click(clicks=2)
        # pyautogui.hotkey('ctrl', 'a')
        # abort_if_not_on_caak_webpage()
        # put_url_to_clipboard(url)
        # paste_url_from_clipboard()

        # NOTE: Old way of inserting the address.
        pyautogui.moveTo(address_bar_coords.x + x_offset, address_bar_coords.y)
        pyautogui.click(clicks=3)
        # OLD version
        # pyautogui.click(clicks=2)
        # pyautogui.hotkey('ctrl', 'a')
        #
        # abort_if_not_on_caak_webpage()
        # pyautogui.press('del')
        # abort_if_not_on_caak_webpage()
        pyautogui.write(url, interval=0.025)

        timeout = (past_average_timeout - timeout_visit_webpage_decay_secs) + retry_counter
        time.sleep(timeout)  # NOTE: Needed to make sure that pyautogui.write() finished its job.

        url_content = get_url_content()
        if url_content == url:
            visit_webpage_times.append(timeout)
            break

        print(f"ULR: expected = {url}, actual = {url_content}")
        print(f"Retrying... (timeout was: {timeout:.1f} sec.)")
        retry_counter += 1

    pyautogui.press('enter')


def reload_webpage():
    print('Reloading...')
    pyautogui.hotkey('ctrl', 'f5')


def wait_until_loaded(is_narrow_page: bool):
    waiting_marker: str = '.'

    n_retries = 0
    download_start = datetime.datetime.now()
    print(f"Waiting for full preview ", end='')
    while True:
        print(waiting_marker, end='')
        time.sleep(timeout_download_subsequent_secs)

        now = datetime.datetime.now()
        if (now - download_start).seconds > max_waiting_time_secs:
            n_retries = 0
            reload_webpage()
            download_start = now
        # DEBUG: Take a screenshot.
        # from PIL import ImageGrab
        # image = ImageGrab.grab()
        # sampled_color = image.getpixel((sample_location.x + x_offset, sample_location.y))
        # image.save("screenshot.png")

        is_loaded: bool = True
        # NOTE: Sometimes the preview is loaded in top-to-bottom fashion, sometimes in bottom-to-top fashion.
        # FIXME: These coordinates are for Chrome in fullscreen mode.
        left: int = 830
        right: int = 1150
        top: int = 400
        bottom: int = 960
        narrow_page_offset: int = 50 if is_narrow_page else 0
        sample_locations = [
            Point(x=left + narrow_page_offset, y=top),
            Point(x=right - narrow_page_offset, y=top),
            Point(x=left + narrow_page_offset, y=bottom),
            Point(x=right - narrow_page_offset, y=bottom),
        ]
        for sample_location in sample_locations:
            sampled_color = get_pixel(sample_location.x + x_offset, sample_location.y)
            if sampled_color == AKMKColors.preview_background:
                is_loaded = False
                break
        if is_loaded:
            break
        n_retries += 1
    print()


def is_download_list_opened():
    download_list_background_color = download_list_background_color_repo[browser]
    sample_location = download_list_sample_location_repo[browser]
    sampled_color = get_pixel(sample_location.x + x_offset, sample_location.y)
    return sampled_color == download_list_background_color


def click_download():
    pyautogui.click(download_button_coords.x + x_offset, download_button_coords.y)


def move_downloaded_files(book_id: ArchiveBookId, repo_dir: Path):
    if not os.path.exists(repo_dir):
        try:
            os.makedirs(repo_dir)
        except OSError:
            print(f"Error while creating directory: {repo_dir}")
            exit(-1)

    book_file_id = get_book_file_id(book_id)
    for (dirpath, dirnames, filenames) in os.walk(download_dir):
        for filename in filenames:
            if f"{book_file_id}#" not in filename or not filename.endswith('.jpg'):
                continue
            try:
                # NOTE: Some files on CAAK server has incorrect suffixes (e.g. 'xxx 1.jpg' instead of 'xxx.jpg').
                # NOTE: Some files could be downloaded multiple times, hence Windows appends ' (N)' to the filename.
                new_filename = re.sub(r'(( \(\d\))|( 1))(?=\.jpg)', '', filename)

                if new_filename == 'AKMKr_AOff_124#0022_':
                    # NOTE: This file is incorrectly named on CAAK server.
                    new_filename = 'AKMKr_AOff_124#0022_r'

                shutil.move(download_dir / filename, repo_dir / new_filename)
            except Exception as e:
                print(f"Error while moving file {book_id}/{filename}: {e}")
        break  # Do not visit directories recursively.


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    num_downloaded_pages = 0

    for archive_signature in archive_books:
        book_file_id = get_book_file_id(archive_signature)
        repo_dir: Path = repo_root_dir / book_file_id
        move_downloaded_files(archive_signature, repo_dir)

    for archive_signature in queue:
        print(f"Processing archive: {archive_signature}")
        archival_entry = archive_books[archive_signature]

        book_file_id = get_book_file_id(archive_signature)
        repo_dir: Path = repo_root_dir / book_file_id

        # move_downloaded_files(archive_signature, repo_dir)
        expected_pages: Dict[str, PageIndex] = get_missing_pages_indexes(archive_signature, repo_dir)
        print(f"\tPage indexes to download: {sorted(expected_pages.values())}")

        indexes_inxs: Set[PageIndex] = set()
        for entry in archival_entry.indexes:
            indexes_inxs.update(range(entry.start_inx, entry.end_inx + 1))

        sdm_imgs_urls: List[str] = []
        if archival_entry.archive_id == ArchiveId.SDM and expected_pages:
            sdm_imgs_urls = get_sdm_imgs_urls(archival_entry.url_id)

        for page_id, page_inx in expected_pages.items():
            if indexes_only and (page_inx not in indexes_inxs):
                continue

            if page_inx % screening_interval != 0:
                continue

            if page_inx in archival_entry.broken_file_indexes:
                print(f"Skipping broken file: #{page_inx}.")
                continue

            # FIXME: DEBUG
            # if archive_signature == 'AEp 31' and page_inx > 130:
            #     continue

            page_type: str = 'p.' if archival_entry.current_page_numbering == PageNumeringType.Pagination else 'f.'
            page_id_human = page_id.split('#')[-1].lstrip('0').replace('_', '')
            print(
                f"Processing: {archive_signature} "
                f"{page_type} {page_id_human} (# "
                f"{page_inx})...")

            start_processing_page_time = datetime.datetime.now()

            if archival_entry.archive_id == ArchiveId.SDM:
                # FIXME: page_inx vs. page_no - wyjaśnić niespójność między SDM a CAAK (bo dla wpisów SDM w
                #  archives.py podawane są *numery* stron, a nie *indeksy* stron.
                sdm_url = sdm_imgs_urls[page_inx - 1]

                with open(Path(repo_dir) / f"{page_id}.jpg", 'wb') as handle:
                    response = requests.get(sdm_url, stream=True)

                    if not response.ok:
                        print(response)

                    for block in response.iter_content(chunk_size=1024):
                        if not block:
                            break

                        handle.write(block)
            elif archival_entry.archive_id == ArchiveId.CAAK:
                page_no = page_inx + 1
                caak_url = build_caak_url(archival_entry, page_no)

                visit_webpage(caak_url)

                time.sleep(visiting_webpage_timeout)
                wait_until_loaded(archival_entry.has_narrow_pages)

                now = datetime.datetime.now()
                elapsed_time = now - start_processing_page_time
                if elapsed_time.seconds < timeout_download_button_click_secs:
                    waiting_time = timeout_download_button_click_secs - int(elapsed_time.seconds)
                    print(f"Waiting {waiting_time} secs more before clicking 'Download' button.")
                    time.sleep(waiting_time)

                # NONTE: In case of the list of downloaded file being visible, click in "safe area" to close it.
                safe_point = safe_point_location_repo[browser]
                pyautogui.click(safe_point.x + x_offset, safe_point.y)

                time.sleep(safe_point_click_timeout)
                click_download()
            else:
                raise NotImplementedError(f'Archive not supported: {archival_entry.archive_id}')

            num_downloaded_pages += 1

            now = datetime.datetime.now()
            total_time = (now - start_time).seconds
            print(f"Downloaded at: {now} \t (avg. speed: {total_time / num_downloaded_pages:.1f} sec./page)")

            elapsed_time = now - start_processing_page_time
            download_interval_secs = download_interval_secs_repo[archival_entry.archive_id]
            if elapsed_time.seconds < download_interval_secs:
                waiting_time = download_interval_secs - int(elapsed_time.seconds)
                print(f"Waiting {waiting_time} secs more before downloading the next page...")
                time.sleep(waiting_time)

            time.sleep(download_safeguard_interval_secs)

            if archival_entry.archive_id == ArchiveId.CAAK and num_downloaded_pages % num_downloads_before_reload == 0:
                print("Preventive reload...")
                reload_webpage()

    print("------------------------")
    print("All downloads completed.")
