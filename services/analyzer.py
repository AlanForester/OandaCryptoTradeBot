import threading
import time

from api.api import Api
from models.quotation import Quotation


class Analyzer:
    task = None
    quotation = Quotation()
    api = None
    thread_stream = None

    def __init__(self, task):
        self.task = task
        self.api = Api()

        ts_repeats = 0
        max_ts_repeats = 4
        last_reception_ts = 0
        while True:
            if not self.thread_stream:
                self.start_stream()
            if self.quotation.ts:
                if last_reception_ts != self.quotation.ts:
                    last_reception_ts = self.quotation.ts
                    ts_repeats = 1
                else:
                    ts_repeats += 1
                    if max_ts_repeats == ts_repeats:
                        self.terminate_stream()
                        ts_repeats = 1
                        continue

                print(self.quotation.ts)
            time.sleep(1)

    def start_stream(self):
        instrument_name = self.task.setting.instrument.instrument
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation, instrument_name))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        del self.thread_stream
