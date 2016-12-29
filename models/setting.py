from providers.providers import Providers


class Setting:
    id = None
    user_id = None
    name = None
    is_default = None
    created_at = None
    updated_at = None
    instrument_id = None
    analyzer_bid_times = None
    analyzer_deep = None
    analyzer_min_deep = None
    analyzer_prediction_expire = None
    analyzer_save_prediction_if_exists = None
    prediction_expire = None
    save_prediction_if_exists = None
    collector_candles_durations = None
    collector_working_interval_sec = None
    trader_min_chance = None
    trader_min_repeats = None
    trader_delay_on_trend = None
    trader_max_count_orders_for_expiration_time = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO settings (user_id, name, is_default, created_at, updated_at, instrument_id, analyzer_bid_times, " \
                "analyzer_deep, analyzer_min_deep, analyzer_prediction_expire, analyzer_save_prediction_if_exists, " \
                "collector_candles_durations, collector_working_interval_sec, trader_min_chance, trader_min_repeats, " \
                "trader_delay_on_trend, trader_max_count_orders_for_expiration_time) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id"
        cursor.execute(query,
                       (self.user_id, self.name, self.is_default, self.created_at, self.updated_at, self.instrument_id,
                        self.analyzer_bid_times, self.analyzer_deep,
                        self.analyzer_min_deep, self.analyzer_prediction_expire,
                        self.analyzer_save_prediction_if_exists,
                        self.collector_candles_durations, self.collector_working_interval_sec, self.trader_min_chance,
                        self.trader_min_repeats, self.trader_delay_on_trend,
                        self.trader_max_count_orders_for_expiration_time))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    def __tuple_str(self):
        return str((self.user_id, self.name, self.is_default, self.created_at, self.updated_at, self.instrument_id,
                    self.analyzer_bid_times, self.analyzer_deep,
                    self.analyzer_min_deep, self.analyzer_prediction_expire,
                    self.analyzer_save_prediction_if_exists,
                    self.collector_candles_durations, self.collector_working_interval_sec, self.trader_min_chance,
                    self.trader_min_repeats, self.trader_delay_on_trend,
                    self.trader_max_count_orders_for_expiration_time))

    @staticmethod
    def model(raw=None):
        return Setting(raw)

    @staticmethod
    def get_settings_count():
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT COUNT(*) FROM settings", [])
        return cursor.fetchone()[0]
