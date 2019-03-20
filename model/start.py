import sys
import model.db_util as util
import pymongo
from progressbar import ProgressBar

from model.Serializer import Serializer
from model.ModelFactory import ModelFactory


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        raise ValueError('No data-file path provided')

    ser = Serializer(filepath)
    ser.serialize_data()
    data = ser.get_models()
    insert_documents(data)


def insert_documents(data):
    """
    :param data: Is a list of serialized documents that should be inserted.
    :return: a list of conflict document ids.
    """
    factory = ModelFactory.get_instance()

    util.set_db(factory)

    """
    How we use MongoDB:
    We have 3 different collections:
        One for manual entries called "manual"
        One for production called "prod"
        One for the in_progress collection called "in_progress"

    After we have scraped we add all the scraped data into the collection "in_progress" and then
    we go through every entry in the "manual" collection and use that entry's ID to query both
    prod and in_progress collection. We compare the two contents in prod and in_progress to see
    if something changed from last time this was run and now. If they do not have the same
    content then we need to alert someone that the manual entry needs to be updated.

    When this is done in_progress will become our new prod.
    """

    factory.get_database().drop_collection("in_progress")

    print('Starting insertion of {} documents'.format(len(data)))
    pbar = ProgressBar()
    for i, doc in enumerate(pbar(data)):
        factory.post_document(doc, "in_progress")
    print('Successfully inserted {} documents'.format(i + 1))

    manual_documents = factory.get_collection("manual").find()

    # These are the IDs of the documents that are changed in manual and have been changed since
    # last time.
    conflict_ids = []
    for manual_document in manual_documents:
        if "id" in manual_document:
            id = manual_document["id"]
        else:
            continue

        factory.get_database().get_collection("in_progress").update({"id": id}, {"$set": {
            "manually_changed": True}})

        prod_match = factory.get_collection("prod").find({"id": id})
        in_progress_match = factory.get_collection("in_progress").find({"id": id})

        prod_match_doc = next(prod_match, None)
        in_progress_doc = next(in_progress_match, None)

        if prod_match_doc and in_progress_doc:
            if prod_match_doc['content'] != in_progress_doc['content']:
                conflict_ids.append({"conflict_id": id, "title": in_progress_doc["content"][
                    "title"]})

    print("Conflict IDs are", conflict_ids)
    # Set ID to be unique.
    factory.get_collection("conflict_ids").create_index([("conflict_id", 1)], unique=True)
    # Insert all the conflict ids into our collection.
    for conflict in conflict_ids:
        try:
            factory.post_document(conflict, "conflict_ids")
        except pymongo.errors.DuplicateKeyError:
            # Then we already know this is a conflict ID and should not be added again to the list.
            pass

    # Delete the backup prod and rename prod to prod2 and then rename in_progress to prod.
    factory.get_database().drop_collection("prod2")
    try:
        factory.get_database().get_collection("prod").rename("prod2")
    except pymongo.errors.OperationFailure:
        pass
    factory.get_database().get_collection("in_progress").rename("prod")

    util.set_index("in_progress", factory)
    util.set_index("prod", factory)
    util.set_index("manual", factory)

    return conflict_ids


if __name__ == '__main__':
    main()
