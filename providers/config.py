import argparse
import json


class Config:
    config_path = ""

    def __init__(self):
        self._parse_args()

    def _parse_args(self):
        """
        Parse commandline arguments.

        :returns: Instance of :class:`argparse.Namespace`.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-c", "--config_path", dest="config_path", type=str, required=True,
            help="Path to configuration file."
        )

        args = parser.parse_args()
        self.config_path = args.config_path

    def parse_config(self):
        """
        Obtain config from configuration file.

        :param self.config_path: Path of the configuation file.

        :returns: The config object.
        """
        config_params = Params()
        config_params.load_config(self.config_path)
        return config_params


class Params(object):

    def __init__(self):
        self.__config_data = {}

    @property
    def config_data(self):
        return self.__config_data

    @property
    def _broker_settings(self):
        return self.__config_data.setdefault("broker", {})

    def get_broker_account_id(self):
        return self._broker_settings["account_id"]

    def get_broker_access_token(self):
        return self._broker_settings["access_token"]

    """Постгрес конфиг"""
    @property
    def _postgres_settings(self):
        return self.__config_data.setdefault("postgres", {})

    def get_db_postgres_username(self):
        return self._postgres_settings["username"]

    def get_db_postgres_password(self):
        return self._postgres_settings["password"]

    def get_db_postgres_hostname(self):
        return self._postgres_settings["hostname"]

    def get_db_postgres_port(self):
        return self._postgres_settings["port"]

    def get_db_postgres_database(self):
        return self._postgres_settings["database"]

    """Редис конфиг"""
    @property
    def _redis_settings(self):
        return self.__config_data.setdefault("redis", {})

    def get_db_redis_db(self):
        return self._redis_settings["db"]

    def set_db_redis_hostname(self, db_redis_hostname):
        self._redis_settings["hostname"] = db_redis_hostname

    def get_db_redis_port(self):
        return self._redis_settings["port"]

    """Загрузка файла"""
    def load_config(self, config_path):
        with open(config_path, "rb") as config_file:
            self.__config_data = json.load(config_file)
