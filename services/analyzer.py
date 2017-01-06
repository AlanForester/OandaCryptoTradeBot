import threading
import time
import json

from api.api import Api
from models.quotation import Quotation
from providers.providers import Providers


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

                surplus_time_5s = int(time.time()) % 5
                if surplus_time_5s == 0:
                    self.handle_quotation()

            time.sleep(1)

    def handle_quotation(self):
        self.save_quotation_to_cache()
        print(time.time())

    def save_quotation_to_cache(self):
        cache = Providers.cache()
        cache.setex(self.get_cache_quotation_key(), 5, self.quotation.value)

    def get_cache_quotation_key(self):
        return "quotation_" + str(self.task.setting_id) + "_" + str(time.time())

    def start_stream(self):
        instrument_name = self.task.setting.instrument.instrument
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation, instrument_name))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        del self.thread_stream
