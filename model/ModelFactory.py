import pymongo
from bson import json_util


class ModelFactory:

    __instance = None
    __database = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ModelFactory.__instance is None:
            ModelFactory()
        return ModelFactory.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ModelFactory.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ModelFactory.__instance = self

    def set_database(self, ip, db_name, username, password, port=27017):
        """ Sets up conncetion to given database"""
        client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/{}"
                                     .format(username, password,
                                             ip, port, db_name)
                                     )
        self.database = client[db_name]

    def get_document(self, query, collection):
        """ Takes a dictionary and checks if all fields in dictionary matches
        the same fields in a document. If so, returns the document """
        col = self.get_collection(collection)
        cursor = col.find(
            {'$text': {'$search': query}}, {'score': {'$meta': "textScore"}}
        )

        # Sort and retrieve the one top scored document
        cursor.sort([('score', {'$meta': "textScore"})]).limit(1)

        # Return first (highest score) document
        for c in cursor:
            return c

        return None

    # TODO: some validation on response to make sure everything is posted
    def post_document(self, data, collection):
        """ Posts JSON data to colletion in db """
        col = self.get_collection(collection)

        # Converts the data correctly if not a dict (str)
        if not isinstance(data, dict):
            data = json_util.loads(data)

        response = col.insert_one(data)
        return response  # TODO: Fix

    def update_document(self, query, data, collection):
        """ Updates the document specified in query with the new data """
        col = self.get_collection(collection)
        data = json_util.loads(data)
        col.find_one_and_update({"$and": [query]}, {"$set": data})

    def get_collection(self, collection):
        return self.database[collection]

    def get_database(self):
        return self.database
