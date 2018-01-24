# -*- coding:utf-8 -*-
import celery_module


"""celery 测试模块"""


celery_module.unzip_file.delay(user_id="59b20e0ade713e1456cfdb45")
celery_module.unzip_file.delay(user_id="59895177de713e304a67d30c")
celery_module.unzip_all_file.delay()