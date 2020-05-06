import os
import sys
import random
from math import *

import redis

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())


class Template:
    vars = []

    def __init__(self):
        self.vars = []
        self.vars.insert(0, "0")

    @classmethod
    def class_method_demo(cls):
        print(cls)

    def print_vars(self):
        print(self.vars)


class Strategy(Template):
    def __init__(self):
        super().__init__()
        print('strategy init')


def spamrun(fn):
    def sayspam(*args):
        print("spam,spam,spam")
        fn(*args)

    return sayspam


def spamrun1(fn):
    def sayspam1(*args):
        print("spam1,spam1,spam1")
        fn(*args)

    return sayspam1


@spamrun
@spamrun1
def useful(a, b):
    print(a * b)


def attrs(**kwds):
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        print('***************')
        print(f)
        return f

    print(kwds)
    return decorate


# @attrs(versionadded="2.2",
#        author="Guido van Rossum")
# def mymethod(f):
#     print(getattr(mymethod, 'versionadded', 0))
#     print(getattr(mymethod, 'author', 0))
#     print(f)

# print('------0-------')
# print(mymethod)
# print('-------1------')
#
# if __name__ == "__main__":
#     mymethod(2)


# ttt = Template()
# ttt1 = Template()
# ttt2 = Template()
# print(Template.vars)
# ttt1.print_vars()
# ttt2.print_vars()

#
# class Sample:
#
#     def __init__(self):
#         print('__init__')
#
#     def __enter__(self):
#         print("in __enter__")
#         return "Foo"
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         print("in __exit__")
#
#
# def get_sample():
#     return Sample()
#
#
# with get_sample() as sample:
#     print("Sample: ", sample)

# # 传递外部类的实例
# class OuterClassA(object):
#
#     def __init__(self):
#         print('outter  init ....')
#         self.a = 0
#
#     def outer_func_1(self, text):
#         print(text)
#
#     class InnerClass(object):
#
#         def __init__(self):
#             print('inner  init ....')
#             self.out = OuterClassA()
#
#         def inner_func_1(self):
#             self.out.outer_func_1('balabala')
#             # pass

#
# outer = OuterClassA()
# outer.outer_func_1('abcdefg')
# print('1')
# inn = outer.InnerClass()
# print('2')
# inn.inner_func_1()
#
#
#
# print('3')
# inn1 = outer.InnerClass()
# print('4')
# inn1.inner_func_1()


import redis_lock
import time as _time


def redis_lock_test():
    conn = redis.StrictRedis(host='nas.willard.love', port=32778)
    with redis_lock.Lock(conn, 'fetch_tick_data_limit_offset_lock', expire=60, auto_renewal=True):
        print('get lock-----------')
        count = 0
        while count < 5:
            print('do sth....count: {}'.format(count))
            count += 1
            _time.sleep(1)
        print('release lock*************')


def pandas_read_csv_test(num):
    # file_name = '/Volumes/1t/macstat/FutureData/future_data_tq/M/M2005/M2005_2020_04_22.csv'
    # import pandas as pd
    # df = pd.read_csv(file_name)
    if num is 2:
        return 1, 2
    return []


def cpu_benchmark():
    def random_sort(n):
        _li = [random.random() for i in range(n)]
        print('start to sort....')
        _res = sorted(_li)
        print('end sort....')
        return _res

    def random_add(n):
        a = 0.1
        for i in range(n):
            a += 3 * log(i+0.1) + cos(i) ** 2
        print('--------------')
        print(a)

    # def random_calculate(n):

    while True:
        # random_sort(20000000)
        random_add(20000000)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'lock_test':
        count = 0
        while count < 5:
            redis_lock_test()
            count += 1
        print('test over...')
    elif len(sys.argv) > 1 and sys.argv[1] == 'exception_test':
        raise Exception('mxw exception....')
    elif len(sys.argv) > 1 and sys.argv[1] == 'cpu_test':
        cpu_benchmark()
    else:
        a, b = pandas_read_csv_test(1)
        print(a, b)
        print('nothing todo.....')
