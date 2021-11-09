from finders import get_lotteries_count, get_losers
from validators import is_quiniela_multiple_format
from structures import quiniela_multiple_data_matrix
from dtos import LotteryResults
import fitz

doc = fitz.open('QuinielaMatutina.pdf')
page = doc[0]

blocks = list(block[4] for block in page.get_text('blocks'))
# for i, p in enumerate(blocks): print(i, ' => ', p.strip())

if not is_quiniela_multiple_format(blocks):
    exit('Formato de extracto no soportado.')

lotteries_count = get_lotteries_count(page)


def extract_results(positions):
    return LotteryResults(
        date=blocks[positions.date].strip(),
        lottery_number=blocks[positions.lottery_number].strip(),
        district=blocks[positions.district].strip().upper(),
        shift=blocks[positions.shift].strip(),
        numbers=extract_lottery_numbers(positions.numbers),
        losers=get_losers(blocks, blocks[positions.shift].strip())
    )


def extract_lottery_numbers(blocks_range):
    numbers = [premio.strip().split('\n', 1)[1] for premio in blocks[blocks_range]]
    return list(enumerate((number for number in numbers), 1))


def print_results(result):
    print("Fecha:", result.date)
    print("Sorteo Número:", result.lottery_number)
    print("Distrito", result.district, '- Turno:', result.shift)
    print('Numeros:', result.numbers)
    # for place, number in result.numbers:
    #     print(place, '=>', number)
    print('No Ganadoras:', result.losers)
    print('---------------------------------------')


print('Cantidad de sorteos:', lotteries_count)
for lottery in range(lotteries_count):
    print_results(extract_results(quiniela_multiple_data_matrix[lottery]))
