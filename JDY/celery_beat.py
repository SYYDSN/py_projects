# -*- coding: utf-8 -*-
import os
import datetime
from celery_module import app
from celery.schedules import crontab

"""celery的定时任务模块"""

dir_path = os.path.dirname(os.path.realpath(__file__))
temp_file_path = os.path.join(dir_path, 'celerybeat-schedule')
print(temp_file_path)
if os.path.isfile(temp_file_path):
    os.remove(temp_file_path)
    print("临时文件 {} 已删除".format(temp_file_path))

app.conf.CELERYBEAT_SCHEDULE = {
    """
    注意时区问题,ubuntu没有修正过的时区,和我们真正的时区相差8小时,win不受此影响
    在此影响下,程序会比预订的时间晚8个小时运行.
    """
    """增加每日检查平台1/2交易信息的作业"""
    'add_check_transaction': {
        'task': 'celery_module.query_transaction',
        'schedule': crontab(minute="10", hour="22"),  # 爬虫服务器没时区问题。由于时区问题实际是临晨6:10点执行
        'args': (2, 3)
    },
    """添加每5分钟在平台服务器检查一下出金申请的作业"""
    'every_file_minutes_check_withdraw': {
        'task': 'celery_module.query_withdraw',
        'schedule': datetime.timedelta(seconds=300)  # 每5分钟检查一次
    },
    """添加每2分钟处理一次作业"""
    'every_minutes_do_works': {
        'task': 'celery_module.do_works',
        'schedule': datetime.timedelta(seconds=120)  # 每2分钟间隔作业一次
    }
}

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("begin on {}".format(now))

if __name__ == "__main__":
    print()
    pass
