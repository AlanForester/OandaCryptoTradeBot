import json

from providers.providers import Providers


class Task:
    id = None
    user_id = 0
    setting_id = 0
    worker_id = 0
    is_enabled = False
    service_name = ""
    params = json.dumps({})
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

    def __tuple_str(self):
        return str((self.user_id, self.setting_id, self.worker_id, self.is_enabled, self.service_name, self.params,
                    self.thread, self.start_at, self.launched_at, self.stop_at, self.terminated_at,
                    self.terminated_code, self.terminated_traceback, self.terminated_description))

    @staticmethod
    def model(raw=None):
        return Task(raw)
