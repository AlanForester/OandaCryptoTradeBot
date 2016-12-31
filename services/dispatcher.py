import threading
import sys
import traceback


class Dispatcher(object):
    threads_count = 0
    worker_id = None

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def start_tracking(self):
        self.start_service("analyzer")
        while True:
            pass

    def start_service(self, service_name, params=None):
        self.threads_count += 1
        try:
            thread = None
            if service_name == "analyzer":
                thread = threading.Thread(target=self.test_thread, name=self.threads_count, args=(params,))

            thread.setDaemon(True)
            thread.run()

        except BaseException:
            ex_type, ex, tb = sys.exc_info()
            tb_list = traceback.extract_tb(tb)
            code = "Normal"
            if ex_type:
                code = str(ex_type.__name__)
            description = ""
            if ex:
                description = str(ex)
            print(self.threads_count, code, tb_list, description)

    def test_thread(self, params):
        d
        pass
