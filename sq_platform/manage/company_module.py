# -*- coding:utf-8 -*-
import sys
import os

"""直接运行此脚本，避免import失败的方法"""
__project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
from api.data.item_module import User, Track
from api.data.base_item_extends import UseHandlerRecord
from api.data.violation_module import VioQueryGenerator
import hashlib
import datetime
from threading import Lock
from log_module import get_logger
import warnings


"""公司模块"""

ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
MyDBRef = mongo_db.MyDBRef
logger = get_logger()
lock_transfer_post = Lock()  # 调动职务的线程锁
lock_transfer_dept = Lock()  # 调动部门的线程锁
lock_rebuild_relation = Lock()  # 重建关系线程锁


class Company(mongo_db.BaseDoc):
    """
    公司类
    """
    _table_name = "company_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['full_name'] = str  # 公司全称,中国的公司法允许公司名称重复,但不允许商标重复
    type_dict['domain'] = str  # 域名,唯一,也可以标识公司的唯一性
    type_dict['prefix'] = str  # 公司查询前缀,唯一.用于向安全模块查询接口.在此查询中向安全模块标识身份的唯一性
    type_dict['short_name'] = str  # 简称
    type_dict['description'] = str  # 公司简介

    def __init__(self, **kwargs):
        """
        构造器,实务中,
        初始化可以使用本方法.
        创建新的Company请使用instance的类方法.
        instance类方法会初始化完成会保存实例到数据库.并生成一个默认部门.
        :param kwargs:
        """
        if 'prefix' not in kwargs:
            raise ValueError("公司查询前缀为必须参数")
        if kwargs['prefix'] == "" or kwargs['prefix'] is None:
            raise ValueError("公司查询前缀必须是一个有效的字符串")
        super(Company, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **kwargs) -> object:
        """
        创建一个实例,此方法还会
        1.保存实例.
        2.创建默认部门,并保存.
        请使用此方法替代__init__来创建新对象.
        :param kwargs:
        :return: Company的实例或者None
        """
        company = cls(**kwargs)
        oid = company.insert()
        if isinstance(company, cls) and isinstance(oid, ObjectId):
            Dept.root_dept(company, desc="{}的顶层部门".format('' if kwargs.get('short_name') else
                                                          kwargs['short_name']))
        else:
            pass
        return company

    def add_admin(self, admin_name: str, admin_password: str, desc: int = '', only_view: bool = False) -> bool:
        """
        添加一个管理员
        :param admin_name:
        :param admin_password:
        :param desc: 说明
        :param only_view:是否是只读管理员?
        :return:
        """
        f = {"user_name": admin_name, "company_id": self.get_dbref()}
        r = CompanyAdmin.find_one_plus(filter_dict=f, instance=False)
        if r is not None:
            ms = "重复的管理员用户名:{}.{}".format(self.get_attr("short_name"), admin_name)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            init = {
                "user_password": admin_password,
                "md5": True,
                "only_view": only_view,
                "description": desc
            }
            init.update(f)
            obj = CompanyAdmin(**init)
            r = obj.save_plus()
            if r is None:
                return False
            else:
                return True

    def get_prefix(self) -> str:
        """
        获取公司的前缀
        :return:
        """
        return self.get_attr("prefix")

    def online_report(self, filter_online: int = 0, sort_dict: dict = None) -> dict:
        """
        统计公司在线情况,返回的是一个list文件.
        :param filter_online: 过滤条件:是否在线? 0/全部,1/在线,-1/离线
        :param sort_dict: 排序字典
        :return:
        """
        """默认最后一次登录时间倒序"""
        if sort_dict is None:
            sort_dict = {"last_update": -1}
        filter_online_list = [0, 1, -1]
        if filter_online == 0:
            pass
        elif filter_online == 1:
            filter_online_list = [1]
        else:
            filter_online_list = [-1]
        company_dbref = self.get_dbref()
        company_id = company_dbref.id
        employees = Company.all_employee(company_id=company_id, sort_dict=sort_dict)
        func_name = "query_violation"  # 查询违章的函数名
        res = list()
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        all_count = len(employees)
        today_reg_count = 0  # 今日注册统计
        vio_count = 0  # 违章查询统计
        hours = 0  # 在线时长统计
        for x in employees:
            user_dbref = DBRef(database=mongo_db.db_name, collection="user_info", id=x['_id'])
            vio = UseHandlerRecord.get_count(user_dbref, func_name)  # 查违章使用次数
            x['query_violation'] = vio
            vio_count += vio
            """检查在线情况?"""
            last_update = User.last_update_cls(x['_id'])
            online = -1 if (now - last_update).total_seconds() > 1500 else 1
            x['online'] = online
            """最后登录时间"""
            x['last_update_str'] = last_update.strftime("%y年%m月%d日%H点%M分")
            x['os_version'] = "未知" if x.get("os_version") is None else x['os_version']
            """注册时间"""
            reg_date = x['create_date']
            cur_year = reg_date.year
            cur_month = reg_date.month
            cur_day = reg_date.day
            if cur_month == month and cur_year == year and cur_day == day:
                today_reg_count += 1
            x['create_date_str'] = reg_date.strftime("%y年%m月%d日%H点%M分")
            """在线时长"""
            online_time = 0.0 if x.get("online_time") is None else x['online_time']
            try:
                online_time = float(online_time)
            except TypeError as e:
                print(e)
                online_time = 0.0
            finally:
                online_time = int(online_time / 60)
                hours += online_time
                x['online_time'] = "{}小时".format(online_time)
            if online in filter_online_list:
                """过滤条件"""
                res.append(mongo_db.to_flat_dict(x))

        resp = dict()
        resp["all"] = all_count
        """今日注册"""
        resp['today_reg'] = today_reg_count
        """平均在线时长"""
        resp['mean'] = 0 if all_count == 0 else round((hours / all_count), 1)
        """违章统计"""
        resp['vio_count'] = vio_count
        resp['employees'] = res
        return resp

    @classmethod
    def get_prefix_by_id(cls, company_id: (str, ObjectId)) -> (None, str):
        """
        获取公司的前缀
        :param company_id:
        :return:
        """
        f = {"_id": mongo_db.get_obj_id(company_id)}
        one = cls.find_one_plus(filter_dict=f, instance=False)
        if one is None:
            return False
        else:
            return one['prefix']

    @classmethod
    def find_by_prefix(cls, pre: str, instance: bool = False) -> (dict, object, None):
        """
        根据前缀查找公司
        :param pre: 前缀
        :param instance: 返回实例还是返回doc? 默认返回doc
        :return:
        """
        if isinstance(pre, str) and len(pre) > 0:
            f = {"prefix": pre}
            one = cls.find_one_plus(filter_dict=f, instance=instance)
            return one
        else:
            pass

    @classmethod
    def validate_employee(cls, company_id: (str, ObjectId), employee_id: (str, ObjectId)) -> (None, dict):
        """
        验证公司是否存在某位员工,如果不存在,返回None,存在,返回职务的字典
        :param company_id:
        :param employee_id:
        :return: 职务信息
        """
        company_id = mongo_db.get_obj_id(company_id)
        employee_id = mongo_db.get_obj_id(employee_id)
        company_dbref = DBRef(database="platform_db", collection=cls.get_table_name(), id=company_id)
        employee = Employee.find_by_id(employee_id)
        if not isinstance(employee, Employee):
            pass
        else:
            employee_dbref = employee.get_dbref()
            now = datetime.datetime.now()
            f_dict = {
                "$and": [
                    {"employee_id": employee_dbref},
                    {"company_id": company_dbref},
                    {"create_date": {"$lte": now}},
                    {"$or": [
                        {"end_date": {"$exists": False}},
                        {"end_date": {"$eq": None}},
                        {"end_date": {"$gte": now}}
                    ]
                    }]
            }
            r = EmployeeCompanyRelation.find_one_plus(filter_dict=f_dict, instance=False)
            if r is None:
                pass
            else:
                """查询职务信息"""
                post = employee.get_post()
                return post

    def hire_one_employee(self, user_id: (str, ObjectId, DBRef), dept_id: (str, ObjectId, DBRef), post_id:
    (str, ObjectId, DBRef)) -> bool:
        """
        雇佣一名员工,这是一个实例方法
        :param user_id: 用户id
        :param dept_id: 岗位id
        :param post_id: 职务id
        :return: 
        """
        """转换user_id为DBRef类型"""
        if isinstance(user_id, DBRef):
            employee_dbref = user_id
        elif isinstance(user_id, (str, ObjectId)):
            if isinstance(user_id, str):
                l = len(user_id)
                if l != 24:
                    ms = "user_id的长度错误,length:{}".format(l)
                    raise ValueError(ms)
                else:
                    user_id = ObjectId(user_id)
            else:
                pass
            employee_dbref = DBRef(database=mongo_db.db_name, collection=Employee.get_table_name(), id=user_id)
        else:
            ms = "错误的user_id类型:{}".format(type(user_id))
            raise ValueError(ms)

        """转换dept_id为DBRef类型"""
        if isinstance(dept_id, DBRef):
            dept_dbref = dept_id
        elif isinstance(dept_id, (str, ObjectId)):
            if isinstance(dept_id, str):
                l = len(dept_id)
                if l != 24:
                    ms = "dept_id的长度错误,length:{}".format(l)
                    raise ValueError(ms)
                else:
                    dept_id = ObjectId(dept_id)
            else:
                pass
            dept_dbref = DBRef(database=mongo_db.db_name, collection=Dept.get_table_name(), id=dept_id)
        else:
            ms = "错误的dept_id类型:{}".format(type(dept_id))
            raise ValueError(ms)

        """转换post_id为DBRef类型"""
        if isinstance(post_id, DBRef):
            post_dbref = post_id
        elif isinstance(post_id, (str, ObjectId)):
            if isinstance(post_id, str):
                l = len(post_id)
                if l != 24:
                    ms = "post_id的长度错误,length:{}".format(l)
                    raise ValueError(ms)
                else:
                    post_id = ObjectId(post_id)
            else:
                pass
            post_dbref = DBRef(database=mongo_db.db_name, collection=Post.get_table_name(), id=post_id)
        else:
            ms = "错误的post_id类型:{}".format(type(post_id))
            raise ValueError(ms)

        company_dbref = self.get_dbref()

        lock_rebuild_relation.acquire()  # 锁定
        """清除旧的关系库"""
        now = datetime.datetime.now()
        f = {
            "$or": [
                {"end_date": {"$gt": now}},
                {"end_date": {"exists": False}}
            ],
            "employee_id": employee_dbref
        }
        u = {"$set": {"end_date": now}}
        EmployeeCompanyRelation.update_many_plus(filter_dict=f, update_dict=u)
        EmployeeDeptRelation.update_many_plus(filter_dict=f, update_dict=u)
        EmployeePostRelation.update_many_plus(filter_dict=f, update_dict=u)
        # 添加员工/公司关系
        company_relation_dbref = EmployeeCompanyRelation.add_relation(emp_dbref=employee_dbref,
                                                                      dbref_name="company_id",
                                                                      dbref_val=company_dbref)
        # 添加员工/部门关系
        dept_relation_dbref = EmployeeDeptRelation.add_relation(emp_dbref=employee_dbref, dbref_name="dept_id",
                                                                dbref_val=dept_dbref)
        # 添加员工/职务关系
        post_relation_dbref = EmployeePostRelation.add_relation(emp_dbref=employee_dbref, dbref_name="post_id",
                                                                dbref_val=post_dbref)
        f = {"_id": employee_dbref.id}
        u = {"$set": {
            "company_relation_id": company_relation_dbref,
            "dept_relation_id": dept_relation_dbref,
            "post_relation_id": post_relation_dbref
        }}
        res = Employee.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
        lock_rebuild_relation.release()  # 释放
        if res is None:
            print("修改用户信息失败,f:{},u:{}".format(f, u))
            return False
        else:
            return True

    @classmethod
    def add_employee(cls, company_id: (str, ObjectId), args_list: (list, dict)) -> None:
        """
        单独/批量添加员工, 重复的导入会覆盖以前的数据.添加一个员工也可以使用此方法.
        调用此方法之前,建议检查对应的权限.
        此方法没有线程锁,方法的逻辑如下:
        1. 确认公司id是否存在?不存在退出,存在就要验证部门id和职务id的合法性
        2. 添加一个employee的对象.
        3. 先清除职员和其他公司的关机记录,然后再创建一条EmployeeCompanyRelation记录.保存.然后在employee添加company_relation_id属性.
        4. 如果有部门id,就验证一下部门id是否存在?存在就添加一条EmployeeDeptRelation记录,不存在就报错.
        先清除员工和其他部门的关系.
        然后在employee添加dept_relation_id属性.如果没有部门id,那就添加一个默认的部门的dept_relation_id属性,
        如果没有默认部门.报错退出.
        5. 如果有职务id,就验证一下职务id是否存在?存在就添加一条EmployeePostRelation记录,不存在就报错.
        先清除员工和其他职务的关系.
        然后在employee添加post_relation_id属性.如果没有职务id,那就添加一个默认的职务的post_relation_id属性,
        如果没有默认职务.报错退出.
        6.再次保存employee的对象
        :param company_id:
        :param args_list: 员工的初始化参数的字典组成的list,一般是从app或者web端接收的信息.包含
        :return:
        """
        company = cls.find_by_id(company_id)
        """如果用户输入的数据不是数组,那就转换成数组,这是应对客户只输入了一个用户信息字典的情况"""
        args_list = [args_list] if not isinstance(args_list, list) else args_list
        """检查公司id是否正确"""
        if isinstance(company, cls):
            """公司存在"""
            company_dbref = company.get_dbref()
            now = datetime.datetime.now()
            for args in args_list:
                dept_id = args.pop("dept_id", None)  # 部门id
                post_id = args.pop("post_id", None)  # 职务id
                """检查部门id是否正确?"""
                dept = Dept.find_by_id(dept_id)
                if dept.get_attr("company_id") != company_dbref:
                    ms = "部门信息:{} 和 公司信息:{} 不符".format(dept_id, company_id)
                    raise ValueError(ms)
                """检查职务id是否正确?"""
                post = Post.find_by_id(post_id)
                if post.get_attr("company_id") != company_dbref:
                    ms = "职务信息:{} 和 公司信息:{} 不符".format(post_id, company_id)
                    raise ValueError(ms)
                """检查注册手机号码是否北占用?"""
                obj = Employee.find_one_plus(filter_dict={"phone_num": args.get("phone_num")}, instance=False)
                if obj is None:
                    """手机号没有被占用,可以创建一个新用户"""
                    pass
                else:
                    """此手机号码已被注册过,添加变成修改"""
                    for k, v in obj.items():
                        if k == "_id":
                            args['_id'] = v
                        elif k not in args:
                            args[k] = v
                        else:
                            pass
                emp = Employee(**args)
                employee_id = emp.save()
                if isinstance(employee_id, ObjectId):
                    """employee插入成功"""
                    employee_dbref = emp.get_dbref()
                    """检查EmployeeCompanyRelation记录是否存在"""
                    f = {"company_id": company_dbref, "employee_id": employee_dbref, "create_date": {"$lte": now},
                         "$or": [
                             {"end_date": {"$exists": False}},
                             {"end_date": {"$eq": None}},
                             {"end_date": {"$gte": now}}
                         ]}
                    company_relation = EmployeeCompanyRelation.find_one_plus(filter_dict=f, instance=True)
                    if company_relation is None:
                        """没有员工和公司的关系记录,检查是否有此人和其他公司的记录?"""
                        f = {
                            "employee_id": employee_dbref,
                            "$or": [
                                {"end_date": {"$exists": False}},
                                {"end_date": {"$eq": None}},
                                {"end_date": {"$gte": now}}
                            ]
                        }
                        relations = EmployeeCompanyRelation.find_plus(filter_dict=f, to_dict=False)
                        for relation in relations:
                            relation.set_attr("end_date", now)
                        """添加EmployeeCompanyRelation记录"""
                        company_relation = EmployeeCompanyRelation(company_id=company_dbref, employee_id=employee_dbref,
                                                                   create_date=now)
                        company_relation_id = company_relation.save()
                        if isinstance(company_relation_id, ObjectId):
                            """添加EmployeeCompanyRelation记录成功"""
                            pass
                        else:
                            raise ValueError("添加EmployeeCompanyRelation记录失败, args={}".format(args))
                    else:
                        """有员工和公司的关系记录,无需添加EmployeeCompanyRelation记录"""
                        pass
                    company_relation_dbref = company_relation.get_dbref()
                    emp.set_attr("company_relation_id", company_relation_dbref)
                    if isinstance(dept, Dept):
                        dept_dbref = dept.get_dbref()
                        """部门存在,无需额外添加Dept记录,检查是否有EmployeeDeptRelation记录"""
                        f = {"company_id": dept_dbref, "employee_id": employee_dbref, "create_date": {"$lte": now},
                             "$or": [
                                 {"end_date": {"$exists": False}},
                                 {"end_date": {"$eq": None}},
                                 {"end_date": {"$gte": now}}
                             ]}
                        dept_relation = Dept.find_one_plus(filter_dict=f, instance=True)
                        if dept_relation is None:
                            """没有员工和部门的关系记录,检查是否有此人和其他部门的记录?"""
                            f = {
                                "employee_id": employee_dbref,
                                "$or": [
                                    {"end_date": {"$exists": False}},
                                    {"end_date": {"$eq": None}},
                                    {"end_date": {"$gte": now}}
                                ]
                            }
                            relations = EmployeeDeptRelation.find_plus(filter_dict=f, to_dict=False)
                            for relation in relations:
                                relation.set_attr("end_date", now)
                            """没有对应的EmployeeDeptRelation记录,可以创建一个"""
                            dept_relation = EmployeeDeptRelation(dept_id=dept_dbref, employee_id=employee_dbref,
                                                                 create_date=now)
                            dept_relation_id = dept_relation.save()
                            if isinstance(dept_relation_id, ObjectId):
                                """EmployeeDeptRelation记录保存成功"""
                                pass
                            else:
                                raise ValueError("{} 部门关系信息保存失败".format(dept_id))
                        else:
                            """有对应的EmployeeDeptRelation记录,无需创建"""
                            pass
                        dept_relation_dbref = dept_relation.get_dbref()
                        emp.set_attr("dept_relation_id", dept_relation_dbref)
                        if isinstance(post, Post):
                            post_dbref = post.get_dbref()
                            """职务存在,无需额外添加Post记录,检查是否有EmployeePostRelation记录"""
                            f = {"post_id": post_dbref, "employee_id": employee_dbref, "create_date": {"$lte": now},
                                 "$or": [
                                     {"end_date": {"$exists": False}},
                                     {"end_date": {"$eq": None}},
                                     {"end_date": {"$gte": now}}
                                 ]}
                            post_relation = Post.find_one_plus(filter_dict=f, instance=True)
                            if post_relation is None:
                                """没有员工和职务的关系记录,检查是否有此人和其他职务的记录?"""
                                f = {
                                    "employee_id": employee_dbref,
                                    "$or": [
                                        {"end_date": {"$exists": False}},
                                        {"end_date": {"$eq": None}},
                                        {"end_date": {"$gte": now}}
                                    ]
                                }
                                relations = EmployeePostRelation.find_plus(filter_dict=f, to_dict=False)
                                for relation in relations:
                                    relation.set_attr("end_date", now)
                                """没有对应的EmployeePostRelation记录,可以创建一个"""
                                post_relation = EmployeePostRelation(post_id=post_dbref, employee_id=employee_dbref,
                                                                     create_date=now)
                                post_relation_id = post_relation.save()
                                if isinstance(post_relation_id, ObjectId):
                                    """EmployeePostRelation记录保存成功"""
                                    pass
                                else:
                                    raise ValueError("{} 职务关系信息保存失败".format(post_id))
                            else:
                                """有对应的EmployeePostRelation记录,无需创建"""
                                pass
                            post_relation_dbref = post_relation.get_dbref()
                            emp.set_attr("post_relation_id", post_relation_dbref)
                            emp_id = emp.save()
                            if isinstance(emp_id, ObjectId):
                                """最终保存成功"""
                                pass
                            else:
                                raise ValueError("最后employee信息保存失败")
                        else:
                            """职务不存在"""
                            raise ValueError("{} 职务不存在".format(post_id))
                    else:
                        """部门不存在"""
                        raise ValueError("{} 部门不存在".format(dept_id))
                else:
                    raise ValueError("用户插入失败,args={}".format(args))
        else:
            raise ValueError("{}公司id错误".format(company_id))

    @classmethod
    def dismiss_employee(cls, company_id: (str, ObjectId), id_list: (list, dict)) -> None:
        """
        解雇单个/多个员工,注意,只是解除公司和员工的雇佣关系.不是删除员工的账户.
        调用此方法之前,建议检查对应的权限.
        此方法没有线程锁,方法的逻辑如下:
        1. 确认公司id是否存在?不存在退出,
        2. 确认员工是否归属这个公司? 确认公司的部门?(确认部门其实是为了确认)
        3. 修改对应的EmployeePostRelation记录
        4. 修改对应的EmployeeDeptRelation记录
        5. 修改对应的EmployeeCompanyRelation记录
        6. 修改employee信息
        :param company_id:
        :param id_list: 员工id组成的list
        :return:
        """
        company = cls.find_by_id(company_id)
        """如果用户输入的数据不是数组,那就转换成数组,这是应对客户只输入了一个用户信息字典的情况"""
        id_list = [id_list] if not isinstance(id_list, list) else id_list
        """检查公司id是否正确"""
        if isinstance(company, cls):
            """公司存在"""
            company_dbref = company.get_dbref()
            for emp_id in id_list:
                emp = Employee.find_by_id(emp_id)
                if isinstance(emp, Employee):
                    """员工id正确,检查归属关系"""
                    company_relation_dbref = emp.get_attr("company_relation_id")
                    if company_relation_dbref is None:
                        print("员工 {} 不属于任何公司".format(emp_id))
                    else:
                        company_relation_id = company_relation_dbref.id
                        company_relation = EmployeeCompanyRelation.find_by_id(company_relation_id)
                        if isinstance(company_relation, EmployeeCompanyRelation) and company_relation.get_attr(
                                "company_id") == company_dbref:
                            """是公司员工"""
                            dept_relation_dbref = emp.get_attr("dept_relation_id")
                            dept_relation_id = dept_relation_dbref.id
                            dept_relation = EmployeeDeptRelation.find_by_id(dept_relation_id)

                            post_relation_dbref = emp.get_attr("post_relation_id")
                            post_relation_id = post_relation_dbref.id
                            post_relation = EmployeePostRelation.find_by_id(post_relation_id)

                            now = datetime.datetime.now()
                            if isinstance(dept_relation, EmployeeDeptRelation):
                                dept_relation.set_attr("end_date", now)
                                dept_relation.save_plus()
                            else:
                                pass
                            if isinstance(post_relation, EmployeePostRelation):
                                post_relation.set_attr("end_date", now)
                                post_relation.save_plus()
                            else:
                                pass
                            company_relation.set_attr("end_date", now)
                            company_relation.save_plus()
                            emp.remove_attr("company_relation_id")
                            emp.remove_attr("dept_relation_id")
                            emp.remove_attr("post_relation_id")
                            emp.save_plus()  # 解雇成功
                        else:
                            ms = "员工id {} 不是 {} 的职员".format(emp_id, company.get_attr("short_name"))
                            print(ms)
                else:
                    raise ValueError("员工id错误 {}".format(emp_id))
        else:
            raise ValueError("公司id错误 {}".format(company_id))

    @classmethod
    def clear_employee(cls, id_list: (list, dict)) -> None:
        """
        清除单个/多个员工及其相关的关系记录,注意,这会完全删除员工的档案.把员工降级为一般用户
        调用此方法之前,建议检查对应的权限.
        此方法没有线程锁,方法的逻辑如下:
        1. 删除对应的EmployeePostRelation记录
        2. 删除对应的EmployeeDeptRelation记录
        3. 删除对应的EmployeeCompanyRelation记录
        4. 修改employee信息
        :param id_list: 员工id组成的list
        :return:
        """
        ms = "正在清除员工和公司之间的记录,清除结束后,员工账户将会变成非企业用户"
        warnings.warn(ms)
        """如果用户输入的数据不是数组,那就转换成数组,这是应对客户只输入了一个用户信息字典的情况"""
        id_list = [id_list] if not isinstance(id_list, list) else id_list
        for emp_id in id_list:
            emp = Employee.find_by_id(emp_id)
            if isinstance(emp, Employee):
                f = {"employee_id": emp.get_dbref()}
                EmployeePostRelation.delete_many(f)
                EmployeeDeptRelation.delete_many(f)
                EmployeeCompanyRelation.delete_many(f)
                emp.remove_attr("company_relation_id")
                emp.remove_attr("dept_relation_id")
                emp.remove_attr("post_relation_id")
                emp.remove_attr("dept_path")
                emp.remove_attr("post_id")
                emp.remove_attr("company_id")
                emp.save_plus()  # 清除成功
            else:
                ms = "员工id {} 错误".format(emp_id)
                print(ms)

    @classmethod
    def delete_employee(cls, company_id: (str, ObjectId), id_list: (list, dict)) -> None:
        """
        这个方法只允许系统管理员使用.
        删除单个/多个员工及其相关的关系记录,注意,这会完全删除员工的档案.用户账户将不可登录,此操作不可逆转.
        调用此方法之前,建议检查对应的权限.
        此方法没有线程锁,方法的逻辑如下:
        1. 确认公司id是否存在?不存在退出,
        2. 确认员工是否归属这个公司? 确认公司的部门?(确认部门其实是为了确认)
        3. 删除对应的EmployeePostRelation记录
        4. 删除对应的EmployeeDeptRelation记录
        5. 删除对应的EmployeeCompanyRelation记录
        6. 删除employee信息
        :param company_id:
        :param id_list: 员工id组成的list
        :return:
        """
        ms = "正在删除员工账户,这将清理员工在系统中的所有记录,用户账户将不再可用,此操作不可逆转"
        warnings.warn(ms)
        company = cls.find_by_id(company_id)
        """如果用户输入的数据不是数组,那就转换成数组,这是应对客户只输入了一个用户信息字典的情况"""
        id_list = [id_list] if not isinstance(id_list, list) else id_list
        """检查公司id是否正确"""
        if isinstance(company, cls):
            """公司存在"""
            company_dbref = company.get_dbref()
            for emp_id in id_list:
                emp = Employee.find_by_id(emp_id)
                if isinstance(emp, Employee):
                    """员工id正确,无需检查归属关系"""
                    company_relation_dbref = emp.get_attr("company_relation_id")
                    company_relation_id = company_relation_dbref.id
                    company_relation = EmployeeCompanyRelation.find_by_id(company_relation_id)
                    if isinstance(company_relation, EmployeeCompanyRelation) and company_relation.get_attr(
                            "company_id") == company_dbref:
                        """是公司员工"""
                        f = {"employee_id": emp.get_dbref()}
                        EmployeePostRelation.delete_many(f)
                        EmployeeDeptRelation.delete_many(f)
                        EmployeeCompanyRelation.delete_many(f)
                        emp.delete_self()  # 删除成功.
                    else:
                        ms = "员工id {} 不是 {} 的职员".format(emp_id, company.get_attr("short_name"))
                        raise ValueError(ms)
                else:
                    raise ValueError("员工id错误 {}".format(emp_id))
        else:
            raise ValueError("公司id错误 {}".format(company_id))

    @classmethod
    def rebuild_relation(cls, company_id: ObjectId, dept_id: ObjectId, post_id: ObjectId, employee_list: list = None):
        """
        重新建立公司,员工,部门和职务之间的关系,用于转变旧的关系模式到新的关系模式
        此方法也可以用来批量转移员工和企业之间的对应关系
        :param company_id:
        :param dept_id:
        :param post_id:
        :param employee_list:ObjectId的list
        :return:
        """
        company_dbref = DBRef(collection="company_info", database="platform_db", id=company_id)
        dept_dbref = DBRef(collection="company_info", database="platform_db", id=dept_id)
        post_dbref = DBRef(collection="company_info", database="platform_db", id=post_id)

        if employee_list is None or len(employee_list) == 0:
            pass
        else:
            lock_rebuild_relation.acquire()  # 锁定
            employee_dbref_list = [DBRef(database=mongo_db.db_name, collection=Employee.get_table_name(), id=x)
                                   for x in employee_list]
            """清除旧的关系库"""
            now = datetime.datetime.now()
            f = {
                "$or": [
                    {"end_date": {"$gt": now}},
                    {"end_date": {"exists": False}}
                ],
                "employee_id": {"$in": employee_dbref_list}
            }
            u = {"$set": {"end_date": now}}
            EmployeeCompanyRelation.update_many_plus(filter_dict=f, update_dict=u)
            EmployeeDeptRelation.update_many_plus(filter_dict=f, update_dict=u)
            EmployeePostRelation.update_many_plus(filter_dict=f, update_dict=u)
            for i, _id in enumerate(employee_list):
                dbref = employee_dbref_list[i]
                # 添加员工/公司关系
                company_relation_dbref = EmployeeCompanyRelation.add_relation(emp_dbref=dbref,
                                                                              dbref_name="company_id",
                                                                              dbref_val=company_dbref)
                # 添加员工/部门关系
                dept_relation_dbref = EmployeeDeptRelation.add_relation(emp_dbref=dbref, dbref_name="dept_id",
                                                                        dbref_val=dept_dbref)
                # 添加员工/职务关系
                post_relation_dbref = EmployeePostRelation.add_relation(emp_dbref=dbref, dbref_name="post_id",
                                                                        dbref_val=post_dbref)
                f = {"_id": _id}
                u = {"$set": {
                    "company_relation_id": company_relation_dbref,
                    "dept_relation_id": dept_relation_dbref,
                    "post_relation_id": post_relation_dbref
                              }}
                res = Employee.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                if res is None:
                    print("修改用户信息失败,f:{},u:{}".format(f, u))
            lock_rebuild_relation.release()  # 释放

    @classmethod
    def transfer_dept(cls, company_id: (str, ObjectId), employee_id: (str, ObjectId), dept_id: (str, ObjectId)) -> bool:
        """
        调动部门
        :param company_id:
        :param employee_id:
        :param dept_id:
        :return:
        """
        res = False
        company = cls.find_by_id(company_id)
        employee = Employee.find_by_id(employee_id)
        dept = Dept.find_by_id(dept_id)
        if isinstance(company, cls) and isinstance(employee, Employee) and isinstance(dept, Dept):
            lock_transfer_dept.acquire()  # 锁定
            """先查找此员工旧的部门关系"""
            employee_dbref = employee.get_dbref()
            now = datetime.datetime.now()
            f = {
                "employee_id": employee_dbref,
                "$or": [
                    {"end_date": {"$exists": False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$gte": now}}
                ]
            }
            old_dept_relations = EmployeeDeptRelation.find_plus(filter_dict=f, to_dict=True)
            for old_dept_relation in old_dept_relations:
                """清除旧关系"""
                f = {"_id": old_dept_relation['_id']}
                u = {"$set": {"end_date": now}}
                EmployeeDeptRelation.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            """创建并保存一条新的员工&部门的关系"""
            dept_dbref = dept.get_dbref()
            args = {
                "_id": ObjectId(),
                "dept_id": dept_dbref,
                "employee_id": employee_dbref,
                "create_date": now
            }
            r = EmployeeDeptRelation.insert_one(**args)
            if isinstance(r, ObjectId):
                """插入新的部门和员工关系成功,更新员工的dept_relation_id"""
                dept_relation_dbref = DBRef(database="platform_db", collection=Dept.get_table_name(), id=r)
                f = {"_id": employee.get_id()}
                u = {"$set": {"dept_relation_id": dept_relation_dbref}}
                r = Employee.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                lock_transfer_dept.release()  # 释放
                if isinstance(r, dict):
                    """更新成功"""
                    res = True
                else:
                    pass
            else:
                lock_transfer_dept.release()  # 释放
                ms = "插入新的EmployeePostRelation对象失败,args={}".format(args)
                logger.exception(ms)
                raise ValueError(ms)
        else:
            ms = "参数和错误,company_id={}, employee_id={},dept_id={}".format(company_id, employee_id, dept_id)
            logger.exception(ms)
            raise ValueError(ms)
        return res

    @classmethod
    def transfer_post(cls, company_id: (str, ObjectId), employee_id: (str, ObjectId), post_id: (str, ObjectId)) -> bool:
        """
        调动岗位
        :param company_id:
        :param employee_id:
        :param post_id: 职务id
        :return:
        """
        res = False
        company = cls.find_by_id(company_id)
        employee = Employee.find_by_id(employee_id)
        post = Post.find_by_id(post_id)
        if isinstance(company, cls) and isinstance(employee, Employee) and isinstance(post, Post):
            lock_transfer_post.acquire()  # 锁定
            """先查找此员工旧的职务关系"""
            employee_dbref = employee.get_dbref()
            now = datetime.datetime.now()
            f = {
                "employee_id": employee_dbref,
                "$or": [
                    {"end_date": {"$exists": False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$gte": now}}
                ]
            }
            old_post_relations = EmployeePostRelation.find_plus(filter_dict=f, to_dict=True)
            for old_post_relation in old_post_relations:
                f = {"_id": old_post_relation['_id']}
                u = {"$set": {"end_date": now}}
                EmployeePostRelation.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            """创建并保存一条新的员工&职务的关系"""
            post_dbref = post.get_dbref()
            args = {
                "_id": ObjectId(),
                "post_id": post_dbref,
                "employee_id": employee_dbref,
                "create_date": now
            }
            r = EmployeePostRelation.insert_one(**args)
            if isinstance(r, ObjectId):
                """插入成功,更新员工的post_relation_id"""
                post_relation_dbref = DBRef(database="platform_db", collection=Post.get_table_name(), id=r)
                f = {"_id": employee.get_id()}
                u = {"$set": {"post_relation_id": post_relation_dbref}}
                r = Employee.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                lock_transfer_post.release()  # 释放
                if isinstance(r, dict):
                    """更新成功"""
                    res = True
                else:
                    pass
            else:
                lock_transfer_post.release()  # 释放
                ms = "插入新的EmployeePostRelation对象失败,args={}".format(args)
                logger.exception(ms)
                raise ValueError(ms)
        else:
            ms = "参数和错误,company_id={}, employee_id={},dept_id={}".format(company_id, employee_id, post_id)
            logger.exception(ms)
            raise ValueError(ms)
        return res

    @classmethod
    def add_post(cls, company_id: (str, ObjectId), post_dict: dict) -> dict:
        """
        添加一个职务,若干  如果存在同名职务,那就返回它而不添加.
        :param company_id:
        :param post_dict: 职务的初始化字典,比如
        driver_dict = {
        "company_id": company_dbref,  # 无需添加亦可
        "post_name": "司机",
        "description": "车辆驾驶员,默认岗位,不可删除",
        "level": 1,
        "default": True,
        }
        :return: doc
        """
        res = None
        company = cls.find_by_id(company_id)
        if not isinstance(company, cls) or 'post_name' not in post_dict:
            ms = "错误的公司id或错误的初始化参数,company_id:{}, post_dict:{}".format(company_id, post_dict)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            company_dbref = company.get_dbref()
            """先查找公司是否已有相同的职务名称?"""
            f = {"company_id": company_dbref, 'post_name': post_dict['post_name']}
            r = Post.find_one_plus(filter_dict=f, instance=False)
            if r is None:
                """还没有相同的职务"""
                if "_id" in post_dict:
                    pass
                else:
                    post_dict['_id'] = ObjectId(None)
                if "company_id" in post_dict:
                    pass
                else:
                    post_dict['company_id'] = company_dbref
                r = Post.insert_one(**post_dict)
                if r is None:
                    ms = "插入失败 post_dict:{}".format(post_dict)
                    logger.exception(ms)
                    raise ValueError(ms)
                else:
                    res = post_dict
            else:
                res = r
        return res

    @classmethod
    def add_dept(cls, company_id: (str, ObjectId), dept_dict: dict) -> dict:
        """
        添加一个部门  如果存在同名部门,那就返回它而不添加.
        :param company_id:
        :param dept_dict: 部门的初始化字典,比如
        dept_dict = {
        "company_id": company_dbref,  # 无需添加亦可
        "dept_name": "xx部门",
        "root_dept"; False,  # 是不是总部?
        "higher_dept": DBRef,  # 上级部门id
        "description": "技术部门",
        "create_date": datetime
        }
        :return: doc
        """
        res = None
        company = cls.find_by_id(company_id)
        if not isinstance(company, cls) or 'dept_name' not in dept_dict:
            ms = "错误的公司id或错误的初始化参数,company_id:{}, post_dict:{}".format(company_id, dept_dict)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            company_dbref = company.get_dbref()
            """先查找公司是否已有相同的部门名称?"""
            f = {"company_id": company_dbref, 'dept_name': dept_dict['dept_name']}
            r = Dept.find_one_plus(filter_dict=f, instance=False)
            if r is None:
                """还没有相同的职务"""
                if "_id" in dept_dict:
                    pass
                else:
                    dept_dict['_id'] = ObjectId(None)
                if "company_id" in dept_dict:
                    pass
                else:
                    dept_dict['company_id'] = company_dbref
                r = Dept.insert_one(**dept_dict)
                if r is None:
                    ms = "插入失败 post_dict:{}".format(dept_dict)
                    logger.exception(ms)
                    raise ValueError(ms)
                else:
                    res = dept_dict
            else:
                res = r
        return res

    @classmethod
    def all_employee(cls, company_id: (str, ObjectId), filter_dict: dict = None, sort_dict: dict = None,
                     can_json: bool = False) -> list:
        """
        获取公司的全部employee
        :param company_id:
        :param filter_dict: 附加的过滤条件
        :param sort_dict: 附加的排序条件
        :param can_json:
        :return: doc的list
        """
        company = cls.find_by_id(company_id)
        res = list()
        if not isinstance(company, cls):
            pass
        else:
            company_dbref = company.get_dbref()
            now = datetime.datetime.now()
            f = {
                "company_id": company_dbref,
                "$or": [
                    {"end_date": {"$exists": False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$gte": now}}
                ]
            }
            rs = EmployeeCompanyRelation.find_plus(filter_dict=f, to_dict=True)
            if len(rs) == 0:
                pass
            else:
                ids = [x['employee_id'].id for x in rs]
                f = {"_id": {"$in": ids}}
                if filter_dict is not None:
                    f.update(filter_dict)
                s = {"_id": 1} if sort_dict is None else sort_dict
                employees = Employee.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=can_json)
                if len(employees) == 0:
                    pass
                else:
                    res = employees
        return res

    @classmethod
    def all_post(cls, company_id: (str, ObjectId)) -> dict:
        """
        根据公司id获取全部的职务的列表
        :param company_id:
        :return:
        """
        company = cls.find_by_id(company_id)
        res = list()
        if not isinstance(company, cls):
            pass
        else:
            company_dbref = company.get_dbref()
            filter_dict = {'company_id': company_dbref}
            res = {str(m['_id']): m['post_name'] for m in Post.find_plus(filter_dict=filter_dict,
                                                                         projection=["_id", "post_name"], to_dict=True)}
        return res

    @classmethod
    def all_dept(cls, company_id: (str, ObjectId, object), can_json: bool = True) -> list:
        """
        根据公司id获取全部的职务的列表
        :param company_id:ObjectId或者cls的实例
        :param can_json:返回的部门字典是否可以直接json? False返回的是Dept的实例的数组
        :return
        """
        to_dict = False if can_json else True
        if isinstance(company_id, cls):
            company = company_id
        else:
            company = cls.find_by_id(company_id)
        res = list()
        if not isinstance(company, cls):
            pass
        else:
            company_dbref = company.get_dbref()
            filter_dict = {'company_id': company_dbref}
            res = Dept.find_plus(filter_dict=filter_dict, to_dict=to_dict, can_json=True)
        return res

    @staticmethod
    def in_post(company_id: (ObjectId, DBRef, str), post_id: (ObjectId, DBRef, str)) -> list:
        """
        查询某个公司，某个岗位的全体人员, 需要重写
        :param company_id: 公司id
        :param post_id: 职务id
        :return: 实例列表
        """
        if not isinstance(company_id, (ObjectId, DBRef, str)) or not isinstance(company_id, (ObjectId, DBRef, str)):
            try:
                raise ValueError("公司id或岗位id类型错误.company_id's type is {},post_id's type is {}".
                                 format(type(company_id), type(post_id)))
            except ValueError as e:
                logger.exception("error")
                print(e)
            except Exception as e:
                print(e)
                raise e
        else:
            """开始检查数据类型并进行转换"""
            if isinstance(company_id, (str, ObjectId)):
                company_obj = Company.find_by_id(company_id)
                if not isinstance(company_obj, Company):
                    try:
                        raise ValueError("获取Company实例失败，company_id={}".
                                         format(company_id))
                    except ValueError as e:
                        logger.exception("error")
                        print(e)
                    except Exception as e:
                        print(e)
                        raise e
                else:
                    company_id = company_obj.get_dbref()
            else:
                pass
            if isinstance(post_id, (str, ObjectId)):
                post_obj = Post.find_by_id(post_id)
                if not isinstance(post_obj, Post):
                    try:
                        raise ValueError("获取Post实例失败，post_id={}".
                                         format(post_id))
                    except ValueError as e:
                        logger.exception("error")
                        print(e)
                    except Exception as e:
                        print(e)
                        raise e
                else:
                    post_id = post_obj.get_dbref()
            else:
                pass
            if not isinstance(company_id, DBRef) or not isinstance(post_id, DBRef):
                """只要2个查询对象有一个不满足类型要求，就抛出异常"""
                try:
                    raise ValueError("转换DBRef对象失败，company_id={},post_id={}".
                                     format(str(company_id), str(post_id)))
                except ValueError as e:
                    logger.exception("error")
                    print(e)
                except Exception as e:
                    print(e)
                    raise e
            else:
                company_id_obj = company_id.id
                post_id_obj = post_id.id
                args = {"post_id.$id": post_id_obj, "company_id.$id": company_id_obj}
                instance_list = Employee.find(**args)
                return instance_list

    @classmethod
    def get_prefix_by_user_id(cls, user_id: (str, ObjectId)) ->str:
        """
        根据用户id获取用户所在公司的前缀,这用于向AI模块查询报告和排名

        用户和公司之间的约束关系如下:
        Employee: 员工类
        Company:  公司类
        EmployeeCompanyRelation: 员工和公司的关系类
        EmployeeCompanyRelation作为桥梁,建立起Employee和Company之间的关系.
        Employee-->EmployeeCompanyRelation<---Company

        EmployeeCompanyRelation的属性说明如下:
        EmployeeCompanyRelation.company_id 是一个DBRef对象,指向Company对象的id
        EmployeeCompanyRelation.employee_id 是一个DBRef对象,指向Employee对象的id
        EmployeeCompanyRelation.create_date 是一个datetime对象,是指关系建立的时间.
        EmployeeCompanyRelation.end_date  是一个datetime对象,是指关系终结的时间.这个属性如果为不存在,为None或者大于当前的时间,
        都可以认为员工和公司间的关系处于有效的状态.

        Employee有一个company_relation_id的属性,DBRef类型.,指向EmployeeCompanyRelation的id.这是个非必须的属性.
        存在的目的用于快速检索EmployeeCompanyRelation对象.

        整个方法的逻辑如下:
        1. 确认user_id有效.
        2. 确认对应的user记录有company_relation_id.
        3. 确认确认对应的user记录有company_relation_id对应的EmployeeCompanyRelation处于有效关系状态.
        4. 查找EmployeeCompanyRelation.company_id对应的Company对象.
        5. 取出Company对象的prefix属性.

        :param user_id: 用户id
        :return: Company.prefix, 散户是xxx作为prefix
        """
        user = User.find_by_id(user_id)
        prefix = "xxx"
        if isinstance(user, User):
            company_relation_dbref = user.get_attr("company_relation_id")
            if company_relation_dbref is None:
                ms = "用户{}没有company_id信息".format(str(user_id))
                print(ms)
                logger.info(ms)
            else:
                company_relation_id = company_relation_dbref.id
                """查找关系对象"""
                company_relation = EmployeeCompanyRelation.find_by_id(company_relation_id)
                if isinstance(company_relation, EmployeeCompanyRelation):
                    """EmployeeCompanyRelation对象存在"""
                    now = datetime.datetime.now()
                    if (not hasattr(company_relation, "end_date")) or company_relation.get_attr("end_date") is None or \
                                    company_relation.get_attr("end_date") < now:
                        """EmployeeCompanyRelation对象有效"""
                        company = Company.find_by_id(company_relation.get_attr(attr_name="company_id").id)
                        if isinstance(company, Company):
                            """公司存在"""
                            if hasattr(company, "prefix"):
                                prefix = company.get_attr("prefix")
                            else:
                                pass
                        else:
                            ms = "company对象错误, {}".format(company_relation.get_attr(attr_name="company_id"))
                            print(ms)
                            logger.info(ms)
                else:
                    ms = "company_relation_dbref:{}错误".format(str(company_relation_dbref))
                    print(ms)
                    logger.info(ms)
        else:
            raise ValueError("错误的用户id:{}".format(str(user_id)))
        return prefix

    @classmethod
    def employee_and_generator_cls(cls, company_id: (ObjectId, str)) -> dict:
        """
        查询一个公司的员工和违章查询器的对应关系的字典.
        :param company_id: 公司id
        :return: dict  example:  {user_id: [generator1_id, generator2_id,...]}
        """
        res = dict()
        es = cls.all_employee(company_id=company_id)
        if len(es) == 0:
            pass
        else:
            for em in es:
                e_id = em['_id']
                gs = VioQueryGenerator.generator_list(e_id)
                gs = [g['_id'] for g in gs]
                res[e_id] = gs
        return res

    @classmethod
    def all_vio_cls(cls, company_id: (ObjectId, str)) -> list:
        """
        查询一个公司的全部的违章记录,这是个临时性方法, 2018-5-23
        :param company_id:
        :return:
        """
        res = list()
        a_d = cls.employee_and_generator_cls(company_id=company_id)
        g_ids = list()
        [g_ids.extend(v) for k, v in a_d.items() if len(v) > 0]
        for g_id in g_ids:
            t = VioQueryGenerator.query(object_id=g_id)
            if "data" in t:
                data = t['data']
                vs = data['violations']
                if len(vs) > 0:
                    res.extend(vs)
                else:
                    pass
            else:
                pass
        return res


class CompanyAdmin(mongo_db.BaseDoc):
    """
    公司管理员,只有这个类的实例才能登录后台
    新振兴的管理员 xzx_root  密码 xzx@1588
    顺丰的管理员   sf_root   密码 Sf@123567
    顺丰的查看员   sf_view   密码 123456
    苏秦的管理员   sq_root   密码 Sq@123457
    """
    _table_name = "company_admin_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['user_name'] = str  # 用户名，唯一
    type_dict['user_password'] = str  # 用户密码
    type_dict['company_id'] = DBRef  # 指向company_id 是哪个公司的管理员?
    type_dict['description'] = str  # 说明
    type_dict['only_view'] = bool  # 是否是只读管理员?(只能查看页面?)这种管理员目前只给查看在线情况信息的功能
    type_dict['user_status'] = int  # 1 为启用,0为停用

    def __init__(self, **kwargs):
        """
        :param kwargs:
        arg md5: 布尔值,是否对user_password进行md5加密?当参数user_password未加密的时候,启用此项
        """
        md5_flag = kwargs.pop("md5", False)
        if 'user_status' not in kwargs:
            kwargs['user_status'] = 1
        if md5_flag:
            user_password = kwargs['user_password']
            if isinstance(user_password, str):
                user_password = hashlib.md5(user_password.encode(encoding='utf-8')).hexdigest()
                kwargs['user_password'] = user_password
            else:
                pass
        super(CompanyAdmin, self).__init__(**kwargs)


class Post(mongo_db.BaseDoc):
    """职务类"""
    _table_name = "post_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['company_id'] = DBRef  # 所属公司 Company,必须
    type_dict['post_name'] = str  # 岗位名称
    type_dict['default_post'] = bool  # 是否是默认职务?默认职务是作为未确认职务时的默认值,只可修改,不可删除
    type_dict['level'] = int  # 职务的级别,1是默认员工.大于1是用来扩展
    type_dict['description'] = str  # 说明
    """
    用来标识此职务是否具备管理权限?或者具备何种管理权限?在目前情况下,可选的值只有0和1
    level=1代表是普通职员
    每个公司内部的职位名称post_name不得重复.
    """

    def __init__(self, **kwargs):
        if "level" not in kwargs:
            kwargs['level'] = 1
        else:
            level = kwargs['level']
            if isinstance(level, (int, str)):
                if isinstance(level, str):
                    try:
                        level = int(level)
                    except ValueError as e:
                        print(e)
                        raise ValueError("{}不能转化为int类型".format(level))
                else:
                    pass
                if 0 > level or level > 1:
                    level = 0
                else:
                    pass
                kwargs['level'] = level
            else:
                raise ValueError("level必须是int,或者可转化为int类型")
        f = {
            "company_id": kwargs['company_id'],
            "post_name": kwargs['post_name']
        }
        r = self.__class__.find_one_plus(filter_dict=f, instance=False)
        if r is None:
            """没有重复的职务"""
            pass
        else:
            kwargs['_id'] = r['_id']
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(Post, self).__init__(**kwargs)

    @classmethod
    def default_post(cls, company_id: (str, ObjectId, Company), post_name: str = None, desc: str = None,
                     instance=False) -> (object, dict):
        """
        获取一个公司的默认职务,一般是这个公司的最低级的职务.
        如果这个默认职务存在,那就取回对应的doc
        如果这个默认职务不存在,那就创建保存,并返回对应的doc
        :param company_id:
        :param post_name:
        :param desc:  备注说明
        :return: doc/实例
        """
        res = None
        if not isinstance(company_id, Company):
            company = Company.find_by_id(company_id)
        else:
            company = company_id
        if not isinstance(company, Company):
            ms = "错误的company_id:{}".format(company_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            """检查是否默认职务已存在?"""
            company_dbref = company.get_dbref()
            post_name = '司机' if post_name is None or post_name == '' else post_name
            f = {
                "company_id": company_dbref,
                "level": 1
            }
            r = cls.find_one_plus(filter_dict=f, instance=False)
            if r is None:
                """默认职务不存在,可以创建"""
                dept_dict = {
                    "_id": ObjectId(),
                    "level": 1,
                    "company_id": company_dbref,
                    "post_name": post_name,
                    "description": desc
                }
                dept_dict = {k: v for k, v in dept_dict.items() if v is not None}
                r = cls.insert_one(**dept_dict)
                if isinstance(r, ObjectId):
                    res = dept_dict
                else:
                    """插入失败"""
                    pass
            else:
                """
                查到一个默认的职务,看看这个职务的名字和参数中的名字是不是一致?
                如果一致,那就pass如果不一致,那就update
                """
                if post_name is None or post_name == "":
                    """参数中的post_name无效,放弃"""
                    pass
                elif "post_name" in r and r['post_name'] == post_name:
                    """相同,不用update"""
                    res = r
                else:
                    """两者不同.update一下再返回"""
                    r_obj = cls.find_one_and_update_plus(filter_dict={"_id": r['_id']},
                                                         update_dict={"$set": {"post_name": post_name}})
                    if r_obj is None:
                        pass
                    else:
                        res = cls(**r_obj) if instance else r_obj
        return res


class Dept(mongo_db.BaseDoc):
    """部门/团队类"""
    _table_name = "dept_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['company_id'] = DBRef  # 所属公司 Company
    # type_dict['leader_id'] = DBRef  # 领导团队 Employee  废弃,以Leader(关系类代替)
    # 废弃,在
    # type_dict['secondary_leaders'] = list  # 除部门正职领导之外的辅助的领导,是Employee的DBRef的list
    type_dict['dept_name'] = str  # 团队名称
    """
    是否是根部门?默认部门是作为未确认部门归属时的默认值,只可修改,不可删除,这种部门一般是在创建公司的时候
    自动创建的,作为所有部门的最高上级部门
    """
    type_dict['root_dept'] = bool   # 默认值 False
    type_dict['description'] = str  # 说明
    type_dict['higher_dept'] = DBRef  # 上级部门
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        """先检查是否有重复的对象
        注意，company_id,higher_dept和dept_name构成联合主键
        """
        if "company_id" not in kwargs or "dept_name" not in kwargs:
            ms = "缺少必须的参数:company_id和dept_name"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            if not isinstance(kwargs['company_id'], DBRef):
                ms = "company_id必须是DBRef对象"
                logger.exception(ms)
                raise ValueError(ms)
            else:
                higher_dept = kwargs.get('higher_dept')
                if higher_dept:
                    f = {
                        "company_id": kwargs['company_id'],
                        "dept_name": kwargs['dept_name'],
                        "$or": [
                            {"higher_dept": None},
                            {"higher_dept": {"$exists": False}}
                        ]
                    }
                else:
                    f = {
                        "company_id": kwargs['company_id'],
                        "dept_name": kwargs['dept_name'],
                        "higher_dept": kwargs.get('higher_dept')
                    }
                r = self.__class__.find_one_plus(filter_dict=f, instance=False)
                if r is None:
                    """没有重复对象"""
                    pass
                else:
                    kwargs['_id'] = r['_id']
                if "create_date" not in kwargs:
                    kwargs['create_date'] = datetime.datetime.now()
                super(Dept, self).__init__(**kwargs)

    @classmethod
    def root_dept(cls, company_id: (str, ObjectId, Company), dept_name: str = None, desc: str="",
                  instance=False) -> object:
        """
        获取一个公司的根部门
        如果这个跟部门存在,那就取回对应的doc
        如果这个根部门不存在,那就创建保存,并返回对应的doc
        :param company_id:
        :param dept_name:
        :param desc:  备注说明
        :param instance:  实例化
        :return:
        """
        res = None
        if not isinstance(company_id, Company):
            company = Company.find_by_id(company_id)
        else:
            company = company_id
        if not isinstance(company, Company):
            ms = "错误的company_id:{}".format(company_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            """检查是否根部门已存在?"""
            company_dbref = company.get_dbref()
            dept_name = company.get_attr("short_name") if dept_name is None or dept_name == '' else dept_name
            f = {
                "company_id": company_dbref,
                "dept_name": dept_name,
                "$or": [
                    {"higher_dept": None},
                    {"higher_dept": {"$exists": False}}
                ]
            }
            r = cls.find_one_plus(filter_dict=f, instance=False)
            if r is None:
                """根部门不存在,可以创建"""
                dept_dict = {
                    "_id": ObjectId(),
                    "root_dept": True,
                    "company_id": company_dbref,
                    "dept_name": dept_name,
                    'description': desc,
                    "higher_dept": None
                }
                r = cls.insert_one(**dept_dict)
                if isinstance(r, ObjectId):
                    res = dept_dict
                else:
                    """插入失败"""
                    pass
            else:
                """查到一个同名的部门,看看这个部门是不是根部门?"""
                if "root_dept" in r and r['root_dept']:
                    """是根部门"""
                    res = r
                else:
                    """update一下再返回"""
                    r_obj = cls.find_one_and_update_plus(filter_dict={"_id": r['_id']},
                                                        update_dict={"$set": {"root_dept": True}})
                    if r_obj is None:
                        pass
                    else:
                        res = r_obj
        res = res if not instance else cls(**res)
        return res

    def dept_path(self, dept_list: list = list()) -> list:
        """获取部门所在的path路径。 因为Relation类的加入,此函数将被废止或改写
        :param dept_list: 上级部门，此参数不需要输入。仅作递归用。
        :return: 由当前部门直至顶层部门的path，含本部门。自顶向下排列,当前部门在数组的末尾。
        """
        dbref_obj = self.get_dbref()
        dept_list.insert(0, dbref_obj)
        higher_dept = Dept.get_instance_from_dbref(self.__dict__.get('higher_dept'))
        if not isinstance(higher_dept, Dept):
            """如果没有上级部门,那就返回"""
            return dept_list
        else:
            return higher_dept.dept_path(dept_list)

    def include_employees(self) -> list:
        """
        部门所包含的所有员工。包括下属部门的员工.因为Relation类的加入,此函数将被废止或改写
        :return: 包含员工ObjectId的list
        """
        dept_dbref = self.get_dbref()
        employees = Employee.find_plus(filter_dict={"dept_path": {"$in": [dept_dbref]}}, projection=["_id"], to_dict=True)
        employees = [x.get("_id") for x in employees]
        return employees

    def include_employees_instance(self) -> list:
        """
        部门所包含的所有员工。包括下属部门的员工.因为Relation类的加入,此函数将被废止或改写
        :return: 包含员工instance的list
        """
        dept_dbref = self.get_dbref()
        employees = Employee.find_plus(filter_dict={"dept_path": {"$in": [dept_dbref]}}, to_dict=False)
        return employees

    @classmethod
    def add_secondary_leader(cls, dept_id: (str, ObjectId), employee_id: (str, ObjectId)) -> dict:
        """
        增加一个副领导.因为Relation类的加入,此函数将被废止或改写
        :param dept_id: 部门id
        :param employee_id: 员工id
        :return: 结果字典
        """
        message = {"message": "success"}
        if isinstance(dept_id, (str, ObjectId)) and isinstance(employee_id, (str, ObjectId)):
            dept = cls.find_by_id(dept_id)
            employee = Employee.find_by_id(employee_id)
            if isinstance(dept, cls) and isinstance(employee, Employee):
                employee_dbref = employee.get_dbref()
                secondary_leader_list = dept.get_attr("secondary_leaders", [])
                if employee_dbref not in secondary_leader_list:
                    secondary_leader_list.append(employee_dbref)
                    dept.set_attr("secondary_leaders", secondary_leader_list)
                    dept.save()
                else:
                    message['message'] = '对象已存在'
            else:
                message['message'] = '对象创建失败'
        else:
            message['message'] = "参数类型错误: dept_id={}, employee_id={}".format(dept_id, employee_id)
        return message

    @classmethod
    def remove_secondary_leader(cls, dept_id: (str, ObjectId), employee_id: (str, ObjectId)) -> dict:
        """
        删除一个副领导.因为Relation类的加入,此函数将被废止或改写
        :param dept_id: 部门id
        :param employee_id: 员工id
        :return: 结果字典
        """
        message = {"message": "success"}
        if isinstance(dept_id, (str, ObjectId)) and isinstance(employee_id, (str, ObjectId)):
            dept = cls.find_by_id(dept_id)
            employee = Employee.find_by_id(employee_id)
            if isinstance(dept, cls) and isinstance(employee, Employee):
                employee_dbref = employee.get_dbref()
                secondary_leader_list = dept.get_attr("secondary_leaders", [])
                if employee_dbref in secondary_leader_list:
                    secondary_leader_list.remove(employee_dbref)
                    dept.set_attr("secondary_leaders", secondary_leader_list)
                    dept.save()
                else:
                    message['message'] = '对象不存在'
            else:
                message['message'] = '对象创建失败'
        else:
            message['message'] = "参数类型错误: dept_id={}, employee_id={}".format(dept_id, employee_id)
        return message

    @classmethod
    def get_include_employees(cls, dept_id: (str, ObjectId)) -> list:
        """
        部门所包含的所有员工，包括下属部门的员工。include_employees实例方法的类实现
        因为Relation类的加入,此函数将被废止或改写
        :param dept_id: 部门id
        :return: 包含员工ObjectId的list
        """
        if isinstance(dept_id, ObjectId):
            pass
        elif isinstance(dept_id, str) and len(dept_id) == 24:
            dept_id = mongo_db.get_obj_id(dept_id)
        else:
            raise TypeError("错误dept_id类型,dept_id‘s: {}".format(type(dept_id)))
        obj = Dept.find_by_id(dept_id)
        if not isinstance(obj, Dept):
            raise ValueError("错误dept_id,dept_id={}".format(dept_id))
        else:
            res = obj.include_employees()
            return res

    @classmethod
    def get_include_employees_instance(cls, dept_id: (str, ObjectId)) -> list:
        """
        部门所包含的所有员工，包括下属部门的员工。include_employees_instance实例方法的类实现
        因为Relation类的加入,此函数将被废止或改写
        :param dept_id: 部门id
        :return: 包含员工instance的list
        """
        if isinstance(dept_id, ObjectId):
            pass
        elif isinstance(dept_id, str) and len(dept_id) == 24:
            dept_id = mongo_db.get_obj_id(dept_id)
        else:
            raise TypeError("错误dept_id类型,dept_id‘s: {}".format(type(dept_id)))
        obj = Dept.find_by_id(dept_id)
        if not isinstance(obj, Dept):
            raise ValueError("错误dept_id,dept_id={}".format(dept_id))
        else:
            res = obj.include_employees_instance()
            return res

    @classmethod
    def get_dept_path(cls, obj: (ObjectId, DBRef), dept_list: list = list()) -> list:
        """
        获取部门所在的path路径。dept_path的类方法
        因为Relation类的加入,此函数将被废止或改写
        :param obj: 一个oid，dbref或者Dept的实例。
        :param dept_list: 上级部门，此参数不需要输入。仅作递归用。
        :return: 由当前部门直至顶层部门的path，含本部门。自顶向下排列
        """
        if isinstance(obj, Dept):
            pass
        elif isinstance(obj, ObjectId):
            obj = cls.find_by_id(obj)
        elif isinstance(obj, DBRef):
            obj = cls.get_instance_from_dbref(obj)
        else:
            try:
                raise TypeError("错误的obj类型，期待Dept/ObjectId/DBRef，得到一个{}".format(type(obj)))
            except TypeError as e:
                logger.error("Error", exc_info=True, stack_info=True)
                print(e)
                raise e
            except Exception as e:
                logger.error("Error", exc_info=True, stack_info=True)
                print(e)
                raise e
            finally:
                obj = None
        if obj is not None:
            return obj.dept_path()


class EmployeeBaseRelation(mongo_db.BaseDoc):
    """
    员工相关的关系基础类,这个类和UserBaseRelation的很相似,但由于关系类的简单,没有做成子类的样子
    类对象的属性至少包含下列属性
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表,
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间
    """

    @classmethod
    def add_relation(cls, emp_dbref: DBRef, dbref_name: str, dbref_val: DBRef) -> DBRef:
        """
        添加一个关系记录.此方法会清除之前的有效关系,
        :param emp_dbref: Employee.dbref
        :param dbref_name: 关联对象的属性名
        :param dbref_val: 关联对象的DBRef
        :return:  关系实例的DBRef对象
        """
        res = None
        if isinstance(emp_dbref, DBRef) and isinstance(dbref_val, DBRef) and isinstance(dbref_name, str):
            init_dict = {
                "employee_id": emp_dbref,
                dbref_name: dbref_val,
                "create_date": datetime.datetime.now()
            }
            """插入之前,需要检查是否已存在相同的可用的关系?如果存在只修改其中的一个,其他的作废"""
            now = datetime.datetime.now()
            f = {
                "employee_id": emp_dbref,
                dbref_name: dbref_val,
                "create_date": {"$lte": now},
                "$or": [
                    {"end_date": {"$exists": False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$gte": now}}
                ]
            }
            s = {"create_date": -1}
            exists_doc = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
            if len(exists_doc) > 0:
                """有重复的关系"""
                old = exists_doc.pop(0)
                f = {"_id": old['_id']}
                u = {"$set": init_dict}
                r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
                if r is None:
                    ms = "修改已存在的关系失败,old={},new={}".format(old, init_dict)
                    logger.exception(ms)
                    raise ValueError(ms)
                else:
                    dbref = DBRef(database="platform_db", collection=cls.get_table_name(), id=r['_id'])
                    res = dbref
                """修改过一个后,是否还有剩余的多余关系?有的话,删除"""
                if len(exists_doc) > 0:
                    ids = [x['_id'] for x in exists_doc]
                    f = {"_id": {"$in": ids}}
                    u = {'end_date': now}
                    cls.update_many_plus(filter_dict=f, update_dict=u)
                else:
                    pass
            else:
                """没有重复的关系,直接插入一个新的"""
                r = cls.insert_one(**init_dict)
                if isinstance(r, ObjectId):
                    """插入成功"""
                    dbref = DBRef(database="platform_db", collection=cls.get_table_name(), id=r)
                    res = dbref
                else:
                    ms = "插入新的关系失败,init={}".format(init_dict)
                    logger.exception(ms)
                    raise ValueError(ms)
        else:
            ms = "参数类型错误:emp_dbref:{},dbref_name:{},dbref_val:{}".format(type(emp_dbref), type(dbref_name),
                                                                         type(dbref_val))
            logger.exception(ms)
            raise TypeError(ms)
        return res

    @classmethod
    def get_relation_by_employee(cls, e_dbref: DBRef, instance: bool = False):
        """
        根据Employee实例的dbref对象查询对应的EmployeeXxxRelation,注意,只会返回
        一个有效的EmployeeXxxRelation对象的实例.一定会验证可用性
        :param e_dbref: Employee.dbref
        :param instance: 返回的EmployeeXxxRelation是实例还是doc?
        :return: EmployeeXxxRelation对象的实例(或doc)/None
        """
        now = datetime.datetime.now()
        f = {
            'employee_id': e_dbref,
            'create_date': {"$lte": now},
            '$or': [
                {'end_date': {'$exists': False}},
                {"end_date": {"$eq": None}},
                {"end_date": {"$gte": now}}
            ]
        }
        s = {'create_date': -1}
        r = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=instance)
        return r

    @classmethod
    def get_relations_by_employee(cls, e_dbref: DBRef, validate: int = 1, to_dict: bool = False,
                                  can_json: bool = False):
        """
        根据Employee实例的dbref对象查询对应的EmployeeXxxRelation,注意,会返回
        一个EmployeeXxxRelation对象的实例的list.
        :param e_dbref: Employee.dbref
        :param validate: 是否只返回可用的对象?1只返回有效的,0全部返回,-1只返回无效的
        :param to_dict: 返回的EmployeeXxxRelation是实例还是doc?
        :param can_json: (返回的是doc的时候),是否做to_flat_dict转换?
        :return: EmployeeXxxRelation对象的实例(或doc)的list
        """
        now = datetime.datetime.now()
        if not isinstance(validate, int):
            try:
                validate = int()
            except Exception as e:
                validate = 1
                print(e)
            finally:
                pass
        validate = 1 if validate >= 1 else (-1 if validate <= -1 else validate)
        if validate == 1:
            """只查有效的"""
            f = {
                'employee_id': e_dbref,
                'create_date': {"$lte": now},
                '$or': [
                    {'end_date': {'$exists': False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$gte": now}}
                ]
            }
        elif validate == -1:
            """只查无效的"""
            f = {
                'employee_id': e_dbref,
                '$or': [
                    {'create_date': {"$gte": now}},
                    {'create_date': {"$eq": None}},
                    {"create_date": {"$exists": False}},
                    {'end_date': {'$exists': False}},
                    {"end_date": {"$eq": None}},
                    {"end_date": {"$lte": now}}
                ]
            }
        else:
            """全部都查"""
            f = {'employee_id': e_dbref}
        s = {'create_date': -1}
        r = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=to_dict, can_json=can_json)
        return r

    @classmethod
    def clear_invalid_relation(cls, e_dbref: DBRef) -> None:
        """
        清除指定用户的无效关系记录
        :param e_dbref: Employee.dbref
        :return:
        """
        invalid_relations = cls.get_relations_by_employee(e_dbref=e_dbref, validate=-1, to_dict=True)
        if len(invalid_relations) > 0:
            f = {"_id": {"$in": [x['_id'] for x in invalid_relations]}}
            cls.delete_many(filter_dict=f)


class EmployeePostRelation(EmployeeBaseRelation):
    """关系表,记录员工和职务的对应关系"""
    _table_name = "employee_post_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表,
    type_dict['post_id'] = DBRef   # 职务id,指向post_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间


class EmployeeCompanyRelation(EmployeeBaseRelation):
    """关系表,记录员工和公司的对应关系"""
    _table_name = "employee_company_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表
    type_dict['company_id'] = DBRef   # 部门id,指向cpmpany_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间


class EmployeeDeptRelation(EmployeeBaseRelation):
    """关系表,记录员工和部门的对应关系"""
    _table_name = "employee_dept_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表
    type_dict['dept_id'] = DBRef   # 部门id,指向dept_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间


class Scheduling(mongo_db.BaseDoc):
    """
    排班/调度 信息,用于指定员工按照哪个排班进行上下班安排,另外,这也是很多算法用于计算有效时间范围的标准
    """
    _table_name = "scheduling_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['name'] = str  # 班次名称
    # 排班的上下班时间段,是list的list,类似 [["09:00", 9]]或者[["09:00", 3], ["13:00",5]],
    # 前者是开始时间,后者是持续时长,单位小时.比如 3.5
    type_dict['scheduling'] = list


class Employee(User):
    """公司员工类,注意，此类的表名也是user_info
    测试团队A组组长: 17321067312
    """
    type_dict = User.type_dict
    type_dict['company_relation_id'] = DBRef  # 和公司的关系id,指向EmployeeCompanyRelation
    type_dict['post_relation_id'] = DBRef     # 岗位关系id,指向employee_post_relation表
    type_dict['dept_relation_id'] = DBRef     # 部门关系id,指向employee_dept_relation表
    type_dict['block_list'] = list            # 不想显示的用户的DBRef组成的list，Employee._id
    type_dict['scheduling'] = list            # 排班的DBRef的list,对应于员工的排班,默认早9点到晚17点.（考虑加班和替班的情况）
    type_dict['employee_number'] = str        # 工号

    def __init__(self, **kwargs):
        company_relation_id = kwargs.pop("company_relation_id", None)
        if isinstance(company_relation_id, (DBRef, ObjectId, str)):
            if not isinstance(company_relation_id, DBRef):
                if isinstance(company_relation_id, str) and len(company_relation_id) == 24:
                    company_relation_id = DBRef(database=mongo_db.db_name,
                                                collection=EmployeeCompanyRelation.get_table_name(),
                                                id=ObjectId(company_relation_id))
                else:
                    company_relation_id = DBRef(database=mongo_db.db_name,
                                                collection=EmployeeCompanyRelation.get_table_name(),
                                                id=company_relation_id)
            else:
                pass
            kwargs['company_relation_id'] = company_relation_id
        else:
            pass

        post_relation_id = kwargs.pop("post_relation_id", None)
        if isinstance(post_relation_id, (DBRef, ObjectId, str)):
            if not isinstance(post_relation_id, DBRef):
                if isinstance(post_relation_id, str) and len(post_relation_id) == 24:
                    post_relation_id = DBRef(database=mongo_db.db_name,
                                                collection=EmployeePostRelation.get_table_name(),
                                                id=ObjectId(company_relation_id))
                else:
                    post_relation_id = DBRef(database=mongo_db.db_name,
                                                collection=EmployeePostRelation.get_table_name(),
                                                id=company_relation_id)
            else:
                pass
            kwargs['post_relation_id'] = post_relation_id
        else:
            pass

        dept_relation_id = kwargs.pop("dept_relation_id", None)
        if isinstance(dept_relation_id, (DBRef, ObjectId, str)):
            if not isinstance(dept_relation_id, DBRef):
                if isinstance(dept_relation_id, str) and len(dept_relation_id) == 24:
                    dept_relation_id = DBRef(database=mongo_db.db_name,
                                             collection=EmployeeDeptRelation.get_table_name(),
                                             id=ObjectId(company_relation_id))
                else:
                    dept_relation_id = DBRef(database=mongo_db.db_name,
                                             collection=EmployeeDeptRelation.get_table_name(),
                                             id=company_relation_id)
            else:
                pass
            kwargs['dept_relation_id'] = dept_relation_id
        else:
            pass

        if "block_list" not in kwargs:
            kwargs['block_list'] = list()
        self.type_dict['block_list'] = list

        super(Employee, self).__init__(**kwargs)

    def get_company(self, to_dict: bool = True) -> dict:
        """
        获取所属的公司对象
        :param to_dict: 返回的是实例还是doc对象? 默认是doc
        :return:
        """
        """查询可用的EmployeeCompanyRelation对象"""
        company_relation_id = self.get_attr("company_relation_id")
        res = dict()
        if not isinstance(company_relation_id, DBRef):
            real_name = ('' if self.get_attr("official_name") is None else self.get_attr("official_name")) \
                if self.get_attr("real_name") is None else self.get_attr("real_name")
            ms = "用户{}({})没有有效的公司关系".format(str(self.get_id()), real_name)
            logger.info(ms)
            warnings.warn(ms)
        else:
            """检查关系是否有效?"""
            now = datetime.datetime.now()
            f = {"employee_id": self.get_dbref(), "create_date": {"$lte": now},
                 "$or": [
                     {"end_date": {"$exists": False}},
                     {"end_date": {"$eq": None}},
                     {"end_date": {"$gte": now}}
                 ]}
            s = {"create_date": -1}
            relation = EmployeeCompanyRelation.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
            if isinstance(dict, relation):
                company = Company.find_by_id(relation.get_attr("company_id").id, to_dict=to_dict)
                res = company
            else:
                pass
        return res

    def get_dept(self, to_dict: bool = True) -> (None, Dept, dict):
        """
        获取职员的部门信息
        :param to_dict: 返回的是实例还是字典
        :return:
        """
        """查询可用的EmployeeDeptRelation对象"""
        dept_relation_id = self.get_attr("dept_relation_id")
        res = dict()
        if not isinstance(dept_relation_id, DBRef):
            real_name = ('' if self.get_attr("official_name") is None else self.get_attr("official_name")) \
                if self.get_attr("real_name") is None else self.get_attr("real_name")
            ms = "用户{}({})没有有效的部门关系".format(str(self.get_id()), real_name)
            logger.info(ms)
            warnings.warn(ms)
        else:
            """检查关系是否有效?"""
            now = datetime.datetime.now()
            f = {"employee_id": self.get_dbref(), "create_date": {"$lte": now},
                 "$or": [
                     {"end_date": {"$exists": False}},
                     {"end_date": {"$eq": None}},
                     {"end_date": {"$gte": now}}
                 ]}
            s = {"create_date": -1}
            relation = EmployeeDeptRelation.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
            if isinstance(dict, relation):
                dept = Dept.find_by_id(relation.get_attr("dept_id").id, to_dict=to_dict)
                res = dept
            else:
                pass
        return res

    def get_post(self, to_dict: bool = True) -> (None, Dept, dict):
        """
        获取职员的职务信息
        :param to_dict: 返回的是实例还是字典
        :return:
        """
        """查询可用的EmployeePostRelation对象"""
        post_relation_id = self.get_attr("post_relation_id")
        res = dict()
        if not isinstance(post_relation_id, DBRef):
            real_name = ('' if self.get_attr("official_name") is None else self.get_attr("official_name")) \
                if self.get_attr("real_name") is None else self.get_attr("real_name")
            ms = "用户{}({})没有有效的职务关系".format(str(self.get_id()), real_name)
            logger.info(ms)
            warnings.warn(ms)
        else:
            """检查关系是否有效?"""
            now = datetime.datetime.now()
            f = {"employee_id": self.get_dbref(), "create_date": {"$lte": now},
                 "$or": [
                     {"end_date": {"$exists": False}},
                     {"end_date": {"$eq": None}},
                     {"end_date": {"$gte": now}}
                 ]}
            s = {"create_date": -1}
            relation = EmployeePostRelation.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
            if isinstance(dict, relation):
                post = Post.find_by_id(relation.get_attr("post_id").id, to_dict=to_dict)
                res = post
            else:
                pass
        return res

    def get_archives(self) -> dict:
        """
        获取个人档案,可以看作是超详细版的个人资料,主要是辅助显示个人详细信息,
        此方法覆盖了父类的方法.用于增强效果(增加组织架构信息的获取)
        :return:
        """
        extend_dict = dict()
        """要从父类方法的结果集中,去掉这些字段"""
        pop_columns = ["dept_path", "company_id", "post_id"]
        # 取出部门信息,Dept类要大改,目前是临时方案
        dept_path = self.get_attr("dept_path")
        if dept_path is None:
            pass
        else:
            my_dept = dept_path.pop(-1)  # 弹出任职的部门
            my_dept = Dept.find_by_id(my_dept.id)
            if isinstance(my_dept, Dept):
                """查询就职部门相关信息"""
                extend_dict['dept_name'] = my_dept.get_attr("dept_name")  # 部门名称
                leader = Employee.find_by_id(my_dept.get_attr("leader_id").id)
                if isinstance(leader, Employee):
                    """取本部门领导名字"""
                    extend_dict['leader_name'] = leader.get_attr("user_name") if leader.get_attr("real_name") is None \
                        else leader.get_attr("real_name")
            if len(dept_path) < 1:
                """没有部门所属"""
                pass
            else:
                # 弹出上级部门
                prev_dept = dept_path.pop(-1)
                prev_dept = Dept.find_by_id(prev_dept.id)
                if isinstance(prev_dept, Dept):
                    extend_dict['prev_dept'] = prev_dept.get_attr("dept_name")

        # 取公司名
        company_id = self.get_attr("company_id")
        if company_id is None:
            pass
        else:
            company = Company.find_by_id(company_id.id)
            if isinstance(company, Company):
                extend_dict['company_name'] = company.get_attr("short_name")
            """临时方案,苏秦的全部转sf的."""
            if company_id.id == ObjectId("59e456854660d32fa2f13642"):
                """如果是苏秦网络的,进行转换"""
                extend_dict['company_name'] = "顺丰速运"
                extend_dict['prev_dept'] = '华新分拨中心'
            else:
                pass
        # 取职务信息
        post_id = self.get_attr("post_id")
        if post_id is None:
            pass
        else:
            post = Post.find_by_id(post_id.id)
            if isinstance(post, Post):
                extend_dict['post_name'] = post.get_attr("post_name")
        raw_dict = super(Employee, self).get_archives()
        raw_dict = {k: v for k, v in raw_dict.items() if k not in pop_columns}
        if isinstance(raw_dict, dict):
            extend_dict.update(raw_dict)
        return extend_dict

    @classmethod
    def get_archives_cls(cls, e_id: (str, ObjectId)) -> (None, dict, list):
        """
        未完成  2018-4-18
        可以看作是Employee.get_archives的类方法.自2018-4-17起,要求获取更详细的个人资料.包括
        1. 用户信息.(含驾照信息)
        2. 相关行车证信息
        3. 部门信息.
        4. 岗位信息
        5. 公司信息
        :param e_id: 员工id或者员工id的list.
        :return: 如果是e_id参数是员工id,这里返回的是None/dict,否则返回list对象
        """
        emp = cls.find_by_id(e_id)
        if isinstance(emp, cls):
            e_dbref = emp.get_dbref()
            """查询公司信息"""
            emp.get_company()
        else:
            ms = "{}不是有效的用户id".format(e_id)
            logger.exception(ms)
            raise ValueError(ms)

    @classmethod
    def get_block_id_list(cls, my_id: (str, ObjectId), to_str: bool = False) -> list:
        """
        获取某用户的屏蔽的用户的ObjectId的list
        :param my_id: 用户id
        :param to_str: 是否做str转换
        :return: list of ObjectId
        """
        emp = Employee.find_by_id(my_id)
        a_list = []
        if not isinstance(emp, cls):
            pass
        else:
            a_list = emp.get_attr("block_list", [])
            if len(a_list) > 0:
                a_list = [str(x.id) for x in a_list] if to_str else [x.id for x in a_list]
            else:
                pass
        return a_list

    @classmethod
    def get_block_members(cls, my_id: (str, ObjectId), to_dict: bool = False) -> list:
        """
        获取某用户的屏蔽的用户的实例
        :param my_id: 用户id
        :param to_dict: 返回实例的列表还是dict的列表
        :return: list
        """
        a_list = cls.get_block_id_list(my_id)
        if to_dict:
            a_list = [cls.find_by_id(employee_id).to_flat_dict() for employee_id in a_list]
        else:
            a_list = [cls.find_by_id(employee_id) for employee_id in a_list]
        return a_list

    @classmethod
    def add_block_id(cls, my_id: (str, ObjectId), block_id: (str, ObjectId, DBRef)) -> dict:
        """
        向某用户的屏蔽列表用添加其他用户id.
        :param my_id: 用户id
        :param block_id:  其他用户id
        :return: dict
        """
        res = {"message": "添加失败"}
        if isinstance(block_id, DBRef):
            pass
        elif isinstance(block_id, ObjectId):
            block_id = cls.find_by_id(block_id).get_dbref()
        elif isinstance(block_id, str):
            block_id = cls.find_by_id(block_id).get_dbref()
        else:
            try:
                raise ValueError("block_id不合法: {}".format(block_id))
            except ValueError as e:
                logger.exception("add_block_id Error")
                raise e
        if isinstance(block_id, DBRef):
            emp = cls.find_by_id(my_id)
            if not isinstance(emp, cls):
                try:
                    raise ValueError("employee 创建失败, my_id: {}".format(my_id))
                except ValueError as e:
                    logger.exception("add_block_id Error")
                    raise e
            else:
                key = "block_list"
                a_list = emp.get_attr(key, [])
                if block_id in a_list:
                    res['message'] = "用户已存在"
                else:
                    a_list.append(block_id)
                    emp.set_attr(key, a_list)
                    emp.save()
                    res['message'] = "success"
        else:
            try:
                raise ValueError("block_id创建失败: {}".format(block_id))
            except ValueError as e:
                logger.exception("add_block_id Error")
                raise e
        return res

    @classmethod
    def remove_block_id(cls, my_id: (str, ObjectId), block_id: (str, ObjectId, DBRef)) -> dict:
        """
        向某用户的屏蔽列表用移除某用户id.
        :param my_id: 用户id
        :param block_id:  用户id
        :return: dict
        """
        res = {"message": "删除失败"}
        if isinstance(block_id, DBRef):
            pass
        elif isinstance(block_id, ObjectId):
            block_id = cls.find_by_id(block_id).get_dbref()
        elif isinstance(block_id, str):
            block_id = cls.find_by_id(block_id).get_dbref()
        else:
            try:
                raise ValueError("block_id不合法: {}".format(block_id))
            except ValueError as e:
                logger.exception("remove_block_id Error")
                raise e
        if isinstance(block_id, DBRef):
            emp = cls.find_by_id(my_id)
            if not isinstance(emp, cls):
                try:
                    raise ValueError("employee 创建失败, my_id: {}".format(my_id))
                except ValueError as e:
                    logger.exception("remove_block_id Error")
                    raise e
            else:
                key = "block_list"
                a_list = emp.get_attr(key, [])
                if block_id not in a_list:
                    res['message'] = "用户不在阻止列表中"
                else:
                    a_list.remove(block_id)
                    emp.set_attr(key, a_list)
                    emp.save()
                    res['message'] = "success"
        else:
            try:
                raise ValueError("block_id创建失败: {}".format(block_id))
            except ValueError as e:
                logger.exception("remove_block_id Error")
                raise e
        return res

    @classmethod
    def subordinates_instance(cls, user_id: (str, ObjectId), can_json: bool = True, include_blocking: bool = False) -> list:
        """
        由于职员和部门的关系(EmployeeDeptRelation)的加入,此方法即将被废止 2018-3-8
        获取指定用户的所有下属的实例，有下属的时候包含自己，如果没有下属，那就返回一个空list
        :param user_id: 指定用户的id
        :param can_json: 是否为json做好类型转换?
        :param include_blocking: 是否包含被阻止的用户列表？
        :return: 下属的id的instance列表
        """
        warnings.warn("此方法已过时, 请使用role包下对应的方法替代, begin at 2018-3-8")
        res = list()
        if isinstance(user_id, (str, ObjectId)):
            """正常的情况"""
            emp_obj = cls.find_by_id(user_id)
            if emp_obj is None:
                """错误的user_id"""
                pass
            else:
                company_dbref = emp_obj.get_attr('company_id')  # 公司id
                if company_dbref is None:
                    pass  # 没有公司信息的，那就是非公司用户
                else:
                    obj_dbref = emp_obj.get_dbref()  # 自己的dbref
                    """确认一下是否是团队领导"""
                    query_dict = {"company_id": company_dbref, "leader_id": obj_dbref}
                    dept_obj = Dept.find_one_plus(filter_dict=query_dict, instance=True)
                    if dept_obj is None:  # 不是部门领导
                        """
                        看一下是不是观察员?注意这是个临时方法,由于不知道如何查询副领导数组包含制定的员工的id导致的窘境.
                        有解决方案第一时间处理这个问题,注意subordinates_id方法也有这个方法
                        """
                        if emp_obj.get_attr("post_id") == DBRef(collection="post_info", database="platform_db",
                                                                id=ObjectId("5a1772fccaef1f6740ff9972")):
                            dept_obj = Dept.get_instance_from_dbref(emp_obj.get_attr("dept_path")[-1])
                        else:
                            pass
                    else:
                        pass
                    if dept_obj is None:
                        pass
                    else:
                        """查找所有的下属，也包括下属的下属"""
                        res = Dept.get_include_employees_instance(dept_id=dept_obj.get_id())
                        if not include_blocking:
                            res = [x for x in res if x.get_id() not in cls.get_block_id_list(user_id)]  # 过滤排除列表
                        if can_json:
                            res = [x.to_flat_dict() for x in res]
        else:
            pass
        return res

    @classmethod
    def subordinates_id(cls, user_id: (str, ObjectId), to_str: bool = False, include_blocking: bool = False) -> list:
        """
        获取制定用户的所有下属的ObjectId，如果没有下属，那就返回一个空list
        由于EmployeeDeptRelation关系类的加入,此方法将被废止
        :param user_id: 指定用户的id
        :param to_str: 是否把下属的id从ObjectId转为str?
        :param include_blocking: 是否包含被阻止的用户列表？
        :return: 下属的id的oid/str列表
        """
        if isinstance(user_id, str) and len(user_id) == 24:
            user_id = mongo_db.get_obj_id(user_id)
        elif isinstance(user_id, ObjectId) or user_id == "debug":  # debug用来调试
            pass
        else:
            raise ValueError("用户id错误，user_id={}".format(user_id))
        res = list()
        if isinstance(user_id, ObjectId):
            """正常的情况"""
            emp_obj = cls.find_by_id(user_id)  # employee实例
            if emp_obj is None:
                """错误的user_id"""
                pass
            else:
                company_dbref = emp_obj.get_attr('company_id')  # 公司id
                if company_dbref is None:
                    pass  # 没有公司信息的，那就是非公司用户
                else:
                    obj_dbref = emp_obj.get_dbref()  # 自己的dbref
                    """确认一下是否是团队领导"""
                    query_dict = {"company_id": company_dbref, "leader_id": obj_dbref}
                    dept_obj = Dept.find_one_plus(filter_dict=query_dict, instance=True)
                    if dept_obj is None:  # 不是部门领导
                        """
                        看一下是不是观察员?注意这是个临时方法,由于不知道如何查询副领导数组包含制定的员工的id导致的窘境.
                        有解决方案第一时间处理这个问题,注意subordinates_id方法也有这个我呢提
                        """
                        if emp_obj.get_attr("post_id") == DBRef(collection="post_info", database="platform_db",
                                                                id=ObjectId("5a1772fccaef1f6740ff9972")):
                            dept_obj = Dept.get_instance_from_dbref(emp_obj.get_attr("dept_path")[-1])
                        else:
                            pass
                    else:
                        pass
                    if dept_obj is None:
                        pass
                    else:
                        """查找所有的下属，也包括下属的下属"""
                        res = Dept.get_include_employees(dept_id=dept_obj.get_id())
                        if not include_blocking:
                            res = [x for x in res if x not in cls.get_block_id_list(user_id)]  # 过滤排除列表
                        if to_str:
                            res = [str(x) for x in res]
        else:
            """debug的情况"""
            employees = Employee.find({})
            employees = [str(x.get_id()) if to_str else x.get_id() for x in employees]
            res = employees
        return res

    @classmethod
    def my_team_last_position(cls, user_id: (str, ObjectId)) -> dict:
        """
        由于EmployeeDeptRelation关系类的加入,此方法将被废止
        获取最后的位置点，这是get_last_position函数的特例化.
        注意:ws_server的all_last_position函数并没有使用这个方法,而是自己实现的.
        :param user_id: 用户的id，24位字符串，
        :return:消息字典
        """
        subordinate_id_list = Employee.subordinates_id(user_id)  # 获取下属/能查看的用户列表。
        if len(subordinate_id_list) == 0:
            """没有下属，只能查看自己的位置了"""
            subordinate_id_list = [mongo_db.get_obj_id(user_id)]
        user_position_dict = Track.get_last_position(subordinate_id_list)  # 获取最后的点信息
        return user_position_dict


if __name__ == "__main__":
    """添加公司管理员"""
    sf_id = ObjectId("59a671a0de713e3db34de8bf")
    sq_id = ObjectId("59e456854660d32fa2f13642")  # 苏秦.公司id
    sf = Company.find_by_id(sf_id)
    sq = Company.find_by_id(sq_id)  # 苏秦
    sq_p = ObjectId("5b0bbb334660d344c0f44bcd") # 苏秦,司机职务.
    sq_d = ObjectId("5b0bbe344660d3466c0352ad") # 苏秦, 昌吉东路部门
    sq_e = ObjectId("59895177de713e304a67d30c")  # me的user_id
    # sq.add_admin(admin_name="sq_root", admin_password="Sq@123457",
    #              desc="苏秦网络管理员")
    # sf.add_admin(admin_name="sf_view", admin_password="123456",
    #              only_view=True,
    #              desc="只有查看本公司在线人数权限")
    """获取公司职员在线情况"""
    # sf.online_report()
    """添加一个部门"""
    # d_dict = {
    #     "dept_name": "昌吉东路部门",
    #     "root_dept": True,
    #     "description": "昌吉东路的研发本部"
    # }
    # Company.add_dept(company_id=sq_id, dept_dict=d_dict)
    """给添加一个职务"""
    # p_dict = {
    #     "post_name": "司机",
    #     "description": "一般员工,默认,不可删除",
    #     "level": 1,
    #     "default": True
    # }
    # Company.add_post(company_id=sq_id, post_dict=p_dict)
    """添加一个管理人员,无管理权限,只是作为旁观者而已"""
    sq.hire_one_employee(user_id=sq_e, dept_id=sq_d, post_id=sq_p)
    # p_id_m = ObjectId("5b03e2004660d34b81a17188")  # 管理人员的post_id
    # u_id_z = ObjectId("5af547e4e39a7b5371943a4a")  # 顺丰华新张小龙id
    # d_id_h = ObjectId("5abcac4b4660d3599207fe18")  # 顺丰华新本部门id
    # print(sf.hire_one_employee(user_id=u_id_z, dept_id=d_id_h, post_id=p_id_m))
    """查询一个公司的全部的违章记录"""
    # dd = Company.all_vio_cls(sf_id)
    # print(dd)
    pass
