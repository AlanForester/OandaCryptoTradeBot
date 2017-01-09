from providers.providers import Providers
from models.quotation import Quotation


class Candle(object):
    instrument_id = None
    from_ts = 0
    till_ts = 0
    duration = 0
    high = 0.0
    low = 0.0
    open = 0.0
    close = 0.0
    range = 0.0
    change = 0.0
    average = 0.0
    average_power = 0.0
    range_power = 0.0
    change_power = 0.0
    high_power = 0.0
    low_power = 0.0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute('INSERT INTO candles (instrument_id, from_ts, till_ts, duration, high, low, "open", '
                             '"close", range, change, average, average_power, range_power, change_power, high_power, '
                             'low_power) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                             'ON CONFLICT (ts,instrument_id) DO NOTHING RETURNING ts',
                             (self.instrument_id, self.from_ts, self.till_ts, self.duration, self.high, self.low,
                              self.open, self.close, self.range, self.change, self.average, self.average_power,
                              self.range_power, self.change_power, self.high_power, self.low_power))

        Providers.db().commit()
        if row:
            return self

    def __tuple_str(self):
        return str((self.instrument_id, self.from_ts, self.till_ts, self.duration, self.high, self.low,
                    self.open, self.close, self.range, self.change, self.average, self.average_power,
                    self.range_power, self.change_power, self.high_power, self.low_power))

    @staticmethod
    def model(raw=None):
        return Candle(raw)

    @staticmethod
    def make(from_ts, duration, instrument_id):
        candle_raw = Quotation.prepare_candle(from_ts, duration, instrument_id)
        candle = Candle(candle_raw)
        candle.instrument_id = instrument_id
        candle.from_ts = from_ts - duration
        candle.till_ts = from_ts
        candle.duration = duration
        candle.range = candle.high - candle.low
        candle.change = candle.open - candle.close

        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM candles WHERE instrument_id=%s AND duration=%s ORDER BY till_ts DESC LIMIT 1",
                       (instrument_id, duration))

        last_candle = Candle()
        last_candle_raw = cursor.fetchone()
        if last_candle_raw:
            last_candle.model(last_candle_raw)

        if last_candle.change != 0:
            candle.change_power = candle.change / (last_candle.change / 100)

        return candle

    @staticmethod
    def save_many(candles: list):
        cursor = Providers.db().get_cursor()
        query = 'INSERT INTO candles (instrument_id, from_ts, till_ts, duration, high, low, "open", "close", range, ' \
                'change, average, average_power, range_power, change_power, high_power, low_power) VALUES ' + \
                ','.join(v.__tuple_str() for v in candles) + ' ON CONFLICT (instrument_id, from_ts, till_ts) DO NOTHING'
        cursor.execute(query)
        Providers.db().commit()
