from providers.providers import Providers


class Instrument:
    id = None
    instrument = None
    pip = None
    name = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                "(%s,%s,%s) ON CONFLICT (instrument) DO NOTHING RETURNING id;"
        cursor.execute(query, (self.instrument, self.pip, self.name))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    @staticmethod
    def model(raw=None):
        return Instrument(raw)

    @staticmethod
    def get_instruments_count():
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT COUNT(*) FROM instruments", [])
        return cursor.fetchone()[0]

    @staticmethod
    def get_instruments_dict(self):
        cursor = Providers.db().get_cursor()
        result_dict = {}
        for active_item in self.config.get_broker_instruments():
            cursor.execute("SELECT * FROM instruments WHERE instrument=%s", [active_item])
            row = cursor.fetchone()
            if row:
                result_dict[active_item] = row.id
        return result_dict

    @staticmethod
    def get_instrument_by_name(name: str):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM instruments WHERE instrument=%s", [name])
        row = cursor.fetchone()
        if row:
            return Instrument(row)

    @staticmethod
    def save_many(instruments: list):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                ",".join(v.__tuple_str() for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"
        cursor.execute(query)
        Providers.db().commit()

    def __tuple_str(self):
        return str((self.instrument, self.pip, self.name))