# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger
from module.driver_module import *


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
    type_dict['resume_id'] = ObjectId  # 简历id
    type_dict['relate_time'] = datetime.datetime  # 和人力资源中介的关联时间
    type_dict['relate_id'] = ObjectId  # 人力资源中介_id,也就是Sales._id,用于判断归属.
    """以下Sales类专有属性"""
    type_dict['name'] = str  # 中介商名字/销售真实姓名.用于展示在二维码上
    type_dict['identity_code'] = str  # 中介商执照号码/销售真实身份证id.用于部分展示在二维码上

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
                print("sale's role is {}".format(role))
                if isinstance(role, int) and role > 0:
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

    @classmethod
    def get_account(cls, u_id: (str, ObjectId), can_json: bool = True) -> dict:
        """
        获取微信账户的信息.
        :param u_id:
        :return:
        :param can_json:
        """
        user = cls.find_by_id(o_id=u_id, to_dict=True, can_json=can_json)
        return user

    @classmethod
    def opt_resume(cls, u_id: (str, ObjectId), resume_args: dict, can_json: bool = True) -> dict:
        """
        操作(查看/添加/修改,但是不能删除)简历,目前只能有一份简历
        :param u_id:  用户id
        :param resume_args:  创建简历的字典
        :param can_json:
        :return:
        """
        mes = {"message": "success"}
        user = cls.find_by_id(o_id=u_id, to_dict=True)
        resume_id = user.get("resume_id", "")
        _id = resume_args.pop("_id", "")
        _id = ObjectId(_id) if isinstance(_id, str) and len(_id) == 24 else _id
        if len(resume_args) == 1 and "_id" in resume_args:
            """字典中只有_id字段表示查看简历"""
            if isinstance(_id, ObjectId) and _id == resume_id:
                r = DriverResume.find_by_id(o_id=_id, to_dict=True, can_json=can_json)
                if isinstance(r, dict):
                    mes['data'] = r
                else:
                    mes['message'] = "查询失败"
            else:
                mes['message'] = "简历id不匹配"
        elif len(resume_args) == 0:
            """字典中没有_id字段表示新用户查看简历,创建一个临时的"""
            resume_init = dict()
            resume_init['wx_id'] = u_id
            resume_init['phone'] = user.get("phone")
        else:
            """添加或者修改"""
            if "phone" not in resume_args:
                resume_args['phone'] = user.get("phone")
            if isinstance(_id, ObjectId):
                """resume_args里有_id视为修改修改简历"""
                if resume_id == _id:
                    f = {"_id": _id}
                    u = {"$set": resume_args}
                    r = DriverResume.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                    if isinstance(r, dict):
                        """修改成功"""
                        pass
                    else:
                        mes['message'] = "修改简历失败"
                else:
                    mes['message'] = "简历id不一致"
            else:
                """添加简历"""
                if isinstance(resume_id, ObjectId):
                    mes['message'] = "只能创建一份简历"
                else:
                    resume_args['_id'] = ObjectId()
                    resume = DriverResume(**resume_args)
                    resume_id = resume.save_plus()
                    if isinstance(resume_id, ObjectId):
                        """由于跨了数据库,这里无法使用事务"""
                        f = {"_id": u_id}
                        u = {"$set": {"resume_id": resume_id}}
                        r = cls.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
                        if r:
                            mes['_id'] = str(resume_id) if can_json else resume_id
                        else:
                            mes['message'] = "保存用户信息失败"
                    else:
                        mes['message'] = "保存简历失败"
        return mes

    @classmethod
    def opt_extend_info(cls, u_id: (str, ObjectId), resume_id: (str, ObjectId), opt: str, arg_dict: dict,
                        can_json: bool = True) -> dict:
        """
        操作(查看/添加/修改/删除)简历的扩展信息,扩展信息包含如下内容:
        1. 添加工作经历  add_work     DriverResume.add_work_history
        2. 编辑工作经历  update_work  DriverResume.update_work_history
        3. 删除工作经历  delete_work  DriverResume.delete_work_history

        4. 添加教育经历  add_education  DriverResume.add_education
        5. 修改教育经历  update_education  DriverResume.update_education
        6. 删除教育经历  delete_education  DriverResume.delete_education


        :param u_id:  用户id
        :param resume_id:  简历的字典
        :param opt:  操作类型
        :param arg_dict:  其他参数组成的字典
        :param can_json:
        :return:
        多种返回结果:
        工作经历: {"message": "success", "_id": WorkHistory._id}
        教育经历: {"message": "success", "_id": Education._id}
        车辆信息: {"message": "success", "_id": Vehicle._id}
        所获荣誉: {"message": "success", "_id": Honor._id}
        """
        mes = {"message": "success"}
        user = cls.find_by_id(o_id=u_id, to_dict=True)
        if isinstance(user, dict):
            if str(resume_id) == str(user.get("resume_id", "")):
                if opt == "add_work":
                    """添加工作经历"""
                    _id = DriverResume.add_work_history(resume_id=resume_id, history_args=arg_dict)
                    mes['_id'] = str(_id) if can_json else _id
                elif opt == "update_work":
                    """修改工作经历"""
                    w_id = arg_dict.pop("work_id", None)
                    if w_id is None:
                        mes['message'] = "缺少必要的参数:work_id"
                    else:
                        _id = DriverResume.update_work_history(resume_id=resume_id, work_id=w_id, update_args=arg_dict)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "delete_work":
                    """删除工作经历"""
                    w_id = arg_dict.pop("work_id", None)
                    if w_id is None:
                        mes['message'] = "缺少必要的参数:work_id"
                    else:
                        _id = DriverResume.delete_work_history(resume_id=resume_id, work_id=w_id)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "add_education":
                    """添加教育经历"""
                    _id = DriverResume.add_education(resume_id=resume_id, init_args=arg_dict)
                    mes['_id'] = str(_id) if can_json else _id
                elif opt == "update_education":
                    """修改教育经历"""
                    e_id = arg_dict.pop("e_id", None)
                    if e_id is None:
                        mes['message'] = "缺少必要的参数:e_id"
                    else:
                        _id = DriverResume.update_education(resume_id=resume_id, e_id=e_id, update_args=arg_dict)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "delete_education":
                    """删除教育经历"""
                    e_id = arg_dict.pop("e_id", None)
                    if e_id is None:
                        mes['message'] = "缺少必要的参数:e_id"
                    else:
                        _id = DriverResume.delete_education(resume_id=resume_id, e_id=e_id)
                        mes['_id'] = str(_id) if can_json else _id
                else:
                    ms = "未知的操作:{}".format(opt)
                    logger.exception(msg=ms)
                    print(ms)
                    mes['message'] = ms
            else:
                mes['message'] = "简历id无效"
        else:
            ms = "错误的用户id:{}".format(u_id)
            logger.exception(msg=ms)
            print(ms)
            mes['message'] = ms
        return mes







if __name__ == "__main__":
    pass
