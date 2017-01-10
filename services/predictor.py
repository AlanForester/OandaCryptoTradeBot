import json
import time

from providers.providers import Providers
from helpers.timehelper import TimeHelper


class Predictor:
    def __init__(self, settings, is_test=False):
        self.settings = settings
        self.is_test = is_test
        self.time_step_on_minute = 5
        self.cache = Providers.cache()

    def cache_prediction(self, time_bid, quotation, sequence):
        time_step = time_bid['time'] / 60 * self.time_step_on_minute
        remaining = TimeHelper.get_remaining_second_to_minute(quotation.time)
        time_left_minute = int((remaining / time_step) * time_step)
        time_left_bid = time_bid['time'] - (60 - time_left_minute)
        if time_bid["purchase"] < remaining:
            pattern = self.save_pattern_from_sequence(sequence)
            pattern_id = pattern["id"]
            duration_candles = pattern["duration"]
            expiration_ts = TimeHelper.get_expiration_time(quotation.time, time_bid)

            prediction_cache_prefix = "prediction"
            if self.is_test:
                prediction_cache_prefix = "test_prediction"

            prediction_cache_key = prediction_cache_prefix + "_" + str(self.settings.instrument_id) + "_" + str(
                int(expiration_ts)) + "_" + str(time_bid['time']) + "_" + str(
                time_left_bid) + "_" + str(
                pattern_id)

            """Проверяем на возможность сохранения повторяющего прогноза за это время"""
            save_prediction = True
            if not self.settings.analyzer_save_prediction_if_exists:
                prediction_exists = self.cache.exists(prediction_cache_key)
                if prediction_exists:
                    save_prediction = False

            """Если повторяющийся прогноз можно сохранить """
            if save_prediction:
                # TODO: Изменить на модель Prediction
                """
                Возвращает кортеж Prediction
                :returns
                    :id = prediction[0]
                    :call_count = prediction[1]
                    :puts_count = prediction[2]
                    :last_call = prediction[3]
                    :used_count = prediction[4]
                    :expires = prediction[5]
                    :delay = prediction[6]
                """
                prediction = self.upsert_prediction(pattern_id, time_bid['time'],
                                                    time_left_bid, duration_candles)
                # print prediction_cache_key, prediction

                """
                Отключаем эту функцию для режима тестирования истории
                (Используется непосредственно в тестировщике)
                """
                # Trader
                # if not self.is_test:
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

                """
                Объект для записи прогноза в кеш для дальнейшей его проверки
                Имеет зависимые поля для тестирования истории
                    call_count
                    puts_count
                    used_count
                    created_at
                    expiration_at
                    bid_time
                """
                redis_object = {
                    "id": prediction[0],
                    "call_count": prediction[1],
                    "puts_count": prediction[2],
                    "last_call": prediction[3],
                    "used_count": prediction[4],
                    "delay": prediction[6],
                    "bid_time": time_bid['time'],
                    "value": quotation.value,
                    "pattern_id": pattern_id,
                    "created_at": quotation.time,
                    "expiration_at": int(expiration_ts)
                }

                """Запись прогноза в редис"""
                if self.is_test:
                    """Для тестирования истории без времени жизни"""
                    self.cache.set(prediction_cache_key, json.dumps(redis_object))
                else:
                    """Запись с временем жизни для реалтайм данных"""
                    self.cache.setex(prediction_cache_key, time_bid['time'] + (time_bid['time'] / 60 * 5),
                                     json.dumps(redis_object))

    def save_pattern_from_sequence(self, sequence):
        cursor = Providers.db().get_cursor()
        first = True
        last = False
        first_id = 0
        last_id = 0
        parent_id = 0
        i = 1
        duration = 0
        for pattern in sequence:
            duration += pattern["duration"]
            if len(sequence) == i:
                last = True

            cursor.execute(
                "INSERT INTO patterns (parent_id,first,last,admission,duration) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (parent_id,last,admission,duration,first) "
                "DO UPDATE SET first=EXCLUDED.first RETURNING id",
                (parent_id, first, last, pattern["admission"], pattern["duration"]))
            pattern_row = cursor.fetchone()
            parent_id = pattern_row[0]
            if first_id == 0:
                first_id = parent_id
            if last:
                last_id = parent_id
            first = False
            i += 1
        Providers.db().commit()
        return {"id": last_id, "duration": duration}

    def upsert_prediction(self, pattern_id, time_bid, time_left, candles_durations):
        cursor = Providers.db().get_cursor()
        expires = 0
        ret = None
        is_update = False
        if len(self.settings.analyzer_prediction_expire) > 0:
            expires_array = self.settings.analyzer_prediction_expire
            expires_array.reverse()
            for expire in self.settings.analyzer_prediction_expire:

                if expire["history_duration"] <= candles_durations:
                    if expire["expire"] > 0:
                        expires = time.time() + expire["expire"]
                    break

            if expires > 0:
                cursor.execute(
                    "SELECT id,calls_count,puts_count,last_call,used_count,expires,delay FROM predictions WHERE "
                    "pattern_id=%s AND instrument_id=%s AND time_bid=%s AND time_left=%s AND is_test=%s "
                    "ORDER BY ts DESC LIMIT 1", (pattern_id, self.settings.instrument_id, time_bid,
                                                 time_left, self.is_test))
                ret = cursor.fetchone()

                if ret and (ret[5] > int(time.time())):
                    self.update_prediction_used_counter(ret[0])
                    is_update = True

        if not is_update:
            cursor.execute("INSERT INTO predictions (pattern_id,instrument_id,time_bid,time_left,used_count,"
                           "calls_count,puts_count,last_call,expires,delay,ts,is_test) VALUES "
                           "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                           "ON CONFLICT (pattern_id,instrument_id,time_bid,time_left,expires,is_test)"
                           "DO UPDATE SET used_count=predictions.used_count + 1 "
                           "RETURNING id,calls_count,puts_count,last_call,used_count, expires, delay",
                           (pattern_id, self.settings.instrument_id, time_bid, time_left, 1, 0, 0, 0, expires, 0,
                            time.time(), self.is_test))
            ret = cursor.fetchone()
        Providers.db().commit()
        return ret