from api.api import Api


class Analyzer:
    task = None
    quotation = None
    api = None

    def __init__(self, task):
        self.task = task
        self.api = Api()
        self.start_stream()

    def start_stream(self):
        self.api.quotations_stream(None, self.task.setting.instrument.instrument)
