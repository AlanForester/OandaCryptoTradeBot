from models.coremodel import CoreModel


class Instrument(CoreModel):
    @staticmethod
    def model(raw=None):
        return _InstrumentModel(raw)

    def get_instruments_count(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM instruments", [])
        return cursor.fetchone()[0]

    def get_instruments_dict(self):
        cursor = self.db.get_cursor()
        result_dict = {}
        for active_item in self.config.get_broker_instruments():
            cursor.execute("SELECT * FROM instruments WHERE instrument=%s", [active_item])
            row = cursor.fetchone()
            if row:
                result_dict[active_item] = row.id
        return result_dict

    def get_instrument_by_name(self, name: str):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM instruments WHERE instrument=%s", [name])
        row = cursor.fetchone()
        if row:
            return Instrument.model(row)

    def save_many(self, instruments):
        cursor = self.db.get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                ",".join(str(v) for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"

        cursor.execute(query)
        self.db.commit()


class _InstrumentModel(object):
    id = None
    instrument = None
    pip = None
    name = None

    def __init__(self, raw=None):
        if raw:
            self.id = raw.id
            self.instrument = raw.instrument
            self.pip = raw.pip
            self.name = raw.name

