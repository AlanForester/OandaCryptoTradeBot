from models.coremodel import CoreModel


class Instrument(CoreModel):
    table_name = 'instruments'

    @property
    def id(self):
        return self.__raw_data.id

    @property
    def instrument(self):
        return self.__raw_data.instrument

    @property
    def pip(self):
        return self.__raw_data.pip

    @property
    def name(self):
        return self.__raw_data.name

    def get_actives_count(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM instruments", [])
        return cursor.fetchone()[0]

    def get_actives_dict(self):
        cursor = self.db.get_cursor()
        result_dict = {}
        for active_item in self.config.get_broker_instruments():
            cursor.execute("SELECT * FROM instruments WHERE instrument=%s", [active_item])
            row = cursor.fetchone()
            if row:
                result_dict[active_item] = row.id
        return result_dict

    def save_many(self, instruments: list(tuple)):
        cursor = self.db.get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name) VALUES " + \
                ",".join(str(v) for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"

        cursor.execute(query)
        self.db.commit()
