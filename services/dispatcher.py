import threading
import sys
import traceback

from providers.providers import Providers
from models.task import Task


class Dispatcher(object):
    threads = []
    worker_id = None

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def start_tracking(self):
        pending_tasks = Task.get_pending(self.worker_id)
        for task in pending_tasks:
            self.start_service(task.service_name)
        while True:
            pass

    def start_service(self, service_name, params=None):
        self.threads.append()
        try:
            thread = None
            if service_name == "analyzer":
                thread = threading.Thread(target=self.test_thread, name=len(self.threads), args=(params,))

            thread.setDaemon(True)
            thread.run()

        except BaseException:
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
            # print(self.threads_count, code, tb_list, description)
        finally:
            print("Fina;l")

    def test_thread(self, params):
        pass
