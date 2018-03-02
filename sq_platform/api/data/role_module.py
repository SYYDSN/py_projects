#  -*- coding: utf-8 -*-
import mongo_db


"""
权限控制模块
目前暂时以用户组来确定权限.
用户执行某一操作的权限描述如下:
某人 使用 某方法 操作 某对象
操作权限 = 对象范围 + 方法
对象范围包括6类:
1. (s)elf 自己 
2. (g)roup 本组 
3. (d)ept 本部门
4. (c)ompay 本公司 
方法分三类: 1. (R)ead 读 2.(W)rite 写 (包含修改) 3.(D)elete 删除


"""


class Rule(mongo_db.BaseDoc):
    """权限规则,一个角色有多个权限规则"""
    _table_name = "rule_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id 唯一
    type_dict['company_id'] = mongo_db.DBRef  # 公司id,确认权限规则属于哪个公司?
    type_dict['method'] = str  # 函数/方法名  公司下面不能有同名的方法名
    type_dict['scope'] = str  # 允许操作的对象范围.用s/g/d/c分别代指自己/本组/本部门/本公司


class Role(mongo_db.BaseDoc):
    """用户角色,也就是用户组的意思"""
    _table_name = "role_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id 唯一
    type_dict['company_id'] = mongo_db.DBRef  # 公司id,确认权限属于哪个公司?
    type_dict['role_name'] = str  # 角色名称,公司内部不重复
