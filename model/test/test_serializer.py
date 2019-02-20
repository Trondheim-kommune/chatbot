from model.Serializer import KeyWord
from model.Serializer import Serializer
from model.Serializer import Content
import pytest
import json


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
