

class Pattern(object):
    id = None
    parent_id = None
    last = None
    admission = None
    duration = None
    first = None

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def __tuple_str(self):
        return str((self.id, self.parent_id, self.last, self.admission, self.duration, self.first))

    @staticmethod
    def model(raw=None):
        return Pattern(raw)

    @staticmethod
    def get_sequences(candles_with_parents, admissions):
        """
        Преобразует массив свечей с родителями в массив последовательностей
        :returns sequences: [{'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 5, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 10, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 15, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 30, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 60, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 120, 'admission': 144}]
        [{'duration': 5, 'admission': 144}, {'duration': 300, 'admission': 34}]
        [{'duration': 10, 'admission': 144}]....
        """
        out = list()
        for candle in candles_with_parents:
            sequence = list()
            obj = dict()
            obj["duration"] = candle["duration"]
            # obj["till_ts"] = candle["till_ts"]
            # obj["from_ts"] = candle["from_ts"]
            # obj["change_power"] = candle["change_power"]
            for admission in admissions:
                if candle["change_power"] <= admission:
                    obj["admission"] = admission
                    break

            if not "admission" in obj:
                obj["admission"] = int(candle["change_power"] / 100) * 100

            sequence.append(obj)
            out.append(sequence)
            if "parents" in candle:
                parents = Pattern.get_sequences(candle["parents"], admissions)
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out
