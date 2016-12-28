from fixtures.instruments import Instruments
from fixtures.settings import Settings
import sys
import traceback


class App(object):

    def __init__(self):
        try:
            App.execute_fixtures()
            while True:
                pass
        finally:
            App.exit_handler()

    @staticmethod
    def exit_handler():
        ex_type, ex, tb = sys.exc_info()
        a = traceback.extract_tb(tb)
        del tb
        print('My application is ending!', tb)
        sys.exit(0)

    @staticmethod
    def execute_fixtures():
        Instruments.up()
        Settings.up()

    @staticmethod
    def start():
        App()
