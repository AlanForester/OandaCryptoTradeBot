import oandapy
import psycopg2
from psycopg2.extras import NamedTupleCursor


def main():
    db = psycopg2.connect(
        database="iqfx",
        user="postgres",
        host="localhost",
        password="",
        cursor_factory=NamedTupleCursor
    )
    oanda = oandapy.API(environment="practice",
                        access_token="45f9a222c095b8b7ca572e3bcb9bbc7c-41bff74ca04f0e6fb6ee42aa149682c3")

    response = oanda.get_prices(instruments="EUR_USD")
    prices = response.get("prices")
    asking_price = prices[0].get("ask")
    print(asking_price)
    # account = "12345"
    # stream = Streamer(environment="practice", access_token="45f9a222c095b8b7ca572e3bcb9bbc7c-41bff74ca04f0e6fb6ee42aa149682c3")
    # stream.rates(account, instruments="EUR_USD")

    # stream = Streamer(environment="practice", access_token="45f9a222c095b8b7ca572e3bcb9bbc7c-41bff74ca04f0e6fb6ee42aa149682c3")
    # stream.events(ignore_heartbeat=False)


if __name__ == '__main__':
    main()
