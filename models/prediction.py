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
    last_cost = 0
    admission = 0
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

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO predictions (sequence_id, setting_id, task_id, time_bid, pattern_id, "
                             "created_cost, expiration_cost, last_cost, admission, range_max_change_cost, "
                             "range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,"
                             "call_max_avg_change_cost, put_max_avg_change_cost, range_sum_max_change_cost,"
                             "call_sum_max_change_cost, put_sum_max_change_cost, count_change_cost,created_at, "
                             "expiration_at, history_num) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                              self.created_cost, self.expiration_cost, self.last_cost, self.admission,
                              self.range_max_change_cost, self.range_max_avg_change_cost, self.call_max_change_cost,
                              self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                              self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                              self.put_sum_max_change_cost, self.count_change_cost, self.created_at,
                              self.expiration_at, self.history_num))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                    self.created_cost, self.expiration_cost, self.last_cost, self.admission,
                    self.range_max_change_cost, self.range_max_avg_change_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                    self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                    self.put_sum_max_change_cost, self.created_at, self.expiration_at, self.history_num))

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
        prediction.history_num = task.get_param("history_num")
        return prediction

    @staticmethod
    def update_cost(quotation, setting_id):
        cursor = Providers.db().get_cursor()
        cost = quotation.value
        count_change_cost = "count_change_cost+1"
        last_cost = "CASE WHEN last_cost != %s AND setting_id = %s AND expiration_at > extract(EPOCH FROM now()) " \
                    "THEN %s ELSE last_cost END" % \
                    (cost, setting_id, cost)
        call_max_change_cost = "CASE WHEN call_max_change_cost < %s - created_cost AND setting_id = %s AND " \
                               "expiration_at > extract(EPOCH FROM now()) " \
                               "THEN %s - created_cost ELSE call_max_change_cost END" % (cost, setting_id, cost)
        call_sum_max_change_cost = "call_sum_max_change_cost + (%s)" % call_max_change_cost
        call_max_avg_change_cost = "CASE WHEN call_max_avg_change_cost != (%s) / (%s) " \
                                   "AND setting_id = %s AND expiration_at > extract(EPOCH FROM now()) " \
                                   "THEN (%s) / (%s) ELSE put_max_avg_change_cost END" % \
                                   (call_sum_max_change_cost, count_change_cost, setting_id, call_sum_max_change_cost,
                                    count_change_cost)

        put_max_change_cost = "CASE WHEN put_max_change_cost < created_cost - %s AND setting_id = %s AND " \
                              "expiration_at > extract(EPOCH FROM now()) THEN created_cost - %s " \
                              "ELSE put_max_change_cost END" % (cost, setting_id, cost)
        put_sum_max_change_cost = "put_sum_max_change_cost + (%s)" % put_max_change_cost
        put_max_avg_change_cost = "CASE WHEN put_max_avg_change_cost != (%s) / (%s) " \
                                  "AND setting_id = %s AND expiration_at > extract(EPOCH FROM now()) " \
                                  "THEN (%s) / (%s) ELSE put_max_avg_change_cost END" % \
                                  (put_sum_max_change_cost, count_change_cost, setting_id, put_sum_max_change_cost,
                                   count_change_cost)
        range_max_change_cost = "CASE WHEN range_max_change_cost < (%s) + (%s) AND setting_id = %s " \
                                "AND expiration_at > extract(EPOCH FROM now()) THEN (%s) + (%s) " \
                                "ELSE range_max_change_cost END" % \
                                (put_max_change_cost, call_max_change_cost, setting_id, put_max_change_cost,
                                 call_max_change_cost)
        range_sum_max_change_cost = "range_sum_max_change_cost + (%s)" % range_max_change_cost
        range_max_avg_change_cost = "CASE WHEN range_max_avg_change_cost != (%s) / (%s) AND setting_id = %s AND " \
                                    "expiration_at > extract(EPOCH FROM now()) " \
                                    "THEN (%s) / (%s) ELSE range_max_avg_change_cost END" % \
                                    (range_sum_max_change_cost, count_change_cost, setting_id,
                                     range_sum_max_change_cost, count_change_cost)

        query = "UPDATE predictions SET " \
                "put_max_change_cost = %s, " \
                "put_max_avg_change_cost = %s, " \
                "call_max_change_cost = %s, " \
                "call_max_avg_change_cost = %s, " \
                "range_max_change_cost = %s, " \
                "range_max_avg_change_cost = %s, " \
                "range_sum_max_change_cost = %s, " \
                "call_sum_max_change_cost = %s, " \
                "put_sum_max_change_cost = %s, " \
                "count_change_cost = %s, " \
                "last_cost=%s" % (put_max_change_cost, put_max_avg_change_cost, call_max_change_cost,
                                  call_max_avg_change_cost, range_max_change_cost,
                                  range_max_avg_change_cost, range_sum_max_change_cost, call_sum_max_change_cost,
                                  put_sum_max_change_cost, count_change_cost, last_cost)
        cursor.execute(query)
        Providers.db().commit()
        return quotation
