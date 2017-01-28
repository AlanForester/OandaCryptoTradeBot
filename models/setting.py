from providers.providers import Providers
from models.instrument import Instrument


class Setting:
    id = None
    user_id = None
    name = None
    is_default = None
    created_at = None
    updated_at = None
    instrument_id = None
    candles_durations = None
    analyzer_working_interval_sec = None
    analyzer_collect_interval_sec = None
    analyzer_bid_times = None
    analyzer_deep = None
    analyzer_min_deep = None
    analyzer_prediction_expire = None
    analyzer_candles_parent_relation = None
    prediction_expire = None
    save_prediction_if_exists = None
    signaler_min_chance = None
    signaler_min_repeats = None
    signaler_delay_on_trend = None
    signaler_min_change_cost = None
    signaler_max_change_cost = None
    analyzer_expiry_time_bid_divider = None

    _instrument = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO settings (user_id, name, is_default, created_at, updated_at, instrument_id, " \
                "candles_durations, analyzer_working_interval_sec, analyzer_collect_interval_sec, " \
                "analyzer_bid_times, analyzer_deep, analyzer_min_deep, analyzer_prediction_expire, " \
                "analyzer_candles_parent_relation," \
                "signaler_min_chance, signaler_min_repeats, signaler_delay_on_trend,signaler_min_change_cost, " \
                "signaler_max_change_cost,analyzer_expiry_time_bid_divider) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id"
        cursor.execute(query,
                       (self.user_id, self.name, self.is_default, self.created_at, self.updated_at, self.instrument_id,
                        self.candles_durations, self.analyzer_working_interval_sec, self.analyzer_collect_interval_sec,
                        self.analyzer_bid_times, self.analyzer_deep, self.analyzer_min_deep,
                        self.analyzer_prediction_expire,
                        self.analyzer_candles_parent_relation, self.signaler_min_chance, self.signaler_min_repeats,
                        self.signaler_delay_on_trend, self.signaler_min_change_cost, self.signaler_max_change_cost,
                        self.analyzer_expiry_time_bid_divider))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    @property
    def instrument(self):
        if not self._instrument:
            self._instrument = Instrument.get_instrument_by_id(self.instrument_id)
        return self._instrument

    def __tuple_str(self):
        return str((self.user_id, self.name, self.is_default, self.created_at, self.updated_at, self.instrument_id,
                    self.candles_durations, self.analyzer_working_interval_sec, self.analyzer_collect_interval_sec,
                    self.analyzer_bid_times, self.analyzer_deep, self.analyzer_min_deep,
                    self.analyzer_prediction_expire, self.analyzer_candles_parent_relation,
                    self.signaler_min_chance, self.signaler_min_repeats, self.signaler_delay_on_trend,
                    self.signaler_min_change_cost, self.signaler_max_change_cost,
                    self.analyzer_expiry_time_bid_divider))

    @staticmethod
    def model(raw=None):
        return Setting(raw)

    @staticmethod
    def get_count():
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT COUNT(*) FROM settings", [])
        return cursor.fetchone()[0]

    @staticmethod
    def get_default():
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM settings WHERE is_default=%s", [True])
        row = cursor.fetchone()
        if row:
            return Setting(row)

    @staticmethod
    def get_by_id(pk):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM settings WHERE id=%s", [pk])
        row = cursor.fetchone()
        if row:
            return Setting(row)
