# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template


app = Flask(__name__)
port = 7999


"""视图函数"""


@app.route('/')
def favicon_func():
    return "hello world!"


@app.route("/news")
def news_func():
    """新闻页"""
    return render_template("news.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
