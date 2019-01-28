import json
from flask import *

app = Flask(__name__)


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
