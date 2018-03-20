#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import telnetlib
from log_module import get_logger
import datetime
from mail_module import send_mail
import time


logger = get_logger()
replica_hosts = [
        {"host": "safego.org", "port": 20000, "fail_count": list(), 'status': "on_line"},
        {"host": "pltf.safego.org", "port": 7171, "fail_count": list(), 'status': "on_line"},
        {"host": "pltf.safego.org", "port": 8181, "fail_count": list(), 'status': "on_line"}
    ]


"""网络测试工具模块"""


def check_server_and_send_mail():
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
    global replica_hosts
    for host in replica_hosts:
        ip = host['host']
        port = host['port']
        fail_count = host['fail_count']
        status = host['status']
        mes = ''
        try:
            t = telnetlib.Telnet(host=ip, port=port, timeout=5)
            t.close()
        except Exception as e:
            mes = "{}:{}连接失败,错误原因:{}".format(ip, port, e)
            logger.exception(mes)
            print(e)
        finally:
            now = datetime.datetime.now()
            if mes != '':
                """连接发生异常"""
                now_status = "off_line"
                fail_count.append(now)
                if len(fail_count) >= 2:
                    """连续失败2次以上"""
                    fail_count = fail_count[-2:]
                else:
                    pass
            else:
                now_status = "on_line"
                fail_count.clear()

            if status != now_status:
                status = now_status
                title = "来自scanner的检测: {}服务器检测{}".format(ip, "正常" if status == "on_line" else "失败")
                content = "来自 39.108.67.178的探测结果 {} 服务器{}:{},mongodb例行检查结果:{}".format(now, ip, port, status)
                send_mail(title=title, content=content)
                host['fail_count'] = fail_count
                host['status'] = status
            else:
                pass


if __name__ == "__main__":
    while 1:
        check_server_and_send_mail()
        time.sleep(60)
    pass