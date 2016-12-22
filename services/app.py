import providers.broker
import providers.database
import providers.cache
import providers.config


class App(object):

    def __init__(self):
        providers.config.get_config()
        providers.database.get_database()
        providers.cache.get_cache()
        providers.broker.get_broker()
        pass

    @staticmethod
    def start():
        App()
