import glob

from finders import get_lotteries_count, get_losers
from validators import is_quiniela_multiple_format
from structures import quiniela_multiple_data_matrix
from dtos import LotteryResults
from database import setup_db, has_been_processed, save_has_been_processed, save_lottery_results
import fitz


def extract_results(positions, blocks):
    return LotteryResults(
        date=blocks[positions.date].strip(),
        lottery_number=blocks[positions.lottery_number].strip(),
        district=blocks[positions.district].strip().upper(),
        shift=blocks[positions.shift].strip(),
        numbers=extract_lottery_numbers(positions.numbers, blocks),
        losers=get_losers(blocks, blocks[positions.shift].strip())
    )


def extract_lottery_numbers(blocks_range, blocks):
    numbers = [premio.strip().split('\n', 1)[1] for premio in blocks[blocks_range]]
    return dict(enumerate((number for number in numbers), 1))


def print_results(result):
    print("Fecha:", result.date)
    print("Sorteo Número:", result.lottery_number)
    print("Distrito", result.district, '- Turno:', result.shift)
    print('Numeros:', result.numbers)
    # for place, number in result.numbers:
    #     print(place, '=>', number)
    print('No Ganadoras:', result.losers)
    print('---------------------------------------')


def parse_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    page = doc[0]

    blocks = list(block[4] for block in page.get_text('blocks'))
    # for i, p in enumerate(blocks): print(i, ' => ', p.strip())

    if not is_quiniela_multiple_format(blocks):
        save_has_been_processed(pdf_path, 'not supported')
        print('------------------------------------')
        print('  Formato de extracto no soportado  ')
        print('------------------------------------')
        return

    lotteries_count = get_lotteries_count(page)

    print('Cantidad de sorteos:', lotteries_count)
    for lottery in range(lotteries_count):
        results = extract_results(quiniela_multiple_data_matrix[lottery], blocks)
        save_lottery_results(results)
        save_has_been_processed(pdf_path, 'ok')
        print_results(results)


# ----------------------------------------------------------
#  === PROGRAM STARTS HERE ================================
# ----------------------------------------------------------

setup_db()
files = glob.glob('downloads/**/*.pdf', recursive=True)
for pdf in files:
    print(f'PATH: {pdf}')
    if not has_been_processed(pdf):
        parse_pdf(pdf)
