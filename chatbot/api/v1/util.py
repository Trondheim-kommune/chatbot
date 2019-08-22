import json


def create_success_response(message, data=None):
    """ Create JSON success response """

    response = {}

    if data:
        response["data"] = data

    response["status"] = "OK"
    response["message"] = message

    return json.dumps(response)
