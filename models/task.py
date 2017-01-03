import json
import time

from providers.providers import Providers


class Task:
    id = None
    user_id = 0
    setting_id = 0
    worker_id = 0
    is_enabled = False
    service_name = ""
    params = json.dumps({})
    status = json.dumps({})
    thread = ""
    start_at = 0
    launched_at = 0
    stop_at = 0
    terminated_at = 0
    terminated_code = ""
    terminated_traceback = json.dumps([])
    terminated_description = ""

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        query = "INSERT INTO tasks (user_id, setting_id, worker_id, is_enabled, service_name, params, status, thread, " \
                "start_at, launched_at, stop_at, terminated_at, terminated_code, terminated_traceback, " \
                "terminated_description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;"
        cursor.execute(query, [self.user_id, self.setting_id, self.worker_id, self.is_enabled, self.service_name,
                               self.params, self.status, self.thread, self.start_at, self.launched_at, self.stop_at,
                               self.terminated_at, self.terminated_code, self.terminated_traceback,
                               self.terminated_description])
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            return self

    def update_on_launch(self):
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET launched_at=%s, thread=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (time.time(), self.thread, self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def update_on_terminate(self):
        cursor = Providers.db().get_cursor()
        query = "UPDATE tasks SET terminated_at=%s, terminated_code=%s, terminated_traceback=%s, " \
                "terminated_description=%s WHERE id=%s RETURNING id;"
        cursor.execute(query, (time.time(), self.terminated_code, self.terminated_traceback,
                               self.terminated_description, self.id))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            return self

    def __tuple_str(self):
        return str((self.user_id, self.setting_id, self.worker_id, self.is_enabled, self.service_name, self.params,
                    self.status, self.thread, self.start_at, self.launched_at, self.stop_at, self.terminated_at,
                    self.terminated_code, self.terminated_traceback, self.terminated_description))

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
