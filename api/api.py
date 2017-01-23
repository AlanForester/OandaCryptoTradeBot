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
        print(start_ts, end_ts)
        delta_ts = end_ts - start_ts
        delta_candles_count = int(delta_ts / 5)
        quotations = []
        while delta_candles_count > 0:
            if delta_candles_count >= 5000:
                count = 5000
            else:
                count = delta_candles_count
            start = datetime.utcfromtimestamp(start_ts).strftime("%Y-%m-%dT%H-%M-%S")
            params = {
                "instrument": instrument.instrument,
                "count": count,
                "candleFormat": "bidask",
                "granularity": granularity,
                "start": start
            }
            candles = self.api.get_history(**params)

            if candles:
                last_time = start_ts
                print(start_ts, len(candles["candles"]))
                for candle in candles["candles"]:
                    quotation = Quotation
                    quotation.ts = int(time.mktime(datetime.strptime(candle["time"], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()))
                    quotation.instrument_id = instrument.id
                    quotation.ask = (candle["highAsk"] + candle["lowAsk"]) / 2
                    quotation.bid = (candle["highBid"] + candle["lowBid"]) / 2
                    quotation.value = (((candle["openBid"] + candle["openAsk"]) / 2) +
                                       ((candle["closeBid"] + candle["closeAsk"]) / 2)) / 2

                    quotations.append(quotation)
                    last_time = quotation.ts
                    if quotation.ts >= end_ts:
                        print("Break")
                        break

                start_ts = last_time
                print(start_ts)
            else:
                start_ts -= count * 5
            delta_candles_count -= count
            #print(len(quotations), start_ts, count)
        return quotations
