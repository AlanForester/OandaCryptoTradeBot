import redis
import providers.globals as gvars

from providers.config import get_config


def get_cache():
    if not gvars.APP_CACHE:
        gvars.APP_CACHE = Cache()
    return gvars.APP_CACHE


class Cache:
    db = None
    hostname = None
    port = None

    _connection = None

    def __init__(self):
        config = get_config()
        self.db = config.get_redis_db()
        self.hostname = config.get_redis_hostname()
        self.port = config.get_redis_port()

        self.connect()

    def connect(self):
        self._connection = redis.StrictRedis(
            host=self.hostname,
            port=self.port,
            db=self.db
        )

    def get_connection(self):
        return self._connection

    def delete(self, key):
        return self._connection.delete(key)

    def keys(self, key):
        return self._connection.keys(key)

    def get(self, key):
        return self._connection.get(key)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self._connection.set(name, value, ex, px, nx, xx)

    def setex(self, name, time, value):
        return self._connection.setex(name, time, value)

    def exists(self, name):
        return self._connection.exists(name)
