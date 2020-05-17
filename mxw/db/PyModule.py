from dataclasses import dataclass
from datetime import date, datetime

from vnpy.trader.constant import Exchange, Interval


# @dataclass
# class Instrument:
#     symbol: str
#     common_symbol: str
#     cn_symbol: str
#     listed_date: date
#     de_listed_date: date
#     exchange: Exchange

@dataclass
class TradingDate:
    date: date
    is_open: int


@dataclass
class Instrument:
    symbol: str
    common_symbol: str
    cn_symbol: str
    listed_date: date
    de_listed_date: date
    maturity_date: date
    exchange: Exchange
    margin_rate: float
    contract_multiplier: float
    trading_hours: str


@dataclass
class OpenInterestHolding:
    symbol: str
    date_time: date

    listed_date: date
    de_listed_date: date
    maturity_date: date
    exchange: Exchange
    margin_rate: float
    contract_multiplier: float
    trading_hours: str


@dataclass
class DailyBarData:
    symbol: str
    exchange: Exchange
    datetime: datetime

    interval: Interval = None
    volume: float = 0
    open_interest: float = 0
    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0
    settle_price: float = 0

    def __post_init__(self):
        """"""
        self.vt_symbol = f"{self.symbol}.{self.exchange.value}"
