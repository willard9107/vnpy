import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from mxw.data_source.tushare_wp import *
from mxw.data_source.tq_wp import *
from mxw.db.DbModule import *
from vnpy.trader.constant import Exchange
from datetime import datetime, timedelta, time
from mxw.data_utils import *


def fresh_all_trading_date():
    all_dates = get_futures_trading_date('20000101', '20221231')
    DbTradingDate.save_all(all_dates)


def fresh_all_exchange_instruments():
    future_exchanges = [Exchange.DCE, Exchange.CZCE, Exchange.CFFEX, Exchange.SHFE, Exchange.INE]
    for exchange in future_exchanges:
        ins_list = get_future_instruments(exchange.value)
        DbInstrument.save_all(ins_list)


data_path = '/Volumes/1t/macstat/FutureData/future_data_tq/'


def fetch_instrument_all_tick_data(ins: DbInstrument, count=-1, argv=None):
    trading_dates = list(DbTradingDate.select().where((DbTradingDate.t_date >= ins.listed_date)
                                                      & (DbTradingDate.t_date <= ins.de_listed_date)
                                                      & (DbTradingDate.is_open == 1)).execute())
    # 2000年以前的合约，查不到交易日期，直接跳过
    if not trading_dates:
        return

    file_path_name = data_path + ins.order_book_symbol + os.sep + ins.order_book_id + os.sep
    if not os.path.exists(file_path_name):
        os.makedirs(file_path_name)

    last_date = trading_dates[0].t_date - timedelta(days=20)
    for trading_date in trading_dates:
        cur_date = datetime.combine(trading_date.t_date, time(hour=17))
        # tqsdk 没有2016年以前的数据，不需要走下面的逻辑
        if get_order_id_year(ins.order_book_id) < 2016 or cur_date < datetime(2016, 1, 1, 0, 0, 0):
            last_date = cur_date
            continue

        # 今天往后的数据，还没有发生，直接结束当前合约的下载
        if cur_date > datetime.now():
            break

        # 临时注释，解决之前已经跑过的空数据
        if ins.order_book_id == 'A1609' and cur_date < datetime(2016, 7, 12):
            last_date = cur_date
            continue
        if ins.order_book_id == 'FG1608' and cur_date < datetime(2016, 5, 9):
            last_date = cur_date
            continue
        if ins.order_book_id == 'AG1606' and cur_date < datetime(2016, 1, 11):
            last_date = cur_date
            continue
        # 临时注释--------end---------------

        file_name = file_path_name + ins.order_book_id + trading_date.t_date.strftime('_%Y_%m_%d.csv')
        # 如果文件存在，说明已经下载过相关内容，跳过
        if os.path.exists(file_name) or os.path.exists(file_name + '.0'):
            last_date = cur_date
            continue
        file_name = file_name + '.tmp'
        print('--------------------------------------------argv={}'.format(argv))
        print('start.count={}---{}.{} start={}, end={}'.format(count, ins.exchange, ins.order_book_id, last_date,
                                                               cur_date))

        tick_list = get_tick_data(ins.to_instrument(), last_date, cur_date, file_name)
        if tick_list:
            # print('save tick data to db....')
            # db_tick_class = get_tick_table_class(ins.order_book_id)
            # db_tick_class.save_all(tick_list)
            # time_record()
            os.rename(file_name, file_name[:-4])
        else:
            print('下载的文件为空 .........')
            if os.path.exists(file_name):
                # os.rename(file_name, file_name[:-4])
                os.rename(file_name, file_name[:-4] + '.0')
            else:
                _f = open(file_name[:-4] + '.0', 'w')
                _f.close()
                print('下载文件不存在，主动创建.0 文件, file_name = {}'.format(file_name[:-4] + '.0'))

        last_date = cur_date

    # print(ins.__data__)
    # print(trading_dates[0].__data__)
    # print(trading_dates[1])
    # print(trading_dates[100])

    pass


def fetch_all_instrument_tick_data(offset: int, limit: int):
    result = DbInstrument.select().where(DbInstrument.de_listed_date > '2016-01-01').order_by(
        DbInstrument.id.desc()).offset(offset).limit(
        limit).execute()
    count = 0
    for ins in result:
        count += 1
        fetch_instrument_all_tick_data(ins, count, argv=[offset, limit])


def fetch_one_instrument_tick_data(symbol_id: str):
    result = DbInstrument.select().where(DbInstrument.order_book_id == symbol_id).execute()
    for ins in result:
        fetch_instrument_all_tick_data(ins)


def auto_command_fetch_one_instrument_tick_data(_num_id):
    offset = _num_id * 50
    while offset < 2950:
        fetch_all_instrument_tick_data(offset, 50)
        offset += 50 * 10
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')
        print('-----------------------------------------')


if __name__ == '__main__':
    if sys.argv[1] == 'one':
        fetch_one_instrument_tick_data(sys.argv[2].upper())
    elif sys.argv[1] == 'ten':
        num_id = int(sys.argv[2])
        if 0 <= num_id < 10:
            auto_command_fetch_one_instrument_tick_data(num_id)
        else:
            print('argument illegal')
    else:
        fetch_all_instrument_tick_data(int(sys.argv[1]), int(sys.argv[2]), sys.argv[1:])

    # fresh_all_trading_date()
    # fresh_all_exchange_instruments()

    # fetch_all_instrument_tick_data(0, 1000)
    pass
