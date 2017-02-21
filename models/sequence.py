import json
import hashlib

from providers.providers import Providers


class Sequence:
    id = None
    json = []
    hash = ""
    duration = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO sequences (json, hash, duration) VALUES (%s,%s,%s) " \
                "ON CONFLICT (hash) DO UPDATE SET hash=EXCLUDED.hash RETURNING id"
        cursor.execute(query, (json.dumps(self.json), self.hash, self.duration))
        row = cursor.fetchone()
        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def get_duration(self):
        total_duration = 0
        for item in self.json:
            total_duration += item["duration"]
        return total_duration

    def get_hash(self):
        string = ""
        for item in self.json:
            string += str(item["duration"]) + str(item["change"])
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def __tuple_str(self):
        return str((json.dumps(self.json), self.get_hash(), self.get_duration()))

    @staticmethod
    def model(raw=None):
        return Sequence(raw)

    @staticmethod
    def save_many(sequences: list):
        cursor = Providers.db().get_cursor()
        query = 'INSERT INTO sequences (json, hash, duration) VALUES ' + \
                ','.join(v.__tuple_str() for v in sequences) + \
                ' ON CONFLICT (hash) DO UPDATE SET hash=EXCLUDED.hash RETURNING id,duration'
        cursor.execute(query)
        Providers.db().commit()
        res = cursor.fetchall()
        if res:
            return res
        return []

    @staticmethod
    def make(sequence_json):
        sequence = Sequence()
        sequence.json = sequence_json
        sequence.hash = sequence.get_hash()
        sequence.duration = sequence.get_duration()
        return sequence

    @staticmethod
    def get_sequences_json(task, candles_with_parents):
        """
        Преобразует массив свечей с родителями в массив последовательностей
        :returns sequences: [{'duration': 5, 'potential': 144}, {'duration': 5, 'potential': 144}]
        """
        out = list()
        for candle in candles_with_parents:
            sequence = list()
            obj = dict()
            obj["duration"] = candle["duration"]
            # obj["till_ts"] = candle["till_ts"]
            # obj["from_ts"] = candle["from_ts"]
            # obj["change_power"] = candle["change_power"]

            if task.setting.analyzer_capacity_type == "potential":
                obj["change"] = int(candle["change_power"]
                                    / task.setting.analyzer_capacity_granularity)
            else:
                obj["change"] = int((candle["change"] / task.setting.instrument.pip)
                                    / task.setting.analyzer_capacity_granularity)

            obj["granularity"] = task.setting.analyzer_capacity_granularity
            sequence.append(obj)
            out.append(sequence)
            if "parents" in candle:
                parents = Sequence.get_sequences_json(task, candle["parents"])
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out
