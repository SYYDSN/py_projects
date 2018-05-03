# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from hashlib import md5
import datetime
from bson.objectid import ObjectId
from module.project_module import Category
import jwt
from log_module import get_logger


"""用户模块"""


cache = mongo_db.cache
logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
secret = "6296d5ab38124c368eb9f97e4b58107d"  # 密钥，为jwt服务。


class User(mongo_db.BaseDoc):
    """
    保存操作者信息的类.管理员用户 proot/P@root1234
    """
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['nick_name'] = str
    type_dict['user_password'] = str
    """
    用户组 分为 admin(管理员)/worker(操作者) 2类
    admin: 除拥有所有worker的操作权限外，还能管理账户和Category
    worker： 视权限设定，能操作Project，Module和Task,也有查看的权限
    """
    type_dict['group'] = str
    """
    可以查看的类别组,默认是空，不可以查看所有类别
    """
    type_dict['allow_view'] = list
    """
    可以编辑的类别组。默认为空，不能操作任何类别
    """
    type_dict['allow_edit'] = list
    type_dict['status'] = int  # 0表示不可用,1表示可用
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "group" not in kwargs:
            kwargs['group'] = "worker"
        if "user_name" not in kwargs:
            ms = "user_name必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            user_name = kwargs['user_name']
            if not isinstance(user_name, str):
                ms = "user_name类型错误，期待str，得到：{}".format(type(user_name))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "user_password" not in kwargs:
            ms = "user_password必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            user_password = kwargs['user_password']
            if not isinstance(user_password, str):
                ms = "user_password类型错误，期待str，得到：{}".format(type(user_password))
                logger.exception(ms)
                raise ValueError(ms)
            else:
                pass
        if "allow_view" not in kwargs:
            kwargs['allow_view'] = list()
        if "allow_edit" not in kwargs:
            kwargs['allow_edit'] = list()
        if "status" not in kwargs:
            kwargs['status'] = 1
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(User, self).__init__(**kwargs)

    @classmethod
    def login(cls, user_name: str, user_password: str) -> dict:
        """
        用户登录,跨域用户登录一般不直接调用此项，而是调用Identity.user_login方法
        :param user_name:
        :param user_password:
        :return:
        """
        mes = {"message": "success"}
        if isinstance(user_name, str):
            if isinstance(user_password, str):
                f = {"user_name": user_name}
                user = cls.find_one_plus(filter_dict=f, instance=False)
                if isinstance(user, dict):
                    user_password_db = user['user_password']
                    if user_password.lower() == user_password_db.lower():
                        nick_name = '' if user.get("nick_name") is None else user['nick_name']
                        user_id = user['_id']
                        group = user['group']
                        data = {
                            "_id": str(user_id), "nick_name": nick_name, "group": group,
                            "allow_view": [str(x) for x in user['allow_view']],
                            "allow_edit": [str(x) for x in user['allow_edit']]
                        }
                        """获取访问规则"""
                        rule_dict = cls.access_rule(user_id=user_id)
                        data.update(rule_dict)
                        mes['data'] = data
                    else:
                        mes['message'] = "密码错误"
                else:
                    mes['message'] = "用户名不存在"
            else:
                mes['message'] = "用户名密码错误，期待一个srt，获得一个{}".format(type(user_password))
        else:
            mes['message'] = "用户名类型错误，期待一个srt，获得一个{}".format(type(user_name))
        return mes

    @classmethod
    def add_user(cls, **kwargs) -> bool:
        """
        添加用户,
        :param kwargs:
        :return:
        """
        if "user_name" not in kwargs or "user_password" not in kwargs:
            ms = "user_name和user_password必须"
            logger.exception(ms)
            raise ValueError(ms)
        if "group" not in kwargs:
            kwargs['group'] = 'worker'
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        user_name = kwargs['user_name']
        user_password = kwargs['user_password']
        if isinstance(user_name, str) and isinstance(user_password, str):
            user_name = user_name.strip()
            user_password = user_password.strip()
            if len(user_name) < 1 or len(user_password) < 1:
                ms = "user_name和user_password长度不能为0! {},{}".format(user_name, user_password)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                new_user_password = md5(user_password.encode(encoding="utf-8")).hexdigest()
                kwargs['user_password'] = new_user_password
                r = cls.insert_one(**kwargs)
                if isinstance(r, ObjectId):
                    return True
                else:
                    return False
        else:
            ms = "user_name和user_password必须是字符串格式! {},{}".format(type(user_name), type(user_password))
            logger.exception(ms)
            raise ValueError(ms)

    @classmethod
    def update_user(cls, user_id: (str, ObjectId), update_dict: dict) -> (None, mongo_db.BaseDoc):
        """
        编辑一个对象
        :param user_id:
        :param update_dict:
        :return:
        """
        instance = cls.find_by_id(user_id)
        if isinstance(instance, cls):
            for k, v in update_dict.items():
                instance.set_attr(k, v)
            r = instance.save_plus()
            if isinstance(r, ObjectId):
                return instance
            else:
                ms = "保存用户失败：instance = {}".format(instance.to_flat_dict())
                print(ms)
                logger.exception(ms)
        else:
            ms = "错误的user_id：{}".format(user_id)
            print(ms)
            logger.exception(ms)

    @classmethod
    def change_password(cls, user_id: (str, ObjectId), new_password: str) -> bool:
        """
        修改密码
        :param user_id:
        :param new_password:
        :return:
        """
        f = {"_id": mongo_db.get_obj_id(user_id)}
        u = {"$set": {"user_password": md5(new_password.encode(encoding="utf-8")).hexdigest()}}
        r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
        if r is None:
            ms = "修改密码失败： user_id:{},new_password:{}".format(user_id, new_password)
            logger.exception(ms)
            res = False
        else:
            res = True
        return res

    @classmethod
    def delete_user(cls, user_id) -> bool:
        """
        删除用户
        :param user_id:
        :return:
        """
        res = False
        if user_id is None:
            ms = "用户id不能为空"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            user_id = mongo_db.get_obj_id(user_id)
            if not isinstance(user_id, ObjectId):
                ms = "错误的user_id:{}".format(user_id)
                logger.exception(ms)
                raise ValueError(ms)
            else:
                if user_id == ObjectId("5ae5440c09d20f658685f3c9"):
                    ms = "管理员账户无法删除"
                    logger.exception(ms)
                    raise ValueError(ms)
                else:
                    f = {"_id": user_id}
                    r = cls.find_one_and_delete(filter_dict=f)
                    if r is None:
                        ms = "删除失败，没有找到对象，user_id={}".format(user_id)
                        logger.exception(ms)
                        raise ValueError(ms)
                    else:
                        res = True
        return res

    @classmethod
    def access_rule(cls, user_id: (str, ObjectId)) -> (None, dict):
        """
        根据用户id返回用户的访问规则
        :param user_id:
        :return:
        """
        res = dict()
        user = cls.find_by_id(user_id)
        if isinstance(user, cls):
            view_ids = user.get_attr("allow_access")
            if view_ids is None or len(view_ids) == 0:
                v_rules = dict()
            else:
                f = {"_id": {"$in": view_ids}}
                views = Category.find_plus(filter_dict=f, to_dict=True)
                v_rules = {x['path']: x['name'] for x in views}
            edit_ids = user.get_attr("allow_edit")
            if edit_ids is None or len(edit_ids) == 0:
                e_rules = dict()
            else:
                f = {"_id": {"$in": edit_ids}}
                edits = Category.find_plus(filter_dict=f, to_dict=True)
                e_rules = {x['path']: x['name'] for x in edits}
            res['view'] = v_rules
            res['edit'] = e_rules
        else:
            pass
        return res

    @classmethod
    def get_all(cls, can_json: bool = False) -> list:
        """
        获取不包括管理员(proot)在内的全部用户,
        :param can_json:
        :return:
        """
        f = {"user_name": {"$ne": "proot"}}
        users = cls.find_plus(filter_dict=f, can_json=can_json)
        return users


class Identity:
    """身份验证类，使用了pyjwt,这不是一个持久化类"""
    _table_name = "identity_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_id'] = DBRef
    type_dict['token'] = str
    type_dict['create_date'] = datetime.datetime
    type_dict['end_date'] = datetime.datetime  # 到期时间

    @classmethod
    def user_login(cls, user_name: str, user_password: str) -> dict:
        """
        用户注册的时候请调用此方法，会返回用户的加密后的token
        :param user_name:
        :param user_password:
        :return:
        """
        mes = User.login(user_name=user_name, user_password=user_password)
        if mes['message'] == "success":
            """登录成功,生成jwt"""
            data = mes.pop('data')
            user_id = data["_id"]
            nick_name = data["nick_name"]
            token = jwt.encode({"user_id": user_id}, secret, algorithm='HS256').decode(encoding="utf-8")
            mes['data'] = {"token": token, "nick_name": nick_name}
        else:
            pass
        return mes

    @classmethod
    def verify(cls, token) -> (str, None):
        """
        验证jwt字符串是否正确
        :param token:
        :return: 用户id的str格式
        """
        decoded = None
        try:
            decoded = jwt.decode(token.encode(encoding="utf-8"), secret, algorithms='HS256')
        except Exception as e:
            ms = "验证分身失败，token：{},错误原因:{}".format(token, e)
            logger.exception(e)
            print(ms)
        finally:
            if decoded is None:
                return None
            else:
                return decoded['user_id']


if __name__ == "__main__":
    # User.add_user(user_name="proot2", user_password="P@root1234", group="admin", nick_name="系统管理员")
    Identity.user_login('proot', md5('P@root1234'.encode()).hexdigest())
    pass