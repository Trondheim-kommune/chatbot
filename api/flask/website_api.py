import model.db_util as db_util
import api.flask.flask_util as flask_util
from model.ModelFactory import ModelFactory
import json
import os
from flask import request, Blueprint

web_api = Blueprint('Website API', __name__, template_folder='templates')

factory = ModelFactory.get_instance()

if os.getenv("TEST_FLAG"):
    db_util.set_db(factory, db="test_db")
else:
    db_util.set_db(factory, db="dev_db")


@web_api.route("/v1/web/conflict_ids", methods=["GET"])
def get_all_conflict_ids():
    """
    :return: a list of {"title" "...", "id": "..."}
    """
    conflict_ids_docs = factory.get_collection("conflict_ids").find()
    conflict_ids = []
    for conflict_id_doc in conflict_ids_docs:
        conflict_ids.append({"id": conflict_id_doc["conflict_id"],
                             "title": conflict_id_doc["title"]})
    return json.dumps(conflict_ids)


@web_api.route("/v1/web/content/", methods=["GET"])
def get_content():
    """
    :return: the content of the prod document and manual document (if we have it)
    """
    id = request.args.get('id')

    document_prod = next(factory.get_collection("prod").find({"id": id}), None)
    output = {"prod": document_prod["content"]}
    document_manual = next(factory.get_collection("manual").find({"id": id}), None)

    if document_manual:
        output["manual"] = document_manual["content"]

    # Add the url
    output["url"] = document_prod["url"]
    return json.dumps(output)


@web_api.route("/v1/web/content/", methods=["POST"])
def update_content():
    """
    Updates the manual collection with new content.
    """
    json_input_data = json.loads(request.data)
    id = json_input_data["data"]["id"]
    content = json_input_data["data"]["content"]
    status = factory.get_database().get_collection("manual").update({"id": id}, {"$set": {
        "content": content}})
    if status["updatedExisting"] is False:
        # If the document wasn't already in the manual db then we need to copy the automatic one
        # first.
        document = next(factory.get_collection("prod").find({"id": id}), None)
        document["content"] = content
        factory.get_database().get_collection("manual").insert_one(document)

    # set manually_changed to true.
    factory.get_database().get_collection("prod").update({"id": id}, {"$set": {
        "manually_changed": True}})

    # delete this document from the conflict ids collection
    factory.get_database().get_collection("conflict_ids").delete_one({"conflict_id": id})
    return flask_util.create_success_response("Success")


@web_api.route("/v1/web/docs/", methods=["GET"])
def get_docs_from_url():
    """
    :return: Every document for a single url with id and title.
    """
    url = request.args.get('url')
    docs = factory.get_collection("prod").find({"url": url})

    out = []
    for doc in docs:
        out.append({"id": doc["id"], "title": doc["content"]["title"]})
    return json.dumps(out)
