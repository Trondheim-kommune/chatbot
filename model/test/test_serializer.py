from model.Serializer import KeyWord
from model.Serializer import Serializer
from model.Serializer import Content
from model.start import insert_documents
import model.db_util as util
from model.ModelFactory import ModelFactory
import pytest
import json
import random


def test_serialize_data():
    # Test that data is serialized correctly
    ser = Serializer("model/test/test_data/test_data.json")
    ser.serialize_data()
    test_data = ser.get_models()

    with open("model/test/test_data/test_data_serialized.json", "r") as f:
        serialized_data = json.load(f)

    assert test_data[0]["url"] == serialized_data[0]["url"]
    assert test_data[0]["id"] == serialized_data[0]["id"]
    assert (
            test_data[0]["content"]["texts"]
            == serialized_data[0]["content"]["texts"]
    )
    assert (
            test_data[1]["content"]["texts"]
            == serialized_data[1]["content"]["texts"]
    )
    assert (
            test_data[0]["header_meta_keywords"][0]
            == serialized_data[0]["header_meta_keywords"][0]
    )


def test_instance_of_KeyWord():
    keyWs = [
        KeyWord("svømme", 0.74),
        KeyWord("fritid", 0.37),
        KeyWord("barnehage", 0.91),
    ]
    # Test that an TypeError is raised when creating a Content object without
    # KeyWord type
    with pytest.raises(TypeError, match="Must be KeyWord type"):

        Content(
            "Åpningstider",
            "Svømmehallen er åpen alle dager 09:00-20:00",
            [["svømme", 0.82], ["åpningstid", 0.87]],
        )

    # Test that no TypeError is raised when creating a Content object with
    # correct KeyWordType
    try:
        Content(
            "Barnehage", "I Trondheim er det mange barnehager", keyWs)
    except TypeError:
        pytest.fail("Failed creating a Content object with correct KeyWords")


def test_insert_document_and_check_conflict():
    """
    Run the start.py file and insert a record into in_progress that has a conflict with the prod
    collection so main method should return the conflict id. Also check if the newly inserted
    document is in prod collection and with the correct manually_changed. Lastly fetch the
    manual document instead of the document in prod collection.
    """
    id = "295cc564fe771fbb92b3278a6eee2d5cbcae2606-3"
    correct_conflicts = [id]

    f = open("model/test/test_data/test_data_in_progress.json")
    serialized_data = json.load(f)

    # Just to make sure the new document has changed we add a number number here.
    random_text = "Inserted_document_website_change: " + str(random.randint(1, 100000))
    serialized_data[0]["content"]["texts"][0] = random_text

    # Check if the document was a conflict.
    conflict_ids = insert_documents(serialized_data, db="test_db")
    assert correct_conflicts[0] == conflict_ids[0]

    # Fetch the document from the prod collection.
    factory = ModelFactory.get_instance()
    util.set_db(factory, db="test_db")
    document = next(factory.get_database().get_collection("prod").find({"id": id}), None)
    assert document["content"]["texts"][0] == random_text

    # Get the manually changed document.
    manually_changed_doc = util.check_manually_changed(factory, document)
    # Check if we actually got the manually changed document.
    assert manually_changed_doc["content"]["texts"][0] == "El manual changos"
