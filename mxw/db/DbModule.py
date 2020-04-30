import dataclasses
from typing import List

from peewee import *
from datetime import datetime, date, timedelta

from mxw.obj import TradingDate, Instrument
from vnpy.trader.constant import Exchange
from vnpy.trader.object import BarData, TickData

db = MySQLDatabase('futures', user='root', host='nas.willard.love', port=32776, password='afsd1423', charset='utf8mb4')
db.connect()


class DbTradingDate(Model):
    id: IntegerField
    t_date: date = DateField()
    is_open: int = IntegerField()
    create_time: datetime = DateTimeField()

    class Meta:
        database = db
        table_name = 'trading_date'

    # @staticmethod
    # def from_trading_date(t_date: TradingDate):
    #     return DbTradingDate()

    @staticmethod
    def save_all(objs: List["TradingDate"]):
        dicts = [{'t_date': i.date, 'is_open': i.is_open} for i in objs]
        with db.atomic():
            for c in chunked(dicts, 100):
                DbTradingDate.insert_many(c).on_conflict_replace().execute()


class DbInstrument(Model):
    id: int = AutoField()
    order_book_id: str = CharField()
    order_book_symbol: str = CharField()
    symbol: str = CharField()
    listed_date: date = DateField()
    de_listed_date: date = DateField()
    maturity_date: date = DateField()
    exchange: str = CharField()
    margin_rate: str = CharField()
    contract_multiplier: int = IntegerField()
    trading_hours: str = CharField()

    create_time: datetime = DateTimeField()

    class Meta:
        database = db
        table_name = 'instrument'

    # @staticmethod
    # def from_intrument(ins: Instrument):
    #     return DbTradingDate()

    def to_instrument(self):
        return Instrument(self.order_book_id, self.order_book_symbol, self.symbol, self.listed_date,
                          self.de_listed_date, self.maturity_date, self.exchange, self.margin_rate,
                          self.contract_multiplier, self.trading_hours)

    @staticmethod
    def save_all(objs: List["Instrument"]):
        dicts = [dataclasses.asdict(i) for i in objs]
        with db.atomic():
            for c in chunked(dicts, 100):
                DbInstrument.insert_many(c).on_conflict_ignore().execute()


def get_tick_table_class(symbol: str):
    class DbTickData(ModelBase):
        """
        Tick data for database storage.

        Index is defined unique with (datetime, symbol)
        """

        datetime: int = BigIntegerField(primary_key=True, )

        volume: float = FloatField()
        open_interest: float = FloatField()
        last_price: float = FloatField()
        last_volume: float = FloatField()

        high_price: float = FloatField(default=0)
        low_price: float = FloatField(default=0)

        bid_price_1: float = FloatField()
        bid_price_2: float = FloatField(null=True)
        bid_price_3: float = FloatField(null=True)
        bid_price_4: float = FloatField(null=True)
        bid_price_5: float = FloatField(null=True)

        ask_price_1: float = FloatField()
        ask_price_2: float = FloatField(null=True)
        ask_price_3: float = FloatField(null=True)
        ask_price_4: float = FloatField(null=True)
        ask_price_5: float = FloatField(null=True)

        bid_volume_1: float = FloatField()
        bid_volume_2: float = FloatField(null=True)
        bid_volume_3: float = FloatField(null=True)
        bid_volume_4: float = FloatField(null=True)
        bid_volume_5: float = FloatField(null=True)

        ask_volume_1: float = FloatField()
        ask_volume_2: float = FloatField(null=True)
        ask_volume_3: float = FloatField(null=True)
        ask_volume_4: float = FloatField(null=True)
        ask_volume_5: float = FloatField(null=True)

        class Meta:
            database = db
            table_name = 'tick_' + symbol.lower()
            table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8mb4']

        @staticmethod
        def from_tick(tick: TickData):
            db_tick = DbTickData()
            db_tick.datetime = int(tick.datetime.timestamp() * 1000000)
            db_tick.volume = tick.volume
            db_tick.open_interest = tick.open_interest
            db_tick.last_price = tick.last_price
            db_tick.last_volume = tick.last_volume

            db_tick.bid_price_1 = tick.bid_price_1
            db_tick.ask_price_1 = tick.ask_price_1
            db_tick.bid_volume_1 = tick.bid_volume_1
            db_tick.ask_volume_1 = tick.ask_volume_1

            if tick.bid_price_2:
                db_tick.bid_price_2 = tick.bid_price_2
                db_tick.bid_price_3 = tick.bid_price_3
                db_tick.bid_price_4 = tick.bid_price_4
                db_tick.bid_price_5 = tick.bid_price_5

                db_tick.ask_price_2 = tick.ask_price_2
                db_tick.ask_price_3 = tick.ask_price_3
                db_tick.ask_price_4 = tick.ask_price_4
                db_tick.ask_price_5 = tick.ask_price_5

                db_tick.bid_volume_2 = tick.bid_volume_2
                db_tick.bid_volume_3 = tick.bid_volume_3
                db_tick.bid_volume_4 = tick.bid_volume_4
                db_tick.bid_volume_5 = tick.bid_volume_5

                db_tick.ask_volume_2 = tick.ask_volume_2
                db_tick.ask_volume_3 = tick.ask_volume_3
                db_tick.ask_volume_4 = tick.ask_volume_4
                db_tick.ask_volume_5 = tick.ask_volume_5

            return db_tick

        def to_tick(self):
            """
            Generate TickData object from DbTickData.
            """
            tick = TickData(
                symbol=symbol,
                datetime=datetime.fromtimestamp(self.datetime / 1000000),
                volume=self.volume,
                open_interest=self.open_interest,
                last_price=self.last_price,
                last_volume=self.last_volume,
                high_price=self.high_price,
                low_price=self.low_price,
                bid_price_1=self.bid_price_1,
                ask_price_1=self.ask_price_1,
                bid_volume_1=self.bid_volume_1,
                ask_volume_1=self.ask_volume_1,
                gateway_name="DB",
            )

            if self.bid_price_2:
                tick.bid_price_2 = self.bid_price_2
                tick.bid_price_3 = self.bid_price_3
                tick.bid_price_4 = self.bid_price_4
                tick.bid_price_5 = self.bid_price_5

                tick.ask_price_2 = self.ask_price_2
                tick.ask_price_3 = self.ask_price_3
                tick.ask_price_4 = self.ask_price_4
                tick.ask_price_5 = self.ask_price_5

                tick.bid_volume_2 = self.bid_volume_2
                tick.bid_volume_3 = self.bid_volume_3
                tick.bid_volume_4 = self.bid_volume_4
                tick.bid_volume_5 = self.bid_volume_5

                tick.ask_volume_2 = self.ask_volume_2
                tick.ask_volume_3 = self.ask_volume_3
                tick.ask_volume_4 = self.ask_volume_4
                tick.ask_volume_5 = self.ask_volume_5

            return tick

        @staticmethod
        def save_all(objs: List["TickData"]):
            dicts = [DbTickData.from_tick(i).to_dict() for i in objs]
            with db.atomic():
                for c in chunked(dicts, 1000):
                    DbTickData.insert_many(c).on_conflict_ignore().execute()

    db.create_tables([DbTickData])
    return DbTickData


class ModelBase(Model):

    def to_dict(self):
        return self.__data__


if __name__ == '__main__':
    tick_class = get_tick_table_class('JD2005')
    tick_class.save_all([TickData('', '', Exchange.DCE, datetime(2019, 1, 1, 12, 0, 0, 123456))])

# tick_class = get_tick_table('jd2012')

#
# # item = DbTradingData(t_date='2019-03-01')
# # item.save()
#
#
#
#
# for item in DbTradingDate.select().dicts().execute():
#     print(item.__str__())
