#  -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import json


app = Flask(__name__)


"""flask server example"""


@app.route("/token", methods=['post', 'get'])
def example():
    # token = request.headers.get("auth-token")  # success
    token = request.headers.get("auth_token")  # error
    result = {"token": token}
    return json.dumps(result)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)