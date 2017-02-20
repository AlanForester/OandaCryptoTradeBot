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
from providers.providers import Providers


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
        self.admissions = [round(i*self.task.setting.analyzer_capacity_granularity, 6) for i in range(-1000, 1001)]

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
        # candles = Candle.get_last(self.quotation.ts, self.task.setting.analyzer_deep,
        #                           self.task.setting.instrument_id, "parent")
        candles = Candle.get_last_with_nesting(self.quotation.ts, self.task.setting.analyzer_deep,
                                               self.task.setting.instrument_id, self.task.setting.candles_durations,
                                               "parent")
        # Получаем разные вариации последовательностей c глубиной вхождения
        sequences = Sequence.get_sequences_json(self.task, candles, self.admissions)

        sequences_models = []
        for sequence in sequences:
            if len(sequence) >= self.task.setting.analyzer_min_deep:
                sequences_models.append(Sequence.make(sequence))

        if len(sequences_models) > 0:
            sequences_ret = Sequence.save_many(sequences_models)
            patterns_models = []
            predictions_models = []
            for time_bid in self.task.setting.analyzer_bid_times:
                for seq in sequences_ret:
                    prediction = Prediction.make(self.task, time_bid, self.quotation, seq)
                    # Проверка оставшегося времени до ставки
                    if prediction.time_to_expiration >= (time_bid['time'] - time_bid['admission']):
                        pattern = Pattern.make(self.task, seq, time_bid, self.quotation)
                        predictions_models.append(prediction)
                        patterns_models.append(pattern)

            if len(patterns_models) > 0:
                patterns_ids = Pattern.save_many(patterns_models)
                i = 0
                for pat_rec in patterns_ids:
                    predictions_models[i].pattern_id = pat_rec.id

                    if Controller.check_on_make_signal(self.task, pat_rec, predictions_models[i], self.quotation):
                        # Проверка условий вероятности при создании сигнала
                        direction = Signaler.check(self.task, pat_rec)
                        if direction:
                            Signaler.make_and_save(self.task, direction, pat_rec, predictions_models[i])
                            if self.task.get_param("history_num", 0) > 0:
                                signals_count = self.task.get_status("checker_signals_count", 0)
                                self.task.update_status("checker_signals_count", signals_count + 1)

                    self.task.storage.insert_prediction(predictions_models[i])
                    i += 1

    def save_candles(self):
        candles_durations = self.task.setting.candles_durations
        Candle.save_through_pg(self.quotation.ts, candles_durations, self.task.setting.instrument_id)

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

                # Перезагружаем настройки
                task.flush_setting()

                # Проверка на рабочее время инструмента
                if not task.setting.instrument.is_works(analyzer.quotation.ts):
                    print("Рынок не работает")
                    save_handle = False
                    analysis_handle = False

                # Защита от повторного срабатывания секунды
                if last_fixed_ts < time_now and not wait:
                    last_fixed_ts = time_now

                    check_expired_predictions_thread = ExThread(target=Controller.check_expired_predictions,
                                                                args=(task, analyzer.quotation))
                    check_expired_predictions_thread.task = task
                    check_expired_predictions_thread.start()

                    check_expired_signals = ExThread(target=Controller.update_expired_signals,
                                                     args=(task, analyzer.quotation))
                    check_expired_signals.task = task
                    check_expired_signals.start()

                    if save_handle:
                        # Устанавливаем настоящее время для котировки и сохраняем
                        # Providers.telebot().send_quotation(task.setting.instrument.instrument + ": "
                        #                                   + str(analyzer.quotation.value))
                        analyzer.quotation.ts = time_now
                        analyzer.quotation.save()
                        print(analyzer.quotation.value)

                        # Сохраняем свечи
                        analyzer.save_candles()

                        # Обновляем параметры стоимости прогнозов
                        Prediction.calculation_cost_for_topical(task, analyzer.quotation)

                        save_handle = False

                    if analysis_handle:
                        # Запускаем поток на анализ
                        # analysis_thread = ExThread(target=analyzer.do_analysis)
                        # analysis_thread.daemon = True
                        # analysis_thread.task = task
                        # analysis_thread.start()
                        # Запускаем поток на проверку прогнозов

                        analysis_handle = False

            time.sleep(0.5)
