#  -*- coding: utf-8 -*-
import mongo_db
import psutil


"""监控模块"""


times = psutil.cpu_times()
print(times)