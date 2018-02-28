#  -*- coding: utf-8 -*-
import mongo_db


"""
权限控制模块
用户执行某一操作的权限描述如下:
某人 使用 某方法 操作 某对象
操作权限 = 对象范围 + 方法
对象范围包括6类:
1. (s)elf 自己 
2. (
方法分三类: 1. (R)ead 读 2.(W)rite 写 (包含修改) 3.(D)elete 删除


"""


class Rule(mongo_db.BaseDoc):
    pass