from models.instrument import Instrument
from api.api import Api


class Instruments:

    @staticmethod
    def up():
        if Instrument().get_instruments_count() == 0:
            api = Api()
            instruments = api.get_instruments()
            out = []
            for instrument in instruments:
                out.append((
                    str(instrument["instrument"]),
                    instrument["pip"],
                    str(instrument["displayName"])
                ))
            if len(out) > 0:
                Instrument().save_many(out)
