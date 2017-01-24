import json
import time

from providers.providers import Providers
from models.task import Task
from models.setting import Setting


class Tasks:
    @staticmethod
    def up(worker_id):
        config = Providers.config()
        service = config.launch_service
        if service:
            task = Task()
            task.user_id = 0  # TODO: Create real users
            task.setting_id = Setting.get_default().id
            task.worker_id = worker_id
            task.is_enabled = True
            task.service_name = service
            task.params = Tasks.get_params(service)
            task.start_at = time.time()
            task.save()

    @staticmethod
    def get_params(service):
        params = {}
        if service == "collector":
            params = {
                "start": int(time.time() - 86400),
                "end": int(time.time())
            }
        if service == "checker":
            params = {
                "start": int(time.time() - 86400),
                "end": int(time.time())
            }
        return params
