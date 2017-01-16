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
        return hashlib.md5(json.dumps(self.json).encode('utf-8')).hexdigest()

    def __tuple_str(self):
        return str((self.json, self.get_hash(), self.get_duration()))

    @staticmethod
    def model(raw=None):
        return Sequence(raw)

    @staticmethod
    def save_and_get(sequence_json):
        sequence = Sequence()
        sequence.json = sequence_json
        sequence.hash = sequence.get_hash()
        sequence.duration = sequence.get_duration()
        sequence.save()
        return sequence


