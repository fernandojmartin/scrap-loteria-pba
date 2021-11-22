import os
import requests
import time
import database as db

from loguru import logger
from concurrent import futures
from modules.config import load_config


def get_download_file_path(file_uri: str) -> str:
    """Given a URI link, parse the file name, make the directory
    where to be saved and return the full path.

    Args:
        file_uri: the URI link

    Returns:
        str: the path to downloads dir + local unique file name
    """
    local_name = file_uri.replace(load_config().files_url, '')
    download_dir = load_config().downloads_dir
    full_path = f'{download_dir}/{local_name}'
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
        message = f'Inaccessible resource: {file_uri}'
        logger.error(message)

        return message

    open(downloaded_path, 'wb').write(file.content)

    time.sleep(1)
    return downloaded_path


def download(file: str) -> str:
    """Invoke the download action of the given file

    Args:
        file (str): the url of the file to be downloaded or info message

    Returns:
        (str) The path of the downloaded file or info message
    """
    if not load_config().tracking_enabled and db.has_been_downloaded(file):
        message = 'Already downloaded - Skipping'
        logger.debug(message)

        return message

    path = download_file(f'{load_config().files_url}{file}')
    return path


def execute_download_process() -> None:
    """Wrapper for the whole download process.

    Returns:
        None
    """
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
