from dataclasses import asdict
from datetime import date, datetime

from pandas import DataFrame

import tushare as ts

from mxw.obj import TradingDate, Instrument

pro = ts.pro_api('4c0f90a3e376dead9ef82f55d86c9c41d6c1ab68b72312ebb9a1be99')


# df = pro.fut_basic(exchange='DCE', fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
# df = pro.fut_holding(trade_date='20200416', symbol='JD2005', exchange='DCE')

# df = pro.ft_tick(symbol='JD2005')


def get_futures_trading_date(start_date: str, end_date: str):
    df = pro.trade_cal(exchange='DCE', start_date=start_date, end_date=end_date)
    result = []
    for index, row in df.iterrows():
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
        ins = Instrument(order_book_id, row['fut_code'], row['name'], list_date, dlist_date, dlist_date, exchange,
                         '0.1', 10, '')
        result.append(ins)
    return result


if __name__ == '__main__':
    # print(get_futures_trading_date('20201201', '20210530'))

    df: DataFrame = pro.fut_basic(exchange='CZCE', fut_type='1')
    df = df.sort_values('list_date')
    print(df.to_string())
    pass
