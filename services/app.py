from fixtures.instruments import Instruments
from fixtures.settings import Settings
import sys
import traceback


class App(object):

    def __init__(self):
        try:
            App.execute_fixtures()
            while True:
                d
                pass
        finally:
            App.exit_handler()

    @staticmethod
    def exit_handler():
        ex_type, ex, tb = sys.exc_info()
        a = traceback.extract_tb(tb)

        print('My application is ending!', a[0].filename, a[0].lineno,a[0].name,a[0].line, str(ex_type.__name__), str(ex))
        # for t in a:
        #     print(t)
        sys.exit(0)

    @staticmethod
    def execute_fixtures():
        Instruments.up()
        Settings.up()

    @staticmethod
    def start():
        App()
