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
    last_call = 0
    max_change = 0
    min_change = 0
    delay = 0
    expires = 0
    history_num = 0
    created_at = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def check_on_expire(self):
        return self.expires > int(time.time())

    def update_used_counter(self):
        cursor = Providers.db().get_cursor()
        cursor.execute(
            "UPDATE patterns SET used_count=used_count+1 "
            "WHERE id=%s", (self.id,))

    def save(self):
        cursor = Providers.db().get_cursor()
        cursor.execute("INSERT INTO patterns (sequence_id,setting_id,task_id,time_bid,used_count,calls_count,"
                       "puts_count,same_count,last_call,max_change,min_change,delay,expires,history_num,created_at) "
                       "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                       "ON CONFLICT (sequence_id,setting_id,time_bid,expires,history_num)"
                       "DO UPDATE SET used_count=patterns.used_count + 1 RETURNING id",
                       (self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.used_count,
                        self.calls_count, self.puts_count, self.same_count, self.last_call, self.max_change,
                        self.min_change, self.delay, self.expires, self.history_num, self.created_at))
        row = cursor.fetchone()
        if row:
            self.id = row.id
        return self

    def __tuple_str(self):
        return str((self.sequence_id, self.setting_id, self.task_id, self.time_bid, self.used_count, self.calls_count,
                    self.puts_count, self.same_count, self.last_call, self.max_change, self.min_change,
                    self.delay, self.expires, self.history_num, self.created_at))

    @staticmethod
    def model(raw=None):
        return Pattern(raw)

    @staticmethod
    def upsert(task, sequence, time_bid):
        model = None
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
            model = Pattern.get_last(sequence.id, time_bid, task)

            if model and model.check_on_expire():
                model.update_used_counter()
                is_update = True

        if not is_update:
            model = Pattern()
            model.sequence_id = sequence.id
            model.setting_id = task.setting.id
            model.task_id = task.id
            model.time_bid = time_bid
            model.used_count = 1
            model.expires = expires
            model.task_id = task.id
            model.history_num = task.get_param("history_num")
            model.created_at = time.time()
            model.save()
        Providers.db().commit()
        return model

    @staticmethod
    def get_last(sequence_id, time_bid, task):
        cursor = Providers.db().get_cursor()
        cursor.execute(
            "SELECT * FROM patterns WHERE sequence_id=%s AND setting_id=%s AND time_bid=%s AND history_num=%s "
            "ORDER BY ts DESC LIMIT 1", (sequence_id, task.setting.instrument_id, time_bid,
                                         task.get_param("history_num")))

        model = cursor.fetchone()
        if model:
            return Pattern.model(model)
