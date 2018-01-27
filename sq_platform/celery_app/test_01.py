# -*- coding: utf-8 -*-
import time
from celery import Celery
from celery.schedules import crontab


"""celery测试模块"""


broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'


app = Celery("my_task", broker=broker, backend=backend)


CELERYBEAT_SCHEDULE = {
    "at_some_time": # 定时任务
    {              
    "task": "add",
    "schedule": crontab(hour=15, minute=16),
    "args": (4, 3)
    }
}

@app.task
def add(x, y):
    time.sleep(5)
    return x + y

