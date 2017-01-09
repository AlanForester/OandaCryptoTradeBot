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
        Dispatcher.launch_task(task, len(self.threads))
        try:
            thread = None
            if task.service_name:
                if task.service_name == "analyzer":
                    thread = threading.Thread(target=Analyzer, args=(task, ), name=len(self.threads))
                if task.service_name == "collector":
                    thread = threading.Thread(target=Collector, args=(task,), name=len(self.threads))
                if task.service_name == "checker":
                    thread = threading.Thread(target=Checker, args=(task,), name=len(self.threads))

            if not thread:
                raise Exception("Launch service is undefined: " + task.service_name)

            thread.setDaemon(True)
            thread.run()

        finally:
            ex_type, ex, tb = sys.exc_info()
            tb_list = traceback.extract_tb(tb)
            code = "WithoutErrors"
            if ex_type:
                code = str(ex_type.__name__)
            description = ""
            if ex:
                description = str(ex)
            if Providers.config().debug:
                traceback.print_tb(tb)
                if ex_type:
                    print(code, description)

            Dispatcher.terminate_task(task, code, tb_list, description)

    @staticmethod
    def launch_task(task, thread):
        task.thread = thread
        return task.update_on_launch()

    @staticmethod
    def terminate_task(task, code: str, traceback, description):
        task.terminated_code = code
        traceback_list = []
        for item in traceback:
            traceback_list.append({
                "filename": item.filename,
                "line_number": item.lineno,
                "method_name": item.name,
                "string": item.line
            })
        task.terminated_traceback = json.dumps(traceback_list)
        task.terminated_description = description
        return task.update_on_terminate()
