import json
import hashlib

from providers.providers import Providers
from models.prediction import Prediction


class Predictor:
    def __init__(self, task):
        self.settings = task.setting
        self.task = task
        # self.cache = Providers.cache()
        # self.is_history_check = False
        # if self.task.service_name == "checker":
        #     self.is_history_check = True

    def make(self, time_bid, quotation, sequence):
        # time_step = time_bid['time'] / 60 * self.time_step_on_minute
        # remaining = TimeHelper.get_remaining_second_to_minute(quotation.time)
        # time_left_minute = int((remaining / time_step) * time_step)
        # time_left_bid = time_bid['time'] - (60 - time_left_minute)
        # if time_bid["purchase"] < remaining:
        # pattern = self.save_pattern_from_sequence(sequence)
        # pattern_id = pattern["id"]
        prediction = Prediction()
        prediction.setting_id = self.settings.id
        prediction.time_bid = time_bid
        prediction.sequence = sequence
        prediction.sequence_hash = hashlib.md5(json.dumps(sequence)).hexdigest()
        prediction.sequence_duration = Prediction.get_sequence_duration(sequence)
        prediction.created_cost = quotation.value
        prediction.created_at = quotation.ts
        prediction.expiration_at = quotation.ts + time_bid
        prediction.task_id = self.task

        # prediction_cache_prefix = "prediction"
        # if self.is_history_check:
        #     prediction_cache_prefix = "test_prediction"

        # prediction_cache_key = prediction_cache_prefix + "_" + str(self.settings.instrument_id) + "_" + str(
        #     int(expiration_ts)) + "_" + str(time_bid['time']) + "_" + str(
        #     time_left_bid) + "_" + str(
        #     pattern_id)

        """Проверяем на возможность сохранения повторяющего прогноза за это время"""
        save_prediction = True
        if not self.settings.analyzer_save_prediction_if_exists:
            if prediction.check_on_expiration():
                save_prediction = False

        # Если повторяющийся прогноз можно отдать из функции """
        if save_prediction:
            return prediction
            # prediction = self.upsert_prediction(pattern_id, time_bid['time'],
            #                                     time_left_bid, duration_candles)
            # print prediction_cache_key, prediction

            # """
            # Отключаем эту функцию для режима тестирования истории
            # (Используется непосредственно в тестировщике)
            # """
            # Trader
            # if not self.is_history_check:
            #     trade_direction = self.trader.check_probability(prediction[1], prediction[2],
            #                                                     prediction[3], prediction[4],
            #                                                     prediction[6])
            #     if trade_direction:
            #         self.trader.trade(
            #             time_bid['time'] / 60,
            #             1,
            #             trade_direction,
            #             prediction[0],
            #             int(expiration_ts),
            #             quotation.value
            #         )

            # """
            # Объект для записи прогноза в кеш для дальнейшей его проверки
            # Имеет зависимые поля для тестирования истории
            #     call_count
            #     puts_count
            #     used_count
            #     created_at
            #     expiration_at
            #     bid_time
            # """
            # redis_object = {
            #     "id": prediction[0],
            #     "call_count": prediction[1],
            #     "puts_count": prediction[2],
            #     "last_call": prediction[3],
            #     "used_count": prediction[4],
            #     "delay": prediction[6],
            #     "bid_time": time_bid['time'],
            #     "value": quotation.value,
            #     "pattern_id": pattern_id,
            #     "created_at": quotation.time,
            #     "expiration_at": int(expiration_ts)
            # }

            # """Запись прогноза в редис"""
            # if self.is_history_check:
            #     """Для тестирования истории без времени жизни"""
            #     self.cache.set(prediction_cache_key, json.dumps(redis_object))
            # else:
            #     """Запись с временем жизни для реалтайм данных"""
            #     self.cache.setex(prediction_cache_key, time_bid['time'] + (time_bid['time'] / 60 * 5),
            #                      json.dumps(redis_object))
