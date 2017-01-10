import threading
import time

from api.api import Api
from models.quotation import Quotation
from models.candle import Candle
from providers.providers import Providers
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
        candles = self.get_last_candles_with_parent(self.quotation.ts, self.task.settings.analyzer_deep)
        """Получаем разные вариации последовательностей c глубиной вхождения"""
        sequences = self.get_sequences_patterns(candles)

        # TODO: Проверить admission при тестировании выбирается всегда паттерн с 0 силой
        for sequence in sequences:
            if len(sequence) >= self.task.settings.analyzer_min_deep:
                for time_bid in self.task.settings.analyzer_bid_times:
                    """Заворачиваем в треды проверки с дальнейшим кешированием прогноза"""
                    cache_thread = threading.Thread(target=Analyzer.save_prediction, args=(time_bid, self.quotation,
                                                                                           sequence,))
                    cache_thread.daemon = True
                    cache_thread.start()
                    # print "Predictor worked at", time.time() - now, "s"

    def get_last_candles_with_parent(self, till_ts, deep):
        """Достаем похожие по длительности свечи в рекурсивной функции
        Вложенность обеспечивается свойством parent
        За уровень вложенности отвечает параметр deep(Глубина)"""
        out = []
        cursor = Providers.db().get_cursor()
        if deep > 0:
            deep -= 1
            """Получаем последний доступный ts свечи"""
            last_candle_till = self.get_last_candle_till_ts(till_ts)

            if last_candle_till:
                """Достаем свечи любой длины за время"""
                cursor.execute(
                    "SELECT change_power,duration,till_ts,from_ts FROM "
                    "candles WHERE till_ts=%s AND instrument_id=%s",
                    [last_candle_till, self.task.setting.instrument_id])
                rows = cursor.fetchall()
                for row in rows:
                    model = dict()
                    model["change_power"] = row.change_power
                    model["duration"] = row.duration
                    # model["till_ts"] = row[2]
                    # model["from_ts"] = row[3]
                    if deep > 0:
                        """Ищем родителей по любой длинне"""
                        model["parents"] = self.get_last_candles_with_parent(row.till_ts, deep)
                    out.append(model)
        return out

    def get_last_candle_till_ts(self, till_ts):
        """Достает время последней свечи
        Без этой проверки свеча может не
        существовать"""
        cursor = Providers.db().get_cursor()
        cursor.execute(
            "SELECT till_ts FROM candles WHERE till_ts<=%s AND instrument_id=%s ORDER BY till_ts DESC LIMIT 1",
            [till_ts, self.task.setting.instrument_id])
        row = cursor.fetchone()
        if row:
            return row.till_ts
        return False

    def get_sequences_patterns(self, candles_with_parents):
        """
        Преобразует массив свечей с родителями в массив последовательностей

        :param candles_with_parents:
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
                parents = self.get_sequences_patterns(candle["parents"])
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out

    @staticmethod
    def run(task):
        model = Analyzer(task)
        value_repeats = 0
        max_value_repeats = 16
        # Последнее пришедшее значение стоимости котировки
        last_quotation_value = 0
        # Последнее зафиксированое время обработки
        last_fixed_ts = 0
        while True:
            # Фиксируем настоящее время обработчика итерации
            time_now = int(time.time())
            if not model.thread_stream:
                model.start_stream()

            print(vars(model.quotation))
            if model.quotation.value:
                # Счетчик устаревших данных котировок
                if last_quotation_value != model.quotation.value:
                    last_quotation_value = model.quotation.value
                    value_repeats = 1
                else:
                    value_repeats += 1
                    if max_value_repeats == value_repeats:
                        model.terminate_stream()
                        value_repeats = 1

                # Защита от повторного срабатывания секунды
                if last_fixed_ts < time_now:
                    last_fixed_ts = time_now

                    # Устанавливаем настоящее время для котировки и сохраняем
                    model.quotation.ts = time_now
                    model.quotation.save()

                    # Проверка возможности начать работу согласно временному рабочему интервалу в конфигурации
                    surplus_time = time_now % model.task.setting.working_interval_sec
                    if surplus_time == 0:
                        Analyzer.save_candles(model.quotation, model.task.setting)

            time.sleep(0.5)

    @staticmethod
    def save_candles(quotation, setting):
        candles = []
        candles_durations = setting.candles_durations
        for duration in candles_durations:
            candle = Candle.make(quotation.ts, duration, setting.instrument_id)
            candles.append(candle)
        Candle.save_many(candles)

    @staticmethod
    def save_prediction(time_bid, quotation, sequence):
        # cache_thread = threading.Thread(target=self.cache_prediction, args=(time_bid, quotation,
        #                                                                     sequence,))
        # cache_thread.daemon = True
        # cache_thread.start()
        pass
