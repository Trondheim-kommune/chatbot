import random

import chatbot.api.v2.models as models

from flask_restplus import Namespace, Resource, fields, abort, reqparse
from flask import request

from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


api = Namespace('v2', description='Chatbot APIv2.1')


factory = ModelFactory.get_instance()
factory.set_db()


prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


link_model = api.model('Link', {
    'title': fields.String(),
    'link': fields.String()
})

answer_model = api.model('Answer', {
    'answer_id': fields.Integer(description='Answer ID used for feedback'),
    'answer': fields.String(description='Textual answer'),
    'links': fields.List(fields.Nested(link_model))
})

response_raw_model = api.model('ResponseRaw', {
    'user_input': fields.String(description='User chat input'),
    'response': fields.List(fields.Nested(answer_model), description='Bot chat response'),
    'session': fields.Integer(description='Chat session ID'),
})

response_model = api.model('Response', {
    'user_input': fields.String(description='User chat input'),
    'response': fields.String(description='Bot chat response'),
    'style': fields.String,
    'session': fields.Integer(description='Chat session ID')
})

response_input_model = api.model('ResponseInput', {
    'user_input': fields.String(description='Use chat input', required=True),
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

session_model = api.model('Session', {
    'session': fields.Integer
})

feedback_model = api.model('Feedback', {
    'session': fields.Integer('Session ID of feedback session'),
    'user_input': fields.String('User input that generated feedback answer'),
    'answer_id': fields.Integer('ID of feedback answer'),
    'answer': fields.String('Feedback answer'),
    'feedback': fields.Integer('Feedback: {-1, 1}')
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
    @api.marshal_with(response_raw_model)
    @api.expect(response_input_model)
    @api.response(400, 'No <field> provided./Invalid ID.')
    def post(self):
        args = request.json
        if not args:
            abort(400, 'No input provided.')
        if not 'session' in args:
            abort(400, 'No session ID provided.')
        if not 'user_input' in args:
            abort(400, 'No user_input provided.')
        # TODO: Verify valid session ID

        source = args['source'] if 'source' in args else 'dev'
        query = args['user_input']
        session = args['session']
        return models.ResponseRaw(query, source, session)


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


class Session(Resource):
    @api.marshal_with(session_model)
    def get(self):
        return {"session": random.randint(1000, 9999)}

    @api.marshal_with(session_model)
    @api.response(400, 'Session already closed or timed out')
    def delete(self, session):
        # TODO: Verify if session is valid
        try:
            session = int(session)
            return {"session": session}
        except:
            abort(400, 'Session ID not an integer.')


class Feedback(Resource):
    @api.marshal_with(feedback_model)
    @api.expect(feedback_model)
    @api.response(400, 'No <field> provided/Invalid feedback value.')
    def post(self):
        args = request.json
        if not args:
            abort(400, 'No input provided.')
        
        for feedback_arg in feedback_model:
            if feedback_arg not in args:
                abort(400, 'No {} provided.'.format(feedback_arg))

        # Validate integer values
        for integer_arg in ('session', 'answer_id', 'feedback'):
            try:
               value = int(args[integer_arg])
            except:
                abort(400, '{} is not and integer.'.format(integer_arg))

        feedback = args['feedback']
        # Validate valid values for feedback
        if not (feedback == 1 or feedback == -1):
            abort(400, 'Invalid feedback value. Accepts {-1, 1} only.')

        session = args['session']
        user_input = args['user_input']
        answer = args['answer']
        answer_id = args['answer_id']

        # TODO: Implement feedback
        return models.Feedback(feedback, session, user_input, 
                               answer, answer_id)


api.add_resource(HelloWorld, '/', methods=['GET'])

api.add_resource(ResponseJSON, '/response/', methods=['POST'])
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

api.add_resource(Session, '/session/', methods=['GET'])
api.add_resource(Session, '/session/<session>/', methods=['DELETE'])

api.add_resource(Feedback, '/feedback/', methods=['POST'])
