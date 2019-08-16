import json
import os


class Config:
    __config = None

    @staticmethod
    def get_config():
        if Config.__config is None:
            Config()

        return Config.__config

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__config is not None:
            raise Exception("This class is a singleton!")
        else:
            f = open("chatbot/settings.json")
            file_raw = f.read()
            f.close()
            config = json.loads(file_raw)
            Config.__config = config

    @staticmethod
    def get_value(keys):
        """
        This is just a function aimed at making it easier to extract values
        from the settings file.
        :param keys: ["Mongo", "Url"]
        :return: The corresponding value to the keys. This might be a single
        value or part of the big settings dictionary.
        """
        val = Config.get_config()
        for key in keys:
            val = val[key]
        return val

    @staticmethod
    def get_mongo_db():
        """ Return the mongodb database to be used, given environment variables
        """
        Config.get_config()
        if str(os.getenv("DEBUG")) == "TRUE":
            return Config.get_value(["mongo", "dev_db"])
        else:
            return Config.get_value(["mongo", "prod_db"])

    @staticmethod
    def get_db_connection():
        """ Return the (url, port) of the mongodb database to be used """
        url = Config.get_value(["mongo", "url"])
        port = Config.get_value(["mongo", "port"])

        return url, port

    @staticmethod
    def get_mongo_db_credentials():
        """ Return (username, password) for mongodb database, given environment
        variables """

        Config.get_config()
        usr = None
        pwd = None
        if str(os.getenv("DEBUG")) == "TRUE":
            usr = Config.get_value(["mongo", "username"])
            pwd = Config.get_value(["mongo", "password"])
        else:
            usr = os.getenv("DB_USER")
            pwd = os.getenv("DB_PWD")

        return usr, pwd

    @staticmethod
    def get_mongo_collection(collection):
        """ Return the given collection string from settings file """
        return Config.get_value(["mongo", "collections", collection])
