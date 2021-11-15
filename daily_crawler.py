import os
import sys
import time
import requests
import re
import database as db
from dotenv import dotenv_values
from concurrent import futures
from bs4 import BeautifulSoup
from loguru import logger

config = dotenv_values('.env')
files_url = config['FILES_URL']
search_url = config['SEARCH_URL']
enable_tracking = True if config['TRACK_PROCESSED'].lower() == 'true' else False
throttle_secs = 1


def get_date_arg() -> str:
    """Get first invocation argument and validate it's the right date format

    Returns:
        str: The date string provided as argv[1]
    """
    args = sys.argv[1:]
    if not args:
        exit('La fecha es requerida como primer argumento')

    if re.search(r"[\d]{4}\/[\d]{2}\/[\d]{2}$", args[0]) is None:
        exit('Formato de fecha inválida. Debe ser AAAA/MM/DD')

    return args[0]


def get_download_file_path(file_uri: str) -> str:
    """Given a URI link, return the file and its local full path where to be saved

    Args:
        file_uri: the URI link

    Returns:
        str: the path to downloads dir + local unique file name
    """
    local_name = file_uri.replace(files_url, '')
    download_dir = 'downloads'
    full_path = download_dir + '/' + local_name
    save_dir = '/'.join(full_path.split('/')[:-1])

    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    return full_path


def download_file(file_uri: str) -> str:
    """Given a URI link, download the file and return its local full path

    Returns:
        str: The path and file name
    """
    downloaded_path = get_download_file_path(file_uri)
    try:
        file = requests.get(file_uri)
        file.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Inaccessible resource: " + file_uri)
        return

    open(downloaded_path, 'wb').write(file.content)

    time.sleep(1)
    return downloaded_path


def should_url_be_stored(url_path: str) -> bool:
    """Start of month should not be stored

    Args:
        url_path (str): the path from the url which contains the date

    Returns:
        bool: if the path only contains year/month

    """
    return re.search(r"[\d]{4}\/[\d]{2}$", url_path) is None


def collect_page_links() -> None:
    page_path = links.pop(0)

    logger.debug('Processing link: ' + page_path)
    if enable_tracking and db.has_been_crawled(page_path):
        logger.debug(' Already crawled - Skipping')
        return

    logger.debug('Crawling ' + search_url + page_path)
    page = requests.get(search_url + page_path)
    content = BeautifulSoup(page.text, 'html.parser')
    got_error = content.find("div", {"id": "error"})
    if got_error:
        logger.error(f'Error: {got_error.text}')
        return

    for a_tag in content.findAll("a"):
        href = a_tag.attrs.get("href")

        if href == "" or href is None:
            continue
        elif "&sort_by" in href or "Thumbs.db" in href:
            continue
        elif href[-4:] == ".pdf":
            if not db.is_to_be_downloaded(href):
                logger.debug('Adding to pdfs: ' + href)
                db.save_to_be_downloaded(href)
            else:
                logger.debug('Already queued for download: ' + href)
        else:
            logger.debug('Adding to links: ' + href)
            links.append(href)

    if enable_tracking and should_url_be_stored(page_path):
        db.save_has_been_crawled(page_path)

    time.sleep(throttle_secs)


def download(pdf):
    logger.debug('Processing PDF: ' + pdf)
    if not enable_tracking and db.has_been_downloaded(pdf):
        print(' Already downloaded - Skipping')
        return

    path = download_file(files_url + pdf)
    return path


def execute_crawling():
    logger.info('- CRAWLING PROCESS -')
    while links:
        collect_page_links()
    logger.info('- CRAWLING FINISHED -')


def execute_downloads():
    logger.info('- DOWNLOAD PDFS PROCESS -')

    pending = db.get_files_to_be_downloaded()
    if not pending:
        logger.error('Nothing to download - Exiting')
        return

    with futures.ThreadPoolExecutor() as threads:
        # it's a tuple, pull first member
        pdfs = [pdf[0] for pdf in pending]
        downloaded_files = threads.map(download, pdfs)

        for downloaded_file in downloaded_files:
            db.save_has_been_downloaded(downloaded_file)
            logger.debug(f'File stored in: {downloaded_file}')


# ----------------------------------------------------------
#  === PROGRAM STARTS HERE ================================
# ----------------------------------------------------------

links = [f"?dir={get_date_arg()}"]
db.setup_db()
start = time.perf_counter()
execute_crawling()
execute_downloads()
logger.info(f'FINISHED: Took {round(time.perf_counter() - start, 2)} secs.')
