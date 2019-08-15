from flask import Flask
from flask_cors import CORS

import chatbot.api.util as util
from chatbot.api.dialogflow import dialog_api
from chatbot.api.web import web_api

app = Flask(__name__)
app.register_blueprint(dialog_api)
app.register_blueprint(web_api)

CORS(app)


@app.route("/", methods=["GET"])
def test():
    return util.create_success_response("Success")
