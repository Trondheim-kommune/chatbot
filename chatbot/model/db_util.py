

# If the document with the same ID is previously manually changed, return the
# manually changed document
def check_manually_changed(factory, document):
    if document["manually_changed"]:
        id = document["id"]
        return next(factory.get_database()
                           .get_collection("manual")
                           .find({"id": id}), None)
    else:
        return document
