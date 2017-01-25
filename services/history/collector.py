import time

from api.api import Api
from datetime import datetime
from models.quotation import Quotation
from helpers.exthread import ExThread
from models.candle import Candle


class Collector:
    quotation = Quotation()

    def __init__(self, task):
        self.task = task
        self.api = Api()
        history = self.get_quotations()
        self.insert_history(history)

    def insert_history(self, history):
        insert_pack = []
        counter = 0
        inserted_count = self.task.get_param("collector_inserted_quotations")
        if not inserted_count:
            inserted_count = 0

        for item in history:
            counter += 1
            insert_pack.append(item)
            if (len(insert_pack) == 100) or (counter == len(history) and len(insert_pack) > 0):
                ts_array = Quotation.save_many(insert_pack)
                insert_pack = []
                inserted_count += len(ts_array)
                if len(ts_array) > 0:
                    # Создаем свечи
                    for row in ts_array:
                        self.save_candles(row.ts)
                self.task.update_status("collector_inserted_quotations", inserted_count)

    def get_quotations(self):
        start = self.task.get_param("start")
        end = self.task.get_param("end")
        return self.collect_history(start, end)

    def collect_history(self, start_ts, end_ts, granularity="S5"):
        max_count = 500
        delta_ts = end_ts - start_ts
        delta_candles_count = int(delta_ts / 5)

        self.task.update_status("collector_total_quotations", delta_candles_count)

        quotations = {}
        threads = []
        while delta_candles_count > 0:
            ExThread.wait_threads(threads, 1)

            if delta_candles_count >= max_count:
                count = max_count
            else:
                count = delta_candles_count
            start = datetime.utcfromtimestamp(start_ts).strftime("%Y-%m-%dT%H-%M-%S")

            thread = ExThread(target=self._fetch_candles, args=(
                self.task.setting.instrument,
                granularity,
                count,
                start,
                quotations
            ))
            thread.task = self.task
            thread.start()
            threads.append(thread)

            start_ts += count * 5
            delta_candles_count -= count

        ExThread.wait_threads(threads, 0)
        result = []

        self.task.update_status("collector_total_quotations", len(quotations))
        if len(quotations) > 0:
            q_keys = quotations.keys()
            for k in sorted(q_keys):
                result.append(quotations[k])

        return result

    def _fetch_candles(self, instrument, granularity, count, start, quotations):
        candles = self.api.get_history(
            instrument=instrument.instrument,
            candleFormat="bidask",
            granularity=granularity,
            count=count,
            start=start
        )
        if candles and len(candles["candles"]) > 0:
            for candle in candles["candles"]:
                quotation = Quotation()
                quotation.ts = int(
                    time.mktime(datetime.strptime(candle["time"], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()))
                quotation.instrument_id = instrument.id
                quotation.ask = (candle["highAsk"] + candle["lowAsk"]) / 2
                quotation.bid = (candle["highBid"] + candle["lowBid"]) / 2
                quotation.value = (((candle["openBid"] + candle["openAsk"]) / 2) +
                                   ((candle["closeBid"] + candle["closeAsk"]) / 2)) / 2

                if quotation.ts not in quotations:
                    quotations[str(quotation.ts)] = quotation

            self.task.update_status("collector_received_quotations", len(quotations))

    def save_candles(self, ts):
        candles = []
        candles_durations = self.task.setting.candles_durations
        for duration in candles_durations:
            candle = Candle.make(ts, duration, self.task.setting.instrument_id)
            candles.append(candle)
        Candle.save_many(candles)
