# -*- coding:utf-8 -*-
import datetime

from celery import Celery

from browser.firefox_module import to_jiandao_cloud
from browser.firefox_module import ShengFX888
from log_module import get_logger
from mail_module import send_mail

logger = get_logger("celery")


"""
exchange 相同的是同一个队列
routing_key 会匹配函数名
save_gps: 存gps数据的而队列，现在不会被使用
save_sensor: 存传感器数据的而队列，现在不会被使用
unzip_file： 解压app用户上传的文件，是一个重负载的队列
"""


CELERY_QUEUES = {
    "test": {"queue": "test", "exchange_type": "direct", "routing_key": "test"},
    "batch_generator_report":{"queue":"batch_generator_report_exchange", "exchange_type": "direct", "routing_key": "batch_generator_report"}
    # Queue(name="fanout_queue_01", exchange=Exchange(name='fanout_queue_01_exchange', type="fanout")),  # 广播类型
}

"""指定路由暂时无法成功"""
CELERY_ROUTES = {
    "generator_yesterday_security_report": "batch_generator_report",
    "celery_module.test": "test"
}

broker_url = "redis://127.0.0.1:6379/12"
backend_url = "redis://127.0.0.1:6379/13"


CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_SERIALIZER = "json"
CELERYD_CONCURRENCY = 2  # 并发worker数
CELERYD_PREFETCH_MULTIPLIER = 4  # celery worker 每次去rabbitmq取任务的数量，我这里预取了4个慢慢执行,因为任务有长有短没有预取太多
CELERYD_MAX_TASKS_PER_CHILD = 200  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，比如200
CELERY_DEFAULT_QUEUE = "default"  # 默认的队列，如果一个消息不符合其他的队列就会放在默认队列里面

app = Celery('my_task', broker=broker_url, backend=backend_url)

app.conf.update(CELERY_TIMEZONE=CELERY_TIMEZONE, CELERY_ROUTES=CELERY_ROUTES,
                   CELERY_TASK_SERIALIZER=CELERY_TASK_SERIALIZER,
                   CELERYD_CONCURRENCY=CELERYD_CONCURRENCY,
                   CELERYD_PREFETCH_MULTIPLIER=CELERYD_PREFETCH_MULTIPLIER,
                   CELERYD_MAX_TASKS_PER_CHILD=CELERYD_MAX_TASKS_PER_CHILD,
                   CELERY_DEFAULT_QUEUE=CELERY_DEFAULT_QUEUE)

"""broker是中间人，backend用来储存结果,从celery.result.AsyncResult对象返回响应结果，两者的设置可以一致"""


@app.task(bind=True)
def return_arg(*args, **kwargs):
    """测试"""
    print(args)
    print(kwargs)


@app.task(bind=True)
def test(self, *args, **kwargs):
    """测试"""
    print(self)
    print(args)
    print(kwargs)


@app.task(bind=True)
def to_jiandao_cloud_and_send_mail(*args, **kwargs):
    print(kwargs)
    res = to_jiandao_cloud(**kwargs)
    if not res:
        title = "{} 发送数据到简道云失败".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        content = str(kwargs)
        send_mail("583736361@qq.com", title, content)
    return res


@app.task(bind=True)
def check_platform_server(*args, **kwargs):
    print(args)
    print(kwargs)
    """在平台服务器检查一下交易记录和出金申请"""
    crawler = ShengFX888()
    crawler.parse_and_save()  # 爬取并保存到数据库
    crawler.db_to_cloud()  # 上传到简道云
    return "check platform server success!"


if __name__ == "__main__":
    pass
    # app.start()
