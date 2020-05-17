# coding=utf-8
import pandas as pd
import numpy as np

# 以下实现排序功能。
series = pd.Series([3, 4, 1, 6], index=['b', 'a', 'd', 'c'])
frame = pd.DataFrame([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]], columns=['b', 'a', 'd', 'c'],
                     index=['one', 'two', 'three'])
# print(frame)
# print(series)
# print('series通过索引进行排序：')
# print(series.sort_index())
# print('series通过值进行排序:')
# print(series.sort_values())
# print('dataframe根据行索引进行降序排序（排序时默认升序，调节ascending参数）：')
# print(frame.sort_index(ascending=False))
# print('dataframe根据列索引进行排序：')
# print(frame.sort_index(axis=1))
# print('dataframe根据值进行排序：')
# print(frame.sort_values(by='b', ))
# print('通过多个索引进行排序：')
# print(frame.sort_values(by=['a', 'c']))

if __name__ == '__main__':
    print(frame)
    print(frame.iloc[0, 3])
    frame.sort_values(by='c',ascending=False,inplace=True)
    print(frame)
