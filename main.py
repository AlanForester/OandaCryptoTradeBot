from services.app import App


def main():
    App.start()
    # global db
    # db = "dasf"
    # config = get_config()
    # oanda = oandapy.API(environment="practice",
    #                     access_token="45f9a222c095b8b7ca572e3bcb9bbc7c-41bff74ca04f0e6fb6ee42aa149682c3")
    #
    # response = oanda.get_prices(instruments="EUR_USD")
    # prices = response.get("prices")
    # asking_price = prices[0].get("ask")
    # print(asking_price)
    # account = "3370950"
    # stream = Streamer(environment="practice", access_token="2b18a96d7af1f8d98191eca470b67858-04fb6f5ecdac7ffd1fc06112f0166da5")
    # stream.rates(account, instruments="EUR_USD,USD_CAD")

    # stream = Streamer(environment="practice", access_token="45f9a222c095b8b7ca572e3bcb9bbc7c-41bff74ca04f0e6fb6ee42aa149682c3")
    # stream.events(ignore_heartbeat=False)


if __name__ == '__main__':
    main()
