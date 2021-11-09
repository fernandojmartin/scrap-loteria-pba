def get_lotteries_count(page):
    return len(
        list(
            filter(
                lambda word: '1º Premio' in word[4],
                page.get_text('blocks')
            )
        )
    )


def get_losers(blocks, shift):
    block = list(filter(lambda b: 'apuestas NO GANADORAS' in b, blocks))[0]
    block = block.lower().strip()
    shift = (shift.strip().lower()) + ':'
    no_winners_shift_start = block.find(shift) + len(shift) + 1
    no_winners_shift_end = block.find(' ', no_winners_shift_start)
    loser = block[no_winners_shift_start:no_winners_shift_end].strip()

    return loser
