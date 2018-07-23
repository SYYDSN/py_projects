# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime


ObjectId = mongo_db.ObjectId


class RawWebChatMessage(mongo_db.BaseDoc):
    """
    原始微信的记录
    """
    _table_name = "raw_webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class WXUserInfo(mongo_db.BaseDoc):
    """从微信接口获取的用户身份信息,目前的用户是测试"""
    _table_name = "wx_user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['nick_name'] = str
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像地址
    type_dict['union_id'] = str
    type_dict['subscribe'] = int   # 是否已关注本微信号
    type_dict['subscribe_scene'] = str   # 用户关注的渠道来源
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        nick_name = kwargs.pop("nickname", "")
        if nick_name != "":
            kwargs['nick_name'] = nick_name
        open_id = kwargs.pop("openid", "")
        if isinstance(open_id, str) and  len(open_id) > 10:
            kwargs['open_id'] = open_id
        head_img_url = kwargs.pop("headimgurl", "")
        if head_img_url != "":
            kwargs['head_img_url'] = head_img_url
        union_id = kwargs.pop("unionid", "")
        if isinstance(union_id, str) and  len(union_id) > 10:
            kwargs['union_id'] = union_id
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(WXUserInfo, self).__init__(**kwargs)

    @classmethod
    def get_extend_info(cls, open_id: str) -> dict:
        """
        获取微信用户的扩展信息(union_id等),这是获取单个微信用户扩展信息的方法
        :param open_id:
        :return:
        """
        u = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN"

    def extend_info(self):
        pass