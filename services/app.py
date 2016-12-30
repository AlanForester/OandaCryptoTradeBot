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


class App(object):
    worker = None

    def __init__(self):
        try:
            Fixtures.execute_fixtures()
            self.launch()
            dispatcher = Dispatcher(self.worker.id)
            dispatcher.start_tracking()
        finally:
            ex_type, ex, tb = sys.exc_info()
            tb_list = traceback.extract_tb(tb)
            code = "Normal"
            if ex_type:
                code = str(ex_type.__name__)
            description = ""
            if ex:
                description = str(ex)
            self.terminate(code, tb_list, description)
            if not Providers.config().debug:
                sys.exit(0)

    def launch(self):
        self.worker = Worker()
        self.worker.host_name = socket.gethostname()
        self.worker.pid = os.getpid()
        self.worker.launched_at = time.time()
        return self.worker.save()

    def terminate(self, code, traceback, description):
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
        self.worker.update_on_terminate()

    @staticmethod
    def start():
        App()

