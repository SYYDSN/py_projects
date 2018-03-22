# -*- coding:utf-8 -*-
import sys
import os

"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
from api.data.item_module import User, Track
import hashlib
import datetime
from log_module import get_logger
import warnings


"""公司模块"""

ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
MyDBRef = mongo_db.MyDBRef
logger = get_logger()


class Company(mongo_db.BaseDoc):
    """公司类"""
    _table_name = "company_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['full_name'] = str  # 公司全称,中国的公司法允许公司名称重复,但不允许商标重复
    type_dict['domain'] = str  # 域名,唯一,在用户访问系统时,标识公司的唯一性
    type_dict['prefix'] = str  # 公司查询前缀,唯一.用于向安全模块查询接口.在此查询中向安全模块标识身份的唯一性
    type_dict['short_name'] = str  # 简称
    type_dict['description'] = str  # 公司简介

    def __init__(self, **kwargs):
        if 'prefix' not in kwargs:
            raise ValueError("公司查询前缀为必须参数")
        if kwargs['prefix'] == "" or kwargs['prefix'] is None:
            raise ValueError("公司查询前缀必须是一个有效的字符串")
        super(Company, self).__init__(**kwargs)

    @classmethod
    def validate_employee(cls, company_id: (str, ObjectId), employee_id: (str, ObjectId)) -> bool:
        """
        公司是否存在某位员工
        :param company_id:
        :param employee_id:
        :return:
        """
        company_id = mongo_db.get_obj_id(company_id)
        employee_id = mongo_db.get_obj_id(employee_id)
        company_dbref = DBRef(database="platform_db", collection=cls.get_table_name(), id=company_id)
        employee_dbref = DBRef(database="platform_db", collection=Employee.get_table_name(), id=employee_id)
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
        :param args_list: 员工的初始化参数的字典组成的list,一般是从app或者web端接收的信息.
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
                        raise ValueError("员工 {} 不属于任何公司".format(emp_id))
                    else:
                        pass
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
                        raise ValueError(ms)
                else:
                    raise ValueError("员工id错误 {}".format(emp_id))
        else:
            raise ValueError("公司id错误 {}".format(company_id))

    @classmethod
    def clear_employee(cls, company_id: (str, ObjectId), id_list: (list, dict)) -> None:
        """
        清除单个/多个员工及其相关的关系记录,注意,这会完全删除员工的档案.把员工降级为一般用户
        调用此方法之前,建议检查对应的权限.
        此方法没有线程锁,方法的逻辑如下:
        1. 确认公司id是否存在?不存在退出,
        2. 确认员工是否归属这个公司? 确认公司的部门?(确认部门其实是为了确认)
        3. 删除对应的EmployeePostRelation记录
        4. 删除对应的EmployeeDeptRelation记录
        5. 删除对应的EmployeeCompanyRelation记录
        6. 修改employee信息
        :param company_id:
        :param id_list: 员工id组成的list
        :return:
        """
        ms = "正在清除员工和公司之间的记录,清除结束后,员工账户将会变成非企业用户"
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
                    """员工id正确,检查归属关系"""
                    company_relation_dbref = emp.get_attr("company_relation_id")
                    if company_relation_dbref is None:
                        raise ValueError("员工 {} 不属于任何公司".format(emp_id))
                    else:
                        pass
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
                        emp.remove_attr("company_relation_id")
                        emp.remove_attr("dept_relation_id")
                        emp.remove_attr("post_relation_id")
                        emp.save()  # 清除成功
                    else:
                        ms = "员工id {} 不是 {} 的职员".format(emp_id, company.get_attr("short_name"))
                        raise ValueError(ms)
                else:
                    raise ValueError("员工id错误 {}".format(emp_id))
        else:
            raise ValueError("公司id错误 {}".format(company_id))

    @classmethod
    def delete_employee(cls, company_id: (str, ObjectId), id_list: (list, dict)) -> None:
        """
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
                    """员工id正确,检查归属关系"""
                    company_relation_dbref = emp.get_attr("company_relation_id")
                    if company_relation_dbref is None:
                        raise ValueError("员工 {} 不属于任何公司".format(emp_id))
                    else:
                        pass
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
        查询某个公司，某个岗位的全体人员
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
    def get_prefix_by_user_id(cls, user_id: (str, ObjectId)) ->(str, None):
        """
        根据用户id获取用户所在公司的前缀
        :param user_id: 用户id
        :return:
        """
        user = User.find_by_id(user_id)
        prefix = None
        if isinstance(user, User):
            company_dbref = user.get_attr("company_id")
            if company_dbref is None:
                ms = "用户{}没有company_id信息".format(str(user_id))
                print(ms)
                logger.info(ms)
            else:
                company_id = company_dbref.id
                company = Company.find_by_id(company_id)
                if isinstance(company, Company):
                    prefix = company.get_attr("prefix")
                else:
                    ms = "company_id:{}错误".format(str(company_id))
                    print(ms)
                    logger.info(ms)
        else:
            raise ValueError("错误的用户id:{}".format(str(user_id)))
        return prefix


class CompanyAdmin(mongo_db.BaseDoc):
    """公司最高管理员"""
    _table_name = "company_admin_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['user_name'] = str  # 用户名，唯一
    type_dict['user_password'] = str  # 用户密码
    type_dict['company_id'] = DBRef  # 指向company_id 是哪个公司的管理员?
    type_dict['description'] = str  # 说明

    def __init__(self, **kwargs):
        """
        :param kwargs:
        arg md5: 布尔值,是否对user_password进行md5加密?当参数user_password未加密的时候,启用此项
        """
        md5_flag = kwargs.pop("md5", False)
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
    type_dict['company_id'] = DBRef  # 所属公司 Company
    type_dict['post_name'] = str  # 岗位名称
    type_dict['default_post'] = bool  # 是否是默认职务?默认职务是作为未确认职务时的默认值,只可修改,不可删除
    type_dict['level'] = int  # 职务的管理级别,默认为0
    type_dict['description'] = str  # 说明
    """
    用来标识此职务是否具备管理权限?或者具备何种管理权限?在目前情况下,可选的值只有0和1
    0代表是普通职员,没有管理权限.
    1代表是管理员,可以查看本组/部门的其他人的信息.
    """

    def __init__(self, **kwargs):
        if "level" not in kwargs:
            kwargs['level'] = 0
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
        super(Post, self).__init__(**kwargs)


class EmployeePostRelation(mongo_db.BaseDoc):
    """关系表,记录员工和职务的对应关系"""
    _table_name = "employee_post_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表,
    type_dict['post_id'] = DBRef   # 职务id,指向post_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间


class Dept(mongo_db.BaseDoc):
    """部门/团队类"""
    _table_name = "dept_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['company_id'] = DBRef  # 所属公司 Company
    # type_dict['leader_id'] = DBRef  # 领导团队 Employee  废弃,以Leader(关系类代替)
    # 废弃,以Leader(关系类代替)
    # type_dict['secondary_leaders'] = list  # 除部门正职领导之外的辅助的领导,是Employee的DBRef的list
    type_dict['dept_name'] = str  # 团队名称
    type_dict['default_dept'] = bool  # 是否是默认部门?默认部门是作为未确认部门归属时的默认值,只可修改,不可删除
    type_dict['description'] = str  # 说明
    type_dict['higher_dept'] = DBRef  # 上级部门

    def __init__(self, **kwargs):
        """先检查是否有重复的对象
        注意，company_id,higher_dept和dept_name构成联合主键
        """
        if 'secondary_leaders' not in kwargs:
            """secondary_leaders是除一把手之外的,拥有领导权限的员工"""
            kwargs['secondary_leaders'] = []
        super(Dept, self).__init__(**kwargs)

    def dept_path(self, dept_list: list = list()) -> list:
        """获取部门所在的path路径。
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
        部门所包含的所有员工。包括下属部门的员工
        :return: 包含员工ObjectId的list
        """
        dept_dbref = self.get_dbref()
        employees = Employee.find_plus(filter_dict={"dept_path": {"$in": [dept_dbref]}}, projection=["_id"], to_dict=True)
        employees = [x.get("_id") for x in employees]
        return employees

    def include_employees_instance(self) -> list:
        """
        部门所包含的所有员工。包括下属部门的员工
        :return: 包含员工instance的list
        """
        dept_dbref = self.get_dbref()
        employees = Employee.find_plus(filter_dict={"dept_path": {"$in": [dept_dbref]}}, to_dict=False)
        return employees

    @classmethod
    def add_secondary_leader(cls, dept_id: (str, ObjectId), employee_id: (str, ObjectId)) -> dict:
        """
        增加一个副领导
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
        删除一个副领导
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


class EmployeeCompanyRelation(mongo_db.BaseDoc):
    """关系表,记录员工和公司的对应关系"""
    _table_name = "employee_company_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['employee_id'] = DBRef  # 员工id,指向user_info表
    type_dict['company_id'] = DBRef   # 部门id,指向cpmpany_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间


class EmployeeDeptRelation(mongo_db.BaseDoc):
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

    def __init__(self, **kwargs):
        self.type_dict['company_id'] = DBRef   # 公司id,指向company_info 即将废止,以company_relation_id替代
        self.type_dict['company_relation_id'] = DBRef  # 和公司的关系id,指向EmployeeCompanyRelation
        self.type_dict['post_id'] = DBRef  # 岗位信息 Post 即将废止,以post_relation_id替代
        self.type_dict['post_relation_id'] = DBRef  # 岗位关系id,指向employee_post_relation表
        self.type_dict['employee_number'] = int  # 工号
        self.type_dict['dept_path'] = list  # 所属团队DBRef组成的list，Dept 即将废止,以dept_relation_id替代
        self.type_dict['dept_relation_id'] = DBRef  # 部门关系id,指向employee_dept_relation表
        self.type_dict['block_list'] = list  # 不想显示的用户的DBRef组成的list，Employee
        self.type_dict['scheduling'] = list   # 排班的DBRef的list,对应于员工的排班,默认早9点到晚17点.（考虑加班和替班的情况）
        super(Employee, self).__init__(**kwargs)

    def get_dept(self) -> Dept:
        """
        获取职员的部门信息
        :return: Dept的实例
        """

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


def rebuild_test_team() -> None:
    """
    完善测试组的真实姓名的信息。在每次增加新的测试司机后调用此函数，
    注意：测试团队A组组长: 17321067312
    :return:
    """
    dept_path_team = [
        {
            "$ref": "dept_info",
            "$id": ObjectId("59e45a0a4660d330ae874756"),
            "$db": "platform_db"
        }
    ]  # 部门path
    post_id_leader = {
        "$ref": "post_info",
        "$id": ObjectId("59e45b804660d33116a179b1"),
        "$db": "platform_db"
    }  # 测试组长的职务id
    post_id_driver = {
        "$ref": "post_info",
        "$id": ObjectId("59e45ba44660d3312b7aa553"),
        "$db": "platform_db"
    }  # 测试司机的职务id
    company_id_team = {
        "$ref": "company_info",
        "$id": ObjectId("59e456854660d32fa2f13642"),
        "$db": "platform_db"
    }  # 公司id
    team = "17321067312 17316381312 17316539612 17316502312 17317656212 17317582912 1064823647987 " \
           "1064823647988".split(" ")
    drivers = User.find(phone_num={"$in": team})
    for driver in drivers:
        phone = driver.get_attr("phone_num")
        user_password = driver.get_attr("user_password")
        post_id = driver.get_attr("post_id")
        dept_path = driver.get_attr("dept_path")
        company_id = driver.get_attr("company_id")
        need_save = False
        if post_id is None:
            need_save = True
            driver.post_id = mongo_db.MyDBRef(post_id_driver)
        if user_password is None:
            need_save = True
            driver.user_password = mongo_db.generator_password(phone[(len(phone) - 6):])
        if dept_path is None:
            need_save = True
            print(dept_path_team)
            driver.dept_path = [mongo_db.MyDBRef(dept) for dept in dept_path_team]
        if company_id is None:
            need_save = True
            driver.company_id = mongo_db.MyDBRef(company_id_team)
        if need_save:
            driver.save()


if __name__ == "__main__":
    # """创建一批员工和新振兴公司之间的雇佣关系"""
    # company = Company.find_by_id(ObjectId("5aab48ed4660d32b752a7ee9"))
    # company_dbref = company.get_dbref()
    # post = Post.find_by_id(ObjectId("5ab21fc74660d376c982ee27"))
    # post_dbref = post.get_dbref()
    # dept = Dept.find_by_id(ObjectId("5ab21b2a4660d3745e53adfa"))
    # dept_dbref = dept.get_dbref()
    # now = datetime.datetime.now()
    # f = {"description": {"$exists": True}}
    # es = Employee.find_plus(filter_dict=f, to_dict=True)
    # for e in es:
    #     post_relation_id = e['post_relation_id']
    #     post_relation_dbref = DBRef(database="platform_db", collection="employee_post_relation", id=post_relation_id)
    #     e["post_relation_id"] = post_relation_dbref
    #     dept_relation_id = e['dept_relation_id']
    #     dept_relation_dbref = DBRef(database="platform_db", collection="employee_dept_relation", id=dept_relation_id)
    #     e["dept_relation_id"] = dept_relation_dbref  # 设置用户和职务的关系id
    #     e = Employee(**e)
    #     e.save()
    """测试批量添加employee的方法"""
    company_id = "5aab48ed4660d32b752a7ee9"
    # company_id = "5aab5db852d59ccd9a300dee"
    e1 = {
        "phone_num": "15618318888", "real_name": "张三",
        "dept_id": "5ab21b2a4660d3745e53adfa", "post_id": "5ab21fc74660d376c982ee27"
    }
    e2 = {
        "phone_num": "15618318889", "real_name": "李四",
        "dept_id": "5ab21b2a4660d3745e53adfa", "post_id": "5ab21fc74660d376c982ee27"
    }
    es = [e1, e2]
    # Company.add_employee(company_id, es)
    Company.dismiss_employee(company_id, ["5ab3533e4660d34126213654", "5ab3516c4660d34002f8e178"])
    pass
