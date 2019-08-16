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

    try:
        fact.post_document(data[0], "test")
        fact.post_document(data[1], "test")
        fact.get_collection("test").create_index(
            [("keywords", pymongo.TEXT),
             ("content.keywords.keyword", pymongo.TEXT)],
            default_language="norwegian")

        # Need to create index for manual incase the collection does not exist
        # yet
        fact.set_index("manual")

        # Test first document
        doc = fact.get_document("emne test", prod_col="test")
        assert doc[0]["content"] == data[0]["content"]

        doc = fact.get_document("emne skole arbeid", prod_col="test")
        assert doc[0]["content"] == data[0]["content"]

        # Test second document
        doc = fact.get_document("bra test", prod_col="test")
        assert doc[0]["content"] == data[1]["content"]

        doc = fact.get_document("bra arbeid emne", prod_col="test")
        assert doc[0]["content"] == data[1]["content"]

        assert not fact.get_document("sakfscfdsojimad", prod_col="test")
    finally:
        fact.get_database().drop_collection("test")


def test_update_document():
    data = '{"name": "testname", "manually_changed": false }'
    try:
        fact.post_document(data, "test")
        fact.get_collection("test").create_index(
            [("name", pymongo.TEXT)], default_language="norwegian")

        newdata = '{"name": "nottestname"}'
        fact.update_document({"name": "testname"}, newdata, "test")
        doc = fact.get_document("nottestname", prod_col="test")[0]

        assert doc["name"] == "nottestname"

    finally:
        fact.get_database().drop_collection("test")
