#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
from manage import company_module
from log_module import get_logger
from api.data import item_module


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


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class Scope:
    """
    权限范围,注意,这不是一个持久化的类
    """
    def __init__(self, scope: (int, str), user_id: ObjectId):
        """
        获取作用范围的过滤器字典
        :param scope: 允许操作的对象范围.字符串格式,有以下取值:
        0. refuse    没有权限.
        1. system    系统级权限,操作全系统的数据,一般颁发给超级管理员,只用做调试或特殊情况,不会颁发给用户.
        2. company   公司级权限,操作本公司数据,一般颁发给公司管理员
        3. dept      部门级权限,操作本部门数据,一般颁发给部门领导,
        4. self      个人级权限,操作自己的数据,一般是普通用户的默认权限.
        5. custom    定制的权限, 比如以列表形式直接列出权限范围.具体方法暂时不明
        :param user_id:
        :return: 返回scope_filter范围过滤器,可能是None或者字典,过滤器字典以scope作为条件限制对象操作范围.其中:
        None     表示没有任何访问权限
        dict()  空字典表示没有条件限制.
        """
        # scope_filter = dict()  # 对象范围限制字典
        scope_filter = None  # 对象范围限制字典,None表示没有权限,
        if scope == 0 or scope == "refuse":
            """没有权限"""
            pass
        elif scope == 1 or scope == "system":
            """系统级权限"""
            scope_filter = dict()
        elif scope == 2 or scope == "company":
            """公司级权限"""
            admin = company_module.CompanyAdmin.find_by_id(user_id)
            if isinstance(admin, company_module.CompanyAdmin):
                """user_id是管理员id"""
                filter_dict = {"admin": admin.get_dbref()}
                company_id = company_module.Company.find_one_plus(filter_dict=filter_dict, projection=["_id"],
                                                               instance=False)
                if isinstance(company_id, ObjectId):
                    """公司存在"""
                    scope_filter = {"company_id": DBRef(collection=company_module.Company.get_table_name(),
                                                        database="platform_db", id=company_id)}
                else:
                    """此管理员帐号没有对应的公司"""
                    ms = "管理员{}没有对应的公司".format(user_id)
                    logger.exception(ms)
                    raise ValueError(ms)
            else:
                """看看是不是员工id?"""
                employee = company_module.Employee.find_by_id(user_id)
                if isinstance(employee, company_module.Employee):
                    """user_id是员工id"""
                    if hasattr(employee, "company_id"):
                        """公司存在"""
                        scope_filter = {"company_id": employee.get_attr("company_id")}
                    else:
                        """员工帐号没有对应的公司"""
                        ms = "员工{}没有对应的公司".format(user_id)
                        logger.exception(ms)
                        raise ValueError(ms)
        elif scope == 3 or scope == "dept":
            """
            部门级权限,此时user_id不能是admin_id,需要判断1.此员工是不是有部门(是不是员工)?如果不是,放弃,是,返回部门权限的筛选条件字典
            """
            employee = company_module.Employee.find_by_id(user_id)
            if isinstance(employee, company_module.Employee):
                user_dbref = DBRef(collection=company_module.Employee.get_table_name(), database="platform_db",
                                   id=user_id)
                """查找user_id对应的关系"""
                filter_dict = {"user_id": user_dbref}
                user_dept_relation = company_module.EmployeeDeptRelation.find_one_plus(filter_dict=filter_dict)
                if user_dept_relation is None:
                    """没有权限"""
                    pass
                else:
                    """部门存在"""
                    scope_filter = {"dept_id": user_dept_relation.get_attr("dept_id")}
            else:
                """没有对应的权限"""
                pass
        elif scope == 4 or scope == "self":
            """
            个人级权限,只检查这个账户是不是存在?
            """
            user = item_module.User.find_by_id(user_id)
            if isinstance(user, item_module.User):
                scope_filter = {"user_id": user.get_dbref()}
            else:
                """用户不存在,没有权限"""
                pass
        elif scope == 5 or scope == "custom":
            """定制的权限,暂未实现"""
            pass
        else:
            pass
        self.__scope = scope
        self.__user_id = user_id
        self.__scope_filter = scope_filter

    def get_filter(self) -> dict:
        """
        获取过滤器字典
        :return:
        """
        return self.__scope_filter

    def set_filter(self, new_filter: dict) -> None:
        """
        设置过滤器字典
        :param new_filter: 新的过滤器字典
        :return:
        """
        self.__scope_filter = new_filter

    def get_scope(self) -> dict:
        """
        获取权限对象范围字符串
        :return:
        """
        return self.__scope

    def set_scope(self, new_scope: (int, str)) -> None:
        """
        设置权限对象范围字符串
        :param new_scope: 权限对象范围字符串
        :return:
        """
        self.__scope = new_scope


class Rule(mongo_db.BaseDoc):
    """权限规则,一个角色有多个权限规则"""
    _table_name = "rule_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id 唯一
    type_dict['role_id'] = DBRef  # 角色id,确认规则属于那个角色?
    type_dict['method'] = str  # 函数/方法名  公司下面不能有同名的方法名
    type_dict['scope'] = str  # 允许操作的对象范围.


class Role(mongo_db.BaseDoc):
    """用户角色,也就是用户组的意思"""
    _table_name = "role_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id 唯一
    type_dict['company_id'] = DBRef  # 公司id,确认权限属于哪个公司?在创建公司的时候,会创建一个默认角色
    type_dict['description'] = str  # 对此角色的说明.非必须
    type_dict['rule_dict'] = dict  # 规则字典

    @classmethod
    def default_role(cls, company_id: (ObjectId, DBRef)) -> object:
        """
        创建并返回一个公司的默认角色
        :return: Role对象实例.注意这个实例并未被保存到数据库.
        """

    @classmethod
    def get_company_id(cls, user_id: ObjectId) -> (ObjectId, None):
        """
        获取一个用户的公司id,
        :param user_id:
        :return:
        """

    @classmethod
    def get_rule_cls(cls, ):
        pass


if __name__ == "__main__":
    init_dict = {

    }