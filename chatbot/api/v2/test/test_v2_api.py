import pytest
import json

from chatbot.api import server
from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


factory = ModelFactory.get_instance()
factory.set_db()


prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


@pytest.fixture(scope='module')
def client():
    return server.app.test_client()


def test_swagger(client):
    response = client.get('/')
    assert response.status_code == 200


def test_response(client):
    query = 'some test response'
    try:
        response = client.get('/v2/response/{}/'.format(query))
        assert response.status_code == 200
        assert json.loads(response.data.decode())['user_input'] == query
    finally:
        factory.delete_document({'unknown_query': query}, conflict_col)


def test_get_conflict_ids(client):
    # Setup two conflicts
    conflicts = [{"conflict_id": "test_conflict_id_{}".format(i),
                  "title": "test_conflict_title_{}".format(i)}
                 for i in range(2)]

    for conflict in conflicts:
        factory.post_document(conflict, conflict_col)

    try:
        response = client.get('/v2/conflict_ids/')
        response_data = json.loads(response.data.decode())

        for conflict in conflicts:
            assert conflict['conflict_id'] in [response['conflict_id']
                                               for response in response_data]
    finally:
        for conflict in conflicts:
            factory.delete_document({'conflict_id': conflict['conflict_id']},
                                    conflict_col)


def test_delete_conflict_ids(client):
    conflict = {'conflict_id': 'test conflict id',
                'title': 'test title'}
    factory.post_document(conflict, conflict_col)

    try:
        idx = conflict['conflict_id']
        response = client.delete('/v2/conflict_ids/{}/'.format(idx))
        assert json.loads(response.data.decode())['deleted_count'] > 0
    finally:
        factory.delete_document({'conflict_id': 'test conflict id'},
                                conflict_col)


def test_get_content(client):
    content = {'id': 'test_content_id',
               'content': {
                   'title': 'test title',
                   'keywords': [],
                   'texts': []
               },
               'url': 'test_url'}
    factory.post_document(content, prod_col)

    try:
        response = client.get('/v2/content/{}/'.format(content['id']))
        response_data = json.loads(response.data.decode())
        assert response_data['prod']['content']['title'] == 'test title'
    finally:
        factory.delete_document({'id': 'test_content_id'}, prod_col)


def test_update_content(client):
    content = {
            "id": "test id",
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
    factory.post_document(content.copy(), prod_col)

    try:
        new_title = 'title has changed'
        content['content']['title'] = new_title
        response = client.put('/v2/content/' + content['id'] + '/',
                              data=json.dumps(content),
                              content_type='application/json')
        response_data = json.loads(response.data.decode())

        assert response_data['content']['title'] == new_title

        response = client.get('/v2/content/{}/'.format(content['id']))
        response_data = json.loads(response.data.decode())
        assert not response_data['prod']['content']['title'] == new_title
        assert response_data['manual']['content']['title'] == new_title

    finally:
        factory.delete_document({'id': 'test id'}, manual_col)
        factory.delete_document({'id': 'test id'}, prod_col)


def test_get_document(client):
    document = {
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
    factory.post_document(document.copy(), prod_col)

    try:
        response = client.get('/v2/contents/?url=' + document['url'])
        response_data = json.loads(response.data.decode())
        assert response_data[0]['id'] == 'test_id_for_url'

    finally:
        factory.delete_document({'id': 'test_id_for_url'}, prod_col)


def test_delete_content(client):
    document = {
            "id": "test id for url",
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
    factory.post_document(document.copy(), prod_col)
    factory.post_document(document.copy(), manual_col)

    try:
        response = client.delete('/v2/content/'+document['id']+'/')
        response_data = json.loads(response.data.decode())
        assert response_data['deleted_count'] > 0
    finally:
        pass
        factory.delete_document({'id': document['id']}, prod_col)
        factory.delete_document({'id': document['id']}, manual_col)


def test_get_unknown_queries(client):
    query = {'query_text': 'test unknown_query'}
    factory.post_document(query.copy(), unknown_col)

    try:
        response = client.get('/v2/unknown_queries/')
        response_data = json.loads(response.data.decode())
        assert query in response_data
    finally:
        factory.delete_document(query, unknown_col)


def test_delete_unknown_query(client):
    query = {'query_text': 'test unknown_query'}
    factory.post_document(query, unknown_col)

    try:
        text = query['query_text']
        response = client.delete('/v2/unknown_queries/{}/'.format(text))
        response_data = json.loads(response.data.decode())
        assert response_data['deleted_count'] > 0
    finally:
        factory.delete_document(query, unknown_col)
