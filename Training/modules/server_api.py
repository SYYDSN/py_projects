# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import orm_module
from mail_module import send_mail
import datetime
import requests


ObjectId = orm_module.ObjectId
DBRef = orm_module.DBRef
app_id = "wxd89f1f72776053ad"                       # app_id
app_secret = "66a4200979bf09dd565180f1bd9c38d4"     # app_secret


"""和微信服务器相关的功能"""


class AccessToken(orm_module.BaseDoc):
    """
    微信服务器access_token对象,因为一天的请求access_token的次数有限,所以一旦获取了access_token后,
    需要自行保存在数据库中.
    """
    _table_name = "access_token_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['token'] = str
    type_dict['expires'] = int
    type_dict['time'] = datetime.datetime

    @classmethod
    def get_token(cls) -> (str, None):
        """
        从本机获取一个access_token字符串. 并注意过期时间.
        这是应用程序获取access_token的主要方法.
        :return:
        """
        res = None
        f = dict()
        s = {"time": -1}
        one = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
        flag = False
        if one is None:
            flag = True
        else:
            """检查access_token是否过期"""
            generate_time = one['time']
            expires = one['expires']
            token = one['token']
            now = datetime.datetime.now()
            delta = (now - generate_time).total_seconds()
            timeout = expires - delta
            if timeout <= 0:
                """超期了"""
                flag = True
            elif 0 <= timeout <= 300:
                """可以开始申请了"""
                flag = True
                res = token
            else:
                res = token
        if flag:
            """从互联网查询"""
            resp = cls.get_token_from_api()
            mes = resp['message']
            if mes != "success":
                """从互联网查询失败"""
                title = "查询access_token失败,错误原因:{}, {}".format(mes, datetime.datetime.now())
                send_mail(title=title)
            else:
                data = resp['data']
                res = data['token']
        return res

    @classmethod
    def get_token_from_api(cls) -> dict:
        """
        从微信服务器获取一个access_token对象.应用程序不应该直接调用本方法.而是使用cls.get_token方法来获取access_token.
        :return: dict
        """
        res = {"message": "success"}
        u = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(app_id,
                                                                                                             app_secret)
        r = requests.get(u)
        if r.status_code == 200:
            resp = r.json()
            error_code = resp.get("errcode")  # 如果返回值是一个int类型,那就代表有错,否则这个值不存在(None)
            if error_code is not None:
                error_reason = resp['errmsg']
                res['message'] = error_reason
            else:
                token = resp['access_token']
                expires = resp['expires_in']
                data = dict()
                data['time'] = datetime.datetime.now()
                data['token'] = token
                data['expires'] = expires
                cls.insert_one(**data)
                res['data'] = data
        else:
            res['message'] = "服务器返回错误的状态:{}".format(r.status_code)
        return res


def get_templates() -> list:
    """
    获取全部的模板信息
    :return:
    """
    u = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token={}".\
        format(AccessToken.get_token())
    r = requests.get(u)
    status = r.status_code
    if status != 200:
        ms = "获取模板信息时,服务器返回了错误的状态码:{}, time:{}".format(status, datetime.datetime.now())
        send_mail(title=ms)
        raise ValueError(ms)
    else:
        data = r.json()
        data


def send_template_message():
    pass


if __name__ == "__main__":
    get_templates()
    pass
