

class Controller:

    @staticmethod
    def check_on_save_pattern():
        return True

    # @staticmethod
    # def check_predictions(self, quotation=None, times=1):
    #     trade_result = None
    #     timestamp = int(time.time())
    #     redis_prefix = "prediction"
    #     if self.is_test:
    #         redis_prefix = "test_prediction"
    #         timestamp = "*"
    #     redis_key = redis_prefix + "_" + str(self.settings.active["db_id"]) + "_" + str(timestamp) + "_*"
    #     predictions_keys = self.redis.keys(redis_key)
    #     if predictions_keys:
    #         test_trading = []
    #         for predictions_key in predictions_keys:
    #             prediction_json = self.redis.get(predictions_key)
    #             self.redis.delete(predictions_key)
    #             if prediction_json:
    #                 prediction = json.loads(prediction_json)
    #                 cursor = self.db.cursor()
    #
    #                 if self.is_test:
    #                     """В режиме теста нет котировки - поэтому достаем вручную"""
    #                     if not quotation:
    #                         cursor.execute(
    #                             "SELECT * FROM quotations WHERE ts<=%s AND active_id=%s ORDER BY ts LIMIT 1",
    #                             (prediction["expiration_at"], self.settings.active["db_id"]))
    #                         row = cursor.fetchone()
    #                         if row:
    #                             quotation = Quotation([row[0], row[4]])
    #                 if quotation:
    #                     call = 0
    #                     put = 0
    #                     last_call = 0
    #                     delay = 0
    #
    #                     if int(prediction["delay"]) > 0:
    #                         delay = prediction["delay"] - 1
    #
    #                     if quotation.value < float(prediction["value"]):
    #                         call = 0
    #                         put = 1
    #                         if prediction["last_call"] < 0:
    #                             last_call = prediction["last_call"] - 1
    #                         else:
    #                             last_call = -1
    #                     else:
    #                         if quotation.value > float(prediction["value"]):
    #                             call = 1
    #                             put = 0
    #                             if prediction["last_call"] > 0:
    #                                 last_call = prediction["last_call"] + 1
    #                             else:
    #                                 last_call = 1
    #
    #                     if abs(last_call) >= self.settings.trader_min_repeats and prediction["delay"] == 0:
    #                         delay = self.settings.trader_delay_on_trend
    #
    #                     cursor.execute("SELECT * FROM predictions WHERE id=%s", (prediction["id"],))
    #                     prediction_pg = cursor.fetchone()
    #                     if not prediction_pg:
    #                         times += 1
    #                         print time.strftime("%b %d %Y %H:%M:%S"), "- Not found in DB from redis:", prediction["id"]
    #                         time.sleep(5)
    #                         self.check_predictions(quotation, times)
    #                     else:
    #                         """Обновляем прогноз и устанавливаем счетчики"""
    #                         cursor.execute(
    #                             "UPDATE predictions SET calls_count=calls_count+%s, puts_count=puts_count+%s, "
    #                             "last_call=%s, delay=%s WHERE id=%s",
    #                             (
    #                                 call,
    #                                 put,
    #                                 last_call,
    #                                 delay,
    #                                 prediction["id"]
    #                             ))
    #
    #                         """Закрытие сделки - если была"""
    #                         cursor.execute(
    #                             "UPDATE orders SET expiration_cost=%s, change=created_cost-%s, closed_at=%s "
    #                             "WHERE active_id=%s AND prediction_id=%s AND expiration_at=%s",
    #                             (
    #                                 quotation.value,
    #                                 quotation.value,
    #                                 int(time.time()),
    #                                 self.settings.active["db_id"],
    #                                 prediction["id"],
    #                                 int(time.time())
    #                             ))
    #
    #                     if self.is_test:
    #                         """
    #                         Торгуем по мере проверки в тестовом режиме
    #                         в будущем сравнивая результаты ставки с прогнозом
    #                         """
    #                         trade_direction = self.trader.check_probability(prediction["call_count"],
    #                                                                         prediction["puts_count"],
    #                                                                         prediction["last_call"],
    #                                                                         prediction["used_count"],
    #                                                                         prediction["delay"])
    #                         if trade_direction:
    #                             """Сравниваем результат с прогнозом"""
    #                             if trade_direction == "put":
    #                                 if put == 1:
    #                                     trade_result = "Put"
    #                                 else:
    #                                     trade_result = "Fail"
    #                             else:
    #                                 if trade_direction == "call":
    #                                     if call == 1:
    #                                         trade_result = "Call"
    #                                     else:
    #                                         trade_result = "Fail"
    #                         else:
    #                             trade_result = "No"
    #                         test_trading.append(trade_result)
    #
    #         self.db.commit()
    #         if self.is_test:
    #             return test_trading