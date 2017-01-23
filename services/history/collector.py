import time

from api.api import Api
from models.quotation import Quotation


class Collector:
    quotation = Quotation()

    def __init__(self, task):
        self.task = task
        self.api = Api()
        self.quotation.instrument_id = self.task.setting.instrument_id
        self.api.get_history(self.task.setting.instrument, int(time.time())-86400, int(time.time()))
