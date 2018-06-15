from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
port = 5678


@app.route('/hello')
def hello_world():
    return render_template("template.html")


@app.route("/test")
def test_func():
    return render_template()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
