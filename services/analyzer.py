import threading
import time

from api.api import Api
from models.quotation import Quotation
from models.candle import Candle
from helpers.fibonacci import FibonacciHelper


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
        self.thread_stream = threading.Thread(target=self.api.quotations_stream, args=(self.quotation,
                                                                                       self.task.setting.instrument))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        self.api.stream.disconnect()
        del self.thread_stream

    def do_analysis(self):
        """Метод подготовки прогнозов"""
        # Получаем свечи разной длинны с их родителями
        candles = Candle.get_last_with_parent(self.quotation.ts, self.task.setting.analyzer_deep,
                                              self.task.setting.instrument_id)
        # Получаем разные вариации последовательностей c глубиной вхождения
        sequences = self.get_sequences(candles)

        # TODO: Проверить admission при тестировании выбирается всегда паттерн с 0 силой
        for sequence in sequences:
            if len(sequence) >= self.task.setting.analyzer_min_deep:
                for time_bid in self.task.setting.analyzer_bid_times:
                    # Заворачиваем в треды проверки с дальнейшим кешированием и проверкой прогноза
                    cache_thread = threading.Thread(target=self.handle_prediction, args=(time_bid, sequence,))
                    cache_thread.daemon = True
                    cache_thread.start()

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

    def get_sequences(self, candles_with_parents):
        """
        Преобразует массив свечей с родителями в массив последовательностей
        :returns sequences: [{'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 10, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 15, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 30, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 60, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 120, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 300, 'admission': 34}]
        [{'duration': 10, 'admission': 144}]....
        """
        out = list()
        for candle in candles_with_parents:
            sequence = list()
            obj = dict()
            obj["duration"] = candle["duration"]
            # obj["till_ts"] = candle["till_ts"]
            # obj["from_ts"] = candle["from_ts"]
            # obj["change_power"] = candle["change_power"]
            for admission in self.admissions:
                if candle["change_power"] <= admission:
                    obj["admission"] = admission
                    break

            if not "admission" in obj:
                obj["admission"] = int(candle["change_power"] / 100) * 100

            sequence.append(obj)
            out.append(sequence)
            if "parents" in candle:
                parents = self.get_sequences(candle["parents"])
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out

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


