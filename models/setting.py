from models.coremodel import CoreModel


class Setting(CoreModel):
    @staticmethod
    def model(raw=None):
        return _SettingModel(raw)

    def get_settings_count(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM settings", [])
        return cursor.fetchone()[0]

    def save(self, instruments: _SettingModel):
        # cursor = self.db.get_cursor()
        # query = "INSERT INTO settings (name, is_default, created_at, updated_at, instrument_id, analyzer_bid_times, " \
        #         "analyzer_deep, analyzer_min_deep, analyzer_prediction_expire, analyzer_save_prediction_if_exists, " \
        #         "collector_candles_durations, collector_working_interval_sec, trader_min_chance, trader_min_repeats, " \
        #         "trader_delay_on_trend, trader_max_count_orders_for_expiration_time) " \
        #         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,);"
        # cursor.execute(query,)
        # self.db.commit()
        print(instruments)


class _SettingModel(object):
    id = None
    name = None
    is_default = None
    created_at = None
    updated_at = None
    instrument_id = None
    analyzer = _SettingAnalyzer()
    collector = _SettingCollector()
    trader = _SettingTrader()

    def __init__(self, raw=None):
        if raw:
            self.id = raw.id
            self.name = raw.name
            self.is_default = raw.is_deault
            self.created_at = raw.created_at
            self.updated_at = raw.updated_at
            self.instrument_id = raw.instrument_id
            self.analyzer.bid_times = raw.analyzer_bid_times


class _SettingAnalyzer(object):
    bid_times = None
    deep = None
    min_deep = None
    prediction_expire = None
    save_prediction_if_exists = None


class _SettingCollector(object):
    candles_durations = None
    working_interval_sec = None


class _SettingTrader(object):
    min_chance = None
    min_repeats = None
    delay_on_trend = None
    max_count_orders_for_expiration_time = None
