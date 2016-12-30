import time
import json

from providers.providers import Providers


class Worker:
    id = None
    host_name = ""
    pid = 0
    launched_at = 0
    terminated_at = 0
    terminated_code = ""
    terminated_traceback = json.dumps({})
    terminated_description = ""

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO workers (host_name, pid, launched_at, terminated_at, " \
                "terminated_code, terminated_traceback, terminated_description) VALUES " + \
                "(%s,%s,%s,%s,%s,%s,%s) RETURNING id;"
        cursor.execute(query, (self.host_name, self.pid, self.launched_at, self.terminated_at, self.terminated_code,
                               self.terminated_traceback, self.terminated_description))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    def update_on_terminate(self):
        cursor = Providers.db().get_cursor()
        query = "UPDATE workers SET terminated_at=%s, terminated_code=%s, terminated_traceback=%s, " \
                "terminated_description=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (time.time(), self.terminated_code, self.terminated_traceback,
                               self.terminated_description, self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def __tuple_str(self):
        return str((self.host_name, self.pid, self.launched_at, self.terminated_at,
                    self.terminated_code, self.terminated_traceback, self.terminated_description))

    @staticmethod
    def model(raw=None):
        return Worker(raw)
