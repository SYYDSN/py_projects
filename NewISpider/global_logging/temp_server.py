from flask import Flask
from flask import request
from global_logging.rpc_client_auth import record_request



app = Flask(__name__)


@app.route("/pools/")
@record_request
def index():
    return "ok"



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
