from fixtures.instruments import Instruments


class App(object):

    def __init__(self):
        App.execute_fixtures()

    @staticmethod
    def execute_fixtures():
        Instruments.up()

    @staticmethod
    def start():
        App()
