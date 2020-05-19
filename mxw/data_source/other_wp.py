from mxw.utils.common_import import *
import json
from datetime import date, datetime
import requests

from mxw.data_utils import *
from vnpy.trader.constant import Exchange
from mxw.db.DbModule import DbOpenInterestHolding


def get_open_interest_data_by_symbol_date(ins: Instrument, _date: date):
    _date_str = _date.strftime('%Y%m%d')
    symbol = exact_exchange_symbol(ins)
    # print(f'17kqh获取龙虎榜信息, date={_date_str}, symbol = {ins.symbol}')

    url_path = f'http://cc.17kqh.com/holding/{symbol}/{_date_str}/'

    def check_date_available():
        before_day = _date - timedelta(days=1)
        before_day_str = before_day.strftime('%Y%m%d')
        check_url = f'http://cc.17kqh.com/datemenu/{symbol}/{before_day_str}/'
        _raw_html = requests.get(check_url).text
        check_dict = json.loads(_raw_html)
        if check_dict.get('n', None) == _date_str:
            return True
        return False

    if not check_date_available():
        print(f'17kqh 没有当前日期数据，跳过, date={_date_str}, symbol = {ins.symbol}', file=sys.stderr)
        return []

    print(f'17kqh----获取龙虎榜信息, date={_date_str}, symbol = {ins.symbol}')
    raw_html = requests.get(url_path).text
    m_time.sleep(0.01)

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
        if len(_dict) < 20 and len(_dict) != 0:
            # raise Exception('持仓龙虎榜数据获取异常，数据量小于20')
            # dingtalk_utils.send_message(f'龙虎榜数据获取异常,只有 {len(_dict)} 条数据 symbol={ins.symbol},date={_date}, type={type_str}')
            print(f'龙虎榜数据获取异常,只有 {len(_dict)} 条数据 symbol={ins.symbol},date={_date}, type={type_str}', file=sys.stderr)
        count = 0
        for item in _dict:
            count += 1
            if item['now'] == 0 and count > 20:
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
    get_open_interest_data_by_symbol_date(Instrument('JD2006', exchange=Exchange.DCE), date(2019, 5, 15))
    get_open_interest_data_by_symbol_date(Instrument('CF2009', exchange=Exchange.CZCE), date(2020, 5, 18))
    pass
