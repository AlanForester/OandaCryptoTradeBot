import threading
import sys
import traceback
import time

from providers.providers import Providers


class ExThread(threading.Thread):
    task = None

    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)

        except BaseException:
            ex_type, ex, tb = sys.exc_info()
            tb_list = traceback.extract_tb(tb)
            code = "WithoutErrors"
            if ex_type:
                code = str(ex_type.__name__)
            description = ""
            if ex:
                description = str(ex)

            if self.task:
                self.terminate(code, tb_list, description)

            if Providers.config().debug:
                traceback.print_tb(tb)
                if ex_type:
                    print(code, description)

        finally:
            del self._target, self._args, self._kwargs

    def terminate(self, code: str, traceback, description):
        traceback_list = []
        for item in traceback:
            traceback_list.append({
                "filename": item.filename,
                "line_number": item.lineno,
                "method_name": item.name,
                "string": item.line
            })

        terminate_log = {
            "time": time.time(),
            "code": code,
            "traceback": traceback_list,
            "description": description
        }
        self.task.append_exception(terminate_log)

    @staticmethod
    def wait_threads(threads, num):
        while len(threads) > num:
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)

