# -*- coding:utf-8 -*-
from celery import Celery
from kombu import Exchange, Queue
from mail_module import send_mail
import requests
import datetime
import asyncio


"""
exchange 相同的是同一个队列
routing_key 会匹配函数名
save_gps: 存gps数据的而队列，现在不会被使用
save_sensor: 存传感器数据的而队列，现在不会被使用
unzip_file： 解压app用户上传的文件，是一个重负载的队列
"""


broker_url = "redis://127.0.0.1:6379/11"
backend_url = "redis://127.0.0.1:6379/12"


CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_SERIALIZER = "json"
CELERYD_CONCURRENCY = 2  # 并发worker数
CELERYD_PREFETCH_MULTIPLIER = 4  # celery worker 每次去rabbitmq取任务的数量，我这里预取了4个慢慢执行,因为任务有长有短没有预取太多
CELERYD_MAX_TASKS_PER_CHILD = 40  # 每个worker执行了多少任务就会死掉，越小释放内存越快
CELERYD_FORCE_EXECV = True          # 有些情况下可以防止死锁


default_exchange = Exchange('default', type='direct')  # 默认交换机
gps_push_exchange = Exchange("score", type='direct')  # 积分计算专用交换机
gps_save_exchange = Exchange("extend", type='direct')  # 备用交换机
"""创建3个队列,一个默认的,一个score专用队列, 一个备用"""
CELERY_QUEUES = (
    Queue('default', exchange=default_exchange, routing_key='default'),
    Queue('score', exchange=gps_push_exchange, routing_key='score'),
    Queue('extend', exchange=gps_save_exchange, routing_key='extend')
)
CELERY_DEFAULT_QUEUE = 'default'  # 默认的队列，如果一个消息不符合其他的队列就会放在默认队列里面
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_ROUTES = (
    {'celery_module.score': {'queue': 'score', 'routing_key': 'score'}},
    {'celery_module.extend': {'queue': 'extend', 'routing_key': 'extend'}}
)
CELERY_IMPORTS = ('celery_module', )


app = Celery('my_task', broker=broker_url, backend=backend_url)
app.conf.update(CELERY_TIMEZONE=CELERY_TIMEZONE,
                CELERY_QUEUES=CELERY_QUEUES,
                CELERY_ROUTES=CELERY_ROUTES,
                CELERY_IMPORTS=CELERY_IMPORTS,
                CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
                CELERYD_CONCURRENCY=CELERYD_CONCURRENCY,
                CELERYD_PREFETCH_MULTIPLIER=CELERYD_PREFETCH_MULTIPLIER,
                CELERYD_MAX_TASKS_PER_CHILD=CELERYD_MAX_TASKS_PER_CHILD,
                CELERY_DEFAULT_ROUTING_KEY=CELERY_DEFAULT_ROUTING_KEY,
                CELERY_DEFAULT_EXCHANGE=CELERY_DEFAULT_EXCHANGE,
                CELERY_DEFAULT_QUEUE=CELERY_DEFAULT_QUEUE
                )

"""
启动队列建议分别用不同的worker启动队列.
python3 -m celery -A celery_module worker -Q default --loglevel=info  # 启动默认队列
"""
"""broker是中间人，backend用来储存结果,从celery.result.AsyncResult对象返回响应结果，两者的设置可以一致"""


@app.task(bind=True)
def test(self, *args, **kwargs):
    """测试"""
    print(self)
    print(args)
    print(kwargs)


@app.task(bind=False)
def send_virtual_trade(trade_json: dict) -> None:
    """
    发送虚拟喊单信号
    :param trade_json: 消息字典
    :return:
    """
    r = requests.post("http://127.0.0.1:8000/listen_virtual_trade", data=trade_json)
    status = r.status_code
    if status == 200:
        resp = r.json()
        mes = resp['message']
        if mes == "success":
            print("ok")
        else:
            print("error")
    else:
        print(status)
    print(trade_json)


if __name__ == "__main__":
    pass
