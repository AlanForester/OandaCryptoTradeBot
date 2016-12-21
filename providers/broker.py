from config import Params as ConfigParams


def get_broker(config):
    return Broker(config)


class Broker:
    account_id, access_token, environment, instruments = None

    def __init__(self, config: ConfigParams):
        self.account_id = config.get_broker_account_id()
        self.access_token = config.get_broker_access_token()
        self.environment = config.get_broker_environment()
        self.instruments = config.get_broker_instruments()
