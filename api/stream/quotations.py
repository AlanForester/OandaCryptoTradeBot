import oandapy


class Quotations(oandapy.Streamer):

    def __init__(self, quotation, count=0, *args, **kwargs):
        super(Quotations, self).__init__(*args, **kwargs)
        self.count = count
        self.reccnt = 0
        self.quotation = quotation

    def on_success(self, data):
        print(data)
        self.reccnt += 1
        if self.reccnt == self.count:
            self.disconnect()

    def on_error(self, data):
        print("Stream error:", data)
        self.disconnect()
