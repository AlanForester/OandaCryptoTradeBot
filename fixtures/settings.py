from models.setting import Setting
from models.instrument import Instrument
from fixtures.instruments import Instruments as InstrumentsFixture


class Settings:

    def up(self):
        setting = Setting()
        if setting.get_settings_count() == 0:
            instrument = Instrument().get_instrument_by_name("EUR_USD")
            if not instrument:
                InstrumentsFixture().up()
                setting.save(0)
