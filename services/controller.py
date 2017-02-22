import time

from models.prediction import Prediction
from models.quotation import Quotation
from models.signal import Signal
from services.signaler import Signaler
from providers.providers import Providers
from models.pattern import Pattern
from models.prediction import Prediction


class Controller:
    @staticmethod
    def check_on_make_prediction(task, prediction: Prediction, pat: Pattern):
        # Проверка на существование сигнала по паттерну за время прогноза
        for prediction_item in task.storage.predictions:
            if prediction_item.pattern_id == pat.id:
                return False
        return True

    @staticmethod
    def check_on_make_signal(task, pat: Pattern, prediction: Prediction, q):
        # Проверка на минимальное время работы паттерна
        if not Pattern.check_on_min_work_time(task, pat, prediction.sequence_duration, q):
            return False

        # Проверка на существование сигнала по паттерну за время прогноза
        for signal_item in task.storage.signals:
            if pat.id == signal_item.pattern_id:
                return False
        return True

    @staticmethod
    def update_expired_signals(task, quotation):
        exist = False
        for signal in task.storage.signals:
            if signal.expiration_at <= quotation.ts:
                task.storage.signals.remove(signal)
                exist = True

        if exist:
            Signal.update_close_cost(task, quotation)

    @staticmethod
    def check_expired_predictions(task, quotation):
        timestamp = quotation.ts

        if Providers.config().no_write:
            Prediction.get_expired(task, timestamp)
        else:
            ended_predictions = Prediction.get_expired(task, timestamp)
            if ended_predictions:
                # Формируем массив патернов для исключения повторения
                taken_patterns = {}
                for prediction in ended_predictions:
                    # Закрываем стоимость прогноза
                    prediction.expiration_cost = quotation.value
                    prediction.expiration_ask = quotation.ask
                    prediction.expiration_bid = quotation.bid

                    # Получаем паттерн с массива полученных патернов
                    if prediction.pattern_id not in taken_patterns:
                        taken_patterns[prediction.pattern_id] = prediction.pattern

                    pattern = taken_patterns[prediction.pattern_id]
                    # Рассчитываем аттрибуты стоимости
                    pattern.calculation_cost_from_prediction(prediction)

                    if quotation.value < prediction.created_cost:
                        pattern.puts_count += 1
                        if pattern.trend < 0:
                            pattern.trend -= 1
                        else:
                            pattern.trend = -1

                        if pattern.trend_max_put_count < abs(pattern.trend):
                            pattern.trend_max_put_count = abs(pattern.trend)

                    if quotation.value > prediction.created_cost:
                        pattern.calls_count += 1
                        if pattern.trend > 0:
                            pattern.trend += 1
                        else:
                            pattern.trend = 1

                        if pattern.trend_max_call_count < pattern.trend:
                            pattern.trend_max_call_count = pattern.trend

                    if quotation.value == prediction.created_cost:
                        pattern.same_count += 1
                        pattern.trend = 0

                    if abs(pattern.trend) >= task.setting.signaler_min_repeats and pattern.delay == 0:
                        pattern.delay = task.setting.signaler_delay_on_trend
                    if pattern.delay > 0:
                        pattern.delay -= 1

                Prediction.save_many(ended_predictions)

                # Обновляем паттерн и устанавливаем счетчики
                if len(taken_patterns) > 0:
                    for item in taken_patterns:
                        taken_patterns[item].update()
