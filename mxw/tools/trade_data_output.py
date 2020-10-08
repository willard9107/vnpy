from mxw.utils.common_import import *
from mxw.db.DbModule import *


def download_daily_k_bar(prefix: str):
    result = DbDailyBar.select().where(DbDailyBar.order_book_id.startswith(prefix)).order_by(
        DbDailyBar.date_time).offset(9999).execute()
    for item in result:
        print(
            f'{item.order_book_id},{item.date_time},{item.open_price},{item.high_price},{item.low_price},{item.close_price},{item.settle_price},{item.volume},{item.open_interest}')

    pass


if __name__ == '__main__':
    download_daily_k_bar('JD')
    pass
