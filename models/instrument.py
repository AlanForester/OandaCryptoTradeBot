import json

from providers.providers import Providers
from datetime import *


class Instrument:
    id = None
    instrument = ""
    pip = 0.0
    name = ""
    not_working_time = []

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name, not_working_time) VALUES " + \
                "(%s,%s,%s,%s) ON CONFLICT (instrument) DO NOTHING RETURNING id;"
        cursor.execute(query, (self.instrument, self.pip, self.name, json.dumps(self.not_working_time)))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    def is_works(self, ts: int):
        """ Метод проверяющий, входит ли таймштамп в нерабочее
        время данного инструмента

        :param int ts: Таймштамп который требуется проверить
        :return bool:
        """
        dt = datetime.fromtimestamp(ts)
        year = dt.year
        month = dt.month
        day = dt.day
        day_of_week = dt.weekday()
        hour = dt.hour
        minute = dt.minute
        second = dt.second

        is_work = True
        for interval_obj in self.not_working_time:
            if interval_obj["start"]["second"] and interval_obj["end"]["second"]:
                if interval_obj["start"]["second"] <= second <= interval_obj["end"]["second"]:
                    is_work = False
                else:
                    is_work = True

            if interval_obj["start"]["minute"] and interval_obj["end"]["minute"]:
                if interval_obj["start"]["minute"] <= minute <= interval_obj["end"]["minute"]:
                    is_work = False
                else:
                    is_work = True

            if interval_obj["start"]["hour"] and interval_obj["end"]["hour"]:
                if interval_obj["start"]["hour"] <= hour <= interval_obj["end"]["hour"]:
                    is_work = False
                else:
                    is_work = True

            if interval_obj["start"]["day"] and interval_obj["end"]["day"]:
                if interval_obj["start"]["day"] <= day <= interval_obj["end"]["day"]:
                    is_work = False
                else:
                    is_work = True
            else:
                if interval_obj["start"]["day_of_week"] and interval_obj["end"]["day_of_week"]:
                    if interval_obj["start"]["day_of_week"] <= day_of_week <= interval_obj["end"]["day_of_week"]:
                        is_work = False
                    else:
                        is_work = True

            if interval_obj["start"]["month"] and interval_obj["end"]["month"]:
                if interval_obj["start"]["month"] <= month <= interval_obj["end"]["month"]:
                    is_work = False
                else:
                    is_work = True

            if interval_obj["start"]["year"] and interval_obj["end"]["year"]:
                if interval_obj["start"]["year"] <= year <= interval_obj["end"]["year"]:
                    is_work = False
                else:
                    is_work = True

            if not is_work:
                break

        return is_work

    def __tuple_str(self):
        return str((self.instrument, self.pip, self.name, json.dumps(self.not_working_time)))

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
    def get_instrument_by_id(pk):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM instruments WHERE id=%s", [pk])
        row = cursor.fetchone()
        if row:
            return Instrument(row)

    @staticmethod
    def save_many(instruments: list):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO instruments (instrument, pip, name, not_working_time) VALUES " + \
                ",".join(v.__tuple_str() for v in instruments) + \
                " ON CONFLICT (instrument) DO NOTHING"
        cursor.execute(query)
        Providers.db().commit()
