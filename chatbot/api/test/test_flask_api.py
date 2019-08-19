import pytest
import json
import time

from chatbot.nlp.query import _handle_not_found
from chatbot.model.model_factory import ModelFactory
from chatbot.api import server
from chatbot.api import dialogflow
from chatbot.util.config_util import Config


factory = ModelFactory.get_instance()
factory.set_db()


# Just see if we can create an intent object that is correct.
def test_create_intent_object():
    # match_entitity = False because entities might change in future and I
    # don't want this test to break in the future.
    intent = dialogflow.create_intent_object(
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
    # Setup two conflicts
    conflicts = [{"conflict_id": "test_conflict_id_{}".format(i),
                  "title": "test_conflict_title_{}".format(i)}
                 for i in range(2)]

    conflict_col = Config.get_mongo_collection("conflicts")
    # Post both focuments to conflict_ids
    for conflict in conflicts:
        factory.post_document(conflict, conflict_col)

    response = app.test_client().get('/v1/web/conflict_ids')

    try:
        response = app.test_client().get('/v1/web/conflict_ids')
        response_json = json.loads(response.data.decode())

        for conflict in conflicts:
            assert conflict["conflict_id"] in [resp["id"]
                                               for resp in response_json]
    finally:
        # Delete test conflits
        for conflict in conflicts:
            factory.delete_document({"conflict_id": conflict["conflict_id"]},
                                    conflict_col)


def test_get_content(app):
    # Setup a content document
    document = {"id": "test_content_id",
                "content": "some_test_content",
                "url": "test_url"}
    prod_col = Config.get_mongo_collection("prod")
    factory.post_document(document, prod_col)

    try:
        url = "/v1/web/content/?id=test_content_id"
        response = app.test_client().get(url)
        response_json = json.loads(response.data.decode())
        print(response_json)

        assert response_json["prod"] == "some_test_content"
    finally:
        # Delete test content
        factory.delete_document({"id": "test_content_id"}, prod_col)


def test_update_content(app):
    # Setup a content document
    input_doc = {
        "data": {
            "id": "test_id",
            "url": "some test url 123",
            "content": {
                "title": "some_test_title",
                "keywords": [
                    {
                        "keyword": "change_from_test",
                        "confidence": 0.2010
                    }
                ],
                "texts": ["some test text"]
            }
        }
    }
    prod_col = Config.get_mongo_collection("prod")
    manual_col = Config.get_mongo_collection("manual")
    factory.post_document(input_doc["data"].copy(), prod_col)

    try:
        # Make a change
        new_title = "title has been changed"
        input_doc["data"]["content"]["title"] = new_title
        response = app.test_client().post('/v1/web/content/',
                                          data=json.dumps(input_doc))
        response = app.test_client().get('/v1/web/content/?id=test_id')
        response_doc = json.loads(response.data.decode())

        print(response_doc)
        assert response_doc["manual"]["title"] == new_title
    finally:
        # Delete test content
        factory.delete_document({"id": "test_id"}, manual_col)
        factory.delete_document({"id": "test_id"}, prod_col)


def test_get_docs_from_url(app):
    # Setup a content document
    input_doc = {
        "data": {
            "id": "test_id_for_url",
            "url": "some test url",
            "content": {
                "title": "some_test_title",
                "keywords": [
                    {
                        "keyword": "change_from_test",
                        "confidence": 0.2010
                    }
                ],
                "texts": ["some test text"]
            }
        }
    }
    prod_col = Config.get_mongo_collection("prod")
    factory.post_document(input_doc["data"].copy(), prod_col)

    try:
        response = app.test_client().get('/v1/web/docs/?url=some test url')
        response_json = json.loads(response.data.decode())
        assert response_json[0]["id"] == "test_id_for_url"
    finally:
        factory.delete_document({"id": "test_id_for_url"}, prod_col)


def test_unknown_query(app):
    """
    This test will create a new unknown query and then get every query and then
    delete that query.  """
    epoch_time = str(int(time.time()))

    # pretends epoch_time is an unknown query string, then we insert it into
    # the collection here
    _handle_not_found(epoch_time)

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

    doc_to_delete = {"data": {"query_text": epoch_time}}
    response = app.test_client().delete('/v1/web/unknown_query',
                                        data=json.dumps(doc_to_delete))

    assert response.status_code == 200
    response_json = json.loads(response.data.decode())
    assert "OK" == response_json["status"]
