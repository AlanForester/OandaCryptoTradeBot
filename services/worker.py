import time
import socket
import os
import json

from models.worker import Worker as WorkerModel


class Worker(object):

    @staticmethod
    def launch():
        model = WorkerModel()
        model.host_name = socket.gethostname()
        model.pid = os.getpid()
        model.launched_at = time.time()
        return model.save()

    @staticmethod
    def terminate(worker: WorkerModel, code, traceback, description):
        worker.terminated_code = code
        traceback_list = []
        for item in traceback:
            traceback_list.append({
                "filename": item.filename,
                "line_number": item.lineno,
                "method_name": item.name,
                "string": item.line
            })
        worker.terminated_traceback = json.dumps(traceback_list)
        worker.terminated_description = description
        worker.update_on_terminate()

