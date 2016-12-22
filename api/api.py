from providers.config import get_config
import oandapy


class Api(object):
    api = None
    account_id = None
    instruments = None

    def __init__(self):
        config = get_config()
        self.account_id = config.get_broker_account_id()
        self.instruments = config.get_broker_instruments()
        self.api = oandapy.API(**{
            "environment": config.get_broker_environment(),
            "access_token": config.get_broker_access_token(),
        })

    def get_instruments(self):
        return self.api.get_instruments(self.account_id)["instruments"]


