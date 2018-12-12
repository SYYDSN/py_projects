#  -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests
from uuid import uuid4
from celery_module.my_celery import app


"""celery任务模块"""


@app.task
def send_uuid():
    u = "http://127.0.0.1:8500/listen"
    r = requests.post(u, data={"mes": uuid4().hex})
    return r.text


@app.task
def add(x, y):
    return int(x) + int(y)


if __name__ == "__main__":
    pass
