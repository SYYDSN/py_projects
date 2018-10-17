#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import request
from flask import abort
from flask import render_template
import json
from bson.objectid import ObjectId
from tools_module import *
from module.event_module import PlatformEvent
from module.identity_validate import GlobalSignature
from module.item_module import RawRequestInfo
from module.document_tools import markdown_to_html
from mail_module import send_mail


"""接受mt4后台推送过来的信息2018-6-29"""


"""注册蓝图"""
mt4_blueprint = Blueprint("mt4_blueprint", __name__, url_prefix="/mt4", template_folder="templates/mt4")


"""用于站点部分的视图函数"""


def index_func() -> str:
    """
    首页的函数,hello world!
    :return:
    """
    return "hello world!, 1 am mt4 server."


def md_view():
    """md文档视图"""
    if request.method.lower() == "get":
        sid = get_arg(request, "sid", "")
        if sid == "bbb5fd48094942be80dbf0467be3d6f6":
            file_name = "platform_api.md"  # 交易平台文档
        elif sid == "bbb5fd48094942be80dbf0467be3d6f7":
            file_name = "quotations_api.md"  # 行情服务推送文档
        else:
            file_name = ""
        if file_name == "":
            return abort(404)
        else:
            content = markdown_to_html(file_name=file_name)
            return render_template("md.html", content=content)
    else:
        return abort(405)


def secret_func() -> str:
    """
    获取服务器端的数字签名和当前算法,node.js服务器用此两项信息来进行和保驾犬后台的加密通讯
    当前情况下.使用sid来换取signature  sid = "bbb5fd48094942be80dbf0467be3d6f6"
    :return:
    """
    mes = {"message": "success"}
    """获取签名和算法"""
    now = datetime.datetime.now()
    sid = get_arg(request, "sid", "")
    if sid == "bbb5fd48094942be80dbf0467be3d6f6":
        """可以请求signature"""
        data = dict()
        r = GlobalSignature.get_signature()
        data['signature'] = r['signature']
        data['algorithm'] = r['algorithm']
        data['expire'] = int(r['expire'] - (now - r['time']).total_seconds())
        mes['data'] = data
    else:
        mes = "未实现"
    return json.dumps(mes)


def mes_func(key) -> str:
    """
    消息的处理函数.接受交易平台推送过来的信息.
    典型的url:
    /mt4/message/push
    :param key: 动词 push/get/delete/update
    :return:
    """
    mes = {"message": "success"}
    if key == "push":
        """推送数据"""
        debug = get_arg(request, "debug", False)  # 调试模式
        if debug:
            oid = RawRequestInfo.record(req=request)
            mes['mid'] = str(oid)
        else:
            payload = get_arg(request, "payload", "")
            if isinstance(payload, str) and len(payload) > 0:
                try:
                    payload = GlobalSignature.decode(payload)
                except Exception as e:
                    mes['message'] = str(e)
                    logger.exception(e)
                    print(e)
                finally:
                    if isinstance(payload, dict):
                        """成功"""
                        data = payload.get("data")
                        if data is None:
                            mes['message'] = "载荷中没有发现data字段"
                        else:
                            try:
                                data = json.loads(data)
                            except Exception as e:
                                print(e)
                                logger.exception(e)
                            finally:
                                if isinstance(data, dict):
                                    init = dict()
                                    for k, v in data.items():
                                        if k in ['deposit_money', 'withdrawal_money']:
                                            k = 'money'
                                        elif k in ['operate_time', 'update_time']:
                                            k = 'time'
                                        elif k in ['deposit_order', 'withdrawal_order']:
                                            k = "order"
                                        else:
                                            k = k.lower()
                                        init[k] = v
                                    obj = PlatformEvent(**init)
                                    r = obj.save_plus()
                                    if isinstance(r, ObjectId):
                                        send_result = False
                                        try:
                                            send_result = obj.send_message()  # 发送钉钉消息
                                        except Exception as e:
                                            t = "{} mt4_view模块发送钉钉消息失败".format(datetime.datetime.now())
                                            content = "init: {}, error: {}".format(init, e)
                                            send_mail(title=t, content=content)
                                            logger.exception(e)
                                        finally:
                                            if not send_result:
                                                t = "{} mt4_view模块发送钉钉消息返回了False".format(datetime.datetime.now())
                                                send_mail(title=t)
                                            else:
                                                pass
                                        mes['id'] = str(r)
                                    else:
                                        mes['message'] = "保存对象失败"
                                        ms = "保存对象失败,args:{}".format(init)
                                        logger.exception(ms)
                                else:
                                    mes['message'] = "data转换失败"
                    else:
                        if mes['message'] == "success":
                            mes['message'] = "解码失败"
                        else:
                            pass
            else:
                mes['message'] = "payload is null"
    elif key == "get":
        mid = request.args.get("mid", "")
        if mid == "":
            mes['message'] = "mid必须"
        elif isinstance(mid, str) and len(mid) == 24:
            f = {"_id": ObjectId(mid)}
            one = RawRequestInfo.find_one_plus(filter_dict=f, instance=False, can_json=True)
            mes['data'] = one
        else:
            mes['message'] = "错误的mid格式"
    else:
        mes = "未实现"
    return json.dumps(mes)


"""集中注册函数"""


mt4_blueprint.add_url_rule(rule="/", view_func=index_func, methods=['get', 'post'])  # hello world
mt4_blueprint.add_url_rule(rule="/api_document", view_func=md_view, methods=['get'])  # api
mt4_blueprint.add_url_rule(rule="/secret", view_func=secret_func, methods=['get', 'post'])  # 获取签名和算法
mt4_blueprint.add_url_rule(rule="/message/<key>", view_func=mes_func, methods=['get', 'post'])  # 接收平台消息
