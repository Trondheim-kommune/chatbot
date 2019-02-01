from Serializer import KeyWord
from Serializer import Serializer
from Serializer import Content
import pytest
import json


def test_serialize_data():
    # Test that data is serialized correctly
    ser = Serializer("mock_data/test_data.json")
    ser.serialize_data()
    test_data = ser.get_model()
    with open("mock_data/test_data_serialized.json", "r") as f:
        serialized_data = json.load(f)

    assert test_data["url"] == serialized_data["url"]
    assert (
        test_data["contents"][0].get_content()["texts"]
        == serialized_data["contents"][0]["texts"]
    )
    assert (
        test_data["contents"][1].get_content()["texts"]
        == serialized_data["contents"][1]["texts"]
    )


def test_instance_of_KeyWord():
    keyWs = [
        KeyWord("svømme", 0.74),
        KeyWord("fritid", 0.37),
        KeyWord("barnehage", 0.91),
    ]
    # Test that an TypeError is raised when creating a Content object without KeyWord type
    with pytest.raises(TypeError, match="Must be KeyWord type"):

        content = Content(
            "Åpningstider",
            "Svømmehallen er åpen alle dager 09:00-20:00",
            [["svømme", 0.82], ["åpningstid", 0.87]],
        )

    # Test that no TypeError is raised when creating a Content object with correct KeyWordType
    try:
        content = Content("Barnehage", "I Trondheim er det mange barnehager", keyWs)
    except TypeError:
        pytest.fail("Failed creating a Content object with correct KeyWords")
