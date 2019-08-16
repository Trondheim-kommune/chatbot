import sys

import pymongo

from progressbar import ProgressBar

from chatbot.model.serializer import Serializer
from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        raise ValueError("No data-file path provided")

    ser = Serializer(filepath)
    ser.serialize_data()
    data = ser.get_models()
    insert_documents(data)


def insert_documents(data):
    """ Insert all provided documents. Checks if the document has been manually
    changed before - if it has, and the new document does not match, it is
    marked as a conflict """
    factory = ModelFactory.get_instance()
    factory.set_db()

    temp_col = Config.get_mongo_collection("temp_scraped")
    manual_col = Config.get_mongo_collection("manual")
    unknown_col = Config.get_mongo_collection("unknown")
    prod_col = Config.get_mongo_collection("prod")
    conflict_col = Config.get_mongo_collection("conflicts")

    print("Starting insertion of {} documents".format(len(data)))
    pbar = ProgressBar()
    for i, doc in enumerate(pbar(data)):
        factory.post_document(doc, temp_col)
    print("Successfully inserted {} documents".format(i + 1))

    manual_docs = factory.get_collection(manual_col).find()

    conflicts = []
    for manual_doc in manual_docs:
        if "id" in manual_doc:
            idx = manual_doc["id"]
        else:
            continue

        # Mark corresponding entry in temp collection as manually changed
        factory.get_database() \
               .get_collection(temp_col) \
               .update_one({"id": idx}, {"$set": {"manually_changed": True}})

        prod_doc = next(factory.get_collection(prod_col).find({"id": idx}),
                        None)
        temp_doc = next(factory.get_collection(temp_col).find({"id": idx}),
                        None)

        if prod_doc and temp_doc:
            if temp_doc["content"] != prod_doc["content"]:
                title = temp_doc["content"]["title"]
                conflicts.append({"conflict_id": idx,
                                  "title": title})

    print("Conflicts: {}".format(conflicts))
    factory.get_collection(conflict_col).create_index([("conflict_id", 1)],
                                                      unique=True)
    for conflict in conflicts:
        try:
            factory.post_document(conflict, conflict_col)
        except pymongo.errors.DuplicateKeyError:
            # In case there are dupliacte, unsolved conflicts
            pass

    # Update production collection
    db = factory.get_database()
    try:
        db.get_collection(prod_col).rename("old_prod")
    except pymongo.errors.OperationFailure:
        # If the prod collection does not exist
        pass

    try:
        db.get_collection(temp_col).rename(prod_col)
    except Exception as e:
        print("Failed to update production db collection")
        print(e)
        db.get_collection("old_prod").rename(prod_col)
    finally:
        db.get_collection("old_prod").drop()
        db.get_collection(temp_col).drop()

    # Update all indexes
    factory.set_index(prod_col)
    factory.set_index(manual_col)
    factory.set_index(temp_col)
    # Removes duplicates
    factory.get_collection(unknown_col).create_index([("query_text", 1)],
                                                     unique=True)

    if not conflicts:
        factory.get_collection(conflict_col).drop()

    return conflicts


if __name__ == "__main__":
    main()
