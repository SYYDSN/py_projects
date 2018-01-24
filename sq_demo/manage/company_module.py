# -*- coding:utf-8 -*-
import sys
import os

"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
from api.data.item_module import User, Track
import error_module
from log_module import get_logger


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
    type_dict['full_name'] = str  # 公司全称
    type_dict['prefix'] = str  # 公司查询前缀,url路径在用做公司标识,唯一.
    type_dict['short_name'] = str  # 简称
    type_dict['description'] = str  # 公司简介
    type_dict['admin'] = DBRef  # 公司管理员 指向company_admin_info

    def __init__(self, **kwargs):
        if 'prefix' not in kwargs:
            raise ValueError("公司查询前缀为必须参数")
        if kwargs['prefix'] == "" or kwargs['prefix'] is None:
            raise ValueError("公司查询前缀必须是一个有效的字符串")
        super(Company, self).__init__(**kwargs)

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
    def all_dept(cls, company_id: (str, ObjectId)) -> list:
        """
        根据公司id获取全部的职务的列表
        :param company_id:
        :return
        """
        company = cls.find_by_id(company_id)
        res = list()
        if not isinstance(company, cls):
            pass
        else:
            company_dbref = company.get_dbref()
            filter_dict = {'company_id': company_dbref}
            res = {str(m['_id']): m['dept_name'] for m in Dept.find_plus(filter_dict=filter_dict, projection=["_id", "dept_name"], to_dict=True)}
        return res

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


class Post(mongo_db.BaseDoc):
    """职务类"""
    _table_name = "post_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['company_id'] = DBRef  # 所属公司 Company
    type_dict['post_name'] = str  # 岗位名称
    type_dict['post_level'] = str  # 岗位级别，某些公司用来区分待遇的标识。也会用来区分不同部门的相同名称的岗位的区别


class Dept(mongo_db.BaseDoc):
    """部门/团队类"""
    _table_name = "dept_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['company_id'] = DBRef  # 所属公司 Company
    type_dict['leader_id'] = DBRef  # 领导团队 Employee
    type_dict['secondary_leaders'] = list  # 除部门正职领导之外的辅助的领导,是Employee的DBRef的list
    type_dict['dept_name'] = str  # 团队名称
    type_dict['description'] = str  # 说明
    type_dict['higher_dept'] = DBRef  # 上级部门

    def __init__(self, **kwargs):
        """先检查是否有重复的对象
        注意，company_id,higher_dept和dept_name构成联合主键
        """
        if 'secondary_leaders' not in kwargs:
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
    dept_path 是此员工所属部门的路径的list，代表了从顶层到此员工位置的部门/团队的路径。
    比如[总公司_DBRef,上海分公司_DBRef,嘉定分部_DBRef,安亭车队_DBRef,A队_DBRef]，
    可根据每一个DBRef对象获知此部门的领导。
    测试团队A组组长: 17321067312
    """

    def __init__(self, **kwargs):
        self.type_dict['company_id'] = DBRef  # 所属公司id  Company
        self.type_dict['post_id'] = DBRef  # 岗位信息 Post
        self.type_dict['dept_path'] = list  # 所属团队DBRef组成的list，Dept
        self.type_dict['block_list'] = list  # 不想显示的用户的DBRef组成的list，Employee
        self.type_dict['scheduling'] = list   # 排班的DBRef的list,对应于员工的排班,默认早9点到晚17点.（考虑加班和替班的情况）
        super(Employee, self).__init__(**kwargs)

    def in_post(self, company_id: (ObjectId, DBRef, str), post_id: (ObjectId, DBRef, str)) -> list:
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
    def get_employee_in_post(cls, company_id: (ObjectId, DBRef, str), post_id: (ObjectId, DBRef, str)) -> list:
        """
        查询某个公司，某个岗位的全体人员,这实际上是self.n_post()的类方法版
        :param company_id: 公司id
        :param post_id: 职务id
        :return: 实例列表
        """
        return cls().in_post(company_id, post_id)

    @classmethod
    def subordinates_instance(cls, user_id: (str, ObjectId), can_json: bool = True, include_blocking: bool = False) -> list:
        """
        获取指定用户的所有下属的实例，有下属的时候包含自己，如果没有下属，那就返回一个空list
        :param user_id: 指定用户的id
        :param can_json: 是否为json做好类型转换?
        :param include_blocking: 是否包含被阻止的用户列表？
        :return: 下属的id的instance列表
        """
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
    employee_id = ObjectId("59cb4c03ad01be0912b34e5a")
    # employee_id = ObjectId("59fa8ee8e39a7b515f288406")
    Employee.subordinates_id(employee_id)
    pass
