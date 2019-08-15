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
        This is just a function aimed at making it easier to extract values from the settings file.
        :param keys: ["Mongo", "Url"]
        :return: The corresponding value to the keys. This might be a single value or part of
        the big settings dictionary.
        """
        val = Config.get_config()
        for key in keys:
            val = val[key]
        return val

    @staticmethod
    def get_mongo_db():
        Config.get_config()
        if os.getenv("TEST_FLAG"):
            return Config.get_value(["mongo", "testing_db"])
        else:
            return Config.get_value(["mongo", "db"])
