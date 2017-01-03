from fixtures.instruments import Instruments
from fixtures.settings import Settings
from fixtures.tasks import Tasks


class Fixtures:

    @staticmethod
    def execute_fixtures():
        Instruments.up()
        #  TODO: Create default user - System and inject to Settings fixture
        Settings.up()

    @staticmethod
    def create_test_task(worker_id):
        Tasks.up(worker_id)
