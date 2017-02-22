import time
import json

from providers.providers import Providers


class Pattern:
    id = None
    setting_id = None
    task_id = None
    time_bid = 0
    sequence = []
    sequence_duration = 0
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

    _is_work_for_signal = None

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
        cursor.execute("INSERT INTO patterns (setting_id,task_id,time_bid,sequence,sequence_duration,"
                       "used_count,calls_count,"
                       "puts_count,same_count,trend,range_max_change_cost, "
                       "range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,"
                       "call_max_avg_change_cost, put_max_avg_change_cost, range_sum_max_change_cost,"
                       "call_sum_max_change_cost, put_sum_max_change_cost, count_change_cost,"
                       "delay,expires,history_num,created_at,trend_max_call_count,trend_max_put_count) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                       "ON CONFLICT (sequence,setting_id,time_bid,expires,history_num)"
                       "DO UPDATE SET used_count=patterns.used_count + 1 RETURNING id",
                       (self.setting_id, self.task_id, self.time_bid, self.sequence, self.sequence_duration,
                        self.used_count,
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
        cursor.execute("UPDATE patterns SET setting_id=%s,task_id=%s,time_bid=%s,sequence=%s,"
                       "sequence_duration=%s,used_count=%s,"
                       "calls_count=%s,puts_count=%s,same_count=%s,trend=%s,range_max_change_cost=%s, "
                       "range_max_avg_change_cost=%s,call_max_change_cost=%s,put_max_change_cost=%s,"
                       "call_max_avg_change_cost=%s, put_max_avg_change_cost=%s, range_sum_max_change_cost=%s,"
                       "call_sum_max_change_cost=%s, put_sum_max_change_cost=%s, count_change_cost=%s,"
                       "delay=%s,expires=%s,history_num=%s,"
                       "created_at=%s, trend_max_call_count=%s, trend_max_put_count=%s WHERE id=%s",
                       (self.setting_id, self.task_id, self.time_bid, self.sequence, self.sequence_duration,
                        self.used_count,
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
        return str((self.setting_id, self.task_id, self.time_bid, self.sequence, self.sequence_duration,
                    self.used_count, self.calls_count,
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
        incr = 1
        if Providers.config().no_write:
            incr = 0
        cursor = Providers.db().get_cursor()
        query = 'INSERT INTO patterns (setting_id,task_id,time_bid,sequence,sequence_duration,' \
                'used_count,calls_count,' + \
                'puts_count,same_count,trend,range_max_change_cost,' + \
                'range_max_avg_change_cost,call_max_change_cost,put_max_change_cost,' + \
                'call_max_avg_change_cost, put_max_avg_change_cost,range_sum_max_change_cost,' + \
                'call_sum_max_change_cost, put_sum_max_change_cost,count_change_cost,' + \
                'delay,expires,history_num,created_at,trend_max_call_count,trend_max_put_count) VALUES ' + \
                ','.join(v.__tuple_str() for v in patterns) + \
                'ON CONFLICT (sequence,setting_id,time_bid,expires,history_num)' + \
                'DO UPDATE SET used_count=patterns.used_count + ' + str(incr) + ' RETURNING *'
        cursor.execute(query)
        Providers.db().commit()
        res = cursor.fetchall()
        if res:
            return res
        return []

    @staticmethod
    def make(task, sequence, time_bid, quotation):

        model = Pattern()
        model.sequence = sequence.string
        model.sequence_duration = sequence.duration
        model.setting_id = task.setting.id
        model.task_id = task.id
        model.time_bid = time_bid['time']
        model.used_count = 1
        model.task_id = task.id
        model.history_num = task.get_param("history_num")
        model.created_at = quotation.ts

        max_duration = 0
        for control in task.setting.analyzer_patterns_control:
            if control["sequence_min_duration"] <= model.sequence_duration:
                if control["sequence_min_duration"] > max_duration:
                    max_duration = control["sequence_min_duration"]
                    if control["expire"] > 0:
                        model_for_expires = Pattern.get_last_on_sequence(sequence, time_bid['time'], task)
                        if model_for_expires and model_for_expires.check_on_expire():
                            model.expires = model_for_expires.expires
                        else:
                            model.expires = int(time.time()) + control["expire"]
                    else:
                        model.expires = 0

        return model

    @staticmethod
    def check_on_min_work_time(task, pattern, sequence_duration, quotation):
        result = True
        max_duration = 0
        for control in task.setting.analyzer_patterns_control:
            if control["sequence_min_duration"] <= sequence_duration:
                if control["sequence_min_duration"] > max_duration:
                    max_duration = control["sequence_min_duration"]
                    if control["min_work_time"] > 0:
                        if quotation.ts - control["min_work_time"] >= pattern.created_at:
                            result = True
                        else:
                            result = False
        return result

    @staticmethod
    def get_last_on_sequence(sequence, time_bid, task):
        cursor = Providers.db().get_cursor()
        cursor.execute(
            "SELECT * FROM patterns WHERE sequence=%s AND setting_id=%s AND time_bid=%s AND history_num=%s "
            "ORDER BY created_at DESC LIMIT 1", (sequence, task.setting.id, time_bid,
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
    def empty_table(task):
        cursor = Providers.db().get_cursor()
        cursor.execute("DELETE FROM patterns WHERE history_num=%s AND setting_id=%s", [
            task.get_param("history_num", 0),
            task.setting_id
        ])
        Providers.db().commit()
