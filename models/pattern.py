import time

from providers.providers import Providers


class Pattern:
    id = None
    sequence_id = None
    setting_id = None
    task_id = None
    time_bid = 0
    used_count = 0
    calls_count = 0
    puts_count = 0
    same_count = 0
    trend = 0
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
    delay = 0
    expires = 0
    history_num = 0
    created_at = 0
    trend_max_call_count = 0
    trend_max_put_count = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def check_on_expire(self):
        return self.expires > int(time.time())

    def update_used_counter(self):
        cursor = Providers.db().get_cursor()
        cursor.execute("UPDATE patterns SET used_count=used_count+1 WHERE id=%s", (self.id,))

    def save(self):
        cursor = Providers.db().get_cursor()
        cursor.execute("INSERT INTO patterns (sequence_id,setting_id,task_id,time_bid,used_count,calls_count,"
                       "puts_count,same_count,trend,range_max_change_cost, "
                       "range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,"
                       "call_max_avg_change_cost, put_max_avg_change_cost, range_sum_max_change_cost,"
                       "call_sum_max_change_cost, put_sum_max_change_cost, count_change_cost,"
                       "delay,expires,history_num,created_at,trend_max_call_count,trend_max_put_count) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                       "ON CONFLICT (sequence_id,setting_id,time_bid,expires,history_num)"
                       "DO UPDATE SET used_count=patterns.used_count + 1 RETURNING id",
                       (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.used_count,
                        self.calls_count, self.puts_count, self.same_count, self.trend, self.range_max_change_cost,
                        self.range_max_avg_change_cost, self.call_max_change_cost,
                        self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                        self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                        self.put_sum_max_change_cost, self.count_change_cost, self.delay,
                        self.expires, self.history_num, self.created_at, self.trend_max_call_count,
                        self.trend_max_put_count))
        Providers.db().commit()
        row = cursor.fetchone()
        if row:
            self.id = row.id
            Providers.db().commit()
        return self

    def update(self):
        cursor = Providers.db().get_cursor()
        cursor.execute("UPDATE patterns SET sequence_id=%s,setting_id=%s,task_id=%s,time_bid=%s,used_count=%s,"
                       "calls_count=%s,puts_count=%s,same_count=%s,trend=%s,range_max_change_cost=%s, "
                       "range_max_avg_change_cost=%s,call_max_change_cost=%s,put_max_change_cost=%s,"
                       "call_max_avg_change_cost=%s, put_max_avg_change_cost=%s, range_sum_max_change_cost=%s,"
                       "call_sum_max_change_cost=%s, put_sum_max_change_cost=%s, count_change_cost=%s,"
                       "delay=%s,expires=%s,history_num=%s,"
                       "created_at=%s, trend_max_call_count=%s, trend_max_put_count=%s WHERE id=%s",
                       (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.used_count,
                        self.calls_count, self.puts_count, self.same_count, self.trend, self.range_max_change_cost,
                        self.range_max_avg_change_cost, self.call_max_change_cost,
                        self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                        self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                        self.put_sum_max_change_cost, self.count_change_cost, self.delay,
                        self.expires, self.history_num, self.created_at, self.trend_max_call_count,
                        self.trend_max_put_count, self.id))
        Providers.db().commit()

    def calculation_cost_from_prediction(self, prediction):
        self.count_change_cost += 1

        self.range_sum_max_change_cost += prediction.range_max_change_cost
        self.range_max_change_cost = prediction.range_max_change_cost \
            if prediction.range_max_change_cost > self.range_max_change_cost else self.range_max_change_cost
        self.range_max_avg_change_cost = self.range_sum_max_change_cost / self.count_change_cost

        self.call_sum_max_change_cost += prediction.call_max_change_cost
        self.call_max_change_cost = prediction.call_max_change_cost \
            if prediction.call_max_change_cost > self.call_max_change_cost else self.call_max_change_cost
        self.call_max_avg_change_cost = self.call_sum_max_change_cost / self.count_change_cost

        self.put_sum_max_change_cost += prediction.put_max_change_cost
        self.put_max_change_cost = prediction.put_max_change_cost \
            if prediction.put_max_change_cost > self.put_max_change_cost else self.put_max_change_cost
        self.put_max_avg_change_cost = self.put_max_change_cost / self.count_change_cost

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.used_count, self.calls_count,
                    self.puts_count, self.same_count, self.trend, self.range_max_change_cost,
                    self.range_max_avg_change_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.call_max_avg_change_cost, self.put_max_avg_change_cost,
                    self.range_sum_max_change_cost, self.call_sum_max_change_cost,
                    self.put_sum_max_change_cost, self.count_change_cost,
                    self.delay, self.expires, self.history_num, self.created_at, self.trend_max_call_count,
                    self.trend_max_put_count))

    @staticmethod
    def model(raw=None):
        return Pattern(raw)

    @staticmethod
    def save_many(patterns: list):
        cursor = Providers.db().get_cursor()
        query = 'INSERT INTO patterns (sequence_id,setting_id,task_id,time_bid,used_count,calls_count,' + \
                'puts_count,same_count,trend,range_max_change_cost,' + \
                'range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,' + \
                'call_max_avg_change_cost, put_max_avg_change_cost,range_sum_max_change_cost,' + \
                'call_sum_max_change_cost, put_sum_max_change_cost,count_change_cost,' + \
                'delay,expires,history_num,created_at,trend_max_call_count,trend_max_put_count) VALUES ' + \
                ','.join(v.__tuple_str() for v in patterns) + \
                'ON CONFLICT (sequence_id,setting_id,time_bid,expires,history_num)' + \
                'DO UPDATE SET used_count=patterns.used_count + 1 RETURNING *'
        cursor.execute(query)
        Providers.db().commit()
        res = cursor.fetchall()
        if res:
            return res
        return []

    @staticmethod
    def upsert(task, sequence, time_bid):
        model = Pattern.make(task, sequence, time_bid)
        model.save()
        return model

    @staticmethod
    def make(task, sequence, time_bid):
        expires = 0
        max_duration = 0
        for expire in task.setting.analyzer_prediction_expire:
            if expire["history_duration"] <= sequence.duration:
                if expire["history_duration"] > max_duration:
                    max_duration = expire["history_duration"]
                    if expire["expire"] > 0:
                        model_for_expires = Pattern.get_last(sequence.id, time_bid['time'], task)
                        if model_for_expires and model_for_expires.check_on_expire():
                            expires = model_for_expires.expires
                        else:
                            expires = int(time.time()) + expire["expire"]
                    else:
                        expires = 0

        model = Pattern()
        model.sequence_id = sequence.id
        model.setting_id = task.setting.id
        model.task_id = task.id
        model.time_bid = time_bid['time']
        model.used_count = 1
        model.expires = expires
        model.task_id = task.id
        model.history_num = task.get_param("history_num")
        model.created_at = time.time()
        return model

    @staticmethod
    def get_last(sequence_id, time_bid, task):
        cursor = Providers.db().get_cursor()
        cursor.execute(
            "SELECT * FROM patterns WHERE sequence_id=%s AND setting_id=%s AND time_bid=%s AND history_num=%s "
            "ORDER BY created_at DESC LIMIT 1", (sequence_id, task.setting.id, time_bid,
                                                 task.get_param("history_num", 0)))

        model = cursor.fetchone()
        if model:
            return Pattern.model(model)

    @staticmethod
    def get_by_id(pk):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM patterns WHERE id=%s", [pk])
        row = cursor.fetchone()
        if row:
            return Pattern(row)

    @staticmethod
    def empty_table():
        cursor = Providers.db().get_cursor()
        cursor.execute("DELETE FROM patterns")
        Providers.db().commit()
