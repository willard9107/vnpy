import time as _time
from datetime import date, datetime

from pandas import DataFrame

import tushare as ts

from mxw.utils import m_constants
from mxw.db.PyModule import TradingDate, DailyBarData
from vnpy.trader.constant import Exchange, Interval
from mxw.data_utils import *

pro = ts.pro_api('4c0f90a3e376dead9ef82f55d86c9c41d6c1ab68b72312ebb9a1be99')


# df = pro.fut_basic(exchange='DCE', fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
# df = pro.fut_holding(trade_date='20200416', symbol='JD2005', exchange='DCE')

# df = pro.ft_tick(symbol='JD2005')


def get_futures_trading_date(start_date: str, end_date: str):
    _df = pro.trade_cal(exchange='DCE', start_date=start_date, end_date=end_date)
    result = []
    for index, row in _df.iterrows():
        a = TradingDate(row['cal_date'], row['is_open'])
        result.append(a)
    return result


def get_future_instruments(exchange: str):
    df: DataFrame = pro.fut_basic(exchange=exchange, fut_type='1')
    df = df.sort_values('list_date')

    result = []
    for index, row in df.iterrows():
        order_book_id = row['ts_code'].split('.')[0]
        list_date = datetime.strptime(row['list_date'], '%Y%m%d').date()
        dlist_date = datetime.strptime(row['delist_date'], '%Y%m%d').date()
        ins = Instrument(order_book_id, row['fut_code'], row['name'], list_date, dlist_date, dlist_date,
                         Exchange(exchange), 0.1, 10, '')
        result.append(ins)
    return result


def get_daily_bar_of_cn_future_exchange(_date: date):
    _datetime = datetime.combine(_date, datetime.min.time())
    _date_str = _date.strftime('%Y%m%d')

    result = []

    for e in m_constants.CHINESE_FUTURE_EXCHANGES_STR:
        # for e in [exchange]:
        _df: DataFrame = pro.fut_daily(trade_date=_date_str, exchange=e)
        _time.sleep(0.5)
        # print(_df.to_string())
        print(f'"{e}" date:{_date}:  日线数据量   {_df.shape[0]}条')
        for index, row in _df.iterrows():
            order_book_id = row['ts_code'].split('.')[0]
            if get_order_id_year(order_book_id) is None:
                continue
            # exchange = row['ts_code'].split('.')[1]
            volume = filter_nan_field(row['vol'], 0)
            oi = filter_nan_field(row['oi'], 0)
            _open = filter_nan_field(row['open'], 0)
            high = filter_nan_field(row['high'], 0)
            low = filter_nan_field(row['low'], 0)
            close = filter_nan_field(row['close'], 0)
            settle = filter_nan_field(row['settle'], 0)

            day_bar = DailyBarData(order_book_id, Exchange(e), _datetime, Interval.DAILY, volume,
                                   oi, _open, high, low, close, settle)
            result.append(day_bar)
    return result


if __name__ == '__main__':
    # print(get_futures_trading_date('20201201', '20210530'))

    # df: DataFrame = pro.fut_basic(exchange='CZCE', fut_type='1')
    # df = df.sort_values('list_date')
    # print(df.to_string())
    _r = get_daily_bar_of_cn_future_exchange(date(2010, 5, 13))
    print(_r)

    pass
