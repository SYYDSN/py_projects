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

    """每日对刚生成的安全报告附加扩展的虚拟数据并发送结果邮件"""
    'generator_yesterday_health_report': {
        'task': 'celery_module.generator_yesterday_health_report',
        'schedule': crontab(minute="30", hour="22"),  # 由于时区问题实际是临晨6:30点执行
        'args': (2, 3)
    },
    """每5分钟检查一下内网的shard服务器是否可以从外网访问"""
    'every_file_minutes_check_mongodb_server': {
        'task': 'celery_module.check_server_and_send_mail',
        'schedule': crontab(minute="*/5", hour="*"),  # 每5分钟检查一次
        'args': (2, 3)
    },
    """每5分钟检查一下内网的shard服务器是否可以从外网访问"""
    'every_file_minutes_batch_insert_gps': {
        'task': 'celery_module.batch_insert_gps',
        'schedule': crontab(minute="*", hour="*"),  # 每分钟检查一次
        'args': (2, 3)
    }
}

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("begin on {}".format(now))

if __name__ == "__main__":
    print()
    pass
