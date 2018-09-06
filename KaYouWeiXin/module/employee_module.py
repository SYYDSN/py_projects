# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger


ObjectId = mongo_db.ObjectId
logger = get_logger()


"""
员工模块
目前支持的数据库是mongodb 4.0+
基于角色的权限管理+扩展的访问规则
用于对项目的用户的权限进行管理.
"""


class Company(mongo_db.BaseDoc):
    """
    公司. 卡佑
    """
    _table_name = "company"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str         # 公司名
    type_dict['license_id'] = str         # 工商许可证id
    type_dict['create_time'] = datetime.datetime         # 创建时间


class Role(mongo_db.BaseDoc):
    """
    角色,权限组.
    这里定义的都是角色的默认权限.
    """
    _table_name = "role"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str         # 角色名/权限组名称
    type_dict['root'] = int         # 是否是最高管理员? 1是,0不是.
    type_dict['desc'] = str         # 说明
    type_dict['create_time'] = datetime.datetime  # 创建时间
    """
    self/dept/company/child分别代表当前用户,对当前各种类型的用户的权限.权限共有2种.
    read/write 分别用r和w替代.有w权限的的也能读,空字符代表没有权限.
    
    添加对象的权限判断逻辑如下:
    举例: 用户A添加一条用户信息B.会进行如下检查:
    1. B用户是添加到哪个dept(C部门)?
    2. A用户的权限是否有dept的w权限?
        if A用户有dept的w权限:
            检查A用户是否属于C部门?
            if A用户输入C部门:
                执行添加用户操作
            else:
                如果A用户属于D部门(而且A用户有dept的w权限),检查D是否是C上级部门?
                if D是C的上级部门:
                    检查A用户是否有下级部门的写权限?(A用户的child权限是否为w?)
                    if A用户的child的权限是w:
                        执行添加用户操作
                    else:
                        权限不足,添加失败
                else:
                    权限不足,添加失败
        else:
            权限不足,添加失败
            
    对于权限的范围所一个说明
    1. self 属于自己的信息(自己创建的,或者和自己关联的)
    2. dept 和自己同一部门的信息
    3. company 和自己同一公司的信息
    4. child 下属部门的信息. 
    """
    type_dict['self'] = str
    type_dict['dept'] = str
    type_dict['company'] = str
    type_dict['child'] = str


class Dept(mongo_db.BaseDoc):
    """
    部门.
    """
    _table_name = "dept"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['parent_id'] = ObjectId  # 上级部门id,为None表示顶层部门.
    type_dict['name'] = str         # 部门名称
    type_dict['desc'] = str         # 说明
    type_dict['create_time'] = datetime.datetime  # 创建时间


class Post(mongo_db.BaseDoc):
    """
    岗位/职务. 某种意义上,职务对应了权限.
    """
    _table_name = "post"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['dept_id'] = ObjectId
    """
    roles是角色对象的id的数组.
    Role._id的list
    因为一个岗位可以有多个权限组,这些权限组组合起来.取最高权限.
    """
    type_dict['roles'] = list
    type_dict['name'] = str         # 岗位/职务名称
    type_dict['manager'] = int         # 是否是管理岗位? 1是,0不是
    type_dict['desc'] = str         # 说明
    type_dict['create_time'] = datetime.datetime  # 创建时间


class Employee(mongo_db.BaseDoc):
    """
    员工类
    """
    _table_name = "employee"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['real_name'] = str     #
    type_dict['account'] = str  # 用户名唯一
    type_dict['password'] = str
    type_dict['post_id'] = ObjectId   # 职务. 由职务可知部门
    type_dict['openid'] = str  # 关联的微信号
    type_dict['phone'] = str  # 关联的手机号
    type_dict['email'] = str
    type_dict['ice_contact'] = str  # 紧急联系人,ICE是 in case of emergency (紧急状况)的意思
    type_dict['ice_phone'] = str  # 紧急电话
    type_dict['last_update'] = datetime.datetime  # 最后修改时间
    type_dict['create_time'] = datetime.datetime  # 创建时间


if __name__ == "__main__":
    i = {
        "_id": ObjectId(),
        "name": "卡佑",
        'desc': "",
        "create_time": datetime.datetime.now()
    }
    Company.insert_one(**i)
    pass

