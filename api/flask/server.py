import json
from flask import *
import dialogflow_v2beta1
import os

app = Flask(__name__)

# This dictionary contains a mapping from synonyms to entity_type in order to match training phrases with
# entities.
entities = {}
# A simple flag if you have already loaded the entities or not.
entities_loaded = False

PROJECT_ID = os.getenv("PROJECT_ID")
print(PROJECT_ID)


@app.route("/flask", methods=["POST"])
def get_response():
    # Read the data sent using POST.
    json_input_data = json.loads(request.data)
    try:
        raw_query_text = json_input_data["queryResult"]["queryText"]
    except KeyError:
        raw_query_text = None

    try:
        intent = json_input_data["queryResult"]["intent"]["displayName"]
    except KeyError:
        intent = None

    try:
        entities = list(json_input_data["queryResult"]["parameters"].keys())
    except KeyError:
        entities = []

    try:
        default_fulfillment_text = json_input_data["queryResult"]["fulfillmentMessages"][0]["text"]["text"][0]
    except KeyError:
        default_fulfillment_text = None

    return json.dumps(
        {"fulfillmentText": get_fulfillmentText(raw_query_text, intent, entities, default_fulfillment_text)})


def get_fulfillmentText(raw_query_text, intent, entities, def_fulfil_text):
    print(raw_query_text)
    print(intent)
    print(entities)
    print(def_fulfil_text)
    return "Works"


@app.route("/create_intent", methods=["POST"])
def create_intent():
    json_input_data = json.loads(request.data)
    try:
        intent_name = json_input_data["intent_name"]
    except KeyError:
        return "Could not find intent_name"

    try:
        training_phrases = json_input_data["training_phrases"]
    except KeyError:
        training_phrases = []

    intent = {
        "display_name": intent_name,
        "webhook_state": True,
        "training_phrases": [],
        "parameters": []
    }

    client = dialogflow_v2beta1.IntentsClient()
    parent = client.project_agent_path(PROJECT_ID)
    parameters = []
    for training_phrase in training_phrases:
        parts = []

        for word in training_phrase.split():
            try:
                # This is when we find an entity matching this specific word in the training phrase.
                # Then we need to add entity type to the word and add the parameter to the intent.
                entity_type = entities[word]
                parts.append({"text": word + " ", "entity_type": "@" + entity_type,
                              "alias": entity_type})

                parameters.append({"display_name": entity_type,
                                   "entity_type_display_name": "@" + entity_type,
                                   "value": "$" + entity_type
                                   })

            except KeyError:
                # All the non-matching words.
                parts.append({"text": word + " "})

        intent["training_phrases"].append({"parts": parts, "type": "EXAMPLE"})

    intent["parameters"] = parameters

    response = client.create_intent(parent, intent)
    try:
        # Return the newly created intent ID.
        return response.name
    except:
        return "Could not get intent ID, failed to insert intent."


# This method is used for fetching every entity and caching it.
def get_entities():
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


def batch_create_intents():
    # TODO https://cloud.google.com/dialogflow-enterprise/docs/reference/rest/v2beta1/projects.agent.intents/batchUpdate
    pass


# Creates entites and adds them into the global entities dictionary.
@app.route("/batch_create_entities", methods=["POST"])
def batch_create_entities():
    json_input_data = json.loads(request.data)

    client = dialogflow_v2beta1.EntityTypesClient()
    parent = client.project_agent_path(PROJECT_ID)

    entity_types = json_input_data["data"]
    # A simple counter for how many entity types we have inserted.
    counter = 0

    for entity_type in entity_types:
        entity_type_out = {"display_name": entity_type["entity_type_name"], "kind": "KIND_MAP",
                           "entities": entity_type["entities"]}
        response = client.create_entity_type(parent, entity_type_out)
        counter += 1

    # After we have inserted all the new entities we get_entities() again.
    # TODO: it would be more efficient to add to the dictionary whilst uploading new entities.
    get_entities()
    return "Added " + str(counter) + " new entity types."


get_entities()
