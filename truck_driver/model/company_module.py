#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
from model.driver_module import DriverResume
import datetime
import warnings
import hashlib


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""公司相关的模型"""


class Company(mongo_db.BaseDoc):
    """公司用户"""
    _table_name = "company"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['full_name'] = str
    type_dict['short_name'] = str
    type_dict['desc'] = str              # 公司简介
    type_dict['user_name'] = str         # 公司账户的登录名,全局唯一
    type_dict['user_password'] = str
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        from_create_func = kwargs.pop("from_create_func", False)
        if isinstance(from_create_func, bool) and from_create_func:
            pass
        else:
            ms = "你正在直接调用Company的初始化函数,请自行检查user_name属性的唯一性"
            warnings.warn(message=ms)
        if "full_name" not in kwargs:
            kwargs['full_name'] = ''
        if "short_name" not in kwargs:
            kwargs['short_name'] = ''
        if "desc" not in kwargs:
            kwargs['desc'] = ''
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        user_name = kwargs.pop("user_name", "")
        if isinstance(user_name, str) and len(user_name) > 1:
            kwargs['user_name'] = user_name
        else:
            ms = "用户名必须是一个有效的字符串,不能是 {}".format(user_name)
            raise ValueError(ms)
        user_password = kwargs.pop("user_password", "")
        if isinstance(user_password, str) and len(user_password) == 32:
            kwargs['user_password'] = user_password
        else:
            ms = "密码格式错误"
            raise ValueError(ms)
        super(Company, self).__init__(**kwargs)

    @classmethod
    def create(cls, save: bool = False, **kwargs) -> object:
        """
        推荐的创建实例的方法,会检查user_name参数是否唯一?
        :param save: 是否创建实例后立即保存?
        :param kwargs:
        :return: 实例对象
        """
        if "from_create_func" not in kwargs:
            kwargs['from_create_func'] = True   # 此参数告诉self.__init__函数,调用者是cls.create函数
        user_name = kwargs.pop("user_name", "")
        if isinstance(user_name, str) and len(user_name) > 1:
            kwargs['user_name'] = user_name
            """查询user_name是否唯一?"""
            f = {"user_name": user_name}
            r = cls.find_one_plus(filter_dict=f, instance=False, can_json=False)
            if r:
                ms = "用户名已存在"
                raise ValueError(ms)
            else:
                pass
        else:
            pass
        instance = cls(**kwargs)
        if save:
            r = instance.save_plus()
            if not isinstance(r, ObjectId):
                ms = "实例保存失败"
                raise ValueError(ms)
            else:
                pass
        return instance

    @classmethod
    def login(cls, user_name: str, user_password: str, can_json: bool = False) -> dict:
        """
        公司用户的登录
        :param user_name:
        :param user_password:
        :param can_json:
        :return:
        """
        mes = {"message": "success"}
        f = {"user_name": user_name}
        projection = ['_id', 'user_name', 'user_password', 'full_name', 'short_name', 'desc']
        one = cls.find_one_plus(filter_dict=f, projection=projection, instance=False)
        if one:
            pw = one.get('user_password', "")
            if isinstance(user_password, str) and user_password.lower() == pw.lower():
                one.pop("user_password", "")
                one = mongo_db.to_flat_dict(one)if can_json else one
                mes['data'] = one
            else:
                mes['message'] = "密码错误"
        else:
            mes['message'] = "用户名不存在"
        return mes

    @classmethod
    def add_company_raw(cls, init: dict = None, md5: bool = False, save: bool = True, instance: bool = False) -> (object, ObjectId):
        """
        此方法原始的添加公司账户的方法.一般只在用做开发级别的调用.也可作为其他函数的底层函数.
        :param init: 初始化实力的参数字典.
        :param md5: 是否对密码属性进行md5转换(默认不转,即密码已经是md5转换过了.如果是node/前端传来的初始化字典,密码是应该
        已经进行过md5转换的,所以这里应该设置为False,如果是直接在内部或命令行调用此方法,此参数一定要被设置为True)
        :param save: 是否创建实例后立即保存?
        :param instance: 返回实例还是ObjectId?默认返回ObjectId
        :return:
        """
        pw = init.pop("user_password", None)
        if pw is None:
            pw = "123456"
        else:
            pw = pw if isinstance(pw, str) else str(pw)
        if md5:
            pw = hashlib.md5(pw.encode(encoding="utf-8")).hexdigest()
        else:
            pass
        init['user_password'] = pw
        return cls.create(save=save, **init) if instance else cls.create(save=save, **init).get_id()

    def resume_favorite(self, page_size: int = 10, ruler: int = 5, page_index: int = 1, to_dict: bool = True,
                        can_json: bool = False) -> dict:
        """
        以分页方式查看收藏的简历
        :param page_size: 每页大小(多少条记录?)
        :param ruler: 翻页器最多显示几个页码？
        :param page_index: 页码(当前页码)
        :param to_dict: 返回的元素是否转成字典(默认就是字典.否则是类的实例)
        :param can_json: 是否调用to_flat_dict函数转换成可以json的字典?
        :return:
        """
        f = {"company_id": self.get_dbref()}
        s = {"time": -1}
        args = dict()
        args['filter_dict'] = f
        args['sort_dict'] = s
        args['page_size'] = page_size
        args['ruler'] = ruler
        args['page_index'] = page_index
        args['to_dict'] = to_dict
        args['can_json'] = can_json
        res = ResumeFavorite.query_by_page(**args)
        return res

    @classmethod
    def get_resume_favorite(cls, company_id: (str, ObjectId), page_size: int = 10, ruler: int = 5, page_index: int = 1,
                            to_dict: bool = True, can_json: bool = False) -> dict:
        """
        以分页方式查看收藏的简历, self/resume_favorite的类方法
        :param company_id:  公司id
        :param page_size: 每页大小(多少条记录?)
        :param ruler: 翻页器最多显示几个页码？
        :param page_index: 页码(当前页码)
        :param to_dict: 返回的元素是否转成字典(默认就是字典.否则是类的实例)
        :param can_json: 是否调用to_flat_dict函数转换成可以json的字典?
        :return:
        """
        company = cls.find_by_id(company_id)
        if not isinstance(company, cls):
            ms = "错误的公司id:{}".format(company_id)
            raise ValueError(ms)
        else:
            return company.resume_favorite(page_size=page_size, ruler=ruler, page_index=page_index, to_dict=to_dict,
                                           can_json=can_json)

    @classmethod
    def in_favorite(cls, company_id: (str, ObjectId), drivers: list, to_str: bool = True) -> dict:
        """
        检查一组给定的简历是否已被收藏?
        :param company_id: 公司id
        :param drivers:  司机建立的_id的ObjectId/DBRef组成的list
        :param to_str:  是否转ObjectId/DBRef
        :return: {driver1_id: "yes", driver2_id: "no",....}
        """
        company = cls.find_by_id(company_id)
        if not isinstance(company, cls):
            ms = "错误的公司id:{}".format(company_id)
            raise ValueError(ms)
        else:
            company_dbref = company.get_dbref()
            resume_ids = list()
            for x in drivers:
                if isinstance(x, str) and len(x) == 24:
                    x = ObjectId(x)
                else:
                    pass
                if isinstance(x, ObjectId):
                    x = DBRef(database=mongo_db.db_name, collection=DriverResume.get_table_name(), id=x)
                else:
                    pass
                if isinstance(x, DBRef):
                    resume_ids.append(x)
                else:
                    pass
            f = {"company_id": company_dbref, "resume_id": {"$in": resume_ids}}
            r = ResumeFavorite.find_plus(filter_dict=f, to_dict=True)
            r = [x['resume_id'] for x in r]
            if to_str:
                res = {str(x.id): ("yes" if x in r else "no") for x in resume_ids}
            else:
                res = {x.id: ("yes" if x in r else "no") for x in resume_ids}
            return res


class ResumeFavorite(mongo_db.BaseDoc):
    """公司的简历收藏夹,用于收藏自己中意的司机"""
    _table_name = "resume_favorite"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # _id
    type_dict['company_id'] = DBRef
    type_dict['resume_id'] = DBRef
    type_dict['time'] = datetime.datetime  # 收藏时间.

    def __init__(self, **kwargs):
        if "company_id" not in kwargs:
            ms = "company_id必须"
            raise ValueError(ms)
        if "resume_id" not in kwargs:
            ms = "resume_id必须"
            raise ValueError(ms)
        if "time" not in kwargs:
            kwargs['time'] = datetime.datetime.now()
        super(ResumeFavorite, self).__init__(**kwargs)


if __name__ == "__main__":
    pass
