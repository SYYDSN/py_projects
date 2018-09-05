# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from collections import OrderedDict
import xmltodict
import dicttoxml
import json
from log_module import get_logger
from module.server_api import generator_relate_img
from module.driver_module import *
from xml.parsers.expat import ExpatError
from mail_module import send_mail
from pdb import set_trace


ObjectId = mongo_db.ObjectId
logger = get_logger()
my_id = "gh_134657758ddf"  # 卡佑公众号id


class XMLMessage:
    """
    一个生消息xml的类
    """
    type_map = {
        "news": "Articles",    # 图文消息
        "music": "Music",      # 音乐消息
        "video": "Video",      # 视频消息
        "voice": "Voice",      # 语音消息
        "image": "Image",      # 图片消息
        "text": "Content"      # 文本消息
    }

    def __init__(self, to_user: str):
        """
        :param to_user: 目标用户的openid
        :param mes_type: 消息类型
        """
        xml = OrderedDict()
        xml['ToUserName'] = to_user
        xml['FromUserName'] = my_id
        xml['CreateTime'] = int(datetime.datetime.now().timestamp())
        self.xml = xml

    def add_text(self, content: str = ""):
        """添加文本消息"""
        xml = self.xml
        xml['MsgType'] = 'text'
        xml['Content'] = content
        return xml

    def add_news(self, item_list: list = None):
        """
        添加图文消息
        :param item_list: 图文对象的字典的数组.第一个图文对象是大图.图文对象的格式如下:
        item = {
                    "Title": "标题",
                    "Description": "文本描述",
                    "PicUrl": "图片素材的地址,支持JPG、PNG格式，较好的效果为大图360*200，小图200*200",
                    "Url": "点击图文消息跳转链接"
                }
        :return:
        """
        xml = self.xml
        xml['MsgType'] = 'news'
        xml['ArticleCount'] = len(item_list)
        r = list()
        if item_list is None:
            xml['ArticleCount'] = 0
        else:
            for x in item_list:
                temp = OrderedDict()
                temp['Title'] = x['title']
                temp['Description'] = x['desc']
                temp['PicUrl'] = x['img_url']
                temp['Url'] = x['url']
                r.append(temp)
        xml['Articles'] = r
        return xml

    @classmethod
    def produce(cls, to_user: str, msg_type: str, data: object, to_xml: bool = True) -> (str, dict):
        """
        生成一个用于回复的xml消息
        :param to_user: 用户的openid
        :param msg_type: 消息类型,仅限于type_map.keys()中的类型.
        :param data:  数据,不同类型的消息,格式要求不同.详见具体的底层函数
        :param to_xml: 是否转换为xml格式?, 否则返回的是以xml为根节点的OrderedDict
        :return:
        """
        func_name = "add_{}".format(msg_type)
        obj = cls(to_user=to_user)
        if hasattr(obj, func_name):
            res = obj.__getattribute__(func_name)(data)
            r = OrderedDict()
            r['xml'] = res

            if to_xml:
                r = dicttoxml.dicttoxml(obj=r, root=False, attr_type=False, cdata=True)
                if msg_type == "news" and len(data) > 1:
                    """满足图文消息恢复格式不对int类型包裹cdata的要求"""
                    l = len(data)
                    b1 = "<ArticleCount><![CDATA[{}]]></ArticleCount>".format(l)
                    b2 = "<ArticleCount>{}</ArticleCount>".format(l)
                    r.replace(b1.encode(), b2.encode())
                return r
            else:
                return r
        else:
            ms = "错误的消息类型: {}".format(msg_type)
            raise ValueError(ms)


class EventHandler:
    """
    当微信服务器推送(事件/文本/图片/扫码)信息到服务器,请调用此函数进行回复
    """
    @classmethod
    def listen(cls, info: dict) -> bytes:
        """
        监听微信推送的事件消息(比如关注公众号, 扫码等).
        检查info字典中的消息类型,如果有对应的处理函数就进行相应的处理
        下面是一些xml信息的示范
        1. 取消关注
        {
            "ToUserName" : "gh_134657758ddf",
            "FromUserName" : "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
            "CreateTime" : "1535603763",
            "MsgType" : "event",
            "Event" : "unsubscribe",
            "EventKey" : null,
            "create_time" : ISODate("2018-08-30T12:36:03.000Z")
        }
        2. 关注公众号
        {
            "ToUserName" : "gh_134657758ddf",
            "FromUserName" : "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
            "CreateTime" : "1535603863",
            "MsgType" : "event",
            "Event" : "subscribe",
            "EventKey" : null,
            "create_time" : ISODate("2018-08-30T12:37:43.000Z")
        }
        3. 扫描委托求职二维码
        {
            "ToUserName" : "gh_134657758ddf",
            "FromUserName" : "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
            "CreateTime" : "1535603967",
            "MsgType" : "event",
            "Event" : "SCAN",
            "EventKey" : "relate_5b56c0f87b3128ec21daa693",
            "Ticket" : "gQEd8DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyZWhPaDBTNG5jaGwxMDAwMGcwN2IAAgRq22tbAwQAAAAA",
            "create_time" : ISODate("2018-08-30T12:39:27.000Z")
        }
        4. 用户公众号发文本消息
        {
            "ToUserName" : "gh_134657758ddf",
            "FromUserName" : "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
            "CreateTime" : "1535604037",
            "MsgType" : "text",
            "Content" : "你好",
            "MsgId" : "6595369118955706758",
            "create_time" : ISODate("2018-08-30T12:40:37.000Z")
        }
        5. 用户公众号发图片
        {
            "ToUserName" : "gh_134657758ddf",
            "FromUserName" : "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
            "CreateTime" : "1535604081",
            "MsgType" : "image",
            "PicUrl" : "http://mmbiz.qpic.cn/mmbiz_jpg/tsJ9TEnc4GLT0fthC4Irho1XpSQiaiauVKLvS3V5tmdiaQJGmibYUFN8UMiaJF6m7r7MFYqHUK8iaqBynUL2TuvAaicLg/0",
            "MsgId" : "6595369307934267784",
            "MediaId" : "rcnvWQheiwfu3de7ThXV7ksvV_KK5FGKuiO1kNJ1_c4Zh3vQ59Qc4ottyvH1ozYM",
            "create_time" : ISODate("2018-08-30T12:41:21.000Z")
        }
        :param info: 消息字典,就是WebChatMessage的实例的doc
        :return:
        """
        res = b''
        if "xml" in info:
            now = datetime.datetime.now()
            xml = info['xml']
            msg_type = xml['MsgType'].lower()
            openid = xml['FromUserName']
            if msg_type == "event":
                """事件"""
                event = xml['Event'].lower()
                if event == "subscribe":
                    """关注公众号"""
                    f = {"openid": openid}
                    u = {"$set": {"subscribe": 1}}
                    WXUser.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
                    data1 = [
                        {
                            "title": "卡佑欢迎你",
                            "img_url": "http://mmbiz.qpic.cn/mmbiz_jpg/KCRpHfdSvS4f5tNDutYeOQGm727dzQyWps0zM6WuRHm"
                                       "LrvwsxibtvxcZEAtToiaUEibHgRaj28o8PAp7edhUcKMNw/0?wx_fmt=jpeg",
                            "desc": "大企业，工作有保障，专业平台 合法营运 收入稳定 合作共赢 福利保障 五险一金 安全保障 专人服务",
                            "url": "http://temp.safego.org/wx/html/about.html"
                        },
                        {
                            "title": "找工作,用卡佑!欢迎新老司机加入, 好工作不等人.现在就去填写简历.",
                            "img_url": "http://mmbiz.qpic.cn/mmbiz_jpg/KCRpHfdSvS4f5tNDutYeOQGm727dzQyWS62gcmK44lRRoJ"
                                       "dv9SkicUl2HZJKictiaV7tdWCUZYMkDcr9pFJAC02vA/0?wx_fmt=jpeg",
                            "desc": "收入稳定, 福利齐全, 欢迎老司机加入, 点此填写简历",
                            "url": "http://temp.safego.org/wx/html/register.html"
                        }
                    ]
                    data = [{
                            "title": "卡佑欢迎你",
                            "img_url": "http://mmbiz.qpic.cn/mmbiz_jpg/KCRpHfdSvS4f5tNDutYeOQGm727dzQyWps0zM6WuRHm"
                                       "LrvwsxibtvxcZEAtToiaUEibHgRaj28o8PAp7edhUcKMNw/0?wx_fmt=jpeg",
                            "desc": "大企业，工作有保障，专业平台 合法营运 收入稳定 合作共赢 福利保障 五险一金 安全保障 专人服务",
                            "url": "http://temp.safego.org/wx/html/register.html"
                        }]

                    res = XMLMessage.produce(to_user=openid, msg_type="news", data=data1)
                elif event == "unsubscribe":
                    """取消关注"""
                    ms = "用户: {} 取消关注".format(openid)
                    logger.info(ms)
                    print(ms)
                    f = {"openid": openid}
                    u = {"$set": {"subscribe": 0}}
                    WXUser.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                elif event == "scan":
                    """扫码"""
                    event_key = xml['EventKey']
                    print("event_key is {}".format(event_key))
                    if event_key.startswith("relate_"):
                        """扫描委托求职二维码"""
                        f = {"openid": openid}
                        user = WXUser.find_one_plus(filter_dict=f, instance=False)
                        data = ''
                        if user is None:
                            data = "尊敬的用户,请先关注卡佑公众号再进行操作"
                        else:
                            phone = user.get("phone", "")
                            resume_id = user.get("resume_id", "")
                            print("phone is {}".format(phone))
                            print("resume_id is {}".format(resume_id))
                            if not isinstance(resume_id, ObjectId):
                                data = "卡佑助手提醒: 你还没填写自己的简历,请点击<a href='http://temp.safego.org/wx/html/register_info." \
                                       "html'>这里填写简历</a>"
                            elif len(phone) != 11:
                                data = "卡佑助手提醒: 你还没绑定手机,请点击<a href='http://temp.safego.org/wx/html/register." \
                                       "html'>这里填写进行绑定</a>"
                            else:
                                s_id = event_key.split("relate_")[-1]
                                sales = WXUser.find_by_id(o_id=s_id, to_dict=True)
                                if sales is None:
                                    pass
                                else:
                                    s_name = sales['name'] if sales.get("name") else sales.get("nick_name", "")
                                    data = "卡佑助手提醒: {}已接受你的求职委托.".format(s_name)
                        if data == "":
                            pass
                        else:
                            res = XMLMessage.produce(to_user=openid, msg_type="text", data=data)
                    else:
                        title = "{} 未意料的扫码事件消息:{}.{}".format(now, msg_type, event_key)
                        content = "{}".format(str(info))
                        send_mail(title=title, content=content)
                elif event == "view":
                    """点击菜单"""
                else:
                    title = "{} 未意料的事件消息:{}.{}".format(now, msg_type, event)
                    content = "{}".format(str(info))
                    send_mail(title=title, content=content)
            elif msg_type == "text":
                """文本消息"""
                s = xml['Content']
                data = "测试文本消息, 你输入的内容是: '{}'".format(s)
                res = XMLMessage.produce(to_user=openid, msg_type="text", data=data)
            elif msg_type == "image":
                """图片消息"""
            else:
                title = "{} 未意料的类型:{}".format(now, msg_type)
                content = "{}".format(str(info))
                send_mail(title=title, content=content)
        else:
            pass
        return res

    @classmethod
    def welcome(cls, openid: str):
        """
        回复消息之欢迎信息,图文消息的示范:
        <xml>
            <ToUserName>< ![CDATA[toUser] ]></ToUserName>
            <FromUserName>< ![CDATA[fromUser] ]></FromUserName>
            <CreateTime>12345678</CreateTime>
            <MsgType>< ![CDATA[news] ]></MsgType>
            <ArticleCount>2</ArticleCount>
            <Articles>                                                      # 文章列表
                <item>
                    <Title>< ![CDATA[title1] ]></Title>
                    <Description>< ![CDATA[description1] ]></Description>
                    <PicUrl>< ![CDATA[picurl] ]></PicUrl>
                    <Url>< ![CDATA[url] ]></Url>
                </item>
                <item>
                    <Title>< ![CDATA[title] ]></Title>
                    <Description>< ![CDATA[description] ]></Description>
                    <PicUrl>< ![CDATA[picurl] ]></PicUrl>
                    <Url>< ![CDATA[url] ]></Url>
                </item>
            </Articles><
        </xml>
        :param openid:
        :return:
        """


class RawWebChatMessage(mongo_db.BaseDoc):
    """
    原始微信的记录
    """
    _table_name = "raw_webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class WebChatMessage(mongo_db.BaseDoc):
    """
    微信的记录,和RawWebChatMessage不同,这个定义了字段类型
    """
    _table_name = "webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['ip'] = str
    type_dict['url'] = str
    type_dict['method'] = str
    type_dict['headers'] = dict
    type_dict['args'] = dict
    type_dict['form'] = dict
    type_dict['xml'] = OrderedDict
    type_dict['time'] = datetime.datetime

    @classmethod
    def instance_from_request(cls, request) -> dict:
        """
        从flask的request获取实例
        :param request:
        :return:
        """
        headers = {k: v for k, v in request.headers.items()}
        args = {k: v for k, v in request.args.items()}
        form = {k: v for k, v in request.form.items()}
        json_data = None if request.json is None else {k: v for k, v in request.headers.items()}
        try:
            xml_data = request.data.decode(encoding="utf-8")
        except Exception as e:
            logger.exception(msg=e)
            xml_data = ''
        finally:
            pass
        try:
            ip = request.headers["X-Forwarded-For"].split(":")[0]
        except KeyError as e:
            print(e)
            ip = request.remote_addr  # 注意：tornado是 request.remote_ip   flask是 req.remote_addr
        if ip.find(",") != -1:
            """处理微信登录时转发的双ip"""
            ip = ip.split(",")[0]
        else:
            pass
        now = datetime.datetime.now()
        data = {
            "ip": ip,
            "url": request.url,
            "method": request.method.lower(),
            "headers": headers,
            "args": args,
            "form": form,
            "json": json_data,
            "xml": xml_data,
            "time": now
        }
        return cls.doc_from_raw(raw=data)

    @classmethod
    def docs_from_raw(cls, filter_dict: dict = None, multi: bool = False) ->(dict, list):
        """
        从RawWebChatMessage的表中,按照条件获取记录,并转换成WebChatMessage的doc,
        主要的工作就是把xml字段从str转换为OrderedDict
        :param filter_dict:
        :param multi: 返回一个还是多个文档?
        :return:
        """
        f = dict() if filter_dict is None else filter_dict
        ses = mongo_db.get_conn(table_name="raw_webchat_message")
        res = ses.find(filter=f, limit=(0 if multi else 1))
        result = list()
        for one in res:
            xml_str = one.get("xml", "")
            if xml_str == "":
                pass
            else:
                error = None
                try:
                    xml = xmltodict.parse(xml_input=xml_str, encoding="utf-8")
                except ExpatError as e:
                    logger.exception(e)
                    print(e)
                    try:
                        xml = json.loads(xml_str)
                    except Exception as e2:
                        logger.exception(e2)
                        print(e2)
                        error = e2
                    finally:
                        pass
                finally:
                    if error is None:
                        print(xml)
                        data = xml.get('xml')
                        if data is None:
                            pass
                        else:
                            if 'CreateTime' in data:
                                create_time = datetime.datetime.fromtimestamp(float(data['CreateTime']))
                                data['create_time'] = create_time
                            else:
                                pass
                            xml = data
                        one['xml'] = xml
                    else:
                        pass
            result.append(one)
        return result

    @classmethod
    def doc_from_raw(cls, raw: dict) -> dict:
        """
        从RawWebChatMessage的doc从转换对象
        :param raw:
        :return:
        """
        one = raw.copy()
        xml_str = one.get("xml", "")
        if xml_str == "":
            pass
        else:
            error = None
            xml = OrderedDict()
            try:
                xml = xmltodict.parse(xml_input=xml_str, encoding="utf-8")
            except ExpatError as e:
                logger.exception(e)
                print(e)
                try:
                    xml = json.loads(xml_str)
                except Exception as e2:
                    logger.exception(e2)
                    print(e2)
                    error = e2
                finally:
                    pass
            finally:
                if error is None:
                    data = xml.get('xml')
                    if data is None:
                        pass
                    else:
                        if 'CreateTime' in data:
                            create_time = datetime.datetime.fromtimestamp(float(data['CreateTime']))
                            data['create_time'] = create_time
                        else:
                            pass
                        xml = data
                    one['xml'] = xml
                else:
                    pass
        return one


class BusinessLicenseImage(mongo_db.BaseFile):
    """
    保存营业执照的图片
    """
    _table_name = "business_license_image"


class PersonLicenseImage(mongo_db.BaseFile):
    """
    手持身份证的图片
    """
    _table_name = "person_license_image"


class WXUser(mongo_db.BaseDoc):
    """从微信接口获取的用户身份信息,目前的用户是测试"""
    _table_name = "wx_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['email'] = str
    type_dict['address'] = str  # 地址
    type_dict['nick_name'] = str
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像图片地址
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
    type_dict['checked'] = int  # 是否已通过兼职/销售/中介的审核? 0/不存在忽略, 1是申请中. 2是申请通过, -1是驳回.
    type_dict['reject_reason'] = str  # 申请驳回原因,只有在checked字段是-1状态,本字段才有效
    type_dict['authenticity'] = int  # 中介商/黄牛/销售 的真实性确认. 在审核通过后这个字段为1,否则为0或者不存在
    type_dict['relate_image'] = str  # 中介商名字/销售二维码图片地址,这个图片保存在微信服务器上.
    type_dict['name'] = str  # 中介商名字/销售真实姓名.用于展示在二维码上
    type_dict['contacts'] = str  # 中介公司联系人,如果是黄牛/销售,那么这里可以和注册用户的real_name是同一人
    type_dict['contacts_num'] = str  # 中介公司联系电话,如果是黄牛/销售,那么这里可以和注册用户的phone一致
    type_dict['contacts_email'] = str  # 中介公司/黄牛/销售联系邮箱,这个是专门用来发送结算信息的
    type_dict['identity_code'] = str  # 中介商执照号码/销售真实身份证id.用于部分展示在二维码上
    type_dict['blank_name'] = str  # 开户行名称.
    type_dict['blank_account'] = str  # 银行账户卡号.
    type_dict['person_id_code'] = str  # 身份证号码, 兼职专用属性
    type_dict['person_license_image_url'] = str  # 手持身份证照片的地址, 兼职专用属性
    type_dict['person_license_image'] = ObjectId  # 手持身份证照片的id, 指向PersonLicenseImage._id,兼职专用属性
    type_dict['business_license_image_url'] = str  # 营业执照照片的地址,
    type_dict['business_license_image'] = ObjectId  # 营业执照照片的id, 指向BusinessLicenseImage._id

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
        改变一个用户的角色,
        如果是从普通用户变成销售/黄牛/中介.除了修改role之外,还需要使用server_api.generator_relate_img生成一张二维码,
        销售/黄牛/中介变成普通用户,只需要修改role即可.
        注意,使用server_api.generator_relate_img生成二维码的方法

        :param user_id:
        :param role:
        :return:
        """
        user = cls.find_by_id(o_id=user_id, to_dict=True)
        if isinstance(user, dict):
            pass
        else:
            ms = "错误的user_id:{}".format(user_id)
            logger.exception(ms)
            raise ValueError(ms)
        user_id = user['_id']
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
        s = {"role": role}
        relate_img = user.get("relate_image", "")
        if isinstance(relate_img, str) and len(relate_img) > 40:
            pass
        else:
            """生成一张关联二维码并保存url"""
            relate_img = generator_relate_img(user_id=user_id)
            s['relate_img'] = relate_img
        u = {"$set": s}
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
            if (isinstance(u_id, str) and len(u_id) == 24) or isinstance(u_id, ObjectId):
                user = cls.find_by_id(o_id=u_id, to_dict=True)
            else:
                user = cls.find_one_plus(filter_dict={"openid": open_id}, instance=False)
            sale = cls.find_by_id(o_id=s_id, to_dict=True)
            if isinstance(user, dict) and isinstance(sale, dict):
                role = sale.get("role", 0)
                print("sale's role is {}".format(role))
                if len(user.get("phone", "")) != 11 or not isinstance(user.get("resume_id"), ObjectId):
                    print("用户没有绑定手机或没有简历信息: {}".format(user))
                    return False
                elif isinstance(role, int) and role > 0:
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
                    print(ms)
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
        print("u_id: {}".format(u_id))
        print("resume_args: {}".format(resume_args))
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

        4. 添加教育经历  add_education     DriverResume.add_education
        5. 修改教育经历  update_education  DriverResume.update_education
        6. 删除教育经历  delete_education  DriverResume.delete_education

        7. 添加荣誉  add_honor     DriverResume.add_honor
        8. 修改荣誉  update_honor  DriverResume.update_honor
        9. 删除荣誉  delete_honor  DriverResume.delete_honor

        10. 添加车辆  add_vehicle     DriverResume.add_vehicle
        11. 修改车辆  update_vehicle  DriverResume.update_vehicle
        12. 删除车辆  delete_vehicle  DriverResume.delete_vehicle


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
                elif opt == "add_honor":
                    """添加荣誉"""
                    _id = DriverResume.add_honor(resume_id=resume_id, init_args=arg_dict)
                    mes['_id'] = str(_id) if can_json else _id
                elif opt == "update_honor":
                    """修改荣誉"""
                    h_id = arg_dict.pop("h_id", None)
                    if h_id is None:
                        mes['message'] = "缺少必要的参数:h_id"
                    else:
                        _id = DriverResume.update_honor(resume_id=resume_id, h_id=h_id, update_args=arg_dict)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "delete_honor":
                    """删除荣誉"""
                    h_id = arg_dict.pop("h_id", None)
                    if h_id is None:
                        mes['message'] = "缺少必要的参数:h_id"
                    else:
                        _id = DriverResume.delete_honor(resume_id=resume_id, h_id=h_id)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "add_vehicle":
                    """添加车辆"""
                    _id = DriverResume.add_vehicle(resume_id=resume_id, init_args=arg_dict)
                    mes['_id'] = str(_id) if can_json else _id
                elif opt == "update_vehicle":
                    """修改车辆"""
                    v_id = arg_dict.pop("v_id", None)
                    if v_id is None:
                        mes['message'] = "缺少必要的参数:v_id"
                    else:
                        _id = DriverResume.update_vehicle(resume_id=resume_id, v_id=v_id, update_args=arg_dict)
                        mes['_id'] = str(_id) if can_json else _id
                elif opt == "delete_vehicle":
                    """删除车辆"""
                    v_id = arg_dict.pop("v_id", None)
                    if v_id is None:
                        mes['message'] = "缺少必要的参数:v_id"
                    else:
                        _id = DriverResume.delete_vehicle(resume_id=resume_id, v_id=v_id)
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

    @classmethod
    def page_resource(cls, u_id: (str, ObjectId), filter_dict: dict = None, projection: list = None, page_size: int = 10,
                      ruler: int = 5, page_index: int = 1) -> dict:
        """
        按月查询,分页显示中介下面的关联的用户资源.
        :param u_id: 中介id
        :param filter_dict: 查询条件字典 默认关联时间倒序
        :param projection:  投影数组,决定输出哪些字段?
        :param page_size:   一页有多少条记录?
        :param ruler:       翻页器最多显示几个页码？
        :param page_index:  当前页码
        :return: 字典对象
        查询结果示范:
        {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        """
        res = dict()
        user = cls.find_by_id(o_id=u_id, to_dict=True)
        if isinstance(user, dict):
            user_id = user['_id']
            f = {"relate_id": user_id}
            if isinstance(filter_dict, dict):
                f.update(filter_dict)
            s = {"relate_time": -1}
            if projection is None:
                p = ["_id", 'head_img_url', "nick_name", "relate_time"]
            else:
                p = projection
            args = {
                "filter_dict": f, "sort_dict": s, "projection": p,
                "page_size": page_size, "ruler": ruler,
                "page_index": page_index
            }
            res = cls.query_by_page(**args)
        else:
            ms = "用户id不存在:{}".format(u_id)
            logger.exception(msg=ms)
            print(ms)
        return res





if __name__ == "__main__":
    """变更用户角色,从一般用户变更为中介"""
    # WXUser.change_role(user_id=ObjectId("5b56c0f87b3128ec21daa693"), role=2)
    """按月查询,分页显示中介下面的关联的用户资源"""
    # WXUser.page_resource(u_id=ObjectId("5b56c0f87b3128ec21daa693"))
    """测试监听"""
    # d = {
    #     'url': 'http://temp.safego.org/message?signature=7adcd3a3f9073c4b0eca36a4d36a4eb342418198&times'
    #             'tamp=1535621448&nonce=873970012&openid=oBBcR1T5r6FCqOo2WNxMqPUqvK_I',
    #     'json': None,
    #     'xml': OrderedDict([('ToUserName', 'gh_134657758ddf'), ('FromUserName', 'oBBcR1T5r6FCqOo2WNxMqPUqvK_I'),
    #                         ('CreateTime', '1535621447'), ('MsgType', 'text'), ('Content', '感觉'),
    #                         ('MsgId', '6595443894336331761'),
    #                         ('create_time', datetime.datetime(2018, 8, 30, 17, 30, 47))]),
    #     'args': {'timestamp': '1535621448', 'signature': '7adcd3a3f9073c4b0eca36a4d36a4eb342418198',
    #              'nonce': '873970012', 'openid': 'oBBcR1T5r6FCqOo2WNxMqPUqvK_I'},
    #     'method': 'post',
    #     'headers': {'X-Forwarded-For': '140.207.54.80', 'Content-Length': '279',
    #                 'Content-Type': 'text/xml', 'Host': 'temp.safego.org',
    #                 'Accept': '*/*', 'Pragma': 'no-cache', 'Connection': 'close',
    #                 'X-Real-Ip': '140.207.54.80', 'User-Agent': 'Mozilla/4.0'},
    #     'ip': '140.207.54.80',
    #     'time': datetime.datetime(2018, 8, 30, 17, 30, 53, 335271),
    #     'form': {}
    # }
    # print(EventHandler.listen(info=d))
    """测试图文消息"""
    dd = [
        {
            "title": "卡佑欢迎你",
            "img_url": "http://mmbiz.qpic.cn/mmbiz_jpg/KCRpHfdSvS4f5tNDutYeOQGm727dzQyWps0zM6WuRHm"
                       "LrvwsxibtvxcZEAtToiaUEibHgRaj28o8PAp7edhUcKMNw/0?wx_fmt=jpeg",
            "desc": "大企业，工作有保障，专业平台 合法营运 收入稳定 合作共赢 福利保障 五险一金 安全保障 专人服务",
            "url": "http://temp.safego.org/wx/html/about.html"
        },
        {
            "title": "欢迎老司机加入, 点此填写简历",
            "img_url": "http://mmbiz.qpic.cn/mmbiz_jpg/KCRpHfdSvS4f5tNDutYeOQGm727dzQyWS62gcmK44lRRoJ"
                       "dv9SkicUl2HZJKictiaV7tdWCUZYMkDcr9pFJAC02vA/0?wx_fmt=jpeg",
            "desc": "收入稳定, 福利齐全, 欢迎老司机加入, 点此填写简历",
            "url": "http://temp.safego.org/wx/html/register.html"
        }
    ]
    XMLMessage.produce(to_user="aaa", msg_type="news", data=dd)
    pass
