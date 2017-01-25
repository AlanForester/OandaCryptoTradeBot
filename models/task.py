import json
import time

from providers.providers import Providers
from models.setting import Setting


class Task:
    id = None
    user_id = 0
    setting_id = 0
    worker_id = 0
    is_enabled = False
    service_name = ""
    params = {}
    status = {}
    thread = ""
    start_at = 0
    launched_at = 0
    stop_at = 0
    terminated_at = 0
    handled_exceptions = json.dumps([])

    _setting = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO tasks (user_id, setting_id, worker_id, is_enabled, service_name, params, status, thread, " \
                "start_at, launched_at, stop_at, terminated_at, handled_exceptions) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;"
        cursor.execute(query, [self.user_id, self.setting_id, self.worker_id, self.is_enabled, self.service_name,
                               json.dumps(self.params), json.dumps(self.status), self.thread, self.start_at,
                               self.launched_at, self.stop_at, self.terminated_at, self.handled_exceptions])
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    def update_status(self, key=None, value=None):
        if key is not None and value is not None:
            self.status[key] = value
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET status=%s WHERE id=%s"
        cursor.execute(query, [json.dumps(self.status), self.id])
        Providers.db().commit()

    def launch(self, thread):
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET launched_at=%s, thread=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (time.time(), thread, self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def terminate(self):
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET terminated_at=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (time.time(), self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def append_exception(self, json_exception):
        self.handled_exceptions.append(json_exception)
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET handled_exceptions=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (json.dumps(self.handled_exceptions), self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def get_param(self, param):
        res = None
        if param == "history_num":
            res = 0
        if param in self.params:
            res = self.params[param]
        return res

    def flush_setting(self):
        self._setting = None

    @property
    def setting(self):
        if not self._setting:
            self._setting = Setting.get_by_id(self.setting_id)
        return self._setting

    def __tuple_str(self):
        return str((self.user_id, self.setting_id, self.worker_id, self.is_enabled, self.service_name, self.params,
                    self.status, self.thread, self.start_at, self.launched_at, self.stop_at, self.terminated_at,
                    self.handled_exceptions))

    @staticmethod
    def model(raw=None):
        return Task(raw)

    @staticmethod
    def get_pending(worker_id):
        tasks = []
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM tasks WHERE worker_id=%s AND is_enabled=%s AND start_at<=%s AND launched_at=%s", [
            worker_id, True, time.time(), 0
        ])
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                tasks.append(Task(row))
        return tasks

    @staticmethod
    def terminate_on_emergency_exit(worker_id):
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET terminated_at=%s WHERE worker_id=%s AND terminated_at=%s;"
        cursor.execute(query, (time.time(), worker_id, 0))
        Providers.db().commit()
