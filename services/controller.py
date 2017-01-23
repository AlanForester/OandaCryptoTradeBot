import time

from models.prediction import Prediction
from models.quotation import Quotation
from services.signaler import Signaler


class Controller:
    @staticmethod
    def check_on_save_pattern():
        return True

    @staticmethod
    def check_predictions(task, quotation=None):
        test_trading = []
        timestamp = int(time.time())
        history_num = task.get_param("history_num")

        # Если это тестирование истории то время не нужно
        if history_num > 0:
            del timestamp

        ended_predictions = Prediction.get_ended(task.setting_id, history_num, timestamp)
        # Формируем массив патернов для исключения повторения
        taken_patterns = []
        for prediction in ended_predictions:
            if history_num > 0:
                """В режиме теста нет котировки - поэтому достаем вручную"""
                quotation = Quotation.get_one_to_ts(prediction.expiration_at, task.setting.instrument_id)

            if quotation:
                # Закрываем стоимость прогноза
                prediction.update_expiration_cost(quotation.value)

                # Получаем паттерн с массива полученных патернов
                if prediction.pattern_id not in taken_patterns:
                    taken_patterns[prediction.pattern_id] = prediction.pattern

                pattern = taken_patterns[prediction.pattern_id]

                if quotation.value < prediction.created_cost:
                    pattern.puts_count += 1
                    if pattern.last_call < 0:
                        pattern.last_call -= 1
                    else:
                        pattern.last_call = -1
                else:
                    if quotation.value > prediction.created_cost:
                        pattern.calls_count += 1
                        if pattern.last_call > 0:
                            pattern.last_call += 1
                        else:
                            pattern.last_call = 1

                if pattern.delay > 0:
                    pattern.delay -= 1
                if abs(pattern.last_call) >= task.settings.trader_min_repeats and pattern.delay == 0:
                    pattern.delay = task.settings.trader_delay_on_trend

                if history_num > 0:
                    # Формируем сигнал для тестовой проверки
                    trade_direction = Signaler.check(task, pattern)
                    test_trading.append({"prediction": prediction.id, "pattern": pattern.id, "signal": trade_direction})

        # Обновляем паттерн и устанавливаем счетчики
        if len(taken_patterns) > 0:
            for item in taken_patterns:
                item.update()

        if history_num > 0:
            return test_trading
