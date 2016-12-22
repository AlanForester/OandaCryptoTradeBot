import psycopg2
import providers.globals as gvars

from providers.config import get_config
from psycopg2.extras import NamedTupleCursor


def get_database():
    if not gvars.APP_DB:
        gvars.APP_DB = Database()
    return gvars.APP_DB


class Database:
    username = None
    password = None
    hostname = None
    port = None
    database = None

    _connection = None

    def __init__(self):
        config = get_config()
        self.username = config.get_postgres_username()
        self.password = config.get_postgres_password()
        self.hostname = config.get_postgres_hostname()
        self.port = config.get_postgres_port()
        self.database = config.get_postgres_database()

        self.connect()

    def connect(self):
        self._connection = psycopg2.connect(
            database=self.database,
            user=self.username,
            host=self.hostname,
            password=self.password,
            cursor_factory=NamedTupleCursor
        )

    def get_connection(self):
        return self._connection

    def get_cursor(self):
        return self._connection.cursor()

    def commit(self):
        return self._connection.commit()


