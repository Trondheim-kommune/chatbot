import pymongo
import os

from bson import json_util

class ModelFactory:

    __instance = None
    __database = None

    @staticmethod 
    def get_instance():
        """ Static access method. """
        if ModelFactory.__instance == None: 
            ModelFactory()
        return ModelFactory.__instance
    
    def __init__(self):
        """ Virtually private constructor. """
        if ModelFactory.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ModelFactory.__instance = self 

    def set_database(self, ip, db_name, username, password, port=27017):
        """ Sets up conncetion to given database"""
        client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/{}"
                                        .format(username, password, ip, port, db_name)
                                    )
        self.database = client[db_name]
    
    # TODO: some validation on response to make sure everything is posted
    def post_document(self, data, collection):
        """ Posts JSON data to colletion in db """
        col = self.database[collection]
        data = json_util.loads(data)
        response = col.insert_one(data)


if __name__ == "__main__":
    fact = ModelFactory.get_instance()
    db = fact.set_database("agent25.tinusf.com", "test_db", 
            str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    with open('schema/example_data.json') as f:
        data =  f.read()
    fact.post_document(data, "site")
