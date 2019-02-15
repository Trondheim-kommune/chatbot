from pymongo import TEXT
import os


# Create indexing based on three different keyword fields
# Set the default language to norwegian to map similar words
def set_index(collection, factory):
    factory.get_collection(collection).create_index(
        [("keywords", TEXT), ("content.keywords.keyword", TEXT),
         ("header_meta_keywords", TEXT)], default_language="norwegian")


def set_db(factory, ip="agent25.tinusf.com", db="dev_db"):
    factory.set_database(ip, db, str(os.getenv('DB_USER')), str(os.getenv("DB_PWD")))
