

class Prediction(object):
    id = None
    setting_id = None
    instrument_id = None
    time_bid = 0
    sequence = []
    sequence_hash = ""
    created_cost = 0
    expiration_cost = 0
    admission = 0.0
    change = 0.0
    expires = 0
    delay = 0
    created_at = 0
    expiration_at = 0
    task_id = 0

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def __tuple_str(self):
        return str((self.id, self.setting_id, self.instrument_id, self.time_bid, self.sequence, self.sequence_hash,
                    self.created_cost, self.expiration_cost, self.admission, self.change,
                    self.expires, self.delay, self.created_at, self.expiration_at, self.task_id))

    @staticmethod
    def model(raw=None):
        return Prediction(raw)

