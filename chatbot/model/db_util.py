from chatbot.util.config_util import Config


# If the document with the same ID is previously manually changed, return the
# manually changed document
def check_manually_changed(factory, document):
    if document["manually_changed"]:
        id = document["id"]
        manual_col = Config.get_mongo_collection("manual")
        return next(factory.get_database()
                           .get_collection(manual_col)
                           .find({"id": id}), None)
    else:
        return document
