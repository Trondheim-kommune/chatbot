import os

from model.ModelFactory import ModelFactory

fact = ModelFactory.get_instance()


def test_get_document_single_field():
    global fact
    data = '{"name": "testname"}'
    fact.set_database("agent25.tinusf.com", "test_db",
                      str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    fact.post_document(data, "test")

    doc = fact.get_document({"name": "testname"}, "test")

    fact.get_database().drop_collection("test")
    assert doc["name"] == "testname"


def test_get_document_multiple_fields():
    global fact
    data = '{"name": "testname", "surname": "testsurname"}'
    fact.set_database("agent25.tinusf.com", "test_db",
                      str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    fact.post_document(data, "test")
    doc = fact.get_document({"name": "testname", "surname": "testsurname"},
                            "test")

    fact.get_database().drop_collection("test")

    assert doc["name"] == "testname" and doc["surname"] == "testsurname"


def test_update_document():
    global fact
    data = '{"name": "testname"}'
    fact.set_database("agent25.tinusf.com", "test_db",
                      str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    fact.post_document(data, "test")
    newdata = '{"name": "nottestname"}'
    fact.update_document({"name": "testname"}, newdata, "test")
    doc = fact.get_document({"name": "nottestname"}, "test")

    fact.get_database().drop_collection("test")

    assert doc["name"] == "nottestname"
