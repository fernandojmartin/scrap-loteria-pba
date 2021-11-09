from dataclasses import dataclass


@dataclass
class DataPositions:
    date: int
    lottery_number: int
    district: int
    shift: int
    numbers: slice


@dataclass
class LotteryResults:
    date: str
    lottery_number: str
    district: str
    shift: str
    numbers: list
    losers: str = -1
