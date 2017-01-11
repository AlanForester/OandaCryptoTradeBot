import json
import sys
import threading
import time
import traceback

from services.history.checker import Checker

from models.task import Task
from providers.providers import Providers
from services.analyzer import Analyzer
from services.history.collector import Collector


class Dispatcher(object):
    threads = []
    worker_id = None

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def start_tracking(self):
        while True:
            pending_tasks = Task.get_pending(self.worker_id)
            for task in pending_tasks:
                thread = threading.Thread(target=self.start_service, args=(task,))
                thread.setDaemon(True)
                thread.start()
            time.sleep(1)

    def start_service(self, task):
        self.threads.append(task)

        service = None
        if task.service_name:
            Dispatcher.launch_task(task, len(self.threads))
            if task.service_name == "analyzer":
                service = Analyzer.run(task)
            if task.service_name == "collector":
                service = Collector(task)
            if task.service_name == "checker":
                service = Checker(task)
            Dispatcher.terminate_task(task)

        if not service:
            raise Exception("Launch service is undefined: " + task.service_name)

    @staticmethod
    def launch_task(task, thread):
        return task.launch(thread)

    @staticmethod
    def terminate_task(task):
        return task.terminate()
