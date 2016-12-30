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
        finally:
            self.exit_handler()

    def exit_handler(self):
        ex_type, ex, tb = sys.exc_info()
        tb_list = traceback.extract_tb(tb)
        code = "Normal"
        if ex_type:
            code = str(ex_type.__name__)
        description = ""
        if ex:
            description = str(ex)
        Worker.terminate(self.worker, code, tb_list, description)
        if not Providers.config().debug:
            sys.exit(0)

    @staticmethod
    def start():
        App()
