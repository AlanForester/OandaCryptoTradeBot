import threading
import time

from api.api import Api
from models.quotation import Quotation
from models.candle import Candle
from helpers.fibonacci import FibonacciHelper
from models.pattern import Pattern


class Analyzer:
    task = None
    quotation = Quotation()
    api = None
    thread_stream = None
    admissions = None

    def __init__(self, task, is_history_check=False):
        self.is_history_check = is_history_check
        self.task = task
        self.api = Api()
        self.quotation.instrument_id = self.task.setting.instrument_id
        self.admissions = FibonacciHelper.get_uniq_unsigned_array(25)

    def start_stream(self):
        instrument_name = self.task.setting.instrument.instrument
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation, instrument_name))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        self.api.stream.disconnect()
        del self.thread_stream

    def do_analysis(self):
        """Метод подготовки прогнозов"""
        """Получаем свечи разной длинны с их родителями"""
        candles = Candle.get_last_with_parent(self.quotation.ts, self.task.setting.analyzer_deep,
                                              self.task.setting.instrument_id)
        """Получаем разные вариации последовательностей c глубиной вхождения"""
        sequences = Pattern.get_sequences(candles, self.admissions)

        # TODO: Проверить admission при тестировании выбирается всегда паттерн с 0 силой
        for sequence in sequences:
            if len(sequence) >= self.task.setting.analyzer_min_deep:
                for time_bid in self.task.setting.analyzer_bid_times:
                    """Заворачиваем в треды проверки с дальнейшим кешированием прогноза"""
                    print(time_bid, sequence)
                    # cache_thread = threading.Thread(target=self.handle_prediction, args=(time_bid, sequence,))
                    # cache_thread.daemon = True
                    # cache_thread.start()
                    # print "Predictor worked at", time.time() - now, "s"

    def handle_prediction(self, time_bid, sequence):
        # cache_thread = threading.Thread(target=self.cache_prediction, args=(time_bid, quotation,
        #                                                                     sequence,))
        # cache_thread.daemon = True
        # cache_thread.start()
        pass

    def save_candles(self):
        candles = []
        candles_durations = self.task.setting.candles_durations
        for duration in candles_durations:
            candle = Candle.make(self.quotation.ts, duration, self.task.setting.instrument_id)
            candles.append(candle)
        Candle.save_many(candles)

    @staticmethod
    def run(task):
        analyzer = Analyzer(task)
        value_repeats = 0
        max_value_repeats = 16
        # Последнее пришедшее значение стоимости котировки
        last_quotation_value = 0
        # Последнее зафиксированое время обработки
        last_fixed_ts = 0
        while True:
            # Фиксируем настоящее время обработчика итерации
            time_now = int(time.time())
            if not analyzer.thread_stream:
                analyzer.start_stream()

            if analyzer.quotation.value:
                # Счетчик устаревших данных котировок
                if last_quotation_value != analyzer.quotation.value:
                    last_quotation_value = analyzer.quotation.value
                    value_repeats = 1
                else:
                    value_repeats += 1
                    if max_value_repeats == value_repeats:
                        analyzer.terminate_stream()
                        value_repeats = 1

                # Защита от повторного срабатывания секунды
                if last_fixed_ts < time_now:
                    last_fixed_ts = time_now

                    # Устанавливаем настоящее время для котировки и сохраняем
                    analyzer.quotation.ts = time_now
                    analyzer.quotation.save()

                    # Проверка возможности начать работу согласно временному рабочему интервалу в конфигурации
                    surplus_time = time_now % analyzer.task.setting.working_interval_sec
                    if surplus_time == 0:
                        print(vars(analyzer.quotation))
                        analyzer.save_candles()
                        analyzer.do_analysis()

            time.sleep(0.5)


