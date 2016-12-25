from models.coremodel import CoreModel


class Setting(CoreModel):
    table_name = 'settings'

    @property
    def id(self):
        return self.__raw_data.id

    @property
    def name(self):
        return self.__raw_data.name

    @property
    def is_default(self):
        return self.__raw_data.is_default

    @property
    def created_at(self):
        return self.__raw_data.created_at

    @property
    def updated_at(self):
        return self.__raw_data.updated_at

    @property
    def instrument_id(self):
        return self.__raw_data.instrument_id

    @property
    def analyzer(self):
        return _SettingAnalyzer(
            bid_times=self.__raw_data.analyzer_bid_times,
            deep=self.__raw_data.analyzer_deep,
            min_deep=self.__raw_data.analyzer_min_deep,
            prediction_expire=self.__raw_data.analyzer_prediction_expire,
            save_prediction_if_exists=self.__raw_data.analyzer_save_prediction_if_exists
        )

    @property
    def collector(self):
        return _SettingCollector(
            candles_durations=self.__raw_data.collector_candles_durations,
            working_interval_sec=self.__raw_data.collector_working_interval_sec
        )

    @property
    def trader(self):
        return _SettingTrader(
            min_chance=self.__raw_data.trader_min_chance,
            min_repeats=self.__raw_data.trader_min_repeats,
            delay_on_trend=self.__raw_data.trader_delay_on_trend,
            max_count_orders_for_expiration_time=self.__raw_data.trader_max_count_orders_for_expiration_time
        )

    def get_settings_count(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM settings", [])
        return cursor.fetchone()[0]

    def save(self, instruments: list(tuple)):
        cursor = self.db.get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                ",".join(str(v) for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"

        cursor.execute(query)
        self.db.commit()


class _SettingAnalyzer(object):
    def __init__(self, bid_times: object, deep: int, min_deep: int, prediction_expire: object,
                 save_prediction_if_exists: bool):
        self.bid_times = bid_times
        self.deep = deep
        self.min_deep = min_deep
        self.prediction_expire = prediction_expire
        self.save_prediction_if_exists = save_prediction_if_exists


class _SettingCollector(object):
    def __init__(self, candles_durations: object, working_interval_sec: int):
        self.candles_durations = candles_durations
        self.working_interval_sec = working_interval_sec


class _SettingTrader(object):
    def __init__(self, min_chance: float, min_repeats: int, delay_on_trend: int,
                 max_count_orders_for_expiration_time: int):
        self.min_chance = min_chance
        self.min_repeats = min_repeats
        self.delay_on_trend = delay_on_trend
        self.max_count_orders_for_expiration_time = max_count_orders_for_expiration_time
