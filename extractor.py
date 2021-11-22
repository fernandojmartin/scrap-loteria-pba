import glob
import fitz

from finders import get_lotteries_count, get_losers
from validators import is_quiniela_multiple_format
from structures import quiniela_multiple_data_matrix
from dtos import LotteryResults, DataPositions
from database import setup_db, has_been_processed, save_has_been_processed, save_lottery_results
from loguru import logger
from modules.config import load_config


def collect_results(positions: DataPositions, blocks: list) -> LotteryResults:
    """Extrae partes del PDF basado en la matris de posiciones provista

    Args:
        positions (DataPositions): Matriz con las posiciones de cada elemento a extraer
        blocks (list): Los bloques de texto encontrados en el PDF

    Returns:
        LotteryResults
    """
    return LotteryResults(
        date=blocks[positions.date].strip(),
        lottery_number=blocks[positions.lottery_number].strip(),
        district=blocks[positions.district].strip().upper(),
        shift=blocks[positions.shift].strip(),
        numbers=extract_lottery_numbers(positions.numbers, blocks),
        losers=get_losers(blocks, blocks[positions.shift].strip())
    )


def extract_lottery_numbers(blocks_range: range, blocks: list) -> dict:
    """Extrae los números ganadores del sorteo basado en el rango de posiciones

    Args:
        blocks_range (range): Rango de posiciones a tomar de la lista
        blocks (list): Los elementos encontrados en el PDF

    Returns:
        dict{puesto: número}
    """
    numbers = [premio.strip().split('\n', 1)[1] for premio in blocks[blocks_range]]
    return dict(enumerate((number for number in numbers), 1))


def print_results(result: LotteryResults) -> None:
    """Imprime a salida estandard los resultados obtenidos

    Args:
        result (LotteryResults): El objeto con los resultados obtenidos

    Returns:
        None
    """
    print('---------------------------------------')
    print(" Fecha:", result.date)
    print(" Sorteo Número:", result.lottery_number)
    print(" Distrito", result.district, '- Turno:', result.shift)
    print(' Números:', result.numbers)
    print(' No Ganadoras:', result.losers)
    print('---------------------------------------')


def report_results(result: LotteryResults) -> None:
    """Serializar los datos extraídos y bajarlo al log

    Args:
        result (LotteryResults): Los datos extraídos para un determinado sorteo

    Returns:
        None
    """
    logger.info(repr([
        ("Fecha", result.date),
        ("Sorteo Número", result.lottery_number),
        ("Distrito", result.district),
        ('Turno', result.shift),
        ('Números', result.numbers),
        ('No Ganadoras', result.losers),
    ]))


def parse_pdf(pdf_path: str) -> None:
    """Procesar y extraer resultados del PDF de resumen

    Args:
        pdf_path: La ruta al archivo físico

    Returns:
        None
    """
    doc = fitz.open(pdf_path)
    page = doc[0]

    blocks = list(block[4] for block in page.get_text('blocks'))
    # for i, p in enumerate(blocks): print(i, ' => ', p.strip())

    if not is_quiniela_multiple_format(blocks):
        if is_tracking_enabled:
            save_has_been_processed(pdf_path, result='not supported')

        logger.error('Formato de extracto no soportado')
        return

    lotteries_count = get_lotteries_count(page)

    logger.info(f'Cantidad de sorteos: {lotteries_count}')

    for lottery in range(lotteries_count):
        results = collect_results(quiniela_multiple_data_matrix[lottery], blocks)
        if is_tracking_enabled:
            save_lottery_results(results)
            save_has_been_processed(pdf_path, 'ok')
        report_results(results)


# ----------------------------------------------------------
#  === PROGRAM STARTS HERE ================================
# ----------------------------------------------------------
is_tracking_enabled = load_config().tracking_enabled

if is_tracking_enabled:
    setup_db()

files = glob.glob('downloads/**/*.pdf', recursive=True)

if not files:
    logger.info('No hay archivos para procesar')

for pdf in files:
    logger.debug(f'Procesando: {pdf}')
    if not is_tracking_enabled or is_tracking_enabled and not has_been_processed(pdf):
        parse_pdf(pdf)

logger.info('Proceso finalizado')
