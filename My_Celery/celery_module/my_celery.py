#  -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from celery import Celery


"""celery主模块"""


app = Celery(
    main="first_celery",
    backend="redis://127.0.0.1:6379/15",
    broker="redis://127.0.0.1:6379/14",
    timezone = "Asia/Shanghai",
    include=['celery_module.my_tasks']
)
app.conf.update(
    result_expires=3600
)


if __name__ == "__main__":
    app.start()
    pass
