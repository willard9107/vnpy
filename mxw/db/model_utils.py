from datetime import date
from functools import lru_cache
from typing import Optional

from mxw.db.DbModule import DbInstrument
from mxw.db.PyModule import Instrument


# def get_instrument_info_by_order_book_id(order_book_id: str):
#     return get_instrument_info_from_db(order_book_id)


@lru_cache(maxsize=99999)
def get_instrument_info_from_db(order_book_id: str) -> Optional[Instrument]:
    result = DbInstrument.select().where(DbInstrument.order_book_id == order_book_id).execute()
    for item in result:
        return item.to_instrument()
    return None


def get_all_instrument_by_trading_date(_date: date):
    _result = DbInstrument.select().where(
        (DbInstrument.listed_date <= _date) & (DbInstrument.de_listed_date >= _date)).execute()

    ins_list = []
    for item in _result:
        ins_list.append(item.to_instrument())
    return ins_list


if __name__ == '__main__':
    print(get_instrument_info_from_db('M2005'))
    pass
