import time

from api.api import Api
from models.quotation import Quotation
from models.candle import Candle
from models.sequence import Sequence
from models.prediction import Prediction
from models.pattern import Pattern
from services.controller import Controller
from services.signaler import Signaler
from helpers.fibonacci import FibonacciHelper
from helpers.exthread import ExThread


class Analyzer:
    task = None
    quotation = Quotation()
    api = None
    thread_stream = None
    admissions = None

    def __init__(self, task):
        self.task = task
        self.api = Api()
        self.quotation.instrument_id = self.task.setting.instrument_id
        self.admissions = FibonacciHelper.get_uniq_unsigned_array(25)

    def start_stream(self):
        self.thread_stream = ExThread(target=self.api.quotations_stream, args=(self.quotation,
                                                                               self.task.setting.instrument))
        self.thread_stream.setDaemon(True)
        self.thread_stream.start()

    def terminate_stream(self):
        self.api.stream.disconnect()
        del self.thread_stream

    def do_analysis(self):
        """Метод подготовки прогнозов"""
        # Получаем свечи разной длинны
        candles = Candle.get_last(self.quotation.ts, self.task.setting.analyzer_deep,
                                  self.task.setting.instrument_id, "parent")

        # Получаем разные вариации последовательностей c глубиной вхождения
        sequences = Sequence.get_sequences_json(candles, self.admissions)

        for sequence in sequences:
            if len(sequence) >= self.task.setting.analyzer_min_deep:
                for time_bid in self.task.setting.analyzer_bid_times:
                    # Заворачиваем в треды проверки с дальнейшим кешированием и проверкой прогноза
                    cache_thread = ExThread(target=self.handle_prediction, args=(time_bid, sequence))
                    cache_thread.daemon = True
                    cache_thread.task = self.task
                    cache_thread.start()

    def handle_prediction(self, time_bid, sequence_json):
        # Получаем свечу и сразу ее сохраняем
        sequence = Sequence.save_and_get(sequence_json)
        # Предварительно собираем прогноз
        prediction = Prediction.make(self.task, time_bid, self.quotation, sequence)
        if Controller.check_on_save_pattern():
            pattern = Pattern.upsert(self.task, sequence, time_bid)
            prediction.pattern_id = pattern.id
            prediction.save()
            # Проверка условий вероятности при создании сигнала
            direction = Signaler.check(self.task, pattern)
            if direction:
                Signaler.make_and_save(self.task, direction, pattern, prediction)
        else:
            prediction.save()

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
        save_handle = False
        analysis_handle = False
        value_repeats = 0
        max_value_repeats = 30
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
                    wait = False
                    value_repeats = 1
                else:
                    wait = True
                    value_repeats += 1
                    if max_value_repeats == value_repeats:
                        analyzer.terminate_stream()
                        value_repeats = 1

                # Проверка возможности начать работу коллектора
                save_surplus_time = time_now % analyzer.task.setting.analyzer_collect_interval_sec
                if save_surplus_time == 0:
                    save_handle = True
                # Проверка возможности начать работу анализатору
                surplus_time = time_now % analyzer.task.setting.analyzer_working_interval_sec
                if surplus_time == 0:
                    analysis_handle = True

                # Защита от повторного срабатывания секунды
                if last_fixed_ts < time_now and not wait:
                    last_fixed_ts = time_now

                    check_expired_predictions_thread = ExThread(target=Controller.check_expired_predictions,
                                                                args=(task, analyzer.quotation))
                    check_expired_predictions_thread.task = task
                    check_expired_predictions_thread.start()

                    if save_handle:
                        # Устанавливаем настоящее время для котировки и сохраняем
                        analyzer.quotation.ts = time_now
                        analyzer.quotation.save()

                        # Сохраняем свечи
                        analyzer.save_candles()

                        # Обновляем параметры стоимости прогнозов
                        Prediction.calculation_cost_for_topical(analyzer.quotation, analyzer.task.setting.id)

                        save_handle = False

                    if analysis_handle:
                        # Перезагружаем настройки
                        task.flush_setting()

                        # Запускаем поток на анализ
                        analysis_thread = ExThread(target=analyzer.do_analysis)
                        analysis_thread.daemon = True
                        analysis_thread.task = task
                        analysis_thread.start()
                        # Запускаем поток на проверку прогнозов

                        analysis_handle = False

            time.sleep(0.5)
