# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from module.data_module import load_data


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


@app.route("/info", methods=['post', 'get'])
def info_func():
    data = load_data()
    return data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
