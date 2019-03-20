from pymongo import TEXT
import os
from util.config_util import Config


# Create indexing based on three different keyword fields
# Set the default language to norwegian to map similar words
def set_index(collection, factory):
    factory.get_collection(collection).create_index(
        [("keywords", TEXT), ("content.keywords.keyword", TEXT),
         ("header_meta_keywords", TEXT)], default_language="norwegian")


def set_db(factory):
    url = Config.get_value(["mongo", "url"])
    port = Config.get_value(["mongo", "port"])
    db = Config.get_mongo_db()

    factory.set_database(url, db, str(os.getenv('DB_USER')), str(os.getenv("DB_PWD")), port=port)


# If the document with the same ID is previously manually changed, return the manually changed
# document
def check_manually_changed(factory, document):
    if document["manually_changed"]:
        id = document["id"]
        return next(factory.get_database().get_collection("manual").find({"id": id}), None)
    else:
        return document
