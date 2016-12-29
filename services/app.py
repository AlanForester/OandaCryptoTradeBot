import sys
import traceback

from fixtures.fixtures import Fixtures
from services.worker import Worker
from providers.providers import Providers


class App(object):
    worker = None

    def __init__(self):
        try:
            Fixtures.execute_fixtures()
            self.worker = Worker.launch()
            while True:
                d
                pass
        finally:
            self.exit_handler()

    def exit_handler(self):
        ex_type, ex, tb = sys.exc_info()
        tb_list = traceback.extract_tb(tb)
        Worker.terminate(self.worker, str(ex_type.__name__), tb_list, str(ex))
        if not Providers.debug():
            sys.exit(0)

    @staticmethod
    def start():
        App()
