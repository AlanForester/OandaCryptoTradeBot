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
    closed_discrepancy_cost = 0
    closed_change_cost = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def save(self):
        cursor = Providers.db().get_cursor()
        row = cursor.execute("INSERT INTO signals (instrument_id,sequence_id,setting_id,task_id,"
                             "pattern_id,created_at,expiration_at,direction,created_cost,expiration_cost,"
                             "closed_cost,max_cost,min_cost,call_max_change_cost,put_max_change_cost,time_bid,"
                             "history_num, closed_discrepancy_cost, closed_change_cost) "
                             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                             (self.instrument_id, self.sequence_id, self.setting_id, self.task_id,
                              self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                              self.expiration_cost, self.closed_cost, self.max_cost, self.min_cost,
                              self.call_max_change_cost, self.put_max_change_cost, self.time_bid, self.history_num,
                              self.closed_discrepancy_cost, self.closed_change_cost))

        Providers.db().commit()
        if row:
            self.id = row.id
            return self

    def __tuple_str(self):
        return str((self.instrument_id, self.sequence_id, self.setting_id, self.task_id,
                    self.pattern_id, self.created_at, self.expiration_at, self.direction, self.created_cost,
                    self.expiration_cost, self.closed_cost, self.max_cost, self.min_cost, self.call_max_change_cost,
                    self.put_max_change_cost, self.time_bid, self.history_num, self.closed_discrepancy_cost,
                    self.closed_change_cost))

    @staticmethod
    def model(raw=None):
        return Signal(raw)

    @staticmethod
    def update_close_cost(task, quotation):
        cursor = Providers.db().get_cursor()
        cursor.execute("UPDATE signals SET closed_cost=%s, closed_discrepancy_cost=%s-expiration_cost, "
                       "closed_change_cost=%s-created_cost WHERE expiration_at<=%s "
                       "AND closed_cost=0 AND task_id=%s RETURNING *",
                       (quotation.value, quotation.value, quotation.value,
                        quotation.ts, task.id))
        Providers.db().commit()
        signals_updated = cursor.fetchall()
        if task.get_param("history_num") == 0:
            for signal in signals_updated:
                Providers.telebot().send_signal(task.setting.instrument.instrument + ": "
                                                + "Закрыт сигнал: " + ("put" if signal.direction == -1 else "call")
                                                + ". Цена " + str(round(signal.created_cost, 5))
                                                + " изменилась на " + str(round(signal.closed_change_cost, 5))
                                                + " с прогнозом " + str(round(signal.expiration_cost, 5))
                                                + " и стала " + str(round(signal.closed_cost, 5)))

    @staticmethod
    def empty_table():
        cursor = Providers.db().get_cursor()
        cursor.execute("DELETE FROM signals")
        Providers.db().commit()

    @staticmethod
    def get_success_percent(task):
        cursor = Providers.db().get_cursor()
        cursor.execute("SELECT * FROM signals WHERE history_num=%s AND closed_cost > 0 AND setting_id=%s", [
            task.get_param("history_num", 0),
            task.setting_id
        ])
        signals = cursor.fetchall()
        success = []
        for signal in signals:
            if signal.direction == -1 and signal.closed_change_cost < 0:
                success.append(signal)
            if signal.direction == 1 and signal.closed_change_cost > 0:
                success.append(signal)
        chance = 0
        if len(signals) > 0:
            chance = round(len(success)/len(signals)*100, 4)
        return chance
