# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from mail_module import send_mail
import datetime
import json
import requests
import hashlib
from uuid import uuid4
from log_module import get_logger


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
app_id = "wx50cbcc5725601880"
app_secret = "1aa28cda9bbb187acb9e1f7464d2b15a"
host_name = "http://temp.safego.org"


"""和微信服务器相关的功能"""


class JSAPITicket(mongo_db.BaseDoc):
    """
    微信jsapi_ticket对象,因为一天的请求jsapi_ticket的次数有限,所以一旦获取了jsapi_ticket后,
    需要自行保存在数据库中.
    """
    _table_name = "js_api_ticket"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['ticket'] = str
    type_dict['expires'] = int
    type_dict['time'] = datetime.datetime

    @classmethod
    def get_ticket(cls) -> (str, None):
        """
        从本机获取一个jsapi_ticket. 并注意过期时间.
        这是应用程序获取jsapi_ticket的主要方法.
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
            token = one['ticket']
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
            resp = cls.get_ticket_from_api()
            mes = resp['message']
            if mes != "success":
                """从互联网查询失败"""
                title = "查询access_token失败,错误原因:{}, {}".format(mes, datetime.datetime.now())
                send_mail(title=title)
            else:
                data = resp['data']
                res = data['ticket']
        return res

    @classmethod
    def get_ticket_from_api(cls) -> dict:
        """
        从微信服务器获取一个jsapi_ticket对象.应用程序不应该直接调用本方法.而是使用cls.get_ticket方法来获取jsapi_ticket.
        注意,获取jsapi_ticket需要用到服务器的基础access_token,也就是AccessToken
        :return: dict
        """
        res = {"message": "success"}
        u = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}" \
            "&type=jsapi".format(AccessToken.get_token())
        r = requests.get(u)
        if r.status_code == 200:
            resp = r.json()
            error_code = resp.get("errcode")  # 如果返回值是一个int类型,那就代表有错,否则这个值不存在(None)
            if error_code != 0:
                error_reason = resp['errmsg']
                res['message'] = error_reason
            else:
                ticket = resp['ticket']
                expires = resp['expires_in']
                data = dict()
                data['time'] = datetime.datetime.now()
                data['ticket'] = ticket
                data['expires'] = expires
                cls.insert_one(**data)
                res['data'] = data
        else:
            res['message'] = "服务器返回错误的状态:{}".format(r.status_code)
        return res

    @classmethod
    def get_signature(cls, cur_url: str) -> dict:
        """
        计算并返回一个签名对象
        签名算法验证页面 https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=jsapisign
        :param cur_url:当前网页的URL，不包含#及其后面部分
        :return:
        """
        noncestr = uuid4().hex
        jsapi_ticket = cls.get_ticket()
        timestamp = int(datetime.datetime.now().timestamp())
        timestamp_str = str(int(datetime.datetime.now().timestamp()))
        l = [("noncestr", noncestr), ("jsapi_ticket", jsapi_ticket), ("timestamp", timestamp_str), ("url", cur_url)]
        l.sort(key=lambda obj: obj[0], reverse=False)
        s = "&".join(["=".join(x) for x in l])

        signature = hashlib.sha1(s.encode()).hexdigest()
        return {"signature": signature, "timestamp": timestamp, "noncestr": noncestr}


class AccessToken(mongo_db.BaseDoc):
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


class PageAuthorization(mongo_db.BaseDoc):
    """
    页面的授权
    """
    _table_name = "page_authorization"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    """
    网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
    """
    type_dict['access_token'] = str
    type_dict['expires_in'] = int  # access_token接口调用凭证超时时间，单位（秒）
    type_dict['refresh_token'] = str  # 用户刷新access_token
    """
    用户唯一标识，
    请注意，在未关注公众号时，用户访问公众号的网页，
    也会产生一个用户和公众号唯一的OpenID
    """
    type_dict['open_id'] = str
    type_dict['scope'] = str    # 用户授权的作用域，使用逗号（,）分隔

    @classmethod
    def _get_by_code(cls, code: str) -> dict:
        """
        根据基础授权的code，获取用户的页面授权信息。 底层函数
        :param code: 基础授权的code
        :return: 
        """
        u = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code". \
            format(app_id, app_secret, code)
        resp = requests.get(u)
        status = resp.status_code
        if status != 200:
            ms = "服务器没有正确的响应，错误码：{}".format(status)
            raise ValueError(ms)
        else:
            data = resp.json()
            if "openid" in data:
                data['time'] = datetime.datetime.now()
                return data
            else:
                data['code'] = code
                ms = "{}".format(data)
                raise ValueError(ms)

    @classmethod
    def _get_user_info_by_access_token(cls, access_token: str, openid: str) -> dict:
        """
        根据用户openid获取用户的信息,  底层函数
        :param access_token:
        :param openid:
        :return:
        返回的字段说明:
        openid   	用户的唯一标识
        nickname	用户昵称
        sex	        用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
        province	用户个人资料填写的省份
        city	    普通用户个人资料填写的城市
        country	    国家，如中国为CN
        headimgurl	用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），
                    用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
        privilege	用户特权信息，json 数组，如微信沃卡用户为（chinaunicom）
        unionid	    只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。
        """
        res = {"message": "未知错误"}
        """这个链接是配合基础access_token使用的"""
        u = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN". \
            format(AccessToken.get_token(), openid)
        """这个链接是配合页面access_token使用的"""
        # u = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN". \
        #     format(access_token, openid)
        resp = requests.get(u)
        status = resp.status_code
        if status != 200:
            ms = "服务器返回了异常的状态码:{}".format(status)
            raise ValueError(ms)
        else:
            # data = resp.json()
            """json返回的内容,requests不好推断编码,所以使用了原始的返回体,自己解码"""
            content = resp.content
            data = json.loads(s=content.decode(), encoding="utf-8")
            logger.info(msg=str(data))
            return data

    @classmethod
    def _refresh_access_token(cls, refresh_token: str) -> dict:
        """
        当access_token过期时,调用此方法刷新access_token
        :param refresh_token: 用于刷新的凭证
        :return:
        返回的例子:
        {
        "access_token":"ACCESS_TOKEN",
        "expires_in":7200,
        "refresh_token":"REFRESH_TOKEN",
        "openid":"OPENID",
        "scope":"SCOPE"
        }
        返回的字段说明:
        access_token	网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
        expires_in	access_token接口调用凭证超时时间，单位（秒）
        refresh_token	用户刷新access_token
        openid	用户唯一标识
        scope	用户授权的作用域，使用逗号（,）分隔
        """
        u = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={}&grant_type=refresh_token&refresh_token={}". \
            format(app_id, refresh_token)
        resp = requests.get(u)
        status = resp.status_code
        if status != 200:
            ms = "服务器返回了异常的状态码:{}".format(status)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            data = resp.json()
            if "access_token" in data:
                return data
            else:
                ms = "服务器返回了错误的消息：{}".format(data)
                logger.exception(ms)
                raise ValueError(ms)

    @classmethod
    def get_user_info(cls, code: str = None, code_dict: dict = None) -> (dict, None):
        """
         根据基础授权的code，获取用户的信息,可以看作是
         cls._get_by_code,cls._get_user_info_by_access_token
         和cls._refresh_access_token的组合函数。
         推荐使用此函数获取用户信息。
        :param code: 基础授权的code
        :param code_dict: cls._get_by_code函数返回的字典。
        :return: 用户信息字典，如果refresh_token都失效了，返回None
        """
        res = None
        """优先使用code_dict参数，检查access_token是否过期，如果过期刷新，刷新失败放弃。返回None"""
        if isinstance(code_dict, dict) and "time" in code_dict and "refresh_token" in code_dict:
            """检查有没有过期？"""
            t = code_dict['time']
            """检查access_token是否过期"""
            if isinstance(t, datetime.datetime):
                pass
            else:
                t = mongo_db.get_datetime_from_str(t)
            if not isinstance(t, datetime.datetime):
                ms = "错误的时间格式:{}".format(t)
                raise ValueError(ms)
            else:
                now = datetime.datetime.now()
                if (now - t).total_seconds() >= 7200:
                    """access_token过期了"""
                    refresh_token = code_dict['refresh_token']
                    code_dict = cls._refresh_access_token(refresh_token=refresh_token)
                    if "refresh_token" not in code_dict:
                        """
                        refresh_token 失效,放弃，返回None
                        """
                        return res
                    else:
                        """刷新access_token成功，进入获取unionid环节"""
                        pass
                else:
                    """access_token没有过期，进入获取unionid环节"""
                    pass
        else:
            code_dict = cls._get_by_code(code=code)
            if "refresh_token" in code_dict:
                """进入获取unionid环节"""
                pass
            else:
                """codes失效"""
                ms = "无效的code：{}".format(code)
                logger.exception(ms)
                raise ValueError(ms)
                return res
        """获取unionid环节"""
        a_t = code_dict['access_token']
        o_i = code_dict['openid']
        data = cls._get_user_info_by_access_token(access_token=a_t, openid=o_i)
        code_dict.update(data)
        return code_dict


def generator_relate_img(user_id: str) -> str:
    """
    生成一个永久的,关联中间商的二维码图片.
    请自行检查原来的图片是否有效
    :param user_id: 中间商/销售/黄牛的id.
    :return:
    """
    user_id = user_id if isinstance(user_id, str) else str(user_id)
    scene_str = "relate_{}".format(user_id)
    param = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": scene_str}}}
    param = json.dumps(param)
    u = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={}".format(AccessToken.get_token())
    r = requests.post(u, data=param)
    status = r.status_code
    if status != 200:
        ms = "服务器没有正确响应,错误码:{}".format(status)
        logger.exception(ms)
        raise ValueError(ms)
    else:
        resp = r.json()
        error = resp.get("errmsg", "")
        ticket = resp.get("ticket", "")
        if ticket == "":
            ms = "获取关联二维码失败,错误原因:{}".format(error)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            img_u = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(ticket)
            return img_u


def download_image(u_id: (str, ObjectId), table_name: str, media_id: str) -> dict:
    """
    从微信服务器下载素材/图片
    :param u_id:   用户id
    :param table_name: 图片对应的表名
    :param media_id:    媒体id
    :return: {"message":"success", "_id": _id, "url": url}
    """
    tables = ['base_file', 'head_image', 'id_image', 'honor_image', 'vehicle_image',
              'driving_license_image', 'rtqc_image']
    mes = {"message": "success"}
    if table_name not in tables:
        ms = "错误的表名: {}".format(table_name)
        logger.exception(msg=ms)
        mes['message'] = ms
        print(ms)
    else:
        pass
    return mes


def get_message_templates() -> list:
    """
    获取全部的消息模板信息
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


def get_materials(m_type: str = 'image', offset: int = 0, count: int = 20) -> dict:
    """
    获取永久素材的列表，也包含公众号在公众平台官网素材管理模块中新建的图文消息、语音、视频等素材
    :param m_type:   素材类型 图片（image）、视频（video）、语音 （voice）、图文（news）
    :param offset:   从全部素材的该偏移位置开始返回，0表示从第一个素材 返回
    :param count:   返回素材的数量，取值在1到20之间
    获取素材列表
    :return:
    """
    tk = AccessToken.get_token()
    u = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={}".format(tk)
    args = {"type": m_type, "offset": offset, "count": count}
    r = requests.post(u, data=json.dumps(args))
    status = r.status_code
    if status != 200:
        ms = "获取模板信息时,服务器返回了错误的状态码:{}, time:{}".format(status, datetime.datetime.now())
        send_mail(title=ms)
        raise ValueError(ms)
    else:
        data = r.json()
        return data


if __name__ == "__main__":
    """获取jsapi_ticket"""
    # ticket = JSAPITicket.get_ticket()
    # JSAPITicket.get_signature("http://temp.safego.org/wx/")
    """测试获取关联二维码"""
    # print(generator_relate_img("5b56bdba7b3128ec21daa4c7"))
    # u2 = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token={}".format(AccessToken.get_token())
    # r = requests.get(u2)
    # print(r.json())
    """获取素材列表"""
    get_materials()
    pass
