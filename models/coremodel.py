import providers.database
import providers.cache
import providers.config


class CoreModel(object):
    table_name = None
    __raw_data = None

    @property
    def db(self):
        return providers.database.get_database()

    @property
    def cache(self):
        return providers.cache.get_cache()

    @property
    def config(self):
        return providers.config.get_config()

    def load(self, raw):
        self.__raw_data = raw

    def find_by_id(self, pk):
        result = None
        if self.table_name:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM "+self.table_name+" WHERE id=%s", [pk])
            row = cursor.fetchone()
            if row:
                result = row
        return result
