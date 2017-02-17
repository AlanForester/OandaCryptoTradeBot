import providers.database
import providers.cache
import providers.config
import providers.telebot

class Providers(object):

    @staticmethod
    def db():
        return providers.database.get_database()

    @staticmethod
    def cache():
        return providers.cache.get_cache()

    @staticmethod
    def config():
        return providers.config.get_config()

    @staticmethod
    def telebot():
        return providers.telebot.get_telebot()

