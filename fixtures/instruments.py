from models.instrument import Instrument
from api.api import Api


class Instruments:

    @staticmethod
    def up():
        if Instrument.get_instruments_count() == 0:
            api = Api()
            instruments = api.get_instruments()
            out = []
            for instrument in instruments:
                model = Instrument()
                model.instrument = str(instrument["instrument"])
                model.pip = instrument["pip"]
                model.name = str(instrument["displayName"])
                out.append(model)
            if len(out) > 0:
                Instrument.save_many(out)
