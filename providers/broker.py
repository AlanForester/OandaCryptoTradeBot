import globals as gvars

from config import get_config


def get_broker():
    if not gvars.APP_BROKER:
        gvars.APP_BROKER = Broker()
    return gvars.APP_BROKER


class Broker:
    account_id, access_token, environment, instruments = None

    def __init__(self):
        config = get_config()
        self.account_id = config.get_broker_account_id()
        self.access_token = config.get_broker_access_token()
        self.environment = config.get_broker_environment()
        self.instruments = config.get_broker_instruments()
