from flask import Flask
from flask_cors import CORS

import chatbot.api.v1.util as util
from chatbot.api.v1.dialogflow import dialog_api as v1_dialog_api
from chatbot.api.v1.web import web_api as v1_web_api

app = Flask(__name__)
app.register_blueprint(v1_dialog_api)
app.register_blueprint(v1_web_api)

CORS(app)


@app.route("/", methods=["GET"])
def test():
    return util.create_success_response("Success")
