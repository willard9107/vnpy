import math
import sys
import os
import time
from datetime import datetime, date
from contextlib import closing

import requests
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader
from mxw.data_utils import get_order_id_year, exact_exchange_symbol
from mxw.obj import Instrument
import pandas as pd
from mxw.data_utils import *

# api = TqApi(TqSim())
# download_tasks = {}
#
# # 下载从 2018-01-01 到 2018-09-01 的 SR901 日线数据
# download_tasks["SR_daily"] = DataDownloader(api, symbol_list="CZCE.SR901", dur_sec=24*60*60,
# start_dt=date(2018, 1, 1), end_dt=date(2018, 9, 1), csv_file_name="data/SR901_daily.csv")
#
#
# # 下载从 2017-01-01 到 2018-09-01 的 rb主连 5分钟线数据
# download_tasks["rb_5min"] = DataDownloader(api, symbol_list="KQ.m@SHFE.rb", dur_sec=5*60,
# start_dt=date(2017, 1, 1), end_dt=date(2018, 9, 1), csv_file_name="data/rb_5min.csv")
#
#
# # 下载从 2018-01-01凌晨6点 到 2018-06-01下午4点 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
# # 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
# # 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
# download_tasks["cu_min"] = DataDownloader(api, symbol_list=["SHFE.cu1805", "SHFE.cu1807", "CFFEX.IC1803"], dur_sec=60,
# start_dt=datetime(2018, 1, 1, 6, 0 ,0), end_dt=datetime(2018, 6, 1, 16, 0, 0), csv_file_name="data/cu_min.csv")
from vnpy.trader.constant import Exchange
from vnpy.trader.object import TickData

api = None
use_count = 0


def tq_connect(renew=False):
    _reconnect = 3
    global use_count, api
    use_count += 1
    while _reconnect > 0:
        try:
            if api is None:
                api = TqApi(TqSim())
                use_count = 0
            elif renew:
                api.close()
                api = TqApi(TqSim())
                use_count = 0
            return api
        except Exception as error:
            print('----------------------------------------------------')
            print(error)
            print('-------------------reconnect---------------------------------')
            _reconnect -= 1
    raise Exception('muxian.wu------tqsdk connect error for 3 times.............')


def get_tick_data(instrument: Instrument, start_date: datetime, end_date: datetime, file_name: str):
    # tqsdk 没有2016年以前的数据，不需要走下面的逻辑
    if get_order_id_year(instrument.order_book_id) < 2016 or end_date < datetime(2016, 1, 1, 0, 0, 0) \
            or instrument.order_book_symbol in ['PM', 'RI', 'WH', 'JR']:
        return []

    exchange_order_id = '{}.{}'.format(instrument.exchange, exact_exchange_symbol(instrument))

    _tq_api = tq_connect()
    download_tasks = {"T_tick": DataDownloader(_tq_api, symbol_list=[exchange_order_id], dur_sec=0,
                                               start_dt=start_date, end_dt=end_date,
                                               csv_file_name=file_name)}

    print('开始 下载 tick数据, {}.{} start={}, end={}'.format(instrument.exchange, instrument.order_book_id, start_date,
                                                        end_date))

    error_flag = False
    # 使用with closing机制确保下载完成后释放对应的资源
    download_over = False
    while not download_over:
        try:
            while not all([v.is_finished() for v in download_tasks.values()]):
                if not _tq_api.wait_update(time.time() + 1):
                    os.remove(file_name)
                    error_flag = True
                    print('fetch tick error-> {}  date = {}'.format(instrument, end_date), file=sys.stderr)
                    break
                # print("progress: ", {k: ("%.2f%%" % v.get_progress()) for k, v in download_tasks.items()})
            download_over = True
        except Exception as error:
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print('download error...................')
            print(error)
            _tq_api = tq_connect(renew=True)

    print('tick 数据下载完成...')
    time_record()

    if error_flag or os.path.getsize(file_name) == 0:
        print('**************************************************')
        print('文件下载为空')
        print('**************************************************')
        return []

    print('read_csv....')
    df = pd.read_csv(file_name)
    # print(time.time())
    time_record()
    result = []
    for index, row in df.iterrows():
        tick_time = datetime.strptime(row[0][:-3], '%Y-%m-%d %H:%M:%S.%f')
        last_price = row[1] if not math.isnan(row[1]) else 0
        highest = row[2]
        lowest = row[3]
        bid_price1 = row[4] if not math.isnan(row[4]) else 0
        bid_volume1 = row[5]
        ask_price1 = row[6] if not math.isnan(row[6]) else 0
        ask_volume1 = row[7]
        volume = row[8]
        open_interest = row[10]
        if volume == 0:
            continue

        # print(row[0], row[1], row['datetime'])
        tick_data = TickData('DB', instrument.order_book_id, Exchange(instrument.exchange), tick_time, volume=volume,
                             open_interest=open_interest, last_price=last_price, bid_price_1=bid_price1,
                             bid_volume_1=bid_volume1, ask_price_1=ask_price1, ask_volume_1=ask_volume1)
        result.append(tick_data)
    print('tick_data return----count= {}'.format(len(result)))
    time_record()
    return result


if __name__ == '__main__':
    # get_tick_data('', '', '')

    # print(date(2016, 2, 1) <= date(2016, 2, 1))

    # data_path = '/Volumes/1t/macstat/FutureData/future_data_tq/'
    # get_tick_data(Instrument('M2005', '', '', '', '', '', 'DCE', '', '', ''), datetime(2019, 5, 17),
    #               datetime(2019, 5, 20, 9, 10), data_path + 'test1.csv')

    # print(datetime.strptime('2020-04-02 14:22:19.796000000','%Y-%m-%d %H:%M:%S.%f'))

    pass
