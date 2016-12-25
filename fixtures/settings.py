from models.instrument import Instrument
from api.api import Api


class Settings:

    def up(self):
        if Instrument().get_actives_count() == 0:
            instruments = self.api.get_instruments()
            out = []
            for instrument in instruments:
                out.append((
                    str(instrument["instrument"]),
                    instrument["pip"],
                    str(instrument["displayName"])
                ))
            if len(out) > 0:
                Instrument().save_many(out)
