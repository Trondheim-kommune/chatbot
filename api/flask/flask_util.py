import json


def create_success_response(message, data=None):
    """
    Used to create the json success response.
    """
    response = {}
    if data:
        # Extra information if needed.
        response["data"] = data
    # Status is either OK or ERROR
    response["status"] = "OK"
    # Human readable message.
    response["message"] = message
    return json.dumps(response)
