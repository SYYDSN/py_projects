# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


@app.route('/query/')
def hello_world():
    return 'Hello Flask!'


if __name__ == '__main__':
    app.run()