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
        self.quotation.instrument_id = self.task.setting.instrument_id
        ts_repeats = 0
        max_ts_repeats = 8
        # Последнее пришедшее значение стоимости котировки
        last_quotation_value = 0
        # Последнее зафиксированое время обработки
        last_fixed_ts = 0
        while True:
            # Фиксируем настоящее время обработчика итерации
            time_now = int(time.time())
            if not self.thread_stream:
                self.start_stream()

            if self.quotation.ts:
                if last_quotation_value != self.quotation.value:
                    last_quotation_value = self.quotation.value
                    ts_repeats = 1
                else:
                    ts_repeats += 1
                    if max_ts_repeats == ts_repeats:
                        self.terminate_stream()
                        ts_repeats = 1

                if last_fixed_ts < time_now:
                    last_fixed_ts = time_now

                    # Устанавливаем настоящее время для котировки и сохраняем
                    self.quotation.ts = time_now
                    self.quotation.save()

                    surplus_time = time_now % self.task.setting.working_interval_sec
                    if surplus_time == 0:
                        print(self.quotation.value, time_now)

            time.sleep(0.5)

    def start_stream(self):
        instrument_name = self.task.setting.instrument.instrument
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation, instrument_name))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        del self.thread_stream
