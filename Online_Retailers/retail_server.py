from flask import Flask


port = 7015
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, Threaded=True)
