from fixtures.instruments import Instruments
from fixtures.settings import Settings


class Fixtures:
    @staticmethod
    def execute_fixtures():
        Instruments.up()
        Settings.up()
