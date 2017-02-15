from providers.providers import Providers


class Signal:
    id = None
    instrument_id = None
    sequence_id = None
    setting_id = None
    task_id = None
    prediction_id = None
    pattern_id = None
    created_at = 0
    expiration_at = 0
    direction = 0
    created_cost = 0
    expiration_cost = 0
    max_cost = 0
    min_cost = 0
    call_max_change_cost = 0
    put_max_change_cost = 0
    time_bid = 0
    history_num = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO signals (instrument_id,sequence_id,setting_id,task_id,prediction_id,"
                             "pattern_id,created_at,expiration_at,direction,created_cost,expiration_cost,max_cost,"
                             "min_cost,call_max_change_cost,put_max_change_cost,time_bid,history_num) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.instrument_id, self.sequence_id, self.setting_id, self.task_id, self.prediction_id,
                              self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                              self.expiration_cost, self.max_cost, self.min_cost, self.call_max_change_cost,
                              self.put_max_change_cost, self.time_bid, self.history_num))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def __tuple_str(self):
        return str((self.instrument_id, self.sequence_id, self.setting_id, self.task_id, self.prediction_id,
                    self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                    self.expiration_cost, self.max_cost, self.min_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.time_bid, self.history_num))

    @staticmethod
    def model(raw=None):
        return Signal(raw)
