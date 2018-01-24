# -*- coding: utf-8 -*-
from test_01 import app
from celery.schedules import crontab
import random

"""
定义任务的运行会在当前目录生成一个celerybeat.pid文件,记得删除,否则下次运行会报错.

crontab()                                                 每分钟执行一次
crontab(minute=0, hour=0)                                 每天午夜执行一次
crontab(minute=0, hour='*/3')                             每天的3的倍数的整点执行: 0, 3, 6, 9, 12, 15, 18, 21
crontab(minute=0, hour='1, 3, 5')                         每天在指定的整点执行
crontab(minute='*/15')                                    每隔15分钟执行一次

"""



app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'test_01.add',
        'schedule': crontab(),
        'args': (7, 7)
    },
}
app.conf.timezone = 'UTC'