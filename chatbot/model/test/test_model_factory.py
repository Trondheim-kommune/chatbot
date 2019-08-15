import json
import pymongo

from chatbot.model.model_factory import ModelFactory

fact = ModelFactory.get_instance()
fact.set_db()


def test_get_document():
    path = "chatbot/model/test/test_data/test_data_model_factory.json"
    with open(path, "r") as f:
        data = json.load(f)

    fact.get_database().drop_collection("test")

    fact.post_document(data[0], "test")
    fact.post_document(data[1], "test")
    fact.get_collection("test").create_index(
        [("keywords", pymongo.TEXT),
         ("content.keywords.keyword", pymongo.TEXT)],
        default_language="norwegian")

    # Test first document
    doc = fact.get_document("emne test", main_collection="test")
    assert doc[0]["content"] == data[0]["content"]

    doc = fact.get_document("emne skole arbeid", main_collection="test")
    assert doc[0]["content"] == data[0]["content"]

    # Test second document
    doc = fact.get_document("bra test", main_collection="test")
    assert doc[0]["content"] == data[1]["content"]

    doc = fact.get_document("bra arbeid emne", main_collection="test")
    assert doc[0]["content"] == data[1]["content"]

    assert not fact.get_document("sakfscfdsojimad", main_collection="test")

    fact.get_database().drop_collection("test")


def test_update_document():
    data = '{"name": "testname", "manually_changed": false }'

    fact.post_document(data, "test")
    fact.get_collection("test").create_index(
        [("name", pymongo.TEXT)], default_language="norwegian")

    newdata = '{"name": "nottestname"}'
    fact.update_document({"name": "testname"}, newdata, "test")
    doc = fact.get_document("nottestname", main_collection="test")[0]

    fact.get_database().drop_collection("test")

    assert doc["name"] == "nottestname"
