import oandapy


class Streamer(oandapy.Streamer):
    def __init__(self, count=10, *args, **kwargs):
        super(Streamer, self).__init__(*args, **kwargs)
        self.count = count
        self.reccnt = 0

    def on_success(self, data):
        print(data, "\n")
        self.reccnt += 1
        if self.reccnt == self.count:
            self.disconnect()

    def on_error(self, data):
        print("Stream disconnect")
        self.disconnect()
