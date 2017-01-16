

class Signal:
    id = None
    instrument_id = None
    sequence_id = None
    setting_id = None
    task_id = None
    created_at = 0
    expiration_at = 0
    closed_at = 0
    direction = 0
    created_cost = 0.0
    projected_cost = 0.0
    expiration_cost = 0.0
    max_cost = 0.0
    min_cost = 0.0
    time_bid = 0
    change = 0.0
    drawdown = 0.0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def __tuple_str(self):
        return str((self.instrument_id, self.sequence_id, self.setting_id, self.task_id, self.created_at,
                    self.expiration_at, self.closed_at, self.direction, self.created_cost, self.projected_cost,
                    self.expiration_cost, self.max_cost, self.min_cost, self.time_bid, self.change, self.drawdown))

    @staticmethod
    def model(raw=None):
        return Signal(raw)



