from fixtures.instruments import Instruments
from fixtures.settings import Settings


class App(object):

    def __init__(self):
        App.execute_fixtures()

    @staticmethod
    def execute_fixtures():
        Instruments.up()
        Settings.up()

    @staticmethod
    def start():
        App()
