from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class TradingDate:
    date: date
    is_open: int


@dataclass
class Instrument:
    order_book_id: str
    order_book_symbol: str
    symbol: str
    listed_date: date
    de_listed_date: date
    maturity_date: date
    exchange: str
    margin_rate: str
    contract_multiplier: int
    trading_hours: str
