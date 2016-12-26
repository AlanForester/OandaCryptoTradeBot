from models.coremodel import CoreModel
from mixins.providers import ProvidersMixin


class Setting(ProvidersMixin):
    @staticmethod
    def model(raw=None):
        return _SettingModel(raw)

    def get_settings_count(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM settings", [])
        return cursor.fetchone()[0]

    def save(self, name, is_default, created_at, updated_at, instrument_id, analyzer_bid_times, analyzer_deep,
             analyzer_min_deep, analyzer_prediction_expire, analyzer_save_prediction_if_exists,
             collector_candles_durations, collector_working_interval_sec, trader_min_chance, trader_min_repeats,
             trader_delay_on_trend, trader_max_count_orders_for_expiration_time):
        cursor = self.db.get_cursor()
        query = "INSERT INTO settings (name, is_default, created_at, updated_at, instrument_id, analyzer_bid_times, " \
                "analyzer_deep, analyzer_min_deep, analyzer_prediction_expire, analyzer_save_prediction_if_exists, " \
                "collector_candles_durations, collector_working_interval_sec, trader_min_chance, trader_min_repeats, " \
                "trader_delay_on_trend, trader_max_count_orders_for_expiration_time) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id"
        cursor.execute(query,
                       (name, is_default, created_at, updated_at, instrument_id, analyzer_bid_times, analyzer_deep,
                        analyzer_min_deep, analyzer_prediction_expire, analyzer_save_prediction_if_exists,
                        collector_candles_durations, collector_working_interval_sec, trader_min_chance,
                        trader_min_repeats, trader_delay_on_trend, trader_max_count_orders_for_expiration_time))
        self.db.commit()
        row = cursor.fetchone()
        if row:
            return row[0]


class _SettingModel(CoreModel):
    id = None
    name = None
    is_default = None
    created_at = None
    updated_at = None
    instrument_id = None
    analyzer_bid_times = None
    analyzer_deep = None
    analyzer_min_deep = None
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
