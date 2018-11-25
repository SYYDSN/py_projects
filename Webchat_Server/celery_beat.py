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
    """每周1检查扣分情况一次"""
    'every_monday_calculate_score': {
        'task': 'celery_module.calculate_score_and_send_mail',
        'schedule': crontab(day_of_week="1", minute="0", hour="6"),  # 每周1检查扣分情况一次
        # 'schedule': crontab(day_of_week="*", minute="*/1", hour="*"),  # 每周1检查扣分情况一次
        'args': ()
    }
}

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("begin on {}".format(now))

if __name__ == "__main__":
    print()
    pass
