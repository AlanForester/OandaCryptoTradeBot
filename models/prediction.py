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
    max_range = 0
    avg_range = 0
    call_max_change = 0
    put_max_change = 0
    call_max_avg_change = 0
    put_max_avg_change = 0
    created_at = 0
    expiration_at = 0
    history_num = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO predictions (sequence_id, setting_id, task_id, time_bid, pattern_id, "
                             "created_cost, expiration_cost, last_cost, admission, max_range, avg_range, "
                             "call_max_change, put_max_change,call_max_avg_change, put_max_avg_change, created_at, "
                             "expiration_at, history_num) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.pattern_id,
                              self.created_cost, self.expiration_cost, self.last_cost, self.admission, self.max_range,
                              self.avg_range, self.call_max_change, self.put_max_change, self.call_max_avg_change,
                              self.put_max_avg_change, self.created_at, self.expiration_at, self.history_num))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.time_bid, self.pattern_id,
                    self.created_cost, self.expiration_cost, self.last_cost, self.admission, self.max_range,
                    self.avg_range, self.call_max_change, self.put_max_change, self.call_max_avg_change,
                    self.put_max_avg_change, self.created_at, self.expiration_at, self.history_num))

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
        last_cost = "CASE WHEN last_cost != %s AND setting_id = %s AND expiration_at > extract(EPOCH FROM now()) " \
                    "THEN %s ELSE last_cost END" % \
                    (cost, setting_id, cost)
        put_max_change = "CASE WHEN put_max_change < created_cost - %s AND setting_id = %s AND " \
                         "expiration_at > extract(EPOCH FROM now()) THEN created_cost - %s ELSE put_max_change END" % \
                         (cost, setting_id, cost)
        put_max_avg_change = "CASE WHEN put_max_avg_change != (put_max_avg_change + (%s)) / 2 AND setting_id = %s " \
                             "AND expiration_at > extract(EPOCH FROM now()) THEN (put_max_avg_change + (%s)) / 2 " \
                             "ELSE put_max_avg_change END" % (put_max_change, setting_id, put_max_change)
        call_max_change = "CASE WHEN call_max_change < %s - created_cost AND setting_id = %s AND " \
                          "expiration_at > extract(EPOCH FROM now()) THEN %s - created_cost ELSE call_max_change " \
                          "END" % (cost, setting_id, cost)
        call_max_avg_change = "CASE WHEN call_max_avg_change != (call_max_avg_change + (%s)) / 2 AND setting_id = %s " \
                              "AND expiration_at > extract(EPOCH FROM now()) THEN (call_max_avg_change + (%s)) / 2 " \
                              "ELSE put_max_avg_change END" % (call_max_change, setting_id, call_max_change)
        max_range = "CASE WHEN max_range < (%s) + (%s) AND setting_id = %s " \
                    "AND expiration_at > extract(EPOCH FROM now()) THEN (%s) + (%s) ELSE max_range END" % \
                    (put_max_change, call_max_change, setting_id, put_max_change, call_max_change)
        avg_range = "CASE WHEN avg_range != (%s) + (%s) AND setting_id = %s AND " \
                    "expiration_at > extract(EPOCH FROM now()) THEN (avg_range + ((%s) + (%s))) / 2 " \
                    "ELSE avg_range END" % (put_max_change, call_max_change, setting_id, put_max_change,
                                            call_max_change)

        query = "UPDATE predictions SET put_max_change = %s, put_max_avg_change = %s, call_max_change = %s, " \
                "call_max_avg_change = %s, max_range = %s, avg_range = %s, last_cost=%s" % (put_max_change,
                                                                                            put_max_avg_change,
                                                                                            call_max_change,
                                                                                            call_max_avg_change,
                                                                                            max_range,
                                                                                            avg_range, last_cost)
        cursor.execute(query)
        Providers.db().commit()
        return quotation
