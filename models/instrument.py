from models.coremodel import CoreModel
from mixins.providers import ProvidersMixin


class Instrument(ProvidersMixin):
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
            return _InstrumentModel(row)

    def save_many(self, instruments: list):
        cursor = self.db.get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                ",".join(str(v) for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"
        cursor.execute(query)
        self.db.commit()

    def save(self, instrument: str, pip: float, name: str):
        cursor = self.db.get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                "(%s,%s,%s)" \
                " ON CONFLICT (instrument) DO NOTHING RETURNING id;"
        cursor.execute(query, (instrument, pip, name))
        self.db.commit()
        return cursor.fetchone()


class _InstrumentModel(CoreModel):
    id = None
    instrument = None
    pip = None
    name = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())
