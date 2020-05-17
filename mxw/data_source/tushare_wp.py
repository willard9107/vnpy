import sys
import time as _time
from datetime import date, datetime

from pandas import DataFrame

import tushare as ts

from mxw.db.DbModule import DbOpenInterestHolding
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
        _time.sleep(0.5)  # tushare限定此接口一分钟只可访问120次，当前配置120次
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


def get_oi_holding_rank(ins: Instrument, _date: date):
    _date_str = _date.strftime('%Y%m%d')

    print(f'tushare获取龙虎榜信息, date={_date_str}, symbol = {ins.symbol}')
    _df: DataFrame = pro.fut_holding(trade_date=_date_str, symbol=ins.symbol,
                                     exchange=ins.exchange.value)
    _time.sleep(0.75)  # tushare限定此接口一分钟只可访问80次，当前配置80次
    _model_list = []
    if len(_df) == 0:
        return []

    def _process_df_data(vol: str, chg: str, _type: int):
        _df1 = _df.sort_values(by=vol, ascending=False)
        # print(_df1.to_string())
        _range = range(20)
        rank_offset = 0
        if _df1.iloc[0].at['broker'] == '期货公司会员':
            _range = range(1, 21)
            rank_offset = -1
        for i in _range:
            if len(_df1) <= i:
                print(f'龙虎榜数据获取异常,只有 {i + rank_offset} 条数据 symbol={ins.symbol},date={_date}, type={vol}',
                      file=sys.stderr)
                break
            df_loc = _df1.iloc[i]
            _model = DbOpenInterestHolding()
            _model.order_book_id = ins.symbol
            _model.date_time = _date
            _model.broker = df_loc.at['broker']
            _model.data_type = _type
            _model.volume = df_loc.at[vol]
            _model.volume_change = df_loc.at[chg]
            _model.rank = i + rank_offset + 1
            _model.create_time = datetime.now()

            if _model.volume is None or _model.volume_change is None \
                    or math.isnan(_model.volume) or math.isnan(_model.volume_change):
                # print(_df.to_string())
                # print(_df1.to_string())
                print(f'龙虎榜数据获取异常,只有 {i + rank_offset} 条数据 symbol={ins.symbol},date={_date}, type={vol}',
                      file=sys.stderr)
                # raise Exception(f'龙虎榜数据获取错误, symbol={ins.symbol},date={_date}, type={vol}, data={_df1.to_string()}')
                break
            _model_list.append(_model)

    _process_df_data('vol', 'vol_chg', 0)
    _process_df_data('long_hld', 'long_chg', 1)
    _process_df_data('short_hld', 'short_chg', 2)

    return _model_list


if __name__ == '__main__':
    # print(get_futures_trading_date('20201201', '20210530'))

    # df: DataFrame = pro.fut_basic(exchange='CZCE', fut_type='1')
    # df = df.sort_values('list_date')
    # print(df.to_string())
    # _r = get_oi_holding_rank(Instrument('M1005', exchange=Exchange.DCE), date(2010, 3, 13))
    # _r = get_oi_holding_rank(Instrument('JD2006', exchange=Exchange.DCE), date(2020, 5, 15))
    _r = get_oi_holding_rank(Instrument('CF2009', exchange=Exchange.CZCE), date(2020, 5, 15))
    for item in _r:
        print(item.__data__)
    # print(_r)

    pass
