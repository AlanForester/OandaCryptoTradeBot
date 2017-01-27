import psycopg2
import providers.globals as gvars

from providers.config import get_config
from psycopg2.extras import NamedTupleCursor


def get_database():
    if not gvars.APP_DB:
        gvars.APP_DB = Database()
    return gvars.APP_DB


class Database:
    connections_count = 5
    connection_used = 0

    username = None
    password = None
    hostname = None
    port = None
    database = None

    _connections = []

    def __init__(self):
        config = get_config()
        self.username = config.get_postgres_username()
        self.password = config.get_postgres_password()
        self.hostname = config.get_postgres_hostname()
        self.port = config.get_postgres_port()
        self.database = config.get_postgres_database()

        i = 0
        while i < self.connections_count:
            self._connections.append(self.connect())
            i += 1

    def connect(self):
        con = psycopg2.connect(
            database=self.database,
            user=self.username,
            host=self.hostname,
            password=self.password,
            cursor_factory=NamedTupleCursor
        )
        con.autocommit = True
        return con

    def get_cursor(self):
        cursor = self._connections[self.connection_used].cursor()
        if self.connection_used >= len(self._connections) - 1:
            self.connection_used = 0
        return cursor

    def commit(self):
        return False
