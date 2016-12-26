import time
import json

from models.setting import Setting
from models.instrument import Instrument
from fixtures.instruments import Instruments as InstrumentsFixture


class Settings:
    @staticmethod
    def up():
        setting = Setting()
        if setting.get_settings_count() == 0:
            instrument = Instrument().get_instrument_by_name("EUR_USD")
            if not instrument:
                InstrumentsFixture().up()
            setting.save(
                name="Default",
                is_default=True,
                created_at=time.time(),
                updated_at=time.time(),
                instrument_id=instrument.id,
                analyzer_bid_times=json.dumps([{"purchase": 0, "time": 180}]),
                analyzer_deep=2,
                analyzer_min_deep=2,
                analyzer_prediction_expire=json.dumps([{"expire": 0, "history_duration": 0}]),
                analyzer_save_prediction_if_exists=False,
                collector_candles_durations=json.dumps([30, 60]),
                collector_working_interval_sec=1,
                trader_min_chance=60,
                trader_min_repeats=2,
                trader_delay_on_trend=0,
                trader_max_count_orders_for_expiration_time=1
            )
