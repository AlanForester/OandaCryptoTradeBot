import time

from providers.providers import Providers
from models.pattern import Pattern


class Prediction(object):
    id = None
    sequence_id = None
    setting_id = None
    task_id = None
    time_bid = 0
    pattern_id = 0
    created_cost = 0
    created_ask = 0
    created_bid = 0
    expiration_cost = 0
    expiration_ask = 0
    expiration_bid = 0
    last_cost = 0
    range_max_change_cost = 0
    range_max_avg_change_cost = 0
    call_max_change_cost = 0
    put_max_change_cost = 0
    call_max_avg_change_cost = 0
    put_max_avg_change_cost = 0
    range_sum_max_change_cost = 0
    call_sum_max_change_cost = 0
    put_sum_max_change_cost = 0
    count_change_cost = 0
    created_at = 0
    expiration_at = 0
    history_num = 0
    time_to_expiration = 0

    _pattern = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO predictions (sequence_id, setting_id, task_id, time_bid, pattern_id, "
                             "created_cost, created_ask, created_bid, expiration_cost,  expiration_ask, "
                             "expiration_bid, last_cost, range_max_change_cost, "
                             "range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,"
                             "call_max_avg_change_cost, put_max_avg_change_cost, range_sum_max_change_cost,"
                             "call_sum_max_change_cost, put_sum_max_change_cost, count_change_cost,created_at, "
                             "expiration_at, history_num, time_to_expiration) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                             "ON CONFLICT "
                             "(sequence_id,setting_id,time_bid,pattern_id,expiration_at,time_to_expiration,history_num)"
                             "DO UPDATE SET expiration_cost=EXCLUDED.expiration_cost RETURNING id"
                             ,
                             (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                              self.created_cost, self.created_ask, self.created_bid, self.expiration_cost,
                              self.expiration_ask, self.expiration_bid, self.last_cost,
                              self.range_max_change_cost, self.range_max_avg_change_cost, self.call_max_change_cost,
                              self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                              self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                              self.put_sum_max_change_cost, self.count_change_cost, self.created_at,
                              self.expiration_at, self.history_num, self.time_to_expiration))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def update_expiration_cost(self, value, ask, bid):
        cursor = Providers.db().get_cursor()
        cursor.execute("UPDATE predictions SET expiration_cost=%s, expiration_ask=%s, expiration_bid=%s "
                       "WHERE id=%s", (value, ask, bid, self.id))
        Providers.db().commit()

    @property
    def pattern(self):
        if not self._pattern:
            self._pattern = Pattern.get_by_id(self.pattern_id)
        return self._pattern

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                    self.created_cost, self.created_ask, self.created_bid, self.expiration_cost,
                    self.expiration_ask, self.expiration_bid, self.last_cost,
                    self.range_max_change_cost, self.range_max_avg_change_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                    self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                    self.put_sum_max_change_cost, self.count_change_cost, self.created_at, self.expiration_at,
                    self.history_num, self.time_to_expiration))

    @staticmethod
    def model(raw=None):
        return Prediction(raw)

    @staticmethod
    def save_many(predictions: list):
        cursor = Providers.db().get_cursor()
        query = 'INSERT INTO predictions (sequence_id, setting_id, task_id, time_bid, pattern_id, ' + \
                'created_cost, created_ask, created_bid, expiration_cost, expiration_ask, expiration_bid, ' \
                'last_cost, range_max_change_cost, ' + \
                'range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,' + \
                'call_max_avg_change_cost, put_max_avg_change_cost, range_sum_max_change_cost,' + \
                'call_sum_max_change_cost, put_sum_max_change_cost, count_change_cost,created_at, ' + \
                'expiration_at, history_num, time_to_expiration) VALUES ' + \
                ','.join(v.__tuple_str() for v in predictions) + 'ON CONFLICT ' \
                '(sequence_id,setting_id,time_bid,pattern_id,expiration_at,time_to_expiration,history_num)' + \
                'DO UPDATE SET expiration_cost=EXCLUDED.expiration_cost RETURNING id'
        cursor.execute(query)
        Providers.db().commit()
        res = cursor.fetchall()
        if res:
            return res
        return []

    @staticmethod
    def make(task, time_bid, quotation, seq):
        prediction = Prediction()
        prediction.setting_id = task.setting.id
        prediction.time_bid = time_bid['time']
        prediction.task_id = task.id
        prediction.sequence_id = seq.id
        prediction.created_cost = quotation.value
        prediction.created_ask = quotation.ask
        prediction.created_bid = quotation.bid
        prediction.created_at = quotation.ts
        expiration_at = quotation.ts + time_bid['time']
        time_to_expiration = time_bid['time'] - (expiration_at % time_bid['time'])
        time_divider = task.setting.analyzer_expiry_time_bid_divider
        prediction.time_to_expiration = int(time_to_expiration / time_divider) * time_divider
        prediction.expiration_at = int(expiration_at / time_bid['time']) * time_bid['time']
        prediction.history_num = task.get_param("history_num")
        return prediction

    @staticmethod
    def get_expired(setting_id, history_num, time=None):
        cursor = Providers.db().get_cursor()
        query = "SELECT * FROM predictions WHERE expiration_cost=0 AND setting_id=%s AND history_num=%s" % \
                (setting_id, history_num)
        if time:
            query += " AND expiration_at<=%s" % time

        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            res = []
            for row in rows:
                res.append(Prediction.model(row))
            return res

    @staticmethod
    def calculation_cost_for_topical(quotation, setting_id):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT update_predictions(%s,%s,%s)", [quotation.ts, setting_id, quotation.value])
        Providers.db().commit()
