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
                "ON CONFLICT (hash) DO NOTHING RETURNING id"
        cursor.execute(query,
                       (json.dumps(self.json), self.hash, self.duration))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    @property
    def duration(self):
        total_duration = 0
        for item in self.json:
            total_duration += item["duration"]
        return total_duration

    @property
    def hash(self):
        return hashlib.md5(json.dumps(self.json).encode('utf-8')).hexdigest()

    def __tuple_str(self):
        return str((self.json, self.hash, self.duration))

    @staticmethod
    def model(raw=None):
        return Sequence(raw)

    @staticmethod
    def save(sequence):
        pattern = Sequence()
        pattern.json = sequence
        pattern.save()
        return pattern


