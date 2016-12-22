class Active(object):
    id = None
    name = ""

    __raw_data = None

    def __init__(self, raw=None):
        if raw:
            self.__raw_data = raw

    @property
    def id(self):
        return self.__raw_data.id

    @property
    def name(self):
        return self.__raw_data.name

    @staticmethod
    def get_actives_dict(config, db):
        cursor = db.cursor()
        result_dict = {}
        for active_item in config.get_broker_instruments():
            cursor.execute("SELECT * FROM actives WHERE name=%s", [active_item])
            row = cursor.fetchone()
            if row:
                result_dict[active_item] = row.id
        return result_dict
