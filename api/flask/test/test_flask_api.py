import pytest
import json
import time
from model import QuerySystem

from api.flask import server
from api.flask import dialogflow_api


# Just see if we can create an intent object that is correct.
def test_create_intent_object():
    # match_entitity = False because entities might change in future and I
    # don't want this test to break in the future.
    intent = dialogflow_api.create_intent_object(
        "Husbybadet", [
            "Når åpner husbybadet?", "husbybadet åpningstid"],
        match_entity=False)

    correct_intent = {
        "display_name": "Husbybadet",
        "parameters": [],
        "training_phrases": [
            {
                "parts": [
                    {
                        "text": "Når "
                    },
                    {
                        "text": "åpner "
                    },
                    {
                        "text": "husbybadet? "
                    }
                ],
                "type": "EXAMPLE"
            },
            {
                "parts": [
                    {
                        "text": "husbybadet "
                    },
                    {
                        "text": "åpningstid "
                    }
                ],
                "type": "EXAMPLE"
            }
        ],
        "webhook_state": True
    }
    assert intent == correct_intent


@pytest.fixture(scope='module')
def app():
    return server.app


def test_get_homepage(app):
    response = app.test_client().get('/')
    assert response.status_code == 200
    response_json = json.loads(response.data.decode())
    assert "OK" == response_json["status"]
    assert "Success" == response_json["message"]


def test_add_and_remove_entities(app):
    epoch_time = str(int(time.time()))
    input_dict = {
        "type": "batch_create_entities",
        "data": [
            {
                "entity_type_name": "automatic_test" + epoch_time + "_1",
                "entities": [
                    {
                        "value": "Bmw",
                        "synonyms": [
                            "dyr bil",
                            "vrooom bil"
                        ]
                    },
                    {
                        "value": "Opel",
                        "synonyms": [
                            "billig",
                            "effektiv"
                        ]
                    }
                ]
            },
            {
                "entity_type_name": "automatic_test" + epoch_time + "_2",
                "entities": [
                    {
                        "value": "Bmw",
                        "synonyms": [
                            "dyr bil",
                            "vrooom bil"
                        ]
                    },
                    {
                        "value": "Opel",
                        "synonyms": [
                            "billig",
                            "effektiv"
                        ]
                    }
                ]
            }
        ]
    }

    response = app.test_client().put('/v1/dialogflow/entities',
                                     data=json.dumps(input_dict))
    assert response.status_code == 200
    response_json = json.loads(response.data.decode())
    # Make sure you got 2 IDs back.
    assert 2 == len(response_json["data"])

    # Now we want to delete the 2 new entities.
    response_2 = app.test_client().delete('/v1/dialogflow/entities',
                                          data=json.dumps(
                                              {"data": response_json["data"]}))
    assert response_2.status_code == 200


def test_add_intents_same_name_throws_exception(app):
    input_dict = {
        "type": "batch_create_intents",
        "data": [
            {
                "intent_name": "1",
                "training_phrases": [
                    "jeg har en Bmw",
                    "Jeg har noe som sier vrooooom"
                ]
            },
            {
                "intent_name": "2",
                "training_phrases": [
                    "jeg har også en Bmw",
                    "Jeg har noe som sier bada bing bada bong"
                ]
            }
        ]
    }
    response = app.test_client().put('/v1/dialogflow/intents',
                                     data=json.dumps(input_dict))
    assert response.status_code == 400
    response_json = json.loads(response.data.decode())
    assert "400 Intent with the display_name '1' already exists." in \
           response_json["message"]
    assert "ERROR" in response_json["status"]


def test_add_intents(app):
    # Just because I want a unique name I use epoch time here.
    epoch_time = str(int(time.time()))

    input_dict = {
        "type": "batch_create_intents",
        "data": [
            {
                "intent_name": epoch_time,
                "training_phrases": [
                    "jeg har en Bmw",
                    "Jeg har noe som sier vrooooom"
                ]
            },
            {
                "intent_name": epoch_time + "_2",
                "training_phrases": [
                    "jeg har også en Bmw",
                    "Jeg har noe som sier bada bing bada bong"
                ]
            }
        ]
    }
    response = app.test_client().put('/v1/dialogflow/intents',
                                     data=json.dumps(input_dict))
    assert response.status_code == 200

    response_json = json.loads(response.data.decode())
    assert "OK" == response_json["status"]
    assert "Batch created 2 intents." == response_json["message"]


def test_get_all_conflicts(app):
    response = app.test_client().get('/v1/web/conflict_ids')
    response_json = json.loads(response.data.decode())
    assert response_json[0]["id"] == "295cc564fe771fbb92b3278a6eee2d5cbcae2606-3"
    assert response_json[0]["title"] == " Velkommen til Trondheim kommune"


def test_get_content(app):
    response = app.test_client().get(
        '/v1/web/content/?id=295cc564fe771fbb92b3278a6eee2d5cbcae2606-3')
    response_json = json.loads(response.data.decode())
    assert response_json["url"] == "https://www.trondheim.kommune.no"
    assert type(response_json["manual"]) is dict
    assert type(response_json["prod"]) is dict


def test_update_content(app):
    input_dict = {
        "data": {
            "id": "295cc564fe771fbb92b3278a6eee2d5cbcae2606-3",
            "content": {
                "title": " Velkommen til Trondheim kommune",
                "keywords": [
                    {
                        "keyword": "change_from_test",
                        "confidence": 0.2010
                    }
                ],
                "texts": [
                    "El manual changos",
                    "New answer"
                ]
            }
        }
    }
    response = app.test_client().post('/v1/web/content/',
                                      data=json.dumps(input_dict))
    assert response.status_code == 200


def test_get_docs_from_url(app):
    response = app.test_client().get('/v1/web/docs/?url=https://www.trondheim.kommune.no')
    response_json = json.loads(response.data.decode())
    assert response_json[0]["id"] == "295cc564fe771fbb92b3278a6eee2d5cbcae2606-3"
    assert response_json[0]["title"] == " Velkommen til Trondheim kommune"


def test_unknown_query(app):
    """
    This test will create a new unknown query and then get every query and then delete that query.
    """
    epoch_time = str(int(time.time()))

    # pretends epoch_time is an unknown query string, then we insert it into the collection here
    QuerySystem.handle_not_found(epoch_time)

    response = app.test_client().get('/v1/web/unknown_queries',
                                     data=json.dumps({}))
    assert response.status_code == 200

    response_json = json.loads(response.data.decode())

    found = False

    for res in response_json:
        if res["query_text"] == epoch_time:
            found = True
            break
    assert found is True

    response = app.test_client().delete('/v1/web/unknown_query',
                                        data=json.dumps({"data": {"query_text": epoch_time}}))

    assert response.status_code == 200
    response_json = json.loads(response.data.decode())
    assert "OK" == response_json["status"]
