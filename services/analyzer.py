import threading
import time

from api.api import Api
from models.quotation import Quotation
from providers.providers import Providers
from models.candle import Candle


class Analyzer:
    task = None
    quotation = Quotation()
    api = None
    thread_stream = None

    def __init__(self, task):
        self.task = task
        self.api = Api()
        self.quotation.instrument_id = self.task.setting.instrument_id
        value_repeats = 0
        max_value_repeats = 16
        # Последнее пришедшее значение стоимости котировки
        last_quotation_value = 0
        # Последнее зафиксированое время обработки
        last_fixed_ts = 0
        while True:
            # Фиксируем настоящее время обработчика итерации
            time_now = int(time.time())
            if not self.thread_stream:
                self.start_stream()

            if self.quotation.value:
                # Счетчик устаревших данных котировок
                if last_quotation_value != self.quotation.value:
                    last_quotation_value = self.quotation.value
                    value_repeats = 1
                else:
                    value_repeats += 1
                    if max_value_repeats == value_repeats:
                        self.terminate_stream()
                        value_repeats = 1

                # Защита от повторного срабатывания секунды
                if last_fixed_ts < time_now:
                    last_fixed_ts = time_now

                    # Устанавливаем настоящее время для котировки и сохраняем
                    self.quotation.ts = time_now
                    self.quotation.save()

                    # Проверка возможности начать работу согласно временному рабочему интервалу в конфигурации
                    surplus_time = time_now % self.task.setting.working_interval_sec
                    if surplus_time == 0:
                        Analyzer.save_candles(self.quotation, self.task.setting)

            time.sleep(0.5)

    def start_stream(self):
        instrument_name = self.task.setting.instrument.instrument
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation, instrument_name))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        self.api.stream.disconnect()
        del self.thread_stream

    @staticmethod
    def save_candles(quotation, setting):
        candles = []
        candles_durations = setting.candles_durations
        for duration in candles_durations:
            candle = Candle.make(quotation.ts, duration, setting.instrument_id)
            candles.append(candle)
        Candle.save_many(candles)
