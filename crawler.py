import os
import requests
from bs4 import BeautifulSoup
import time
import database as db
import re

files_url = "http://www.loteria.gba.gov.ar/extractosOficiales/"
search_url = "http://www.loteria.gba.gov.ar/extractosOficiales/ver_extractos.php"
throttle_secs = 1


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
        os.makedirs(save_dir)

    return full_path


def download_file(file_uri) -> str:
    """Given a URI link, download the file and return its local full path

    Returns:
        str: The path and file name
    """
    downloaded_path = get_download_file_path(file_uri)
    try:
        file = requests.get(file_uri)
        file.raise_for_status()
    except requests.exceptions.RequestException as e:
        exit("Inaccessible resource: " + file_uri)

    open(downloaded_path, 'wb').write(file.content)

    time.sleep(1)
    return downloaded_path


def should_url_be_stored(url) -> bool:
    """Only start of month should not be stored"""
    return re.search(r"[\d]{4}\/[\d]{2}$", url) is None


def collect_page_links() -> None:
    page_path = links.pop(0)

    print('Processing link: '+page_path)
    if db.has_been_crawled(page_path):
        print(' Already crawled - Skipping')
        return

    print('Crawling '+search_url+page_path)
    page = requests.get(search_url+page_path)
    content = BeautifulSoup(page.text, 'html.parser')

    for a_tag in content.findAll("a"):
        href = a_tag.attrs.get("href")

        if href == "" or href is None:
            continue
        elif "&sort_by" in href or "Thumbs.db" in href:
            continue
        elif href[-4:] == ".pdf":
            if not db.is_to_be_downloaded(href):
                print('Adding to pdfs: '+href)
                db.save_to_be_downloaded(href)
            else:
                print('Already queued for download: ' + href)
        else:
            print('Adding to links: '+href)
            links.append(href)

    if should_url_be_stored(page_path):
        db.save_has_been_crawled(page_path)

    time.sleep(throttle_secs)


links = ["?dir=2017/02"]

# ----------------------------------------------------------
#  === PROGRAM STARTS HERE ================================
# ----------------------------------------------------------
db.setup_db()

print('- CRAWLING PROCESS -')
while links:
    collect_page_links()


print('- DOWNLOAD PDFS PROCESS -')
pending = db.get_files_to_be_downloaded()
if not pending:
    print('Nothing to download - Exiting')
    exit()

for pdf in pending:
    pdf = pdf[0]  # it's a tuple, pull first member
    print('Processing PDF: '+pdf)
    if db.save_has_been_downloaded(pdf):
        print(' Already downloaded - Skipping')
        continue

    path = download_file(files_url+pdf)
    db.save_has_been_downloaded(pdf)
    print('File stored in: ' + path)


