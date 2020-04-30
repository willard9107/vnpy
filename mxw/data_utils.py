import time

from mxw.obj import Instrument


def exact_exchange_symbol(ins: Instrument):
    if ins.exchange in ['DCE', 'INE', 'SHFE']:
        return ins.order_book_id.lower()
    elif ins.exchange in ['CZCE']:
        ori = ins.order_book_id.upper()
        return ori[:-4]+ori[-3:]
    else:
        return ins.order_book_id.upper()


def get_order_id_year(order_id: str):
    y = int(order_id[-4:-2])
    if y < 50:
        y += 2000
    else:
        y += 1900
    return y


last_time = time.time()
def time_record():
    global last_time
    cur_time = time.time()
    print('耗时: {}秒'.format(cur_time - last_time))
    last_time = cur_time


if __name__ == '__main__':
    # print(get_order_id_year('CU2105'))
    time_record()
    time.sleep(1)
    time_record()
    time.sleep(3)
    time_record()
    time.sleep(2)
    time_record()
    pass
