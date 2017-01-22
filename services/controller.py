import time

from models.prediction import Prediction
from providers.providers import Providers
from models.quotation import Quotation


class Controller:
    @staticmethod
    def check_on_save_pattern():
        return True

    @staticmethod
    def check_predictions(task, quotation=None, times=1):
        cursor = Providers.db().get_cursor()

        trade_result = None
        # redis_prefix = "prediction"
        # if self.is_test:
        #     redis_prefix = "test_prediction"
        #     timestamp = "*"
        # redis_key = redis_prefix + "_" + str(self.settings.active["db_id"]) + "_" + str(timestamp) + "_*"

        # predictions_keys = self.redis.keys(redis_key)

        test_trading = []
        timestamp = int(time.time())
        history_num = task.get_param("history_num")
        # Если это тестирование истории то время не нужно
        if history_num > 0:
            del timestamp

        ended_predictions = Prediction.get_ended(task.setting_id, history_num, timestamp)
        for prediction in ended_predictions:
            if history_num > 0:
                """В режиме теста нет котировки - поэтому достаем вручную"""
                cursor.execute(
                    "SELECT * FROM quotations WHERE ts<=%s AND instrument_id=%s ORDER BY ts LIMIT 1",
                    (prediction.expiration_at, task.setting.instrument_id))
                row = cursor.fetchone()
                if row:
                    quotation = Quotation.model(row)

            if quotation:
                # Закрываем стоимость прогноза
                prediction.update_expiration_cost(quotation.value)

                call = 0
                put = 0
                last_call = 0
                delay = 0

                if int(prediction["delay"]) > 0:
                    delay = prediction["delay"] - 1

                if quotation.value < float(prediction["value"]):
                    call = 0
                    put = 1
                    if prediction["last_call"] < 0:
                        last_call = prediction["last_call"] - 1
                    else:
                        last_call = -1
                else:
                    if quotation.value > float(prediction["value"]):
                        call = 1
                        put = 0
                        if prediction["last_call"] > 0:
                            last_call = prediction["last_call"] + 1
                        else:
                            last_call = 1

                if abs(last_call) >= task.settings.trader_min_repeats and prediction["delay"] == 0:
                    delay = task.settings.trader_delay_on_trend

                cursor.execute("SELECT * FROM predictions WHERE id=%s", (prediction["id"],))
                prediction_pg = cursor.fetchone()
                if not prediction_pg:
                    times += 1
                    print
                    time.strftime("%b %d %Y %H:%M:%S"), "- Not found in DB from redis:", prediction["id"]
                    time.sleep(5)
                    self.check_predictions(quotation, times)
                else:
                    """Обновляем прогноз и устанавливаем счетчики"""
                    cursor.execute(
                        "UPDATE predictions SET calls_count=calls_count+%s, puts_count=puts_count+%s, "
                        "last_call=%s, delay=%s WHERE id=%s",
                        (
                            call,
                            put,
                            last_call,
                            delay,
                            prediction["id"]
                        ))

                    """Закрытие сделки - если была"""
                    cursor.execute(
                        "UPDATE orders SET expiration_cost=%s, change=created_cost-%s, closed_at=%s "
                        "WHERE active_id=%s AND prediction_id=%s AND expiration_at=%s",
                        (
                            quotation.value,
                            quotation.value,
                            int(time.time()),
                            self.settings.active["db_id"],
                            prediction["id"],
                            int(time.time())
                        ))

                if self.is_test:
                    """
                    Торгуем по мере проверки в тестовом режиме
                    в будущем сравнивая результаты ставки с прогнозом
                    """
                    trade_direction = self.trader.check_probability(prediction["call_count"],
                                                                    prediction["puts_count"],
                                                                    prediction["last_call"],
                                                                    prediction["used_count"],
                                                                    prediction["delay"])
                    if trade_direction:
                        """Сравниваем результат с прогнозом"""
                        if trade_direction == "put":
                            if put == 1:
                                trade_result = "Put"
                            else:
                                trade_result = "Fail"
                        else:
                            if trade_direction == "call":
                                if call == 1:
                                    trade_result = "Call"
                                else:
                                    trade_result = "Fail"
                    else:
                        trade_result = "No"
                    test_trading.append(trade_result)

        self.db.commit()
        if self.is_test:
            return test_trading
