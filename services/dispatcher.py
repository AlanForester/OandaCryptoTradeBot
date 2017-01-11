import time

from services.history.checker import Checker
from models.task import Task
from services.analyzer import Analyzer
from services.history.collector import Collector
from helpers.exthread import ExThread


class Dispatcher(object):
    threads = []
    worker_id = None

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def start_tracking(self):
        while True:
            pending_tasks = Task.get_pending(self.worker_id)
            for task in pending_tasks:
                thread = ExThread(target=self.start_service, args=(task,))
                thread.setDaemon(True)
                thread.start()
            time.sleep(1)

    def start_service(self, task):
        self.threads.append(task)

        thread = None
        try:
            if task.service_name == "analyzer":
                thread = ExThread(target=Analyzer.run, args=(task, ), name=len(self.threads))
            if task.service_name == "collector":
                thread = ExThread(target=Collector, args=(task,), name=len(self.threads))
            if task.service_name == "checker":
                thread = ExThread(target=Checker, args=(task,), name=len(self.threads))

            if thread:
                self.launch_task(task, len(self.threads))
                thread.task = task
                thread.run()
        finally:
            self.terminate_task(task)

        if not thread:
            raise Exception("Launch service is undefined: " + task.service_name)

    @staticmethod
    def launch_task(task, thread):
        return task.launch(thread)

    @staticmethod
    def terminate_task(task):
        return task.terminate()
