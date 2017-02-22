import json
import hashlib

from providers.providers import Providers


class Sequence:
    id = None
    json = []
    duration = 0
    string = ""

    def __init__(self, raw=None):
        if raw:
            self.__dict__.update(raw._asdict())

    def get_string(self):
        string = ""
        i = 0
        for item in self.json:
            string += str(item["duration"]) + ":" + str(item["change"]) + ":" + str(item["granularity"])
            i += 1
            if len(self.json) > i:
                string += ","
        return string

    def get_duration(self):
        total_duration = 0
        for item in self.json:
            total_duration += item["duration"]
        return total_duration

    def __tuple_str(self):
        return str((json.dumps(self.json), self.get_duration()))

    @staticmethod
    def model(raw=None):
        return Sequence(raw)

    @staticmethod
    def make(sequence_json):
        sequence = Sequence()
        sequence.json = sequence_json
        sequence.duration = sequence.get_duration()
        sequence.string = sequence.get_string()
        return sequence

    @staticmethod
    def get_sequences_json(task, candles_with_parents):
        """
        Преобразует массив свечей с родителями в массив последовательностей
        :returns sequences: [{'duration': 5, 'potential': 144}, {'duration': 5, 'potential': 144}]
        """
        out = list()
        for candle in candles_with_parents:
            sequence = list()
            obj = dict()
            obj["duration"] = candle["duration"]

            if task.setting.analyzer_capacity_type == "potential":
                obj["change"] = int(candle["change_power"]
                                    / task.setting.analyzer_capacity_granularity)
            else:
                obj["change"] = int((candle["change"] / task.setting.instrument.pip)
                                    / task.setting.analyzer_capacity_granularity)

            obj["granularity"] = task.setting.analyzer_capacity_granularity
            sequence.append(obj)
            out.append(sequence)
            if "parents" in candle:
                parents = Sequence.get_sequences_json(task, candle["parents"])
                if len(parents) > 0:
                    for p in parents:
                        with_parents = sequence + p
                        out.append(with_parents)
        return out
