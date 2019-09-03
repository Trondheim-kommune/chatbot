import json
import os

from flask import jsonify, request, Blueprint
from flask_cors import CORS

import dialogflow_v2beta1

import google.api_core.exceptions as google_exceptions

from chatbot.nlp.query import QueryHandler
from chatbot.api.v1.exceptions import InvalidDialogFlowID
import chatbot.api.v1.util as util


PROJECT_ID = os.getenv("PROJECT_ID")

query_handler = QueryHandler()

# Used for mapping synonyms to entity_type
entities = {}

entities_loaded = False

dialog_api = Blueprint('DialogFlow APIv1',
                       __name__,
                       url_prefix='/v1/dialogflow',
                       template_folder='templates')
CORS(dialog_api)


@dialog_api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


# Register handle for flask_exceptions error messages.
@dialog_api.errorhandler(InvalidDialogFlowID)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@dialog_api.route("/response", methods=["POST"])
def get_response():
    """ Returns the response to a given query. Capable of passing on raw query
    text, display name, query parameters, entities and intents from DialogFlow
    """

    json_input_data = json.loads(request.data)
    try:
        raw_query_text = json_input_data["queryResult"]["queryText"]
    except KeyError:
        raw_query_text = None

    response = query_handler.get_response(raw_query_text)
    return json.dumps({"fulfillmentText": response})


def create_intent_object(intent_name, training_phrases, match_entity=True):
    """ Take in a name and training phrases and creates the intent
    object and maps intents to entities if it finds a match. (Also a
    variable match_entity if you do not wish to match with entities you
    can turn it off.) """

    intent = {
        "display_name": intent_name,
        "webhook_state": True,
        "training_phrases": [],
        "parameters": []
    }

    parameters = []
    for training_phrase in training_phrases:
        parts = []

        for word in training_phrase.split():
            try:
                if not match_entity:
                    # If you don't want to match with entities just append
                    # regular and continue to the next one.
                    parts.append({"text": word + " "})
                    continue
                # This is when we find an entity matching this specific word
                # in the training phrase. Then we need to add entity type to
                # the word and add the parameter to the intent.
                entity = entities[word]
                parts.append(
                    {"text": word + " ", "entity_type": "@" + entity,
                     "alias": entity})

                parameters.append({"display_name": entity,
                                   "entity_type_display_name": "@" + entity,
                                   "value": "$" + entity})

            except KeyError:
                # All the non-matching words.
                parts.append({"text": word + " "})

        intent["training_phrases"].append({"parts": parts, "type": "EXAMPLE"})

    intent["parameters"] = parameters
    return intent


@dialog_api.route("/intent", methods=["PUT"])
def create_intent_post():
    json_input_data = json.loads(request.data)
    try:
        intent_name = json_input_data["intent_name"]
    except KeyError:
        return "Could not find intent_name"

    try:
        training_phrases = json_input_data["training_phrases"]
    except KeyError:
        training_phrases = []

    try:
        intent = create_intent(intent_name, training_phrases)
        return util.create_success_response("Intent created", data=intent.name)
    except google_exceptions.FailedPrecondition as e:
        # Intent with same name exception.
        raise InvalidDialogFlowID(str(e), status_code=400)


def create_intent(intent_name, training_phrases):
    """ Create a single intent.
    :param intent_name: A simple string.
    :param training_phrases: A list containing multiple training_phrases.
    :return: the newly created intent. """

    client = dialogflow_v2beta1.IntentsClient()
    parent = client.project_agent_path(PROJECT_ID)

    intent = create_intent_object(intent_name, training_phrases)
    return client.create_intent(parent, intent)


def get_entities():
    """ Fetch and cache all entities """
    global entities_loaded

    global entities
    entities = {}
    client = dialogflow_v2beta1.EntityTypesClient()
    parent = client.project_agent_path(PROJECT_ID)

    # For every entity_type element
    for element in client.list_entity_types(parent):
        entity_type = element.display_name
        for entity in element.entities:
            # Get every synonym.
            for synonym in entity.synonyms:
                # Insert them into the big dictionary.
                entities[synonym] = entity_type

    entities_loaded = True


@dialog_api.route("/intents", methods=["PUT"])
def batch_create_intents_post():
    json_input_data = json.loads(request.data)
    intents = json_input_data["data"]

    try:
        # Since response from batch_create_intents is an operation/ future
        # object we don't really have anything to return here. So just a
        # simple counter, so atleast we know how many intents we created.
        counter = batch_create_intents(intents)
        return util.create_success_response(
            "Batch created " + str(counter) + " intents.")
    except google_exceptions.FailedPrecondition as e:
        # Intent with same name exception.
        raise InvalidDialogFlowID(str(e), status_code=400)


def batch_create_intents(intents):
    """ Inserts multiple intents at the same time, much more
    efficient than running the create_intent multiple times.
    :param intents: list of intents you want to create.
    :return: int of """
    intents_out = []

    # A simple counter for how many intents we have inserted.
    counter = 0

    for intent in intents:
        current_intent = create_intent_object(intent["intent_name"],
                                              intent["training_phrases"])
        intents_out.append(current_intent)
        counter += 1

    client = dialogflow_v2beta1.IntentsClient()
    parent = client.project_agent_path(PROJECT_ID)

    client.batch_update_intents(parent, "no",
                                intent_batch_inline={"intents": intents_out})
    return counter


def get_all_intents():
    client = dialogflow_v2beta1.IntentsClient()
    parent = client.project_agent_path(PROJECT_ID)
    return client.list_intents(parent)


@dialog_api.route("/entities", methods=["PUT"])
def batch_create_entities_post():
    json_input_data = json.loads(request.data)
    entity_types = json_input_data["data"]

    try:
        ID_list = batch_create_entities(entity_types)
        return util.create_success_response("Batch created entities.",
                                            data=ID_list)
    except google_exceptions.FailedPrecondition as e:
        # Entity with same name exception.
        raise InvalidDialogFlowID(str(e), status_code=400)


def batch_create_entities(entity_types):
    """ Creates entites and adds them into a global entity dictionary.
    :param entity_types: A list of entity types.
    :return: a list of the entity ID's created. """
    client = dialogflow_v2beta1.EntityTypesClient()
    parent = client.project_agent_path(PROJECT_ID)

    # A list of the newly created entities ID's.
    ID_list = []

    for entity_type in entity_types:
        entity_type_out = {"display_name": entity_type["entity_type_name"],
                           "kind": "KIND_MAP",
                           "entities": entity_type["entities"]}
        response = client.create_entity_type(parent, entity_type_out)

        ID_list.append(response.name.split("/")[-1])
    # After we have inserted all the new entities we get_entities() again.
    get_entities()

    return ID_list


@dialog_api.route("/entities", methods=["DELETE"])
def batch_delete_entities_post():
    json_input_data = json.loads(request.data)
    entity_ids = json_input_data["data"]

    try:
        batch_delete_entities(entity_ids)
        # Since reponse is an operation/ future object we don't really have
        # anything to return here.
        return util.create_success_response("Batch deleted entities.")
    except google_exceptions.FailedPrecondition as e:
        raise InvalidDialogFlowID(str(e), status_code=400)


def batch_delete_entities(entity_ids):
    """ Batch deletes multiple entities
    :param entity_ids: list of ids to delete
    :return: response which is an operation/ future object. """

    client = dialogflow_v2beta1.EntityTypesClient()
    parent = client.project_agent_path(PROJECT_ID)

    entity_ids_fixed_path = []

    # This may seems weird and it seems like it would not be necessary but
    # there is a bug with the api and therefore we have to append the
    # beginning of the path to every entity_id in order to get this to work.
    for entity_id in entity_ids:
        entity_ids_fixed_path.append(parent + "/entityTypes/" + entity_id)

    return client.batch_delete_entity_types(parent, entity_ids_fixed_path)
