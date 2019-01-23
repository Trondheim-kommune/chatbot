import json
from flask import *
app = Flask(__name__)



@app.route("/", methods= ["POST"])
def user():
    data = request.data
    jsonData = json.loads(data)
    print(jsonData)
    return data
