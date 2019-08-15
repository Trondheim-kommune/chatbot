import json

from flask import request, Blueprint

from chatbot.model.model_factory import ModelFactory
from chatbot.nlp.keyword import lemmatize_content_keywords
import chatbot.api.util as flask_util


web_api = Blueprint('Website API', __name__, template_folder='templates')

factory = ModelFactory.get_instance()
factory.set_db()


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
    """ Update the manual collection with new content. """

    json_input_data = json.loads(request.data)
    id = json_input_data["data"]["id"]
    content = json_input_data["data"]["content"]

    lemmatize_content_keywords(content)

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


@web_api.route("/v1/web/doc", methods=["DELETE"])
def delete_manual_document():
    """ Delete a document from the manual collection """
    json_input_data = json.loads(request.data)
    document_id = json_input_data["data"]["id"]
    factory.get_database().get_collection("manual").delete_one({"id": document_id})
    factory.get_database().get_collection("prod").update({"id": document_id}, {"$set": {
        "manually_changed": False}})
    factory.get_database().get_collection("conflict_ids").delete_one({"conflict_id": document_id})
    return flask_util.create_success_response("Successfully deleted manual entry")


@web_api.route("/v1/web/unknown_query", methods=["DELETE"])
def delete_unknown_query():
    """ Delete a query from the unknown_query collection.
    :return: A success json if it was successful.
    """
    json_input_data = json.loads(request.data)
    query_text = json_input_data["data"]["query_text"]
    factory.get_database().get_collection("unknown_queries").delete_one({"query_text": query_text})
    return flask_util.create_success_response("Successfully deleted an unknown query.")


@web_api.route("/v1/web/unknown_queries", methods=["GET"])
def get_all_unknown_queries():
    """
    :return: a list of unknown queries.
    """
    unknown_queries_docs = factory.get_collection("unknown_queries").find()
    unknown_queries = [{"query_text": unknown_query_doc["query_text"]} for unknown_query_doc in
                       unknown_queries_docs]
    return json.dumps(unknown_queries)
