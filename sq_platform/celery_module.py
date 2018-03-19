# -*- coding:utf-8 -*-
from log_module import get_logger
from celery import Celery
from api.data import item_module
from bson.objectid import ObjectId
from api.data.item_module import *
from api.user.security_module import *
from api.data.file_module import when_upload_success
from api.data.file_module import unzip_all_user_file
from mongo_db import get_conn, get_obj_id, cache, replica_hosts
import telnetlib
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
    "batch_generator_report":{"queue":"batch_generator_report_exchange", "exchange_type":"direct", "routing_key": "batch_generator_report"}
    # Queue(name="fanout_queue_01", exchange=Exchange(name='fanout_queue_01_exchange', type="fanout")),  # 广播类型
}

"""指定路由暂时无法成功"""
CELERY_ROUTES = {
    "generator_yesterday_security_report": "batch_generator_report",
    "celery_module.test": "test"
}

broker_url = "redis://127.0.0.1:6379/15"
backend_url = "redis://127.0.0.1:6379/14"


CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_SERIALIZER = "json"
CELERYD_CONCURRENCY = 2  # 并发worker数
CELERYD_PREFETCH_MULTIPLIER = 4  # celery worker 每次去rabbitmq取任务的数量，我这里预取了4个慢慢执行,因为任务有长有短没有预取太多
CELERYD_MAX_TASKS_PER_CHILD = 10  # 每个worker执行了多少任务就会死掉，越小释放内存越快
CELERYD_FORCE_EXECV = True          # 有些情况下可以防止死锁
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
def unzip_file(*args, **kwargs):
    """解压app用户上传的传感器数据"""
    zip_path = kwargs['zip_path']
    when_upload_success(zip_path=zip_path)
    return "ok"


@app.task(bind=True)
def unzip_all_file(*args, **kwargs):
    """解压所有用户上传的传感器数据"""
    unzip_all_user_file()
    return "unzip all file ok"


@app.task(bind=True)
def save_gps(*args, **kwargs):
    """
    保存gps数据
    """
    gps = item_module.GPS(**kwargs)
    message = {"message": "success"}
    try:
        result = gps.insert()
        if isinstance(result, ObjectId):
            pass
        else:
            message['message'] = '插入失败'
    except Exception as e:
        message['message'] = '插入失败'
        logger.exception("Error: ")
    finally:
        return message


@app.task(bind=True)
def save_sensor(*args, **kwargs):
    """
    保存传感器数据
    """
    sensor = item_module.Sensor(**kwargs)
    message = {"message": "success"}
    try:
        result = sensor.insert()
        if isinstance(result, ObjectId):
            pass
        else:
            message['message'] = '插入失败'
    except Exception as e:
        message['message'] = '插入失败'
        logger.exception("Error: ")
    finally:
        return message


@app.task
def generator_yesterday_security_report(*args, **kwargs):
    """
    生成昨天的安全报告。被beat于每天凌晨00：30分调用一次
    同时会生成一份虚拟的安全报告的扩展数据,用于更新
    :param args:
    :param kwargs:
    :return:
    """
    all_user_id = User.get_all_user_id()
    day = datetime.datetime.today() - datetime.timedelta(days=1)
    [SecurityReport.create_instance_by_day(user_id, day, True) for user_id in all_user_id]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ms = " generator_yesterday_security_report function success!".format(now)
    logger.info(ms)
    return now


@app.task
def generator_yesterday_health_report(*args, **kwargs):
    """
    生成昨天的健康报告
    此任务应该被定时装置调用,在每天的凌晨2点-3点运行.
    :param args:
    :param kwargs:
    :return:
    """
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    title = "{}健康报告生成日志".format(now.strftime("%F"))
    content = ''
    user_ids = User.get_all_user_id()
    for user_id in user_ids:
        try:
            res = HealthReport.get_instance(user_id, yesterday)
            if res is None:
                ms = "{},用户 {} 生成安全报告失败".format(now.strftime("%Y-%m-%d %H:%M:%S"), user_id)
                content += "{}\n".format(ms)
                logger.exception(ms)
        except Exception as e:
            ms = "{},用户 {} 生成安全报告出错,错误原因:{}".format(now.strftime("%Y-%m-%d %H:%M:%S"), user_id, str(e))
            content += "{}\n".format(ms)
            print(e)
            logger.exception(ms)
        finally:
            pass
    if content != "":
        """有内容的时候才发送邮件"""
        send_mail(title=title, content=content)


@app.task
def batch_insert_gps(*args, **kwargs):
    """批量插入gps数据
    用于处理app端的实时gps数据.定时批量插入
    """
    res = item_module.GPS.async_insert_many()
    log_type = "celery_module.batch_insert_gps"
    info = {"return": res}
    item_module.Log.record(log_type, info)
    print(res)


@app.task
def check_server_and_send_mail(*args, **kwargs):
    """
    检查副本集合的服务器是否在线?如果不在线的话就发送email.(只有在状态改变的时候才发生送email)
    :param args:
    :param kwargs:
    :return:
    """

    """
    status_dict是存放上一次服务器探测结果的字典,以服务器的 ip+":"+port为key,相关信息字典为value
    {
    "192.168.0.110:27017":
    {"ip":"192.168.0.110","port":"27017", "last_time":"2017-11-27 10:11:21.940", "last_status": True},
    ....
    }
    """
    key = "replica_set_status"
    status_dict = {} if cache.get(key) is None else cache.get(key)
    for host in replica_hosts:
        current_status = False
        ip = host['host']
        port = host['port']
        try:
            t = telnetlib.Telnet(host=ip, port=port, timeout=15)
            current_status = True
            t.close()
        except Exception as e:
            mes = "{}:{}连接失败,错误原因:{}".format(ip, port, e)
            logger.exception(mes)
            print(e)
        finally:
            now = datetime.datetime.now()
            temp_key = "{}:{}".format(ip, port)
            temp_value = {
                "ip": ip, "port": port, "last_time": now,
                "last_status": current_status
            }
            prev_status = None
            if len(status_dict) == 0:
                pass
            else:
                try:
                    prev_status = status_dict[temp_key]['last_status']
                except KeyError as e:
                    print(e)
                except TypeError as e:
                    print(e)
                finally:
                    pass
            flag_mail = False
            status_dict[temp_key] = temp_value
            cache.set(key, status_dict, timeout=60 * 5)
            if prev_status is None and not current_status:
                """第一次就检测服务器失败"""
                flag_mail = True
            elif prev_status is not None and prev_status != current_status:
                flag_mail = True
            else:
                pass
            if flag_mail:
                title = "{} 服务器mongodb检测{}".format(ip, "正常" if current_status else "失败")
                content = "{} 服务器ip:{},mongodb例行检查结果:{}".format(now, ip, current_status)
                send_mail(title=title, content=content)
            else:
                pass
    ms = "check_server_and_send_mail 函数检测结果: {}".format(status_dict)
    logger.info(ms)  # celery有特殊的日志系统,传统的做法无效


if __name__ == "__main__":
    check_server_and_send_mail()
    # app.start()
