# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
BaseDoc = mongo_db.BaseDoc


class RepeatInstanceError(ValueError):
    """自定义一个异常,用于提醒错误的种类"""
    pass


class Category(BaseDoc):
    """项目的类别，比如前端？后端？app？"""
    _table_name = "category_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str
    type_dict['path'] = str  # url的path
    type_dict['status'] = str  # 状态 normal/stop/invalid  正常/停用/无效(相当于删除一个记录)
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            ms = "name必须"
            logger.exception(ms)
            raise ValueError(ms)
        if "path" not in kwargs:
            ms = "path必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            name = kwargs['name']
            if not isinstance(name, str):
                ms = "name类型错误，期待str，得到：{}".format(type(name))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if 'status' not in kwargs:
            kwargs['status'] = "normal"
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(Category, self).__init__(**kwargs)

    @classmethod
    def add_instance(cls, **kwargs) -> (None, BaseDoc):
        """
        添加一个实例
        此方法需要被子类重写.
        :param kwargs:
        :return:
        """
        the_path = kwargs.get("path")
        if the_path is None:
            raise ValueError("path参数必须")
        else:
            condition_dict = {"path": the_path}
            if cls.exists(condition_dict=condition_dict):
                raise RepeatInstanceError("重复的对象")
            else:
                instance = cls(**kwargs)
                r = instance.insert()
                if isinstance(r, ObjectId):
                    return instance
                else:
                    return None

    @classmethod
    def exists(cls, condition_dict: dict) -> bool:
        """
        添加实例之前,用于判断是否有重复的实例存在?
        :param condition_dict: 判断是否重复的条件字典
        :return:
        """
        f = {"status": {"$ne": "invalid"}}
        f.update(condition_dict)
        r = cls.find_one_plus(filter_dict=f)
        if r is None:
            return False
        else:
            return True

    @classmethod
    def update_instance(cls, o_id: (str, ObjectId), update_dict: dict) -> (None, BaseDoc):
        """
        编辑一个对象
        :param o_id:
        :param update_dict:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            for k, v in update_dict.items():
                instance.set_attr(k, v)
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return instance
            else:
                ms = "保存实例失败：instance = {}".format(instance.to_flat_dict())
                print(ms)
                logger.exception(ms)
        else:
            ms = "错误的oid：{}".format(o_id)
            print(ms)
            logger.exception(ms)

    @classmethod
    def delete_instance(cls, o_id: (str, ObjectId)) -> bool:
        """
        删除一个实例,注意，这里是真的删除数据库的记录。
        :param o_id:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            r = instance.delete_self()
            return r
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
            return False

    @classmethod
    def get_all(cls, ignore: list = ['invalid'], can_json: bool = False) -> list:
        """
        查询所有记录,
        :param ignore:  ignore 数组,哪些status可以忽略?
        :param can_json:
        :return:
        """
        f = {"status": {"$nin": ignore}}
        return cls.find_plus(filter_dict=f, can_json=can_json)

    @classmethod
    def drop(cls, o_id) -> bool:
        """
        修改一个实例的状态为invalid（无效） ，这相当与删除一个对象
        :param o_id:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            instance.set_attr("status", "invalid")
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return True
            else:
                ms = "删除失败，o_id:{}".format(o_id)
                logger.exception(ms)
                print(ms)
                return False
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
            return False

    @classmethod
    def up(cls, o_id) -> bool:
        """
        修改一个实例的状态为normal（正常） ，这相当与启用一个对象
        :param o_id:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            instance.set_attr("status", "normal")
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return True
            else:
                ms = "删除失败，o_id:{}".format(o_id)
                logger.exception(ms)
                print(ms)
                return False
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
            return False

    @classmethod
    def down(cls, o_id) -> bool:
        """
        修改一个实例的状态为stop（正常） ，这相当与停用一个对象
        :param o_id:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            instance.set_attr("status", "stop")
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return True
            else:
                ms = "删除失败，o_id:{}".format(o_id)
                logger.exception(ms)
                print(ms)
                return False
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
            return False

    @classmethod
    def change_status(cls, o_id, status: str) -> bool:
        """
        修改一个实例的状态,作为drop/up/stop三种方法的补充.
        :param o_id:
        :param status:
        :return:
        """
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            instance.set_attr("status", status)
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return True
            else:
                ms = "修改失败，o_id:{}，status:{}".format(o_id, status)
                logger.exception(ms)
                print(ms)
                return False
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
            return False


class Project(Category):
    """项目类"""
    _table_name = "project_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['category_id'] = DBRef
    type_dict['name'] = str
    type_dict['description'] = str
    type_dict['status'] = str    # 状态 normal/stop/suspend/invalid
    type_dict['module_list'] = list  # 模块的列表
    type_dict['create_date'] = datetime.datetime
    type_dict['begin_date'] = datetime.datetime
    type_dict['end_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            ms = "name必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            name = kwargs['name']
            if not isinstance(name, str):
                ms = "name类型错误，期待str，得到：{}".format(type(name))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "status" not in kwargs:
            kwargs['status'] = "normal"
        else:
            status = kwargs['status']
            if status not in ['normal', 'stop', 'suspend', 'invalid']:
                ms = "status错误，必须是normal/stop/suspend/invalid，得到：{}".format(status)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "category_id" not in kwargs:
            ms = "category_id必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            category_id = kwargs['category_id']
            if not isinstance(category_id, DBRef):
                ms = "category_id类型错误，期待DBRef，得到：{}".format(type(category_id))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        else:
            create_date = kwargs['create_date']
            create_date = create_date if isinstance(create_date, datetime.datetime) else \
                mongo_db.get_datetime_from_str(create_date)
            if not isinstance(create_date, datetime.datetime):
                ms = "create_date类型错误，期待datetime，得到：{}".format(type(create_date))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        mongo_db.BaseDoc.__init__(self, **kwargs)

    @classmethod
    def add_instance(cls, **kwargs) -> (None, BaseDoc):
        """
        添加一个实例
        此方法需要被子类重写.
        :param kwargs:
        :return:
        """
        category_id = kwargs.get("category_id")
        name = kwargs.get("name")
        if not isinstance(category_id, DBRef):
            raise ValueError("category_id参数错误")
        elif name == "" or name is None:
            raise ValueError("name参数错误")
        else:
            f = {"name": name, "category_id": category_id}
            if cls.exists(condition_dict=f):
                raise RepeatInstanceError("重复的对象")
            else:
                instance = cls(**kwargs)
            r = instance.insert()
            if isinstance(r, ObjectId):
                return instance
            else:
                return None

    @classmethod
    def get_tasks(cls, o_id: (str, ObjectId), task_type: str = None, task_status: (str, list) = None,
                  can_json: bool = True) -> (None, list):
        """
        获取项目的所有任务，返回的是doc的list
        :param o_id: 项目的_id, ObjectId
        :param task_type: 任务类型， 任务有feature和debug两种。None表示查询全部类型的任务
        :param task_status: 任务状态。任务的状态有： normal/complete/fail/drop/suspend/delay
                          normal: 正常状态，一般新建任务都处于这个状态。默认值
                          complete: 任务已完成
                          fail:  任务失败
                          drop:  任务已被放弃
                          suspend: 任务暂停
                          delay: 任务超期
                          None表示查询所有状态的任务
                          str 表示查询某一种状态的任务
                          list 是类型的数组，可以查询多种状态的任务
        :param can_json: doc对象是否可以直接转为json？
        :return: Task类的doc的list
        """
        project = cls.find_by_id(o_id)
        if isinstance(project, cls):
            p_dbref = project.get_dbref()
            type_list = []
            if task_type is None:
                type_list = ['feature', 'debug']
            else:
                type_list.append(task_type)
            status_list = []
            if task_status is None:
                status_list = ['normal', 'complete', 'fail', 'drop', 'suspend', 'delay']
            elif isinstance(task_status, str):
                status_list.append(task_status)
            elif isinstance(task_status, list):
                status_list = task_status
            else:
                ms = "task_status参数类型错误，{}".format(type(task_status))
                logger.exception(ms)
                raise ValueError(ms)
            f = {
                "project_id": p_dbref,
                "status": {"$in": status_list},
                "type": {"$in": type_list}
            }
            s = {"begin_date": 1}
            records = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
            rs = list()
            delay_id_list = list()
            now = datetime.datetime.now()
            for record in records:
                """把超期的任务滤出来"""
                end_date = record['end_date']
                status = record['status']
                if end_date >= now and status == "normal":
                    """超期的任务"""
                    record['status'] = "delay"
                    delay_id_list.append(record['_id'])
                else:
                    pass
                if can_json:
                    record = mongo_db.to_flat_dict(record)
                else:
                    pass
                rs.append(record)
            if len(delay_id_list) > 0:
                f = {"_id": {"$in": delay_id_list}}
                u = {"$set": {"status": "delay"}}
                cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            else:
                pass
        else:
            rs = None
        return rs

    @classmethod
    def add_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> bool:
        """
        添加一个模块
        :param o_id:
        :param module_dbref:
        :return:
        """
        res = False
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            if isinstance(module_dbref, DBRef):
                module_list = instance.get_attr("module_list")
                if not isinstance(module_list, list):
                    module_list = list()
                else:
                    pass
                if module_dbref in module_list:
                    ms = "被添加的模块已存在，o_id:{}, module:{}".format(o_id, module_dbref)
                    print(ms)
                    logger.exception(ms)
                else:
                    module_list.append(module_dbref)
                    instance.set_attr("module_list", module_list)
                    r = instance.save_plus()
                    if isinstance(r, ObjectId):
                        res = True
                    else:
                        ms = "保存实例失败,instance={}".format(instance.to_flat_dict())
                        logger.exception(ms)
                        print(ms)
            else:
                ms = "module_dbref类型错误，module_dbref:{}".format(type(module_dbref))
                logger.exception(ms)
                print(ms)
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
        return res

    @classmethod
    def remove_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> bool:
        """
        移除一个模块
        :param o_id:
        :param module_dbref:
        :return:
        """
        res = False
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            if isinstance(module_dbref, DBRef):
                module_list = instance.get_attr("module_list")
                if not isinstance(module_list, list):
                    ms = "module_list不存在，o_id:{}, module:{}".format(o_id, module_dbref)
                    print(ms)
                    logger.exception(ms)
                else:
                    if module_dbref not in module_list:
                        ms = "的模块不存在，o_id:{}, module:{}".format(o_id, module_dbref)
                        print(ms)
                        logger.exception(ms)
                    else:
                        module_list.remove(module_dbref)
                        instance.set_attr("module_list", module_list)
                        r = instance.save_plus()
                        if isinstance(r, ObjectId):
                            res = True
                        else:
                            ms = "保存实例失败,instance={}".format(instance.to_flat_dict())
                            logger.exception(ms)
                            print(ms)
            else:
                ms = "module_dbref类型错误，module_dbref:{}".format(type(module_dbref))
                logger.exception(ms)
                print(ms)
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
        return res


class Module(Project):
    """模块信息"""
    _table_name = "module_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['project_id'] = DBRef
    type_dict['name'] = str
    type_dict['description'] = str
    type_dict['status'] = str  # 状态 normal/stop/suspend/invalid
    type_dict['task_list'] = list  # 任务的列表
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            ms = "name必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            name = kwargs['name']
            if not isinstance(name, str):
                ms = "name类型错误，期待str，得到：{}".format(type(name))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "status" not in kwargs:
            kwargs['status'] = "normal"
        else:
            status = kwargs['status']
            if status not in ['normal', 'stop', 'suspend', 'invalid']:
                ms = "status错误，必须是normal/stop/suspend/invalid，得到：{}".format(status)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "project_id" not in kwargs:
            ms = "project_id必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            project_id = kwargs['project_id']
            if not isinstance(project_id, DBRef):
                ms = "project_id类型错误，期待DBRef，得到：{}".format(type(project_id))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        else:
            create_date = kwargs['create_date']
            create_date = create_date if isinstance(create_date, datetime.datetime) else \
                mongo_db.get_datetime_from_str(create_date)
            if not isinstance(create_date, datetime.datetime):
                ms = "create_date类型错误，期待datetime，得到：{}".format(type(create_date))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        mongo_db.BaseDoc.__init__(self, **kwargs)

    @classmethod
    def add_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> bool:
        """
        废弃父类的方法
        :param o_id:
        :param module_dbref:
        :return:
        """
        ms = "此方法只能在Project类中被调用"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def remove_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> bool:
        """
        废弃父类的方法
        :param o_id:
        :param module_dbref:
        :return:
        """
        ms = "此方法只能在Project类中被调用"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def add_instance(cls, **kwargs) -> (None, BaseDoc):
        """
        添加一个实例
        此方法需要被子类重写.
        :param kwargs:
        :return:
        """
        project_id = kwargs.get("project_id")
        name = kwargs.get("name")
        if not isinstance(project_id, DBRef):
            raise ValueError("project_id参数错误")
        elif name == "" or name is None:
            raise ValueError("name参数错误")
        else:
            f = {"name": name, "project_id": project_id}
            if cls.exists(condition_dict=f):
                raise RepeatInstanceError("重复的对象")
            else:
                instance = cls(**kwargs)
            r = instance.insert()
            if isinstance(r, ObjectId):
                return instance
            else:
                return None

    @classmethod
    def add_task(cls, o_id: (str, ObjectId), task_dbref: DBRef) -> bool:
        """
        添加一个任务
        :param o_id:
        :param task_dbref:
        :return:
        """
        res = False
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            if isinstance(task_dbref, DBRef):
                task_list = instance.get_attr("task_list")
                if not isinstance(task_list, list):
                    task_list = list()
                else:
                    pass
                if task_dbref in task_list:
                    ms = "被添加的任务已存在，o_id:{}, task:{}".format(o_id, task_dbref)
                    print(ms)
                    logger.exception(ms)
                else:
                    task_list.append(task_dbref)
                    instance.set_attr("task_list", task_list)
                    r = instance.save_plus()
                    if isinstance(r, ObjectId):
                        res = True
                    else:
                        ms = "保存实例失败,instance={}".format(instance.to_flat_dict())
                        logger.exception(ms)
                        print(ms)
            else:
                ms = "task_dbref类型错误，task_dbref:{}".format(type(task_dbref))
                logger.exception(ms)
                print(ms)
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
        return res

    @classmethod
    def remove_task(cls, o_id: (str, ObjectId), task_dbref: DBRef) -> bool:
        """
        移除一个任务
        :param o_id:
        :param task_dbref:
        :return:
        """
        res = False
        instance = cls.find_by_id(o_id)
        if isinstance(instance, cls):
            if isinstance(task_dbref, DBRef):
                task_list = instance.get_attr("task_list")
                if not isinstance(task_list, list):
                    ms = "task_list不存在，o_id:{}, module:{}".format(o_id, task_dbref)
                    print(ms)
                    logger.exception(ms)
                else:
                    if task_dbref not in task_list:
                        ms = "任务不存在，o_id:{}, module:{}".format(o_id, task_dbref)
                        print(ms)
                        logger.exception(ms)
                    else:
                        task_list.remove(task_dbref)
                        instance.set_attr("task_list", task_list)
                        r = instance.save_plus()
                        if isinstance(r, ObjectId):
                            res = True
                        else:
                            ms = "保存实例失败,instance={}".format(instance.to_flat_dict())
                            logger.exception(ms)
                            print(ms)
            else:
                ms = "task_dbref类型错误，task_dbref:{}".format(type(task_dbref))
                logger.exception(ms)
                print(ms)
        else:
            ms = "找不到对应的实例，o_id:{}".format(o_id)
            logger.exception(ms)
            print(ms)
        return res

    @classmethod
    def get_tasks(cls, o_id: (str, ObjectId), task_type: str = None, task_status: (str, list) = None,
                  can_json: bool = True) -> (None, list):
        """
        获取模块的所有任务，返回的是doc的list
        :param o_id: 模块的_id, ObjectId
        :param task_type: 任务类型， 任务有feature和debug两种。None表示查询全部类型的任务
        :param task_status: 任务状态。任务的状态有： normal/complete/fail/drop/suspend/delay
                          normal: 正常状态，一般新建任务都处于这个状态。默认值
                          complete: 任务已完成
                          fail:  任务失败
                          drop:  任务已被放弃
                          suspend: 任务暂停
                          delay: 任务超期
                          None表示查询所有状态的任务
                          str 表示查询某一种状态的任务
                          list 是类型的数组，可以查询多种状态的任务
        :param can_json: doc对象是否可以直接转为json？
        :return: Task类的doc的list
        """
        module = cls.find_by_id(o_id)
        if isinstance(module, cls):
            m_dbref = module.get_dbref()
            type_list = []
            if task_type is None:
                type_list = ['feature', 'debug']
            else:
                type_list.append(task_type)
            status_list = []
            if task_status is None:
                status_list = ['normal', 'complete', 'fail', 'drop', 'suspend', 'delay']
            elif isinstance(task_status, str):
                status_list.append(task_status)
            elif isinstance(task_status, list):
                status_list = task_status
            else:
                ms = "task_status参数类型错误，{}".format(type(task_status))
                logger.exception(ms)
                raise ValueError(ms)
            f = {
                "module_id": m_dbref,
                "status": {"$in": status_list},
                "type": {"$in": type_list}
            }
            s = {"begin_date": 1}
            records = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
            rs = list()
            delay_id_list = list()
            now = datetime.datetime.now()
            for record in records:
                """把超期的任务滤出来"""
                end_date = record['end_date']
                status = record['status']
                if end_date >= now and status == "normal":
                    """超期的任务"""
                    record['status'] = "delay"
                    delay_id_list.append(record['_id'])
                else:
                    pass
                if can_json:
                    record = mongo_db.to_flat_dict(record)
                else:
                    pass
                rs.append(record)
            if len(delay_id_list) > 0:
                f = {"_id": {"$in": delay_id_list}}
                u = {"$set": {"status": "delay"}}
                cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            else:
                pass
        else:
            rs = None
        return rs


class Task(Project):
    """任务信息"""
    _table_name = "task_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['project_id'] = DBRef
    type_dict['module_id'] = DBRef
    type_dict['name'] = str
    type_dict['description'] = str
    """
    任务状态 
    normal: 正常状态，一般新建任务都处于这个状态。默认值
    complete: 任务已完成
    fail:  任务失败
    drop:  任务已被放弃
    suspend: 任务暂停
    delay: 任务超期，注意，这个状态不是在查询的时候才计算，靠时间比对判断。
    invalid: 被删除的任务，不应该被查询到
    """
    type_dict['status'] = str
    type_dict['type'] = str  # 任务类型 feature（功能）/debug（除虫），默认feature
    # type_dict['task_list'] = list  # 任务的列表
    type_dict['create_date'] = datetime.datetime
    type_dict['begin_date'] = datetime.datetime  # 计划的开始日期 2018-4-10 00：00：00
    type_dict['end_date'] = datetime.datetime   # 计划的结束日期 2018-4-10 00：00：00

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            ms = "name必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            name = kwargs['name']
            if not isinstance(name, str):
                ms = "name类型错误，期待str，得到：{}".format(type(name))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "status" not in kwargs:
            kwargs['status'] = "normal"
        else:
            status = kwargs['status']
            if status not in ['normal', 'complete', 'fail', 'drop', 'suspend', 'delay', 'invalid']:
                ms = "status错误，必须是'normal', 'complete', 'fail', 'drop', 'suspend', 'delay', 'invalid'，得到：{}".format(status)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "type" not in kwargs:
            kwargs['type'] = "feature"
        else:
            the_status = kwargs['type']
            if the_status not in ['feature', 'debug']:
                ms = "status错误，必须是'feature', 'debug'，得到：{}".format(the_status)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "project_id" not in kwargs:
            ms = "project_id必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            project_id = kwargs['project_id']
            if not isinstance(project_id, DBRef):
                ms = "project_id类型错误，期待DBRef，得到：{}".format(type(project_id))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "module_id" not in kwargs:
            ms = "module_id必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            module_id = kwargs['module_id']
            if not isinstance(module_id, DBRef):
                ms = "module_id类型错误，期待DBRef，得到：{}".format(type(module_id))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        else:
            create_date = kwargs['create_date']
            create_date = create_date if isinstance(create_date, datetime.datetime) else \
                mongo_db.get_datetime_from_str(create_date)
            if not isinstance(create_date, datetime.datetime):
                ms = "create_date类型错误，期待datetime，得到：{}".format(type(create_date))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "begin_date" not in kwargs:
            ms = "缺少必要参数：begin_date"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            begin_date = kwargs['begin_date']
            begin_date = begin_date if isinstance(begin_date, datetime.datetime) else \
                mongo_db.get_datetime_from_str(begin_date)
            if not isinstance(begin_date, datetime.datetime):
                ms = "begin_date类型错误，期待datetime，得到：{}".format(type(begin_date))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "end_date" not in kwargs:
            ms = "缺少必要参数：end_date"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            end_date = kwargs['end_date']
            end_date = end_date if isinstance(end_date, datetime.datetime) else \
                mongo_db.get_datetime_from_str(end_date)
            if not isinstance(end_date, datetime.datetime):
                ms = "end_date类型错误，期待datetime，得到：{}".format(type(end_date))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        mongo_db.BaseDoc.__init__(self, **kwargs)

    @classmethod
    def add_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> None:
        """
        废弃父类的方法
        :param o_id:
        :param module_dbref:
        :return:
        """
        ms = "此方法只能在Project类中被调用"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def remove_module(cls, o_id: (str, ObjectId), module_dbref: DBRef) -> None:
        """
        废弃父类的方法
        :param o_id:
        :param module_dbref:
        :return:
        """
        ms = "此方法只能在Project类中被调用"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def drop(cls, o_id) -> None:
        """
        废弃父类的方法
        """
        ms = "此方法在Task类中被废弃,请用Task.change_status方法"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def up(cls, o_id) -> None:
        """
        废弃父类的方法
        """
        ms = "此方法在Task类中被废弃,请用Task.change_status方法"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def down(cls, o_id) -> None:
        """
        废弃父类的方法
        """
        ms = "此方法在Task类中被废弃,请用Task.change_status方法"
        logger.exception(ms)
        raise AttributeError(ms)

    @classmethod
    def add_instance(cls, **kwargs) -> (None, BaseDoc):
        """
        添加一个实例
        此方法需要被子类重写.
        :param kwargs:
        :return:
        """
        project_id = kwargs.get("project_id")
        name = kwargs.get("name")
        if not isinstance(project_id, DBRef):
            raise ValueError("project_id参数错误")
        elif name == "" or name is None:
            raise ValueError("name参数错误")
        else:
            f = {"name": name, "project_id": project_id}
            if cls.exists(condition_dict=f):
                raise RepeatInstanceError("重复的对象")
            else:
                instance = cls(**kwargs)
            r = instance.insert()
            if isinstance(r, ObjectId):
                return instance
            else:
                return None


if __name__ == "__main__":
    """添加项目"""
    c_id = DBRef(id=ObjectId("5ae5992409d20f1079d86b75"), collection=Category.get_table_name())  # 前端
    # Project.add_instance(category_id=c_id, name="保驾犬平台管理页面")
    """添加模块"""
    p_id = DBRef(id=ObjectId("5ae5d89709d20f36f19d90d4"), collection=Project.get_table_name())  # 保驾犬平台管理页面
    # Module.add_instance(project_id=p_id, name="电子地图")
    """查询模块的任务"""
    m_id = ObjectId("5ae5d94209d20f378cb5999f")
    Module.get_tasks(o_id=m_id)
    pass