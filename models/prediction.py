import time
import json

from providers.providers import Providers


class Prediction(object):
    id = None
    setting_id = None
    time_bid = 0
    sequence = []
    sequence_hash = ""
    sequence_duration = 0
    created_cost = 0
    expiration_cost = 0
    admission = 0.0
    change = 0.0
    expires = 0
    delay = 0
    created_at = 0
    expiration_at = 0
    task_id = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def check_on_expiration(self):
        check = False
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE setting_id=%s AND expiration_at=%s",
                       [self.setting_id, self.expiration_at])
        row = cursor.fetchone()
        if row:
            check = True
        return check

    def __tuple_str(self):
        return str((self.id, self.setting_id, self.time_bid, self.sequence, self.sequence_hash,
                    self.sequence_duration, self.created_cost, self.expiration_cost, self.admission, self.change,
                    self.expires, self.delay, self.created_at, self.expiration_at, self.task_id))

    @staticmethod
    def model(raw=None):
        return Prediction(raw)

    @staticmethod
    def get_sequence_duration(sequence):
        total_duration = 0
        for item in sequence:
            total_duration += item["duration"]
        return total_duration

    @staticmethod
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