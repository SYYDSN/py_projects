# -*- coding:utf-8 -*-
import time
from celery import Celery
from db_module import bak_sql_session
from db_module import structure_sql


broker_url = "redis://127.0.0.1:6379/0"
backend_url = "redis://127.0.0.1:6379/1"
celery = Celery('tanks', broker=backend_url, backend=backend_url)


"""broker是中间人，backend用来储存结果,从celery.result.AsyncResult对象返回响应结果，两者的设置可以一致"""


@celery.task
def bak_customer(**kwargs):
    """
    异步保存用户
    """
    sql = structure_sql("add", "customer_info", **kwargs)
    ses = bak_sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()


