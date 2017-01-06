import sys
import traceback
import time
import socket
import os
import json

from fixtures.fixtures import Fixtures
from models.worker import Worker
from providers.providers import Providers
from services.dispatcher import Dispatcher
from models.task import Task


class App(object):
    worker = None

    def __init__(self):
        self.launch()
        try:
            if self.worker:
                Fixtures.execute_fixtures()
                Fixtures.create_test_task(self.worker.id)
                Dispatcher(self.worker.id).start_tracking()
        finally:
            ex_type, ex, tb = sys.exc_info()
            tb_list = traceback.extract_tb(tb)
            code = "WithoutErrors"
            if ex_type:
                code = str(ex_type.__name__)
            description = ""
            if ex:
                description = str(ex)
            if self.worker:
                self.terminate(code, tb_list, description)
            if Providers.config().debug:
                traceback.print_tb(tb)
                if ex_type:
                    print(code, description)
            sys.exit(0)

    def launch(self):
        self.worker = Worker()
        self.worker.host_name = socket.gethostname()
        self.worker.pid = os.getpid()
        self.worker.launched_at = time.time()
        return self.worker.save()

    def terminate(self, code: str, traceback, description):
        self.worker.terminated_code = code
        traceback_list = []
        for item in traceback:
            traceback_list.append({
                "filename": item.filename,
                "line_number": item.lineno,
                "method_name": item.name,
                "string": item.line
            })
        self.worker.terminated_traceback = json.dumps(traceback_list)
        self.worker.terminated_description = description
        if code == "KeyboardInterrupt":
            Task.update_on_terminate_keyboard_interrupt(self.worker.id, self.worker.terminated_code, [], "")
        self.worker.update_on_terminate()

    @staticmethod
    def start():
        App()
