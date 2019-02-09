import pytest
import json
import time

from api.flask import server


# Just see if we can create an intent object that is correct.
def test_create_intent_object():
    # match_entitity = False because entities might change in future and I
    # don't want this test to break in the future.
    intent = server.create_intent_object(
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
    assert b'{"status": "OK", "message": "Success"}' in response.data


def test_add_and_remove_entities(app):
    input_dict = {
        "type": "batch_create_entities",
        "data": [
            {
                "entity_type_name": "automatic_test00",
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
                "entity_type_name": "automatic_test01",
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

    response = app.test_client().post('/v1/batch_create_entities',
                                      data=json.dumps(input_dict))
    assert response.status_code == 200
    response_json = json.loads(response.data.decode())
    # Make sure you got 2 IDs back.
    assert 2 == len(response_json["data"])

    # Now we want to delete the 2 new entities.
    response_2 = app.test_client().post('/v1/batch_delete_entities',
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
    response = app.test_client().post('/v1/batch_create_intents',
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
    response = app.test_client().post('/v1/batch_create_intents',
                                      data=json.dumps(input_dict))
    assert response.status_code == 200
    assert b'{"status": "OK", "message": "Batch created 2 intents."}' in \
        response.data
