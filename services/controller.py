import time

from models.prediction import Prediction
from models.pattern import Pattern
from models.sequence import Sequence


class Controller:

    @staticmethod
    def is_save_prediction(setting, prediction):
        # Проверяем на возможность сохранения повторяющего прогноза за это время
        save_prediction = True
        if not setting.analyzer_save_prediction_if_exists:
            if prediction.exists_on_expiration():
                save_prediction = False
        return save_prediction

    @staticmethod
    def upsert_pattern(prediction):
        cursor = self.db.cursor()
        expires = 0
        ret = None
        is_update = False

        expires = 0
        max_duration = 0
        for expire in task.setting.analyzer_prediction_expire:
            if expire["history_duration"] <= sequence.duration:
                if expire["history_duration"] > max_duration:
                    max_duration = expire["history_duration"]
                    if expire["expire"] > 0:
                        expires = time.time() + expire["expire"]
                    else:
                        expires = 0
        if expires > 0:
            # Установка истечения срока прогноза по длительности паттерна

            cursor.execute(
                "SELECT id,calls_count,puts_count,last_call,used_count,expires,delay FROM predictions WHERE "
                "pattern_id=%s AND active_id=%s AND time_bid=%s AND time_left=%s AND is_test=%s "
                "ORDER BY ts DESC LIMIT 1", (pattern_id, self.settings.active["db_id"], time_bid,
                                             time_left, self.is_test))
            ret = cursor.fetchone()

            if ret and (ret[5] > int(time.time())):
                self.update_prediction_used_counter(ret[0])
                is_update = True

        if not is_update:

            cursor.execute("INSERT INTO predictions (pattern_id,active_id,time_bid,time_left,used_count,"
                           "calls_count,puts_count,last_call,expires,delay,ts,is_test) VALUES "
                           "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                           "ON CONFLICT (pattern_id,active_id,time_bid,time_left,expires,is_test)"
                           "DO UPDATE SET used_count=predictions.used_count + 1 "
                           "RETURNING id,calls_count,puts_count,last_call,used_count, expires, delay",
                           (pattern_id, self.settings.active["db_id"], time_bid, time_left, 1, 0, 0, 0, expires, 0,
                            time.time(), self.is_test))
            ret = cursor.fetchone()
        self.db.commit()
        return ret
