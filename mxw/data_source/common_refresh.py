from mxw.utils.common_import import *

from mxw.utils import dingtalk_utils
from mxw.data_source.tq_wp import *
from mxw.db.DbModule import *
from vnpy.trader.constant import Exchange
from mxw.data_utils import *
from mxw.data_source import other_wp, tushare_wp
from mxw.db import model_utils


def fresh_all_trading_date():
    all_dates = tushare_wp.get_futures_trading_date('20000101', '20221231')
    DbTradingDate.save_all(all_dates)


def fresh_all_exchange_instruments():
    future_exchanges = [Exchange.DCE, Exchange.CZCE, Exchange.CFFEX, Exchange.SHFE, Exchange.INE]
    for exchange in future_exchanges:
        ins_list = tushare_wp.get_future_instruments(exchange.value)
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

        tick_flag, tick_list = get_tick_data(ins.to_instrument(), last_date, cur_date, file_name, process=False)
        if tick_flag:
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
    lock = redis_lock.Lock(common_utils.redis_conn, "auto_command_fetch_one_instrument_tick_data__" + str(_num_id),
                           expire=4, auto_renewal=True)
    if lock.acquire(blocking=False):
        print("Got the lock.")
        offset = _num_id * 50
        while offset < 2950:
            fetch_all_instrument_tick_data(offset, 50)
            offset += 50 * 10
            print('--------------*****************---------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')
            print('-----------------------------------------')

        dingtalk_utils.send_message('第{}部分下载完成...'.format(_num_id))

        lock.release()
    else:
        print("Someone else has the lock.")
        print("you maybe set wrong parameters.....")


def fetch_daily_bar_data():
    """根据日k线数据库的最新数据，或者还没有获取的数据"""
    start_date = date(2010, 1, 1)
    _max_daily_bar = DbDailyBar.select().order_by(DbDailyBar.id.desc()).first()
    if _max_daily_bar is not None:
        start_date = _max_daily_bar.date_time

    trading_dates = DbTradingDate.select().where((DbTradingDate.t_date > start_date)
                                                 & (DbTradingDate.t_date <= date.today())
                                                 & (DbTradingDate.is_open == 1)).execute()
    for _t_date in trading_dates:
        _d_bars = tushare_wp.get_daily_bar_of_cn_future_exchange(_t_date.t_date)
        DbDailyBar.save_all(_d_bars)
        print(f'date: {_t_date.t_date}  数据已存储...')


def fetch_oi_by_ins_date(ins: Instrument, _date: date):
    def check_date_exist(_t_d: date):
        _max_oi = DbOpenInterestHolding.select().where(
            (DbOpenInterestHolding.date_time == _t_d) & (DbOpenInterestHolding.order_book_id == ins.symbol)).first()
        if _max_oi is not None:
            return True
        return False

    if check_date_exist(_date):
        print(f'合约龙虎榜存在，跳过.. date={_date}, symbol = {ins.symbol}')
        return

    '''切换持仓获取数据源，tushare && 17kqh
    17kqh 数据源访问快，而且每天更新快，但是数据不全，只有几个主力合约的数据，而且最早到19年元旦
    tushare 数据全，但是访问限速，更新慢
    先用17kqh爬取近两年的数据，能爬到多少爬多少
    然后使用tushare查漏补缺，tushare也查不到的数据，做占位处理（标记当前合约已查询过，后续更新数据不再查询）
    '''
    model_list = tushare_wp.get_oi_holding_rank(ins, _date)
    # model_list = other_wp.get_open_interest_data_by_symbol_date(ins, _date)

    DbOpenInterestHolding.bulk_create(model_list)
    return model_list


def fetch_open_interest_holding_rank(start_date_str: str, end_date_str=None):
    start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
    end_date = date.today()
    if datetime.now().time() < d_time(17, 0):
        end_date = end_date - timedelta(days=1)

    if end_date_str:
        _end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
        if _end_date < end_date:
            end_date = _end_date

    trading_dates = DbTradingDate.select().where((DbTradingDate.t_date >= start_date)
                                                 & (DbTradingDate.t_date <= end_date)
                                                 & (DbTradingDate.is_open == 1)).execute()
    print(f'交易天数：{trading_dates.count}')
    _format = '%Y-%m-%d'
    for _t_date in trading_dates:
        _date = _t_date.t_date

        time_record()
        model_list = []
        all_ins = model_utils.get_all_instrument_by_trading_date(_date)
        print(f'date={_date.strftime(_format)}, 共获取合约数{len(all_ins)}，开始获取当天龙虎榜信息....')
        count = 1
        for ins in all_ins:
            # print(f'process...{count}/{len(all_ins)}')
            count += 1
            print(f'获取龙虎榜信息.{count}/{len(all_ins)}, date={_date}, symbol = {ins.symbol}')
            fetch_oi_by_ins_date(ins, _date)

    return None


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'one':
            fetch_one_instrument_tick_data(sys.argv[2].upper())
        elif len(sys.argv) > 1 and sys.argv[1] == 'ten':
            num_id = int(sys.argv[2])
            if 0 <= num_id < 10:
                auto_command_fetch_one_instrument_tick_data(num_id)
            else:
                print('argument illegal')
        elif len(sys.argv) > 3 and sys.argv[1] == 'oi_holding':
            fetch_open_interest_holding_rank(sys.argv[2], sys.argv[3])
        else:
            # fetch_all_instrument_tick_data(int(sys.argv[1]), int(sys.argv[2]), sys.argv[1:])
            # fetch_daily_bar_data()
            # fetch_open_interest_holding_rank('20200101', '20200519')
            # fetch_open_interest_holding_rank('20190101', '20191231')
            fetch_open_interest_holding_rank('20180101', '20181231')
            # fetch_open_interest_holding_rank('20200518')
            print('nothing...')
            # raise Exception('持仓龙虎榜数据获取异常，数据量小于20')

        # fresh_all_trading_date()
        # fresh_all_exchange_instruments()

        # fetch_all_instrument_tick_data(0, 1000)
    except Exception as e:
        dingtalk_utils.send_message(f'脚本运行发生异常 sys.argv:\n{sys.argv}\nmsg:--- {e}\n{traceback.format_exc()}')

    pass
