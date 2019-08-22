import chatbot.api.v2.models as models

from flask_restplus import Namespace, Resource, fields, abort

from chatbot.model.model_factory import ModelFactory
from chatbot.util.config_util import Config


api = Namespace('v2', description='Chatbot APIv2')


factory = ModelFactory.get_instance()
factory.set_db()

prod_col = Config.get_mongo_collection("prod")
manual_col = Config.get_mongo_collection("manual")
conflict_col = Config.get_mongo_collection("conflicts")
unknown_col = Config.get_mongo_collection("unknown")


direct_response_model = api.model('DirectResponse', {
    'user_input': fields.String(description='User chat input', required=True),
    'response': fields.String(description='Bot chat response', required=True)
})

conflict_model = api.model('Conflict', {
    'conflict_id': fields.String(description='Document ID for conflict',
                                 required=True),
    'title': fields.String(description='Title of conflict content',
                           required=True)
})

delete_model = api.model('Delete', {
    'acknowledged': fields.Boolean(descrpition='True if DB operation was ok',
                                   required=True),
    'deleted_count': fields.Integer(description='How many docs were removed',
                                    required=True)
})


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Response(Resource):
    @api.marshal_with(direct_response_model)
    def get(self, query):
        return models.DirectResponse(user_input=query)


class FullResponse(Resource):
    def get(self):
        pass


class ConflictIDs(Resource):
    @api.marshal_with(conflict_model)
    def get(self):
        conflict_ids = factory.get_collection(conflict_col).find()
        return [models.Conflict(conflict['conflict_id'], conflict['title'])
                for conflict in conflict_ids]

    @api.marshal_with(delete_model)
    @api.response(200, 'Success', delete_model)
    @api.response(404, 'Conflict not found')
    def delete(self, conflict_id):
        result = factory.delete_document({"conflict_id": conflict_id},
                                         conflict_col)
        if result.deleted_count > 0:
            return result
        else:
            abort(404, 'Conflict not found')


api.add_resource(HelloWorld,
                 '/',
                 methods=['GET'])
api.add_resource(Response,
                 '/response/<string:query>/',
                 methods=['GET'])
api.add_resource(FullResponse,
                 '/response/',
                 methods=['GET'])
api.add_resource(ConflictIDs,
                 '/conflict_ids/',
                 methods=['GET'])
api.add_resource(ConflictIDs,
                 '/conflict_ids/<conflict_id>/',
                 methods=['DELETE'])
