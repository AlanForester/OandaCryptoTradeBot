import time
import json

from models.setting import Setting
from models.instrument import Instrument
from fixtures.instruments import Instruments as InstrumentsFixture


class Settings:
    @staticmethod
    def up():
        if Setting.get_count() == 0:
            instrument = Instrument.get_instrument_by_name("EUR_USD")
            if not instrument:
                InstrumentsFixture.up()
            model = Setting()
            model.user_id = 0  # TODO: Create real users
            model.name = "Default",
            model.is_default = True,
            model.created_at = time.time(),
            model.updated_at = time.time(),
            model.instrument_id = instrument.id,
            model.candles_durations = json.dumps([30, 60]),
            model.working_interval_sec = 1,
            model.analyzer_bid_times = json.dumps([{"purchase": 0, "time": 180}]),
            model.analyzer_deep = 2,
            model.analyzer_min_deep = 2,
            model.analyzer_prediction_expire = json.dumps([{"expire": 0, "history_duration": 0}]),
            model.analyzer_save_prediction_if_exists = False,
            model.trader_min_chance = 60,
            model.trader_min_repeats = 2,
            model.trader_delay_on_trend = 0,
            model.trader_max_count_orders_for_expiration_time = 1
            model.save()
