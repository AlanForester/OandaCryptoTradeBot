from providers.providers import Providers


class Signal:
    id = None
    instrument_id = None
    sequence_id = None
    setting_id = None
    task_id = None
    pattern_id = None
    created_at = 0
    expiration_at = 0
    direction = 0
    created_cost = 0
    expiration_cost = 0
    closed_cost = 0
    max_cost = 0
    min_cost = 0
    call_max_change_cost = 0
    put_max_change_cost = 0
    time_bid = 0
    history_num = 0
    discrepancy_cost = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO signals (instrument_id,sequence_id,setting_id,task_id,"
                             "pattern_id,created_at,expiration_at,direction,created_cost,expiration_cost,"
                             "closed_cost,max_cost,min_cost,call_max_change_cost,put_max_change_cost,time_bid,"
                             "history_num, discrepancy_cost) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.instrument_id, self.sequence_id, self.setting_id, self.task_id,
                              self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                              self.expiration_cost, self.closed_cost, self.max_cost, self.min_cost,
                              self.call_max_change_cost, self.put_max_change_cost, self.time_bid, self.history_num,
                              self.discrepancy_cost))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def __tuple_str(self):
        return str((self.instrument_id, self.sequence_id, self.setting_id, self.task_id,
                    self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                    self.expiration_cost, self.closed_cost, self.max_cost, self.min_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.time_bid, self.history_num, self.discrepancy_cost))

    @staticmethod
    def model(raw=None):
        return Signal(raw)

    @staticmethod
    def update_close_cost(task, quotation):
        cursor = Providers.db().get_cursor()
        cursor.execute("UPDATE signals SET closed_cost=%s, discrepancy_cost=expiration_cost-%s WHERE expiration_at<=%s "
                       "AND closed_cost=0 AND task_id=%s", (quotation.value, quotation.value, quotation.ts, task.id))
        Providers.db().commit()
