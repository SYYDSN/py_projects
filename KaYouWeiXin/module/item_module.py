# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger
from uuid import uuid4


ObjectId = mongo_db.ObjectId
logger = get_logger()


class RawWebChatMessage(mongo_db.BaseDoc):
    """
    原始微信的记录
    """
    _table_name = "raw_webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class WXUser(mongo_db.BaseDoc):
    """从微信接口获取的用户身份信息,目前的用户是测试"""
    _table_name = "wx_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['nick_name'] = str
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像地址
    type_dict['subscribe'] = int   # 是否已关注本微信号
    type_dict['subscribe_scene'] = str   # 用户关注的渠道来源
    type_dict['subscribe_time'] = datetime.datetime   # 用户关注的时间
    type_dict['access_token'] = str  # 访问access_token
    type_dict['expires_in'] = int  # access_token的过期时间
    type_dict['time'] = datetime.datetime  # access_token的获取时间
    type_dict['refresh_token'] = str  # access_token的refresh_token
    type_dict['role'] = int  # 角色: 1为销售人员 2为中介商 3为黄牛 为空/0是一般人员
    """以下是一般用户/司机专有属性"""
    type_dict['relate_time'] = datetime.datetime  # 和人力资源中介的关联时间
    type_dict['relate_id'] = ObjectId  # 人力资源中介_id,也就是Sales._id,用于判断归属.

    def __init__(self, **kwargs):
        nick_name = kwargs.pop("nickname", "")
        if nick_name != "":
            kwargs['nick_name'] = nick_name
        head_img_url = kwargs.pop("headimgurl", "")
        if head_img_url != "":
            kwargs['head_img_url'] = head_img_url
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(WXUser, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **raw_dict):
        """
        从为新获取到的用户信息的字典创建一个对象.
        :param raw_dict:
        :return:
        """
        subscribe_time = raw_dict.pop("subscribe_time", None)
        if isinstance(subscribe_time, (int, float)):
            raw_dict['subscribe_time'] = datetime.datetime.fromtimestamp(subscribe_time)
        elif isinstance(subscribe_time, str) and subscribe_time.isdigit():
            raw_dict['subscribe_time'] = datetime.datetime.fromtimestamp(int(subscribe_time))
        else:
            pass
        return cls(**raw_dict)

    @classmethod
    def wx_login(cls, **info_dict: dict) -> dict:
        """
        微信用户登录,如果是新用户,那就创建,否则,那就修改.
        :param info_dict:
        :return:
        """
        openid = info_dict.pop("openid")
        res = None
        if openid is None:
            pass
        else:
            f = {"openid": openid}
            init = cls.instance(**info_dict)
            init = init.get_dict(ignore=['_id', "openid"])
            u = {"$set": init}
            res = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
        return res

    @classmethod
    def change_role(cls, user_id: (str, ObjectId), role: int) -> bool:
        """
        改变一个用户的角色
        :param user_id:
        :param role:
        :return:
        """
        if isinstance(user_id, ObjectId):
            pass
        elif isinstance(user_id, str) and len(user_id) == 24:
            user_id = ObjectId(user_id)
        else:
            ms = "错误的user_id:{}".format(user_id)
            logger.exception(ms)
            raise ValueError(ms)
        if isinstance(role, float):
            role = int(role)
        elif isinstance(role, int):
            pass
        elif isinstance(role, str) and role.isdigit():
            role = int(role)
        else:
            ms = "错误的role:{}".format(role)
            logger.exception(ms)
            raise ValueError(ms)
        ses = cls.get_collection()
        f = {"_id": user_id}
        u = {"$set": {"role": role}}
        return_doc = mongo_db.ReturnDocument.AFTER
        doc = ses.find_one_and_update(filter=f, update=u, upsert=True, return_document=return_doc)
        return True if doc else False

    @classmethod
    def relate(cls, u_id: str = None, open_id: str = None, s_id: str = None) -> bool:
        """
        建立用户和中介的关联
        :param u_id: 用户_id 优先用_id查询
        :param open_id: 用户openid
        :param s_id:  中介_id
        :return:
        """
        if (u_id is None and open_id is None) or s_id is None:
            ms = "参数错误! u_id:{}, openid: {}, s_id: {}".format(u_id, open_id, s_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            if isinstance(u_id, str) and len(u_id) == 24:
                user = cls.find_by_id(o_id=u_id, to_dict=True)
            else:
                user = cls.find_one_plus(filter_dict={"openid": open_id}, instance=False)
            sale = cls.find_by_id(o_id=s_id, to_dict=True)
            if isinstance(user, dict) and isinstance(sale, dict):
                role = sale.get("role", 0)
                if isinstance(role, int) and role < 1:
                    relate_time = datetime.datetime.now()
                    relate_id = sale['_id']
                    f = {"_id": user['_id']}
                    u = {"$set": {"relate_id": relate_id, "relate_time": relate_time}}
                    r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                    if r is None:
                        return False
                    else:
                        return True
                else:
                    ms = "用户角色不合法:{}".format(role)
                    logger.exception(ms)
                    raise ValueError(ms)
            else:
                ms = "至少一个用户id无效:{}{}".format(u_id, s_id)
                logger.exception(ms)
                raise ValueError(ms)




class Sales(WXUser):
    """
    销售人员/黄牛/人力资源中介的微信账户
    """
    _table_name = "wx_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str          # 绑定的手机号码
    type_dict['nick_name'] = str      # 微信的昵称
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像地址
    type_dict['subscribe'] = int  # 是否已关注本微信号
    type_dict['subscribe_scene'] = str  # 用户关注的渠道来源
    type_dict['subscribe_time'] = datetime.datetime  # 用户关注的时间
    type_dict['access_token'] = str  # 访问access_token
    type_dict['expires_in'] = int  # access_token的过期时间
    type_dict['time'] = datetime.datetime  # access_token的获取时间
    type_dict['refresh_token'] = str  # access_token的refresh_token
    type_dict['role'] = int  # 角色: 1为销售人员 2为中介商 3为黄牛 为空/0是一般人员

    """
    用户的唯一号码,中介商用于展示在二维码上,关联一般用户用,保证唯一.
    是1--100000的数字,使用了整数类型.
    一般用户这个值一个uuid字符串
    """
    type_dict['only'] = int
    """以下Sales类专有属性"""
    type_dict['name'] = str  # 中介商名字/销售真实姓名.用于展示在二维码上
    type_dict['identity_code'] = str  # 中介商执照号码/销售真实身份证id.用于部分展示在二维码上

    def __init__(self, **kwargs):
        only = kwargs.get("only")
        if isinstance(only, (float, int)) or (isinstance(only, str) and only.isdigit()):
            if isinstance(only, float):
                kwargs['only'] = int(only)
            elif isinstance(only, int):
                pass
            else:
                kwargs['only'] = int(only)
        else:
            ms = "{} 不是一个有效的数字".format(only)
            logger.exception(ms)
            raise ValueError(ms)
        nick_name = kwargs.pop("nickname", "")
        if nick_name != "":
            kwargs['nick_name'] = nick_name
        head_img_url = kwargs.pop("headimgurl", "")
        if head_img_url != "":
            kwargs['head_img_url'] = head_img_url
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        mongo_db.BaseDoc.__init__(self, **kwargs)

    @classmethod
    def create_and_save(cls, **kwargs) -> (None, dict):
        """
        创建(并保存)新对象的时候的专用函数.
        如果是旧的对象,请直接调用__init__函数来完成.
        创建并保存实例, 由于要保证中介商的only属性的: 1,唯一性, 2自增长.
        需要使用事务来完成此项工作.
        :param kwargs:
        :return: 成功返回doc,否则None
        """
        if "_id" in kwargs:
            ms = "本函数只能创建新的对象"
            logger.exception(ms)
            raise ValueError(ms)
        only = kwargs.pop("only", None)
        if only is None:
            pass
        elif isinstance(only, (float, int)) or (isinstance(only, str) and only.isdigit()):
            if isinstance(only, float):
                only = int(only)
            elif isinstance(only, int):
                pass
            else:
                only = int(only)
        else:
            only = None
        doc = None
        if only is None:
            """
            查找表中最大的only,使用事务
            """
            client = mongo_db.get_client()
            handler = client[mongo_db.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as session:
                with session.start_transaction():
                    """一旦出现异常会自动调用session.abort_transaction()"""
                    f = {"only": {"$type": [16, 18, 1]}}
                    s = [("only", -1)]
                    projection = ['only']
                    r = handler.find_one(filter=f, sort=s, projection=projection)
                    if r is None:
                        only = 1
                    else:
                        only = r['only'] + 1
                    kwargs['only'] = only
                    obj = cls(**kwargs)
                    u = obj.get_dict()
                    u.pop("_id")
                    f = {"openid": u.pop("openid", None)}
                    u = {"$set": u}
                    return_doc = mongo_db.ReturnDocument.AFTER
                    doc = handler.find_one_and_update(filter=f, update=u, upsert=True, return_document=return_doc)
        else:
            client = mongo_db.get_client()
            handler = client[mongo_db.db_name][cls.get_table_name()]
            kwargs['only'] = only
            obj = cls(**kwargs)
            u = obj.get_dict()
            u.pop("_id")
            f = {"openid": u.pop("openid", None)}
            u = {"$set": u}
            return_doc = mongo_db.ReturnDocument.AFTER
            doc = handler.find_one_and_update(filter=f, update=u, upsert=True, return_document=return_doc)
        return doc


if __name__ == "__main__":
    pass
