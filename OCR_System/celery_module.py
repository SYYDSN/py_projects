# -*- coding:utf8 -*-
import time
from celery import Celery



broker_url = "redis://127.0.0.1:6379/0"
backend_url = "redis://127.0.0.1:6379/1"
celery = Celery('tanks', broker=backend_url, backend=backend_url)


"""broker是中间人，backend用来储存结果,从celery.result.AsyncResult对象返回响应结果，两者的设置可以一致"""


@celery.task
def send_message(message):
    """
    使用send_message.delay(message)延时操作时。
    返回对象是一个AsyncResult对象，需要使用get方法获得真是的返回值
    """
    print("任务{}已接收".format(message))
    time.sleep(2)
    print("任务{}已完成".format(message))
    return "延时任务{}完成".format(message)


@celery.task
def my_polling(tank_name):
    while True:
        print("轮询 {} 已开始".format(tank_name))
        time.sleep(3)
    global status
    status = False


@celery.task
def any_func(func, *args, **kwargs):
    global func_dict
    func = func_dict[func]
    print("{} 函数运行开始".format(func.__name__))
    func(*args, **kwargs)
    print("{} 函数运行结束".format(func.__name__))
