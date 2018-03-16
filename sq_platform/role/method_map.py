#  -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))  # 项目目录
if project_dir not in sys.path:
    print(project_dir)
    sys.path.append(project_dir)
from manage import company_module
from mongo_db import ObjectId, DBRef
from log_module import get_logger
import mongo_db
from error_module import pack_message


logger = get_logger()


"""这是一个存放函数/方法名称和函数/方法对应关系的文件,为role_module模块服务"""


def get_func(func_name: str):
    """
    根据权限提供的函数名,返回对应的函数体
    :param func_name:
    :return:
    """
    global FUNC_MAP
    func_map = FUNC_MAP.copy()
    return func_map.get(func_name, None)


def func_names() -> list:
    """
    获取所有定义过的函数名
    :return:
    """
    global FUNC_MAP
    names = list(FUNC_MAP.keys())
    return names


def get_company_by_domain(domain: str) -> (dict, None):
    """
    根据访问的域名判断这是对哪个公司进行访问?
    如果在本机调试状态,建议在域名后面追加domain的参数用于进行修正.
    权限:
    1.不限
    :param domain: 请求的域名
    :return:
    """
    filter_dict = {"domain": domain}
    r = company_module.Company.find_one_plus(filter_dict=filter_dict, instance=False)
    return r


def web_login(user_name: str, user_password: str, company_id: ObjectId, rule: int = 2) -> dict:
    """
    在网页端进行登录操作,
    权限:
    1.不限
    函数会依次进行一下的检查:
    1. 是管理员?
    2. 员工? 还是普通用户?

    :param user_name: 用户名
    :param user_password: 密码
    :param company_id: 公司id
    :param rule: 权限,默认公司级别
    :return: 消息字典
    """
    m = {"message": "success"}
    if rule == 0:
        m['message'] = "没有权限"
    else:
        filter_dict = {
            "user_name": user_name,
            "user_password": user_password,
            "company_id": DBRef(database="platform_db", collection=company_module.Company.get_table_name(),
                                id=company_id)
        }
        r = company_module.CompanyAdmin.find_one_plus(filter_dict=filter_dict, instance=False)
        if r:
            """是管理员"""
            r['class'] = "admin"
            m['data'] = r
        else:
            """不是管理员,查user_info表.这个方法是测试用的,实际上要查用户和公司的关系,而且用户不一定是企业"""
            filter_dict = {
                "user_name": user_name,
                "user_password": user_password
            }
            r = company_module.Employee.find_one_plus(filter_dict=filter_dict, instance=False)
            if r is None:
                """既不是管理员也不是一般用户"""
                m['message'] = "用户名或密码错误"
            else:
                if hasattr(r, "company_relation_id"):
                    """是员工"""
                    r['class'] = 'employee'
                else:
                    r['class'] = 'user'
                m['data'] = r
    return m


def create_dept(user_id: ObjectId, company_id: ObjectId, dept_name: str, description: str = '',
                higher_dept_id: (str, ObjectId, DBRef) = None, scope: int = 0) -> dict:
    """
    创建部门
    权限:
    1. 公司管理员
    2. 被赋予权限的角色
    :param user_id:  管理员/有权限的用户的id
    :param company_id: 公司id
    :param dept_name: 部门名称
    :param description: 部门说明
    :param higher_dept_id: 上级部门id
    :param scope: 权限范围
    :return:
    """
    message = {"message": "success"}
    admin_id = mongo_db.get_obj_id(user_id) if isinstance(user_id, str) else user_id
    company_id = mongo_db.get_obj_id(company_id) if isinstance(company_id, str) else company_id
    if isinstance(admin_id, ObjectId) and isinstance(company_id, ObjectId):
        admin_dbref = DBRef(collection=company_module.CompanyAdmin.get_table_name(), database="platform_db",
                           id=admin_id) if isinstance(admin_id, ObjectId) else admin_id
        filter_dict = {"admin": admin_dbref, "_id": company_id}
        company = company_module.Company.find_one_plus(filter_dict=filter_dict)
        if company is None:
            message['message'] = "没有找到对应的公司"
        else:
            """拥有对应的权限"""
            init_dict = dict()  # 初始化参数
            company_dbref = DBRef(database="platform_db", id=company_id,
                                            collection=company_module.Company.get_table_name())
            init_dict['company_id'] = company_dbref
            dept_name = dept_name
            if dept_name is None or (isinstance(dept_name, str) and dept_name.strip() == ""):
                ms = "部门名称不能为None或者空字符"
                logger.exception(msg=ms)
                message['message'] = ms
                return message
            else:
                init_dict['dept_name'] = dept_name
            description = description
            if description is None or (isinstance(description, str) and description.strip() == ""):
                pass
            else:
                init_dict['description'] = description
            """开始转换上级部门id"""
            higher_dept = company_module.Dept.find_by_id(higher_dept_id)
            if higher_dept is None:
                pass
            else:
                higher_dept = DBRef(collection=company_module.Dept.get_table_name(), database="platform_db",
                                    id=higher_dept_id)
                init_dict['higher_dept'] = higher_dept
                filter_dict = {"company_id": company_dbref, "dept_name": dept_name}
                res = company_module.Dept.find_one_plus(filter_dict=filter_dict)
                if res is None:
                    res = company_module.Dept.insert_one(**init_dict)
                    if res is None:
                        message['message'] = "插入失败"
                    else:
                        pass  # 插入成功
                else:
                    message['message'] = "重复的部门"
    else:
        message['message'] = "参数错误"
    return message


def view_all_dept(user_id: ObjectId = None, can_json: bool = True) -> dict:
    """
    以列表形式返回指定公司的全部部门信息.
    权限:
    1. 公司管理员
    2. 公司所有职员
    :param user_id: 管理员id/员工id,
    :param can_json: 返回的部门字典是否可以直接json? False返回的是Dept的实例的数组
    :return:
    """
    message = {"message": "success"}
    admin_id = mongo_db.get_obj_id(user_id) if isinstance(user_id, str) else user_id
    employee_id = mongo_db.get_obj_id(user_id) if isinstance(user_id, str) else user_id
    if isinstance(admin_id, ObjectId):
        admin_dbref = DBRef(collection=company_module.CompanyAdmin.get_table_name(), database="platform_db",
                            id=admin_id) if isinstance(admin_id, ObjectId) else admin_id
        filter_dict = {"admin": admin_dbref}
        company_id = company_module.Company.find_one_plus(filter_dict=filter_dict, instance=True)
        if company_id is None:
            """不是管理员"""
            employee_id = mongo_db.get_obj_id(employee_id) if isinstance(employee_id, str) else employee_id
            if isinstance(employee_id, ObjectId):
                employee = company_module.Employee.find_by_id(employee_id)
                if isinstance(employee, company_module.Employee):
                    company_dbref = employee.get_attr("company_id")
                    if isinstance(company_dbref, DBRef):
                        company_id = company_dbref.id
                        company = company_module.Company.find_by_id(company_id)
                        if isinstance(company, company_module.Company):
                            dept_list = company_module.Company.all_dept(company, can_json=can_json)
                            message['dept_list'] = dept_list
                        else:
                            message['message'] = "company_id无效"
                    else:
                        message['message'] = "employee没有company_id"
                else:
                    message['message'] = "employee_id没有对应的实例"
            else:
                message['message'] = "employee_id不合法"
        else:
            dept_list = company_module.Company.all_dept(company_id=company_id, can_json=can_json)
            message['dept_list'] = dept_list
    else:
        message['message'] = "user_id错误"
    return message


def edit_dept(**kwargs) -> dict:
    """
    修改部门信息
    权限
    1. 管理员
    2. 被赋予权限的角色
    :param kwargs:
    有2个必须参数,
    1. admin_id: 公司管理员id. str/ObjectId
    2. dept_id: 部门id
    其他的参数用于修改dept信息
    :return:
    """
    message = {"message": "success"}
    if kwargs is None:
        message['message'] = "参数不能为空"
    else:
        admin_id, dept_id = None, None
        try:
            admin_id = kwargs.pop("admin_id")
            dept_id = kwargs.pop("dept_id")
        except KeyError as e:
            print(e)
            logger.exception(e)
        finally:
            if admin_id is None or dept_id is None:
                ms = "缺少必须参数"
                message['message'] = ms
            else:
                admin_id = admin_id if isinstance(admin_id, ObjectId) else mongo_db.get_obj_id(admin_id)
                if isinstance(admin_id, ObjectId):
                    admin_dbref = DBRef(database="platform_db",
                                        collection=company_module.CompanyAdmin.get_table_name(),
                                        id=admin_id)
                    filter_dict = {"admin": admin_dbref}
                    company = company_module.Company.find_one_plus(filter_dict=filter_dict, instance=True)
                    if isinstance(company, company_module.Company):
                        """检查dept的company是否一致?"""
                        dept_id = dept_id if isinstance(dept_id, ObjectId) else mongo_db.get_obj_id(dept_id)
                        filter_dict = {"company_id": company.get_dbref(), "_id": dept_id}
                        dept = company_module.Dept.find_one_plus(filter_dict=filter_dict, instance=True)
                        if isinstance(dept, company_module.Dept):
                            for k, v in kwargs:
                                dept.set_attr(k, v)
                            dept_id = dept.save()
                            if isinstance(dept_id, ObjectId):
                                """修改成功"""
                            else:
                                message['message'] = "修改失败"
                        else:
                            message['message'] = '没有找到对应的部门'
                    else:
                        message['message'] = "没有找到对应的公司"
                else:
                    message['message'] = "错误的admin_id"

    return message


FUNC_MAP = {
        "get_company_by_domain": get_company_by_domain,
        "web_login": web_login,
        "create_dept": create_dept,
        "view_all_dept": view_all_dept
    }


if __name__ == "__main__":
    edit_dept([12, 12])
    pass