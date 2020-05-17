import json
from datetime import date, datetime
import requests

from mxw.data_utils import *
from vnpy.trader.constant import Exchange
from mxw.db.DbModule import DbOpenInterestHolding


def get_open_interest_data_by_symbol_date(ins: Instrument, _date: date):
    _date_str = _date.strftime('%Y%m%d')
    symbol = exact_exchange_symbol(ins)
    url_path = f'http://cc.17kqh.com/holding/{symbol}/{_date_str}/'
    raw_html = requests.get(url_path).text

    buy_sep = 'var dataBuy = '
    sell_sep = 'var dataSale = '
    vol_sep = 'var dataCj = '

    def _process_17kqh_str(sym: str):
        _start = raw_html.find(sym)
        _end = raw_html.find(']', _start)
        _str = raw_html[_start + len(sym):_end + 1]
        return json.loads(_str.replace('\'', '"'))

    _model_list = []

    def _store_data_by_type(type_str: str, type_int: int):
        _dict = _process_17kqh_str(type_str)
        if len(_dict) < 20:
            raise Exception('持仓龙虎榜数据获取异常，数据量小于20')
        count = 0
        for item in _dict:
            count += 1
            if item['now'] == 0:
                continue
            _model = DbOpenInterestHolding()
            _model.order_book_id = ins.symbol
            _model.date_time = _date
            _model.broker = item['category']
            _model.data_type = type_int
            _model.volume = item['now']
            _model.volume_change = item['chg']
            _model.rank = count
            _model.create_time = datetime.now()

            _model_list.append(_model)

    _store_data_by_type(vol_sep, 0)
    _store_data_by_type(buy_sep, 1)
    _store_data_by_type(sell_sep, 2)
    return _model_list


if __name__ == '__main__':
    get_open_interest_data_by_symbol_date(Instrument('JD2006', exchange=Exchange.DCE), date(2020, 5, 15))
    get_open_interest_data_by_symbol_date(Instrument('CF2009', exchange=Exchange.CZCE), date(2020, 5, 15))
    pass
