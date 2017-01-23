import oandapy
import time

from api.stream.quotations import Quotations
from datetime import datetime
from providers.config import get_config
from models.quotation import Quotation


class Api(object):
    api = None
    account_id = None
    instruments = None
    environment = None
    access_token = None
    stream = None

    def __init__(self):
        config = get_config()
        self.account_id = config.get_broker_account_id()
        self.environment = config.get_broker_environment()
        self.access_token = config.get_broker_access_token()
        self.api = oandapy.API(**{
            "environment": config.get_broker_environment(),
            "access_token": config.get_broker_access_token(),
        })

    def get_instruments(self):
        return self.api.get_instruments(self.account_id)["instruments"]

    def quotations_stream(self, quotation, instrument):
        self.stream = Quotations(quotation, 0, environment=self.environment, access_token=self.access_token)
        self.stream.rates(self.account_id, instrument.instrument)

    def get_history(self, instrument, start_ts, end_ts, granularity="S5"):
        max_count = 5000
        delta_ts = end_ts - start_ts
        delta_candles_count = int(delta_ts / 5)
        quotations = {}
        while delta_candles_count > 0:
            if delta_candles_count >= max_count:
                count = max_count
            else:
                count = delta_candles_count
            start = datetime.utcfromtimestamp(start_ts).strftime("%Y-%m-%dT%H-%M-%S")
            candles = self.api.get_history(
                instrument=instrument.instrument,
                candleFormat="bidask",
                granularity=granularity,
                count=count,
                start=start
            )
            if candles and len(candles["candles"]) > 0:
                for candle in candles["candles"]:
                    quotation = Quotation
                    quotation.ts = int(
                        time.mktime(datetime.strptime(candle["time"], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()))
                    quotation.instrument_id = instrument.id
                    quotation.ask = (candle["highAsk"] + candle["lowAsk"]) / 2
                    quotation.bid = (candle["highBid"] + candle["lowBid"]) / 2
                    quotation.value = (((candle["openBid"] + candle["openAsk"]) / 2) +
                                       ((candle["closeBid"] + candle["closeAsk"]) / 2)) / 2

                    if quotation.ts not in quotations:
                        quotations[quotation.ts] = quotation

            start_ts += count * 5
            delta_candles_count -= count
            print(len(quotations), start_ts, count)
            time.sleep(1)
            
        result = []
        if len(quotations) > 0:
            for k, v in quotations.items():
                result.append(v)
        return result
