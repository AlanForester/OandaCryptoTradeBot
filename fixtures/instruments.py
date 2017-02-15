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
                model.not_working_time = [{
                    "start": {
                        "year": None,
                        "month": None,
                        "day": None,
                        "day_of_week": 4,
                        "hour": 22,
                        "minute": None,
                        "second": None
                    },
                    "end": {
                        "year": None,
                        "month": None,
                        "day": None,
                        "day_of_week": 6,
                        "hour": 22,
                        "minute": None,
                        "second": None
                    }
                }]
                out.append(model)
            if len(out) > 0:
                Instrument.save_many(out)
