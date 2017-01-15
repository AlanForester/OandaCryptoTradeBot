import time

from providers.providers import Providers


class Prediction(object):
    id = None
    sequence_id = None
    setting_id = None
    task_id = None
    time_bid = 0
    pattern_id = 0
    created_cost = 0
    expiration_cost = 0
    admission = 0.0
    change = 0.0
    created_at = 0
    expiration_at = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO predictions (sequence_id, setting_id, task_id, time_bid, pattern_id, "
                             "created_cost, expiration_cost, admission, change, created_at, expiration_at) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                              self.created_cost, self.expiration_cost, self.admission, self.change, self.created_at,
                              self.expiration_at))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def exists_on_expiration(self):
        check = False
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE setting_id=%s AND expiration_at=%s AND sequence_id=%s",
                       [self.setting_id, self.expiration_at, self.sequence_id])
        row = cursor.fetchone()
        if row and row[0] > 0:
            check = True
        return check

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.time_bid, self.pattern_id,
                    self.created_cost, self.expiration_cost, self.admission, self.change,
                    self.created_at, self.expiration_at))

    @staticmethod
    def model(raw=None):
        return Prediction(raw)

    @staticmethod
    def make(task, time_bid, quotation, sequence):
        prediction = Prediction()
        prediction.setting_id = task.setting.id
        prediction.time_bid = time_bid
        prediction.task_id = task.id
        prediction.sequence_id = sequence.id
        prediction.created_cost = quotation.value
        prediction.created_at = quotation.ts
        prediction.expiration_at = quotation.ts + time_bid
        return prediction
