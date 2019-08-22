from flask import Flask
from flask_cors import CORS
from flask_restplus import Api

from chatbot.api.v1.dialogflow import dialog_api as v1_dialog_api
from chatbot.api.v1.web import web_api as v1_web_api
from chatbot.api.v2.api import api as v2_api

app = Flask(__name__)

# Register version 1 blueprints. These two APIs does not use flask_restplus,
# but define their own namespaces of '/v1/dialogflow' and '/v1/web'
# They are are also not documented through Swagger
app.register_blueprint(v1_dialog_api)
app.register_blueprint(v1_web_api)

api = Api(app, version='2.0')
api.add_namespace(v2_api)

CORS(app)
