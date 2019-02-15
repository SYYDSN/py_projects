# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from pony_orm import Person
import ujson
from rpc_client import RPC
from flask_cors import CORS


app = Flask(__name__)
# CORS(app)


@app.route("/", methods=['post', 'get'])
def index():
    checked = RPC.before(request)
    if checked:
        print(checked)
        name = request.args.get("name", "")
        age = 10
        authorization = request.headers.get("authorization", "")
        try:
            age = int(request.args.get("age", ""))
        except Exception as e:
            print(e)
        finally:
            if name == "":
                res = {"message": "name is required"}
            else:
                res = Person.add(name=name, age=age)
            res['authorization'] = authorization
            res = RPC.after(res, to_json=False)
    else:
        res = checked
    return ujson.dumps(res)


@app.route("/test", methods=['post', 'get'])
def index2():
        return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
