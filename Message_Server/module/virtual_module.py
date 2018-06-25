# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from module.item_module import Signal
from bson.objectid import ObjectId
import datetime


"""
此模块用于根据老师喊单的信号，生成对应的虚拟喊单信号
"""


class VirtualSignal(Signal):
    """
    虚拟交易信号，以原始交易信号为蓝本生成。
    目前已知的虚拟方式如下：
    1. follow  正向
    2. reverse 反向
    3. random  随机
    虚拟信号和原始喊单信号共用一个表。
    """
    def __init__(self, signal: Signal, direction: str, ):