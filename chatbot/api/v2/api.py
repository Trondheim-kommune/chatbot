import chatbot.api.v2.models as models

from flask_restplus import Namespace, Resource, fields, abort, reqparse
from flask import request

from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


api = Namespace('v2', description='Chatbot APIv2')


factory = ModelFactory.get_instance()
factory.set_db()


prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


response_model = api.model('Response', {
    'user_input': fields.String(description='User chat input'),
    'response': fields.String(description='Bot chat response'),
    'style': fields.String,
    'session': fields.Integer(description='Chat session ID'),
})

response_input_model = api.model('Response', {
    'user_input': fields.String(description='Use chat input', required=True),
    'style': fields.String,
    'session': fields.Integer(description='Chat session ID', required=True),
    'source': fields.String
})

conflict_model = api.model('Conflict', {
    'id': fields.String(description='Document ID for conflict'),
    'title': fields.String(description='Title of conflict content')
})

delete_model = api.model('Delete', {
    'acknowledged': fields.Boolean(description='True if DB operation was ok'),
    'deleted_count': fields.Integer(description='How many docs were removed')
})

document_model = api.model('Document', {
    'id': fields.String(description='Content doc ID'),
    'title': fields.String(description='Content doc title')
})

keyword_model = api.model('Keyword', {
    'keyword': fields.String,
    'confidence': fields.Float
})

inner_content_model = api.model('InnerContent', {
    'title': fields.String,
    'keywords': fields.List(fields.Nested(keyword_model)),
    'text': fields.String,
    'links': fields.List(fields.List(fields.String))
})

content_model = api.model('Content', {
    'id': fields.String,
    'url': fields.String,
    'content': fields.Nested(inner_content_model)
})

content_collection_model = api.model('ContentCol', {
    'prod': fields.Nested(content_model),
    'manual': fields.Nested(content_model),
    'url': fields.String
})

unknown_query_model = api.model('UnknownQuery', {
    'query_text': fields.String
})


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


response_parser = reqparse.RequestParser()
response_parser.add_argument('style', required=False)
response_parser.add_argument('source', required=False)


class Response(Resource):
    @api.marshal_with(response_model)
    @api.expect(response_parser)
    def get(self, query):
        args = response_parser.parse_args()
        style = args['style'] if 'style' in args else 'plain'
        source = args['source'] if 'source' in args else 'dev'
        return models.Response(query, style, source)


class ResponseJSON(Resource):
    @api.marshal_with(response_model)
    @api.expect(response_input_model)
    @api.response(417, 'No session provided.')
    @api.response(417, 'No user_input provided.')
    @api.response(400, 'Invalid session ID.')
    def get(self):
        args = request.json
        if not args:
            abort(400, 'No input provided.')
        if not 'session' in args:
            abort(417, 'No session ID provided.')
        if not 'user_input' in args:
            abort(417, 'No user_input provided.')
        # TODO: Verify valid session ID

        style = args['style'] if 'style' in args else 'plain'
        source = args['source'] if 'source' in args else 'dev'
        query = args['user_input']
        session = args['session']
        return models.Response(query, style, source, session)


class ConflictIDs(Resource):
    @api.marshal_with(conflict_model)
    def get(self):
        conflict_ids = factory.get_collection(conflict_col).find()
        return [models.Conflict(conflict['id'], conflict['title'])
                for conflict in conflict_ids]

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Conflict not found')
    def delete(self, conflict_id):
        result = factory.delete_document({'id': conflict_id},
                                         conflict_col)
        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Conflict not found')


url_parser = reqparse.RequestParser()
url_parser.add_argument('url', required=True)


class Contents(Resource):
    @api.marshal_with(document_model)
    @api.expect(url_parser)
    @api.response(404, 'Document not found')
    def get(self):
        url = url_parser.parse_args()['url']
        docs = factory.get_collection(prod_col).find({'url': url})
        docs = [models.Document(doc['id'], doc['content']['title'])
                for doc in docs]
        return docs if docs else abort(404, 'Document not found')


class Content(Resource):
    @api.marshal_with(content_collection_model)
    @api.response(404, 'Content not found')
    def get(self, content_id):
        query = {'id': content_id}
        prod = next(factory.get_collection(prod_col).find(query), None)
        manual = next(factory.get_collection(manual_col).find(query), None)

        response = {}
        if prod:
            response['prod'] = prod
        else:
            abort(404, 'Content not found')

        response['manual'] = manual if manual else {}
        response['url'] = prod['url'] if prod else ''

        return response

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Content not found')
    def delete(self, content_id):
        query = {'id': content_id}
        result = factory.delete_document(query, manual_col)
        factory.update_document(query, {'manually_changed': False}, manual_col)
        factory.update_document(query, {'manually_changed': False}, prod_col)

        # Delete conflict if there was one
        factory.delete_document({'id': content_id}, conflict_col)

        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Content not found')

    @api.expect(content_model)
    @api.marshal_with(content_model)
    @api.response(400, 'Content IDs does not match!')
    @api.response(404, 'Content not found')
    def put(self, content_id):
        # Grab the data from request payload
        input_data = api.payload

        new_content = input_data['content']
        input_content_id = input_data['id']

        if not input_content_id == content_id:
            abort(400, 'Content IDs does not match!')

        query = {'id': content_id}
        # Check if the content that is requested changed actually exists
        old_content = factory.get_database() \
                             .get_collection(prod_col) \
                             .find(query)
        old_content = next(old_content, None)
        if not old_content:
            abort(404, 'Content not found')

        index = ({'id': content_id}, {'$set': {'content': new_content}})
        status = factory.get_database() \
                        .get_collection(manual_col)\
                        .update(*index)
        if status['updatedExisting'] is False:
            # If the document wasn't already in the manual collection, we need
            # to copy the automatic one first from prod
            old_content['content'] = new_content
            factory.get_database() \
                   .get_collection(manual_col) \
                   .insert_one(old_content)

        # set manually_changed to true
        index = ({'id': content_id}, {'$set': {'manually_changed': True}})
        new_document = factory.get_database() \
                              .get_collection(prod_col) \
                              .update(*index)

        # delete this document from the conflict collection
        query = {'id': content_id}
        factory.get_database().get_collection(conflict_col).delete_one(query)

        if new_document['updatedExisting']:
            return input_data


class UnknownQueries(Resource):
    @api.marshal_with(unknown_query_model)
    def get(self):
        unknown_queries = factory.get_collection(unknown_col).find()
        unknown_queries = [{'query_text': unknown_query['query_text']}
                           for unknown_query in unknown_queries]
        return unknown_queries

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Document not found')
    def delete(self, unknown_query):
        result = factory.delete_document({'query_text': unknown_query},
                                         unknown_col)
        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Unknown query not found')


api.add_resource(HelloWorld, '/', methods=['GET'])

api.add_resource(ResponseJSON, '/response/', methods=['GET'])
api.add_resource(Response, '/response/<string:query>/', methods=['GET'])

api.add_resource(ConflictIDs, '/conflict_ids/', methods=['GET'])
api.add_resource(ConflictIDs,
                 '/conflict_ids/<conflict_id>/',
                 methods=['DELETE'])

api.add_resource(Contents, '/contents/', methods=['GET'])
api.add_resource(Content,
                 '/content/<content_id>/',
                 methods=['GET', 'PUT', 'DELETE'])

api.add_resource(UnknownQueries, '/unknown_queries/', methods=['GET'])
api.add_resource(UnknownQueries,
                 '/unknown_queries/<unknown_query>/',
                 methods=['DELETE'])
