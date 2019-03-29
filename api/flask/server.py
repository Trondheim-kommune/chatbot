from flask import Flask
from flask_cors import CORS
import api.flask.flask_util as util
from api.flask.dialogflow_api import dialog_api
from api.flask.website_api import web_api

app = Flask(__name__)
app.register_blueprint(dialog_api)
app.register_blueprint(web_api)

CORS(app)


@app.route("/", methods=["GET"])
def test():
    return util.create_success_response("Success")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
