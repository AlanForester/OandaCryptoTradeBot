import providers.database
import providers.cache
import providers.config


class CoreModel(object):

    @property
    def db(self):
        return providers.database.get_database()

    @property
    def cache(self):
        return providers.cache.get_cache()

    @property
    def config(self):
        return providers.config.get_config()

