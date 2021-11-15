import sys
import time
import re
import database as db
from loguru import logger

from modules.config import parse_config
import modules.scraping as scraping
import modules.downloading as downloading


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


# ----------------------------------------------------------
#  === PROGRAM STARTS HERE ================================
# ----------------------------------------------------------

links = [f'{parse_config().date_query_param}{get_date_arg()}']
db.setup_db()
start = time.perf_counter()
scraping.execute_crawling_process(links)
downloading.execute_download_process()
logger.info(f'FINALIZADO: Tiempo {round(time.perf_counter() - start, 2)} segs.')
