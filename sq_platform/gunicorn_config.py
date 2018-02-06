#  -*- coding: utf-8 -*-
import multiprocessing


"""gunicorn的配置文件"""


# 预加载资源
preload_app = True
# 绑定
bind = "0.0.0.0:5000"
# 进程数
workers = multiprocessing.cpu_count() * 2 + 1
# 线程数
threads = multiprocessing.cpu_count() * 2
# 等待队列最大长度,超过这个长度的链接将被拒绝连接
backlog = 2048
# 工作模式
# worker_class = "egg:meinheld#gunicorn_worker"
worker_class = "gevent"
# 最大客户客户端并发数量,对使用线程和协程的worker的工作有影响
worker_connections = 1200
# 进程名称
proc_name = 'gunicorn.pid'
# 进程pid记录文件
pidfile = 'app_run.log'
# 日志等级
loglevel = 'debug'
# 日志文件名
logfile = 'debug.log'
# 访问记录
accesslog = 'access.log'
# 访问记录格式
access_log_format = '%(h)s %(t)s %(U)s %(q)s'

"""
运行方式
命令行 gunicorn -c gunicorn_config.py flask_server:app
如果在虚拟环境下运行(双py的ubuntu之流需要虚拟环境,否则会路径混乱):

"""