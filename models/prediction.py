

class Prediction(object):
    id = None
    pattern_id = None
    instrument_id = None
    time_bid = None
    time_left = None
    used_count = None
    calls_count = None
    puts_count = None
    last_call = None
    expires = None
    delay = None
    ts = None
    is_test = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def __tuple_str(self):
        return str((self.id, self.pattern_id, self.instrument_id, self.time_bid, self.time_left, self.used_count,
                    self.calls_count, self.puts_count, self.last_call, self.expires, self.delay, self.ts, self.is_test))

    @staticmethod
    def model(raw=None):
        return Prediction(raw)

