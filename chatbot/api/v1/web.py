import json

from flask import request, Blueprint

from chatbot.model.model_factory import ModelFactory
from chatbot.nlp.keyword import lemmatize_content_keywords
from chatbot.util.config_util import Config
import chatbot.api.v1.util as flask_util


web_api = Blueprint('Website APIv1',
                    __name__,
                    url_prefix='/v1/web',
                    template_folder='templates')

factory = ModelFactory.get_instance()
factory.set_db()

prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


@web_api.route("/conflict_ids", methods=["GET"])
def get_all_conflict_ids():
    """
    :return: a list of {"title" "...", "id": "..."}
    """
    conflict_ids_docs = factory.get_collection(conflict_col).find()
    conflict_ids = []

    # Validate if result is empty or does not contain keys
    try:
        for conflict_id_doc in conflict_ids_docs:
            conflict_ids.append({"id": conflict_id_doc["conflict_id"],
                                 "title": conflict_id_doc["title"]})
    except KeyError:
        pass

    return json.dumps(conflict_ids)


@web_api.route("/content/", methods=["GET"])
def get_content():
    """
    :return: the content of the prod document and manual document
    (if we have it) """

    id = request.args.get('id')

    response = {}
    prod = next(factory.get_collection(prod_col).find({"id": id}), None)
    manual = next(factory.get_collection(manual_col).find({"id": id}), None)

    # TODO: Return not found if not
    response["prod"] = prod["content"] if prod else None
    response["manual"] = manual["content"] if manual else None
    response["url"] = prod["url"] if prod else None

    return json.dumps(response)


# TODO: This should use PUT and verify that the content exists
@web_api.route("/content/", methods=["POST"])
def update_content():
    """ Update the manual collection with new content. """

    json_input_data = json.loads(request.data)
    id = json_input_data["data"]["id"]
    content = json_input_data["data"]["content"]

    lemmatize_content_keywords(content)

    index = ({"id": id}, {"$set": {"content": content}})
    status = factory.get_database().get_collection(manual_col).update(*index)
    if status["updatedExisting"] is False:
        # If the document wasn't already in the manual db then we need to copy
        # the automatic one first.
        document = next(factory.get_collection(prod_col).find({"id": id}),
                        None)
        # TODO: If document is None, return a Bad Request because the content
        # that is attempted to be updated does not exists
        document["content"] = content
        factory.get_database().get_collection(manual_col).insert_one(document)

    # set manually_changed to true.
    index = ({"id": id}, {"$set": {"manually_changed": True}})
    factory.get_database().get_collection(prod_col).update(*index)

    # delete this document from the conflict ids collection
    query = {"conflict_id": id}
    factory.get_database().get_collection(conflict_col).delete_one(query)
    return flask_util.create_success_response("Success")


@web_api.route("/docs/", methods=["GET"])
def get_docs_from_url():
    """
    :return: Every document for a single url with id and title.
    """
    url = request.args.get('url')
    docs = factory.get_collection(prod_col).find({"url": url})

    out = []
    for doc in docs:
        out.append({"id": doc["id"], "title": doc["content"]["title"]})
    return json.dumps(out)


@web_api.route("/v1/web/doc", methods=["DELETE"])
def delete_manual_document():
    """ Delete a document from the manual collection """
    json_input_data = json.loads(request.data)
    document_id = json_input_data["data"]["id"]
    factory.get_database() \
           .get_collection(manual_col) \
           .delete_one({"id": document_id})
    factory.get_database() \
           .get_collection(prod_col) \
           .update({"id": document_id}, {"$set": {"manually_changed": False}})
    factory.get_database().get_collection(conflict_col) \
                          .delete_one({"conflict_id": document_id})
    success_msg = "Successfully deleted manual entry"
    return flask_util.create_success_response(success_msg)


@web_api.route("/unknown_query", methods=["DELETE"])
def delete_unknown_query():
    """ Delete a query from the unknown_query collection.
    :return: A success json if it was successful.
    """
    json_input_data = json.loads(request.data)
    query_text = json_input_data["data"]["query_text"]
    factory.get_database() \
           .get_collection(unknown_col) \
           .delete_one({"query_text": query_text})
    success_msg = "Successfully deleted an unknown query."
    return flask_util.create_success_response(success_msg)


@web_api.route("/unknown_queries", methods=["GET"])
def get_all_unknown_queries():
    """
    :return: a list of unknown queries.
    """
    unknown_queries_docs = factory.get_collection(unknown_col).find()
    unknown_queries = [{"query_text": unknown_query_doc["query_text"]}
                       for unknown_query_doc in unknown_queries_docs]
    return json.dumps(unknown_queries)
