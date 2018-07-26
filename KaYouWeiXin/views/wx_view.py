#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import send_file
from flask import make_response
from flask import abort
from tools_module import *
from mongo_db import BaseFile
from io import BytesIO
from mongo_db import to_flat_dict
from module.sms_module import *
from module.server_api import *
from module.item_module import *
import json
import requests


"""注册蓝图"""
wx_blueprint = Blueprint("wx_blueprint", __name__, url_prefix="/wx", template_folder="templates")


"""用于公众号页面的视图函数"""


@check_platform_session
def hello() -> str:
    """hello world"""
    wx_user = get_platform_session_arg("wx_user")
    return "hello baby <a href='/wx/auth/info'>去授权</a><br><h2>{}</h2>".format(str(wx_user))


@check_platform_session
def file_func(action, table_name):
    """
    保存/获取文件,
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,对应mongo_db.BaseFile
    2. flash_image                闪卡图片类,对应model.flash_image.FlashImage
    """
    tables = ['base_file', 'flash_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        r = BaseFile.save_flask_file(req=request, collection=table_name)
        if isinstance(r, ObjectId):
            mes['_id'] = str(r)
        else:
            mes['message'] = "保存失败"
    elif action == "view":
        """获取文件"""
        fid = get_arg(request, "fid", "")
        if isinstance(fid, str) and len(fid) == 24:
            fid = ObjectId(fid)
            f = {"_id": fid}
            r = BaseFile.find_one_cls(filter_dict=f, collection=table_name)
            if r is None:
                return abort(404)
            else:
                mime_type = "image/jpeg" if r.get('mime_type') is None else r['mime_type']
                file_name = "1.jpeg" if r.get('file_name') is None else r['file_name']
                """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
                file_name = file_name.encode().decode('latin-1')
                data = r['data']
                data = BytesIO(initial_bytes=data)
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


def auth_demo(key: str = None) -> str:
    """
    用户授权页面，仅仅为了获取用户信息
    :param key: 参数，默认是base/snsapi_base,也可以是info/snsapi_userinfo
    :return:
    """
    if key is None or key == "" or key == "base":
        key = "snsapi_base"
    else:
        key = "snsapi_userinfo"  # 授权类型
    url = request.referrer
    url = request.args.get("url", "{}/hello".format(host_name)) if url is None or url == "" else url
    redirect_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}" \
                       "&response_type=code&scope={}&state=STATE#wechat_redirect".format(app_id, url, key)
    return redirect(redirect_url)


def page_auth_demo():
    """
    页面授权示范页
    :return:
    """
    code = request.args.get("code", "")
    if code == "":
        data = dict()
    else:
        data = PageAuthorization.get_user_info(code=code)
    return render_template("page_auth_demo.html", data=data)


def get_code_and_redirect() -> str:
    """
     获取用户code,生产环境使用.
    :return:
    """
    key = "snsapi_userinfo"  # 授权类型
    url = "{}/wx/draw_user_info".format(host_name)
    ref = request.args.get("ref", "")
    url = request.args.get("url", "{}/hello".format(host_name)) if url is None or url == "" else url
    redirect_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}" \
                       "&response_type=code&scope={}&state={}#wechat_redirect".format(app_id, url, key, ref)
    return redirect(redirect_url)


def draw_user_info():
    """
    这是一个重定向的视图,在实际生产中用于获取用户信息.
    :return:
    """
    ref = get_arg(request, "state", "")
    ref = base64.urlsafe_b64decode(ref).decode()
    code = request.args.get("code", "")
    if code == "":
        return abort(401)
    else:
        data = PageAuthorization.get_user_info(code=code)
        if "openid" in data:
            """成功"""
            obj = WXUser.wx_login(**data)
            session["wx_user"] = obj
            return redirect(ref)
            # return render_template("page_auth.html", ref=ref, data=data)
        else:
            return abort(403)


def wx_js_func():
    """
    返回微信JS-SDK注入配置信息后的js脚本.
    脚本内容说明
    wx.config({
    debug: true, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
    appId: '', // 必填，公众号的唯一标识
    timestamp: , // 必填，生成签名的时间戳
    nonceStr: '', // 必填，生成签名的随机串
    signature: '',// 必填，签名
    jsApiList: [] // 必填，需要使用的JS接口列表
    });
    所有js的接口
    onMenuShareTimeline          "分享到朋友圈”按钮点击状态及自定义分享内容接口（即将废弃）
    onMenuShareAppMessage        “分享给朋友”按钮点击状态及自定义分享内容接口（即将废弃）
    onMenuShareQQ                “分享到QQ”按钮点击状态及自定义分享内容接口
    onMenuShareWeibo             “分享到腾讯微博”按钮点击状态及自定义分享内容接口
    onMenuShareQZone             “分享到QQ空间”按钮点击状态及自定义分享内容接口
    startRecord                  开始录音接口
    stopRecord                   停止录音接口
    onVoiceRecordEnd             监听录音自动停止接口
    playVoice                    播放语音接口
    pauseVoice                   暂停播放接口
    stopVoice                    停止播放接口
    onVoicePlayEnd               监听语音播放完毕接口
    uploadVoice                  上传语音接口
    downloadVoice                下载语音接口
    chooseImage                  拍照或从手机相册中选图接口
    previewImage                 预览图片接口
    uploadImage                  上传图片接口
    downloadImage                下载图片接口
    translateVoice               识别音频并返回识别结果接口
    getNetworkType               获取网络状态接口
    openLocation                 使用微信内置地图查看位置接口
    getLocation                  获取地理位置接口
    hideOptionMenu
    showOptionMenu
    hideMenuItems                关闭当前网页窗口接口
    showMenuItems                批量显示功能按钮接口
    hideAllNonBaseMenuItem       隐藏所有非基础按钮接口
    showAllNonBaseMenuItem       显示所有功能按钮接口
    closeWindow                  关闭当前网页窗口接口
    scanQRCode                   调起微信扫一扫接口
    chooseWXPay                  发起一个微信支付请求
    openProductSpecificView      跳转微信商品页接口
    addCard                      批量添加卡券接口
    chooseCard                   拉取适用卡券列表并获取用户选择信息
    openCard                     查看微信卡包中的卡券接口

    :return: js脚本
    """
    debug = get_arg(request, "debug", "0")
    debug = "true" if debug == "1" else "false"
    cur_url = request.referrer.split("#")[0]
    api_list = get_arg(request, "api", "")
    api_list = api_list.split(" ") if api_list != "" else list()
    signature_dict = JSAPITicket.get_signature(cur_url=cur_url)
    signature = signature_dict['signature']
    timestamp = signature_dict['timestamp']
    noncestr = signature_dict['noncestr']
    s = "wx.config({debug: " + debug + ", appId: '" + app_id + "', timestamp: " + str(timestamp) + ",nonceStr: '" + \
        noncestr + "', signature: '" + signature + "', jsApiList: " + "{}".format(api_list) + "});"
    resp = make_response(s)
    resp.headers['Content-Type'] = "application/javascript"
    return resp


@check_platform_session
def wx_js_api_demo():
    """
    一个演示页面,用于测试wx的js-sdk接口的初始化工作(测试wx_js_func函数)
    :return:
    """
    return render_template("wx_js_api_demo.html")


@check_platform_session
def sms_func(key):
    """
    发送/校验短信
    :return:
    """
    mes = {"message": "success"}
    user = get_platform_session_arg("wx_user", None)
    if user is None:
        mes['message'] = "未登录"
    else:
        _id = user['_id']
        phone = get_arg(request, "phone", "")
        if key in ["get", "send"]:
            """发送短信"""
            if check_phone(phone):
                mes = send_sms(phone)
            else:
                mes['message'] = "错误的手机号码"
        elif key == "check":
            """校验短信"""
            code = get_arg(request, "code", "")
            mes = validate_sms(phone, code)
            if mes['message'] == "success":
                """清除短信"""
                # clear_sms_code(phone)
                pass
            """更新手机绑定信息"""
            f = {"_id": _id}
            u = {"$set": {"phone": phone}}
            r = WXUser.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            if isinstance(r, dict):
                """成功"""
                pass
            else:
                mes['message'] = "绑定手机失败"
        else:
            mes['message'] = "未知的操作:{}".format(key)
    ms = "sms_func 返回的消息:{}".format(mes)
    logger.info(ms)
    print(ms)
    return json.dumps(mes)


@check_platform_session
def resume_opt_func():
    """
    操作(查看/添加/修改,但是不能删除)简历
    :return:
    """
    mes = {"success": "error"}
    user = get_platform_session_arg("wx_user")
    u_id = user['_id']
    resume_args = get_args(request)
    try:
        mes = WXUser.opt_resume(u_id=u_id, resume_args=resume_args)
    except Exception as e:
        ms = "发生错误:{}".format(str(e))
        print(ms)
        logger.exception(mes=ms)
        mes['message'] = ms
    finally:
        return json.dumps(mes)


@check_platform_session
def common_view_func(html_name: str):
    """
    通用页面视图
    param html_name:  html文件名,包含目录路径
    :return:
    """
    user = get_platform_session_arg("wx_user")
    u_id = user['_id']
    template_dir = os.path.join(__project_dir__, 'templates')
    file_names = os.listdir(template_dir)
    if html_name in file_names:
        kwargs = dict()  # 页面传参数
        kwargs['user'] = to_flat_dict(user)
        """
        传参数的步骤暂时省略
        """
        return render_template(html_name, **kwargs)
    else:
        return abort(404)





"""集中注册函数"""


"""hello"""
wx_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""保存或者获取文件(mongodb存储)"""
wx_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['post', 'get'])
"""获取用户授权页面"""
wx_blueprint.add_url_rule(rule="/auth_demo/<key>", view_func=auth_demo, methods=['post', 'get'])
"""页面授权示范页"""
wx_blueprint.add_url_rule(rule="/page_auth_demo", view_func=page_auth_demo, methods=['post', 'get'])
"""生产环境,获取用户code"""
wx_blueprint.add_url_rule(rule="/get_code_and_redirect", view_func=get_code_and_redirect, methods=['post', 'get'])
"""生产环境,获取用户信息"""
wx_blueprint.add_url_rule(rule="/draw_user_info", view_func=draw_user_info, methods=['post', 'get'])
"""生产环境,获取JS-SDK初始化用的脚本"""
wx_blueprint.add_url_rule(rule="/js_sdk_init", view_func=wx_js_func, methods=['post', 'get'])
"""JS-SDK初始化用脚本的演示页面"""
wx_blueprint.add_url_rule(rule="/js_sdk_init_demo", view_func=wx_js_api_demo, methods=['get'])
"""发送/校验短信"""
wx_blueprint.add_url_rule(rule="/sms/<key>", view_func=sms_func, methods=['post', 'get'])
"""操作(查看/添加/修改,但是不能删除)简历"""
wx_blueprint.add_url_rule(rule="/resume/opt", view_func=resume_opt_func, methods=['post', 'get'])
"""通用页面视图"""
wx_blueprint.add_url_rule(rule="/html/<html_name>", view_func=common_view_func, methods=['post', 'get'])