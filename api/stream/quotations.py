import oandapy
import time

from models.quotation import Quotation


class Quotations(oandapy.Streamer):
    quotation = Quotation

    def __init__(self, quotation, count=0, *args, **kwargs):
        super(Quotations, self).__init__(*args, **kwargs)
        self.count = count
        self.reccnt = 0
        self.quotation = quotation

    def on_success(self, data):
        if "tick" in data:
            tick = data["tick"]
            self.quotation.ask = tick["ask"]
            self.quotation.bid = tick["bid"]
            self.quotation.ts = int(time.time())
            self.quotation.value = (tick["ask"] + tick["bid"]) / 2
        self.reccnt += 1
        if self.reccnt == self.count:
            self.disconnect()

    def on_error(self, data):
        print("Stream error:", data)
        self.disconnect()
