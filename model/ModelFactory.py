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

    def set_database(self, ip, db_name, username, password, port):
        """ Sets up conncetion to given database"""
        client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/{}"
                                     .format(username, password,
                                             ip, port, db_name)
                                     )
        self.database = client[db_name]

    def get_document(self, query, main_collection="prod", manual_collection="manual",
                     number_of_docs=30):
        """
        Searches for documents using MongoDB in a given document collection.
        Get 15 results from prod. Get 15 from Manual.
        Go through every doc in prod and delete the ones with manually_changed=true.
        Then return every remaining document, remember it's not sorted now, but for what we need
        it for this is not necessary.
        """
        main_col = self.get_collection(main_collection)
        cursor = main_col.find({'$text': {'$search': query}}, {'score': {'$meta': 'textScore'}})
        # Sort and retrieve some of the top scoring documents.
        cursor.sort([('score', {'$meta': 'textScore'})]).limit(number_of_docs)

        docs = []
        for doc in cursor:
            if doc["manually_changed"] is False:
                docs.append(doc)

        manual_col = self.get_collection(manual_collection)
        cursor = manual_col.find({'$text': {'$search': query}}, {'score': {'$meta': 'textScore'}})
        # Sort and retrieve some of the top scoring documents.
        cursor.sort([('score', {'$meta': 'textScore'})]).limit(number_of_docs)
        for doc in cursor:
            docs.append(doc)

        return docs

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
