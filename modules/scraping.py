import re
import requests
import time
import database as db

from bs4 import BeautifulSoup
from loguru import logger
from modules.config import parse_config


def should_url_be_stored(url_path: str) -> bool:
    """Start of month should not be stored

    Args:
        url_path (str): the path from the url which contains the date

    Returns:
        bool: if the path only contains year/month

    """
    return re.search(r"[\d]{4}\/[\d]{2}$", url_path) is None


def parse_page_contents(content: BeautifulSoup, links: list) -> None:
    """Given the page content, extracts certain links and appends it to the given list

    Args:
        content (BeautifulSoup): page content parsed by BeautifulSoup
        links ([str]): List of links to be crawled

    Returns:
        None

    """
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


def collect_page_links(links: list) -> None:
    """Process one entry from the given links list and extract other links from those
    web pages. Those new gotten links will be appended to the same list.

    Args:
        links ([str]): The links of the pages to be scraped

    Returns:
        None
    """
    page_path = links.pop(0)

    logger.debug(f'Processing link: {page_path}')
    if parse_config().tracking_enabled and db.has_been_crawled(page_path):
        logger.debug('Already crawled - Skipping')
        return

    full_url = f'{parse_config().search_url}{page_path}'
    logger.debug(f'Crawling {full_url}')

    page = requests.get(full_url)
    content = BeautifulSoup(page.text, 'html.parser')
    got_error = content.find("div", {"id": "error"})

    if got_error:
        logger.error(f'Error: {got_error.text}')
        return

    parse_page_contents(content, links)

    if parse_config().tracking_enabled and should_url_be_stored(page_path):
        db.save_has_been_crawled(page_path)

    time.sleep(parse_config().throttle_secs)


def execute_crawling_process(links: list):
    """Wrapper for the whole scrapping process

    Args:
        links ([str]): List of links to be crawled

    Returns:
        None
    """
    logger.info('- CRAWLING PROCESS -')
    while links:
        collect_page_links(links)
    logger.info('- CRAWLING FINISHED -')
