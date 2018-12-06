#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
from pymongo import WriteConcern
import random
import datetime


ObjectId = orm_module.ObjectId


"""
系统管理员
系统日志
"""


class Company(orm_module.BaseDoc):
    """
    公司信息
    """
    _table_name = "company_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['company_name'] = str
    type_dict['code_length'] = int  # 条码长度.默认35
    type_dict['inventory_threshold'] = int  # 设定的最小库存空白条码数量阈值,低于此会报警
    type_dict['printed_threshold'] = int  # 设定的已打印未使用的条码数量阈值,低于此会报警
    type_dict['desc'] = str
    type_dict['last'] = datetime.datetime
    type_dict['time'] = datetime.datetime
    type_dict['organization'] = dict  # 组织架构 {"name": 生产部: "children": [], ...},

    @classmethod
    def get_threshold(cls) -> dict:
        """
        获取公司的空白库存最低阈值和已打印可用条码阈值
        :return:
        """
        res = {"inventory_threshold": None, "printed_threshold": None}
        col = orm_module.get_conn(table_name=cls.get_table_name())
        r = col.find_one(filter=dict())
        if r is None:
            pass
        else:
            res['inventory_threshold'] = r.get("inventory_threshold")
            res['printed_threshold'] = r.get("printed_threshold")
        return res


class Product(orm_module.BaseDoc):
    """公司产品信息"""
    _table_name = "product_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['product_name'] = str  # 产品名称
    type_dict['specification'] = str  # 产品规格
    type_dict['net_contents'] = str  # 净含量,
    type_dict['package_ratio'] = str  # 包装比例 200:1
    # type_dict['batch_number'] = str  # 批号
    type_dict['last'] = datetime.datetime
    type_dict['time'] = datetime.datetime

    @classmethod
    def add(cls, **kwargs) -> dict:
        """
        添加产品
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        product_name = kwargs.get("product_name", "")
        specification = kwargs.get("specification", "")
        net_contents = kwargs.get("net_contents", "")
        package_ratio = kwargs.get("package_ratio", "")
        db_client = orm_module.get_client()
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
        f = {
            "product_name": product_name,
            "specification": specification,
            "net_contents": net_contents,
            "package_ratio": package_ratio
        }
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                r = col.find_one(filter=f, session=ses)
                if r is None:
                    now = datetime.datetime.now()
                    f['time'] = now
                    f['last'] = now
                    r = col.insert_one(document=f, session=ses)
                    if r is None:
                        mes['message'] = "保存失败"
                    else:
                        pass
                else:
                    mes['message'] = "重复的产品信息"
        return mes

    @classmethod
    def selector_data(cls, filter_dict: dict = None) -> dict:
        """
        获取产品的选择器
        :param filter_dict: 查询字典,None表示查询第一级
        :return:
        每一级别的查询方式如下:
        第一级: None
            返回{product_name:_id}
        第二级: {"product_name": product_name}
            返回{specification:_id}
        第三级: {"specification": specification}
            返回{net_contents:_id}
        第四级: {"net_contents": net_contents}
            返回{package_ratio:_id}
        """
        pipeline = []
        match = {"$match": filter_dict if filter_dict else dict()}
        pipeline.append(match)
        if filter_dict is None:
            add = {"$addFields": {"name": "$product_name"}}
            pipeline.append(add)
        elif "product_name" in filter_dict and "specification" in filter_dict and "net_contents" in filter_dict:
            add = {"$addFields": {"name": "$package_ratio"}}
            pipeline.append(add)
        elif "product_name" in filter_dict and "specification" in filter_dict:
            add = {"$addFields": {"name": "$net_contents"}}
            pipeline.append(add)
        elif "product_name" in filter_dict:
            add = {"$addFields": {"name": "$specification"}}
            pipeline.append(add)
        else:
            pass
        pipeline.append({"$project": {"_id": 1, "name": 1}})
        col = cls.get_collection()
        resp = col.aggregate(pipeline=pipeline)
        resp = {x['name']: str(x['_id']) for x in resp}
        return resp


class Dept(orm_module.BaseDoc):
    """部门信息"""
    _table_name = "dept_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['company_id'] = ObjectId
    type_dict['dept_name'] = str
    type_dict['time'] = datetime.datetime


class Role(orm_module.BaseDoc):
    """
    角色/权限组
    """
    _table_name = "role_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['role_name'] = str  # root 权限组只能有一个用户
    """
    rules是规则字典. url_path: access_value
    {view_url1: 1, view_url2: 3, ....}
    限制:    
    用户模型必须有
    1. dept_id   部门id,也可以用组id代替 部门id中有公司id
    2. role_id    角色id
    """
    type_dict['rules'] = dict
    type_dict['last'] = datetime.datetime  # 最后修改时间
    type_dict['time'] = datetime.datetime

    @classmethod
    def add(cls, **kwargs) -> dict:
        """
        添加角色
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        role_name = kwargs.get("role_name", '')
        db = orm_module.get_client()
        conn = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db)
        write_concern = WriteConcern(w=1, j=True)
        with db.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = conn.find_one(filter={'role_name': role_name})
                if r is not None:
                    ms = "角色 {} 已存在!".format(role_name)
                    mes['message'] = ms
                else:
                    """添加"""
                    r = conn.insert_one(kwargs)
                    if r is None:
                        ms = "保存用户账户失败"
                        mes['message'] = ms
                    else:
                        pass
        return mes

    @classmethod
    def all_rules(cls) -> list:
        """
        查询所有的rule,不包括root
        :return:
        """
        f = {"role_name": {"$ne": "root"}}
        data = cls.find(filter_dict=f)
        return [x for x in data]

    @classmethod
    def paging_info(cls, filter_dict: dict, page_index: int = 1, page_size: int = 10, can_json: bool = False) -> dict:
        """
        分页查看角色信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        pipeline = list()
        pipeline.append({"$match": filter_dict})
        lookup = {
            "from": "user_info",
            "let": {"role_id": "$_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$role_id", "$$role_id"]}}},  # user_info.role_id = role_info._id
                {"$addFields": {"count": {"$sum": 1}}},                     # 增加一个计数字段.
                {"$project": {"_id": 0, "user_count": "$count"}}            # 不显示_id,重命名子查询的count字段
            ],
            "as": "user_info"
        }
        replace = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects': [  # 混合文档.value是一个数组,用第二个元素覆盖第一个.注意这个顺序很重要.
                            {'$arrayElemAt': ["$user_info", 0]},  # 取主文档中user_info字段的第一个元素
                            # 取上一阶段结果中.列表字段(数组的第一个元素指示)的第0个(数组的最后一个元素指示))
                            '$$ROOT']  # 标识根文档
                    }
                }

        }
        pipeline.append({"$lookup": lookup})
        pipeline.append(replace)
        pipeline.append({"$project": {"user_info": 0}})  # 移除子查询字段
        r = cls.aggregate(pipeline=pipeline)
        return r


class User(orm_module.BaseDoc):
    """用户表"""
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str
    type_dict['nick_name'] = str
    type_dict['dept_id'] = ObjectId
    type_dict['role_id'] = ObjectId
    type_dict['last'] = datetime.datetime
    type_dict['time'] = datetime.datetime
    type_dict['status'] = int         # 用户状态,默认值1.可用. 0禁用

    @classmethod
    def add_user(cls, **kwargs) -> dict:
        """
        添加用户
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        user_name = kwargs.get("user_name", '')
        pwd = kwargs.get("password", '')
        args = {"user_name": user_name, "password": pwd}
        db = orm_module.get_client()
        conn = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db)
        write_concern = WriteConcern(w=1, j=True)
        with db.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = conn.find_one(filter={'user_name': user_name})
                if r is not None:
                    ms = "账户 {} 已存在!".format(user_name)
                    mes['message'] = ms
                else:
                    """提取其他信息"""
                    role_id_str = kwargs.get("role_id", '')
                    if isinstance(role_id_str, str) and len(role_id_str) == 24:
                        role_id = ObjectId(role_id_str)
                    elif isinstance(role_id_str, ObjectId):
                        role_id = role_id_str
                    else:
                        role_id = None
                    args['role_id'] = role_id
                    args['dept_id'] = None
                    now = datetime.datetime.now()  # 创建时间
                    args['time'] = now
                    args['last'] = now
                    args['status'] = 1
                    nick_name = kwargs.get("nick_name", "")
                    if isinstance(nick_name, str) and len(nick_name) > 0:
                        args['nick_name'] = nick_name
                    else:
                        nick_name = "guest_{}".format(str(random.randint(1, 99)).zfill(2))
                        args['nick_name'] = nick_name
                    r = conn.insert_one(args)
                    if r is None:
                        ms = "保存用户账户失败"
                        mes['message'] = ms
                    else:
                        pass
        return mes

    @classmethod
    def login(cls, user_name: str, password: str) -> dict:
        """
        管理员登录检查
        当前管理员: root/Ems@123457
        :param user_name:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        f = {"user_name": user_name}
        conn = cls.get_collection()
        r = conn.find_one(filter=f)
        if r is None:
            mes['message'] = "用户名不存在"
        else:
            if user_name != "root" and r['status'] == 0:
                mes['message'] = "账户已被禁用"
            else:
                if password.lower() == r['password'].lower():
                    mes['_id'] = r['_id']
                else:
                    mes['message'] = '密码错误'
        return mes

    @classmethod
    def change_pw(cls, u_id: ObjectId, pwd_old: str, pw_n1: str, pw_n2: str) -> dict:
        """
        修改密码
        :param u_id:
        :param pwd_old:
        :param pw_n1:
        :param pw_n2:
        :return:
        """
        mes = {"message": 'unknow error!'}
        db_client = orm_module.get_client()
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                f = {"_id": u_id}
                p = ["_id", "password"]
                r = col.find_one(filter=f, projection=p)
                if r is None:
                    mes['message'] = "错误的用户id:{}".format(u_id)
                else:
                    if r.get("password", "").lower() == pwd_old.lower():
                        if pw_n1 == pw_n2:
                            pw = pw_n1.lower()
                            u = {"$set": {"password": pw}}
                            r = col.find_one_and_update(filter=f, update=u, return_document=orm_module.ReturnDocument.AFTER)
                            if r['password'] == pw:
                                mes['message'] = "success"
                            else:
                                mes['message'] = "保存失败"
                    else:
                        mes['message'] = "原始密码错误"
        return mes

    @classmethod
    def get_role(cls, user: (dict, str, ObjectId)) -> dict:
        """
        获取一个用户的权限组.权限组中有2个特殊的权限组
        root: 系统管理员.  拥有所有权限
        guest: 来宾   所有的访问权限都是最低
        :param user:
        :return:
        """
        mes = {"message": "success"}
        user = cls.find_by_id(o_id=user, to_dict=True) if isinstance(user, (str, ObjectId)) else user
        if isinstance(user, (User, dict)):
            """是实例或者doc"""
            user = user.get_dict() if isinstance(user, User) else user
            role_id = user.get("role_id", '')
            if role_id == "":
                mes['message'] = "用户缺少角色信息: user: {}".format(user)
            else:
                f = {"_id": role_id}
                ses = Role.get_collection()
                r = ses.find_one(filter=f)
                if r is None:
                    mes['message'] = "错误的角色id: {}".format(role_id)
                else:
                    mes['role'] = r
        else:
            mes['message'] = "参数错误: user:{}".format(user)
        return mes

    @classmethod
    def paging_info(cls, filter_dict: dict, page_index: int = 1, page_size: int = 10, can_json: bool = False,
                   include_role: bool = True, include_dept: bool = True) -> dict:
        """
        分页查看用户信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :param include_role: 是否包含角色信息?
        :param include_dept: 是否包含部门信息?
        :return:
        """
        join_cond = list()
        if include_role:
            join_cond_role = {
                "table_name": "role_info",
                "local_field": "role_id",
                "field_map": {"role_name": "role_name", "role_id": "role_id"},
                "flat": True
            }
            join_cond.append(join_cond_role)
        else:
            pass
        if include_dept:
            join_cond_dept = {
                "table_name": "dept_info",
                "local_field": "dept_id",
                "field_map": {"dept_name": "dept_name", "dept_id": "dept_id"},
                "flat": True
            }
            join_cond.append(join_cond_dept)
        else:
            pass
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,            # join查询角色表 role_info
            "sort_cond": [('time', -1), ('last', -1)],   # 主文档排序条件
            "page_index": page_index,        # 当前页
            "page_size": page_size,  # 每页多少条记录
            "can_json": can_json
        }
        r = User.query(**kw)
        return r


class ProductLine(orm_module.BaseDoc):
    """
    生产线设备
    """
    _table_name = "product_line"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str
    type_dict['desc'] = str
    type_dict['time'] = datetime.datetime

    @classmethod
    def paging_info(cls, filter_dict: dict, page_index: int = 1, page_size: int = 10,
                    can_json: bool = False) -> dict:
        """
        分页查看设备信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        """
        不用field_map字段是不对子查询做更名,
        flat = False是保留多个子查询的内容
        """
        join_cond = {
            "table_name": "embedded",
            "local_field": "_id",
            "foreign_field": "line_id",
            "flat": False
        }
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,
            "sort_cond": [('time', -1)],  # 主文档排序条件
            "page_index": page_index,  # 当前页
            "page_size": page_size,  # 每页多少条记录
            "can_json": can_json
        }
        r = cls.query(**kw)
        return r


class Embedded(orm_module.BaseDoc):
    """
    嵌入式设备
    """
    _table_name = "embedded"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['line_id'] = ObjectId
    type_dict['ip'] = str
    """
    children是执行板信息
    children = {
        uuid4().hex: ip,
    }
    """
    type_dict['children'] = dict


class ProduceTask(orm_module.BaseDoc):
    """
    生产任务
    """
    _table_name = "produce_task"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['task_name'] = str
    type_dict['task_desc'] = str
    type_dict['plan_number'] = int  # 计划生产数量
    type_dict['actual_number'] = int  # 实际生产数量
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['status'] = int   # 状态, -1 删除, 0 默认未开始/停止, 1 进行中
    type_dict['create'] = datetime.datetime  # 任务创建日期
    type_dict['product_id'] = ObjectId

    @classmethod
    def paging_info(cls, filter_dict: dict, page_index: int = 1, page_size: int = 10, can_json: bool = False) -> dict:
        """
        分页查看生产任务信息.
        :param filter_dict: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        filter_dict.update({"status": {"$ne": -1}})
        join_cond = list()
        product_cond = {
            "table_name": "product_info",
            "local_field": "product_id",
            "foreign_field": "_id",
            "flat": True
        }
        join_cond.append(product_cond)

        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,  # join查询角色表 role_info
            "sort_cond": [('create', -1), ('begin', -1)],  # 主文档排序条件
            "page_index": page_index,  # 当前页
            "page_size": page_size,  # 每页多少条记录
            "can_json": can_json
        }
        r = ProduceTask.query(**kw)
        return r

    @classmethod
    def delete_tasks(cls, ids: list) -> dict:
        """
        批量删除任务
        :param ids:
        :return:
        """
        mes = {"message": "success"}
        ids = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        cls.delete_many(filter_dict={"_id": {"$in": ids}})
        return mes

    @classmethod
    def task_summary(cls) -> dict:
        """
        查看所有任务的概况/统计信息
        :return:
        """



if __name__ == "__main__":
    """添加一个管理员"""
    # root_init = {
    #     "user_name": "root", "password": "e10adc3949ba59abbe56e057f20f883e",
    #     "role_id": ObjectId("5bdfad388e76d6efa7b92d9e"),
    #     "nick_name": "系统管理员"
    # }
    # print(User.add_user())
    # sorted_cond = {"create_time": -1, "last_update": -1}
    # r = User.query_by_page2(filter_dict=dict(), sort_cond=sorted_cond)
    """事务测试"""
    # db_client = orm_module.get_client()
    # w = orm_module.get_write_concern()
    # col = orm_module.get_conn(table_name="user_info", db_client=db_client, write_concern=w)
    # with db_client.start_session(causal_consistency=True) as ses:
    #     with ses.start_transaction(write_concern=w):
    #         f = {"user_name": "root"}
    #         r = col.find_one(filter=f, session=ses)
    #         if r is None:
    #             f['password'] = "123456"
    #             r = col.insert_one(document=f, session=ses)
    Product.selector_data()
    pass