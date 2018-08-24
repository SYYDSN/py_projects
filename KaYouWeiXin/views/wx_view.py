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
from bson.objectid import ObjectId
from tools_module import *
from mongo_db import BaseFile
from mongo_db2 import BaseFile as BaseFile2
from io import BytesIO
from mongo_db import to_flat_dict
from module.sms_module import *
from module.server_api import *
from module.item_module import *
import json
from module.driver_module import *
from module.server_api import *
from pdb import set_trace
from uuid import uuid4
from pdb import set_trace
import requests
from PIL import Image
from mongo_db import get_datetime_from_str


"""注册蓝图"""
wx_blueprint = Blueprint("wx_blueprint", __name__, url_prefix="/wx", template_folder="templates")


"""用于公众号页面的视图函数"""


@check_platform_session
def hello(user: dict = None) -> str:
    """hello world
    :param user:  用户字典
    """
    return "hello baby <a href='/wx/auth/info'>{}去授权</a><br><h2>{}</h2>".format(user.get("nick_name"), str(user['_id']))


@check_platform_session
def file_func(user: dict = None, action: str = "get", table_name: str = "base_info"):
    """
    保存/获取文件, 此函数目前不常用,是对微信用户数据库的操作.
    :param user:  用户字典
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,BaseFile
    """
    tables = ['base_file', 'flash_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        r = BaseFile.save_flask_file(req=request, collection=table_name, owner=user['_id'])
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


@check_platform_session
def resume_image_func(user: dict = None, action: str = 'get', table_name: str = "base_file"):
    """
    保存/获取简历的图片,
    :param user:  用户字典
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,BaseFile
    """
    tables = ['base_file', 'head_image', 'id_image', 'honor_image', 'vehicle_image', 'driving_license_image',
              'rtqc_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        r = BaseFile2.save_flask_file(req=request, collection=table_name, owner=user['_id'])
        if isinstance(r, ObjectId):
            mes['url'] = "/wx/resume_image/view/{}?fid={}".format(table_name, str(r))
        else:
            mes['message'] = "保存失败"
    elif action == "view":
        """获取文件"""
        fid = get_arg(request, "fid", "")
        if isinstance(fid, str) and len(fid) == 24:
            fid = ObjectId(fid)
            f = {"_id": fid}
            print("table_name: {}, fid: {}".format(table_name, fid))
            r = BaseFile2.find_one_cls(filter_dict=f, collection=table_name)
            if r is None:
                return abort(404)
            else:
                mime_type = "image/jpeg" if r.get('mime_type') is None else r['mime_type']
                file_name = "1.jpeg" if r.get('file_name') is None else r['file_name']
                """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
                file_name = file_name.encode().decode('latin-1')
                img = Image.open(BytesIO(initial_bytes=r['data']))
                """这2个参数暂时用不上"""
                img_width = img.width
                img_height = img.height
                """重设图片大小"""
                size = get_arg(req=request, arg="size", default_value="")  # 参数size用于重设尺寸 size=width*height
                if size != "":
                    temp = size.split("*")
                    if len(temp) > 1 and temp[0].isdigit() and temp[1].isdigit():
                        width = int(temp[0])
                        height = int(temp[1])
                    else:
                        width = 80
                        height = 60
                    img = img.resize(size=(width, height))
                else:
                    pass
                """旋转图片,虽然理论上可以进行任何角度的旋转,但是出于效果,最好只进行90度的整数倍旋转"""
                rotate = get_arg(req=request, arg="rotate", default_value="0")  # 参数rotate用于旋转图片 rotate=90
                if isinstance(rotate, str) and rotate.isdigit():
                    rotate = int(rotate)
                    img = img.rotate(rotate)
                else:
                    pass
                data = BytesIO()
                if img.mode == "RGBA":
                    """
                    png图片是4通道.而JPEG是RGB三个通道，所以PNG转BMP时候程序不知道A通道怎么办,
                    会报 cannot write mode RGBA as JPEG  的错误.
                    解决方法是检查img的mode,进行针对性的处理.
                    文件的后缀名也要做针对性的修改
                    """
                    file_format = "png"
                    file_name = "{}.{}".format(file_name.split(".")[0], file_format)
                else:
                    if img.mode != "GBA":
                        """转换图像格式"""
                        img = img.convert("RGB")
                    else:
                        pass
                    file_format = file_name.split(".")[-1]
                img.save(fp=data, format=file_format)
                data = BytesIO(initial_bytes=data.getvalue())  # initial_bytes的值必须是二进制本身,不能是ByteIO对象.
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


@check_platform_session
def download_image_func(user: dict = None, table_name: str = "base_file"):
    """
    从微信服务器下载图片,
    param user:  用户字典
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,BaseFile
    """
    tables = ['base_file', 'head_image', 'id_image', 'honor_image', 'vehicle_image', 'driving_license_image',
              'rtqc_image', 'business_license_image']
    table_name = table_name if table_name in tables else 'base_file'

    """保存文件"""
    db_str = get_arg(request, "db", "mongo_db2")
    handler_map = {"mongo_db": BaseFile, "mongo_db2": BaseFile2}
    handler = handler_map.get(db_str) if handler_map.get(db_str) else BaseFile2

    server_id = get_arg(request, "server_id", "")
    if server_id == "":
        mes['message'] = "没有server_id"
    else:
        field_name = get_arg(request, "field_name", "")
        print("table_name: {}, db: {}, field_name: {}, server_id: {}".format(table_name, db_str, field_name, server_id))
        """从微信服务器下载图片"""
        u = "https://api.weixin.qq.com/cgi-bin/media/get?access_token={}&media_id={}".format(
            AccessToken.get_token(), server_id)
        resp = requests.get(u)
        status = resp.status_code
        if status != 200:
            mes['message'] = "微信图片服务器没有正确响应:{}".format(status)
        else:
            content = resp.content
            # set_trace()
            if isinstance(content, bytes):
                img = BytesIO(initial_bytes=content)
                r = handler.save_cls(file_obj=img, collection=table_name, owner=user['_id'])
                if isinstance(r, ObjectId):
                    if db_str == "mongo_db2":
                        """简历相关的图片和文件"""
                        mes[field_name + '_url'] = "/wx/resume_image/view/{}?fid={}".format(table_name, str(r))
                    else:
                        """非简历相关的图片和文件"""
                        mes[field_name + '_url'] = "/wx/file/view/{}?fid={}".format(table_name, str(r))
                    mes[field_name] = str(r)
                else:
                    mes['message'] = "保存失败"
            else:
                mes['message'] = "没有获取到图片二进制文件"
    print(mes)
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
    这是一个重定向的视图,在实际生产中用于获取用户微信相关信息.
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
            session["user_id"] = obj['_id']
            session["update_date"] = datetime.datetime.now()
            return redirect(ref)
            # return render_template("page_auth.html", ref=ref, data=data)
        else:
            return abort(403)


@check_platform_session
def back_apply(user: dict = None):
    """
    撤回(中介/兼职)的认证申请.
    :param user:
    :return:
    """
    if not isinstance(user, dict):
        return abort(404)
    else:
        mes = {"message": "unknown error"}
        u_id = get_arg(request, "u_id", "")
        if isinstance(u_id, str) and len(u_id) == 24:
            if u_id == str(user['_id']):
                """参数正确"""
                if user.get('checked', 0) == 1 and user.get("authenticity", 0) == 1:
                    """可以撤回"""
                    f = {"_id": user['_id']}
                    u = {"checked": 0}
                    r = WXUser.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
                    if r is None:
                        mes['message'] = "撤回失败"
                    else:
                        mes['message'] = "success"
            else:
                mes['message'] = "请求无法满足"
        else:
            mes['message'] = "参数错误"
        return json.dumps(mes)


@check_platform_session
def self_info_func(user: dict = None, key: str = "view"):
    """
    用户对用户信息的有限的操作,对一些允许的字段的添加和修改,
     这里,既不能新增用户,也不能删除用户,只有修改和查看
     param user:  用户字典
     param key:  操作类型
    :return:
    """
    if not isinstance(user, dict):
        return abort(404)
    else:
        mes = {"message": "unknown error"}
        if key == "view":
            """查看用户信息"""
            ignore_fields = [
                'openid', 'unionid', 'subscribe', 'subscribe_scene', 'subscribe_time',
                'access_token', 'expires_in', 'time', 'refresh_token'
            ]
            mes['data'] = mongo_db.to_flat_dict(user, ignore_columns=ignore_fields)
        elif key == "update":
            """更新/修改用户信息"""
            check_pass = user.get("checked", 0)  # 中介/兼职审核状态
            if check_pass == 1 or check_pass == 2:
                ignore_fields = [
                    'openid', 'unionid', 'subscribe', 'subscribe_scene', 'subscribe_time',
                    'access_token', 'expires_in', 'time', 'refresh_token', 'role',
                    'resume_id', 'relate_time', 'relate_id', 'relate_image', 'authenticity',
                    'relate_image', 'name', 'identity_code', 'blank_name', 'blank_account'

                ]
            else:
                ignore_fields = [
                    'openid', 'unionid', 'subscribe', 'subscribe_scene', 'subscribe_time',
                    'access_token', 'expires_in', 'time', 'refresh_token', 'role',
                    'resume_id', 'relate_time', 'relate_id', 'relate_image', 'authenticity',
                    'relate_image'
                ]
            args = get_args(request)
            s = dict()
            names = WXUser.type_dict.keys()
            for k, v in args.items():
                if k in names:
                    if k in ignore_fields:
                        pass
                    else:
                        s[k] = v
                else:
                    """忽略不在字段定义中的参数"""
                    pass
            if len(s) == 0:
                mes['message'] = "缺少必要的参数"
            else:
                f = {"_id": user['_id']}
                s['checked'] = 1  # 提交审核状态
                u = {"$set": s}
                r = WXUser.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
                if r is None:
                    ms = "修改数据失败! f:{}, u: {}".format(f, u)
                    logger.exception(msg=ms)
                    print(ms)
                    mes['message'] = "修改数据失败"
                else:
                    mes['message'] = "success"
        else:
            ms = "未知的key: {}".format(key)
            logger.exception(msg=ms)
            print(ms)
            mes['message'] = mes
        return json.dumps(mes)


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
def wx_js_api_demo(user: dict = None):
    """
    一个演示页面,用于测试wx的js-sdk接口的初始化工作(测试wx_js_func函数)
    param user:  用户字典
    :return:
    """
    return render_template("wx_js_api_demo.html")


@check_platform_session
def sms_func(user: dict = None, key: str = 'check'):
    """
    发送/校验短信
    param user:  用户字典
    param key: 操作类型
    :return:
    """
    mes = {"message": "success"}
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
                """更新手机绑定信息"""
                f = {"_id": _id}
                u = {"$set": {"phone": phone}}
                r = WXUser.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                if isinstance(r, dict):
                    """成功"""
                    session['user_id'] = r['_id']
                    session.pop('wx_user', None)
                else:
                    mes['message'] = "绑定手机失败"
            else:
                pass
        else:
            mes['message'] = "未知的操作:{}".format(key)
    ms = "sms_func 返回的消息:{}".format(mes)
    logger.info(ms)
    print(ms)
    return json.dumps(mes)


@check_platform_session
def resume_opt_func(user: dict = None):
    """
    操作(查看/添加/修改,但是不能删除)简历
    param user:  用户字典
    :return:
    """
    user2 = {
        "_id": ObjectId("5b56bdba7b3128ec21daa4c7"),
        "openid": "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
        "access_token": "12_ypF7a9ujmbnNYnbtZF8eyLyy23H9YmST6pMPYAuYefQizi4CrFOupAlLXKMe2dfRGa2Ezt0ApdHHTz-LdX8qtYVS8qTq2OQtnW5ZXtvUCGQ",
        "city": "闵行",
        "country": "中国",
        "expires_in": 7200,
        "groupid": 0,
        "head_img_url": "http://thirdwx.qlogo.cn/mmopen/dUtvxcibjGMKAzSRePkx3ZGZnRMsDyzU6f8fNjxtrS2nXCcwMPQUbZM4YYfS1vhWoObUHQaErCDEjNrStKszkiaA/132",
        "language": "zh_CN",
        "nick_name": "徐立杰",
        "province": "上海",
        "qr_scene": 0,
        "qr_scene_str": "",
        "refresh_token": "12_7h-zJ5RYfKWjYp7AQOiIe7VdFaZxw7gPFe3xxVVx4eEGdtuaYYK4st9HgSADdvJo_QpSLkF2JLP4Royzd_NfLde291LetISRV32TjtRweMQ",
        "remark": "",
        "scope": "snsapi_userinfo",
        "sex": 1,
        "subscribe": 1,
        "subscribe_scene": "ADD_SCENE_SEARCH",
        "tagid_list": [],
        "relate_img": "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=gQF78DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyQm9HVjAxNG5jaGwxMDAwME0wN2QAAgQmRFhbAwQAAAAA",
        "phone": "15618317376",
        "resume_id": ObjectId("5b5a96d9bede684e68049f01")
    }
    user = user2 if user is None else user
    mes = {"success": "error"}
    u_id = user['_id']
    resume_args = get_args(request)
    print("resume_opt_func args: {}".format(resume_args))
    if "time" in resume_args:
        resume_args['time'] = get_datetime_from_str(resume_args['time'])
    if "relate_time" in resume_args:
        resume_args['relate_time'] = get_datetime_from_str(resume_args['relate_time'])
    if "relate_id" in resume_args:
        relate_id = resume_args['relate_id']
        resume_args['relate_id'] = relate_id if isinstance(relate_id, ObjectId) else ObjectId(relate_id)
    if "resume_id" in resume_args:
        resume_id = resume_args['resume_id']
        resume_args['resume_id'] = resume_id if isinstance(resume_id, ObjectId) else ObjectId(resume_id)
    if "business_license_image" in resume_args:
        business_license_image = resume_args['business_license_image']
        resume_args['business_license_image'] = business_license_image if isinstance(business_license_image, ObjectId) \
            else ObjectId(business_license_image)
    if "authenticity" in resume_args:
        authenticity = resume_args['authenticity']
        resume_args['authenticity'] = authenticity if isinstance(authenticity, bool) else bool(authenticity)
    if "expected_salary" in resume_args:
        try:
            raw_expected_salary = resume_args['expected_salary']
            print("raw_expected_salary: {}".format(raw_expected_salary))
            expected_salary = json.loads(raw_expected_salary)
            print("expected_salary: {}".format(expected_salary))
            resume_args['expected_salary'] = expected_salary
        except Exception as e:
            logger.exception(msg=e)
            raise e
        finally:
            pass
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
def resume_extend_info_func(user: dict = None):
    """
    param user:  用户字典
    对简历的扩展信息的操作.
    简历的扩展信息包括:
    1.
    :return:
    """
    mes = {"success": "error"}
    u_id = user['_id']
    # u_id = ObjectId("5b56bdba7b3128ec21daa4c7")
    arg_dict = get_args(request)
    if "begin" in arg_dict:
        arg_dict['begin'] = get_datetime_from_str(arg_dict['begin'])
    if "end" in arg_dict:
        arg_dict['end'] = get_datetime_from_str(arg_dict['end'])
    if arg_dict is None or len(arg_dict) == 0:
        mes['message'] = "参数不能为空"
    else:
        resume_id = arg_dict.pop("resume_id", "")
        if isinstance(resume_id, str) and len(resume_id) == 24:
            resume_id = ObjectId(resume_id)
            opt = arg_dict.pop("opt", "")
            mes = WXUser.opt_extend_info(u_id=u_id, resume_id=resume_id, opt=opt, arg_dict=arg_dict)
        else:
            mes['message'] = "简历id错误"
    return json.dumps(mes)


@check_platform_session
def build_relate(user: dict = None):
    """
    用户手动建立和中介/兼职/销售的关联关系
    :param user:
    :return:
    """
    # user = WXUser.find_by_id("5b56be217b3128ec21daa50a", to_dict=True)
    mes = {"message": "error"}
    if user is None:
        mes['message'] = "用户不能为空"
    else:
        role = user.get("role", 0)
        if role > 0:
            ms = "用户:{}的角色不能委托他人求职".format(user)
            logger.exception(msg=ms)
            mes['message'] = "当前用户角色无法委托求助"
        else:
            s_id = get_arg(request, 's_id', "")
            if isinstance(s_id, str) and len(s_id) == 24:
                sales = WXUser.find_by_id(o_id=s_id, to_dict=True)
                if sales is None:
                    mes['message'] = "sid非法"
                else:
                    s_role = sales.get("role", 0)
                    if s_role < 1:
                        mes['message'] = "被委托人身份校验失败"
                    else:
                        r = WXUser.relate(u_id=user['_id'], s_id=sales['_id'])
                        if r:
                            mes['message'] = "success"
                        else:
                            mes['message'] = "委托失败"
            else:
                mes['message'] = "sid错误"
    return json.dumps(mes)


@check_platform_session
def common_view_func(user: dict = None, html_name: str = ''):
    """
    通用页面视图
    param user:  用户字典
    param html_name:  html文件名,包含目录路径
    :return:
    """
    # user = WXUser.find_by_id("5b56be217b3128ec21daa50a", to_dict=True)
    user2 = {
        "_id": ObjectId("5b56bdba7b3128ec21daa4c7"),
        "openid": "oBBcR1T5r6FCqOo2WNxMqPUqvK_I",
        "access_token": "12_ypF7a9ujmbnNYnbtZF8eyLyy23H9YmST6pMPYAuYefQizi4CrFOupAlLXKMe2dfRGa2Ezt0ApdHHTz-LdX8qtYVS8qTq2OQtnW5ZXtvUCGQ",
        "city": "闵行",
        "country": "中国",
        "expires_in": 7200,
        "groupid": 0,
        "head_img_url": "http://thirdwx.qlogo.cn/mmopen/dUtvxcibjGMKAzSRePkx3ZGZnRMsDyzU6f8fNjxtrS2nXCcwMPQUbZM4YYfS1vhWoObUHQaErCDEjNrStKszkiaA/132",
        "language": "zh_CN",
        "nick_name": "徐立杰",
        "province": "上海",
        "qr_scene": 0,
        "qr_scene_str": "",
        "refresh_token": "12_7h-zJ5RYfKWjYp7AQOiIe7VdFaZxw7gPFe3xxVVx4eEGdtuaYYK4st9HgSADdvJo_QpSLkF2JLP4Royzd_NfLde291LetISRV32TjtRweMQ",
        "remark": "",
        "scope": "snsapi_userinfo",
        "sex": 1,
        "subscribe": 1,
        "subscribe_scene": "ADD_SCENE_SEARCH",
        "tagid_list": [],
        "relate_img": "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=gQF78DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyQm9HVjAxNG5jaGwxMDAwME0wN2QAAgQmRFhbAwQAAAAA",
        "phone": "15618317376",
        "resume_id": ObjectId("5b5a96d9bede684e68049f01")
    }
    user = user2 if user is None else user
    template_dir = os.path.join(__project_dir__, 'templates')
    file_names = os.listdir(template_dir)
    ver = uuid4().hex
    kwargs = dict()  # 页面传参数
    kwargs['version'] = ver
    kwargs['user'] = to_flat_dict(user)
    if html_name in file_names:
        """页面存在"""
        resume_pages = [                              # 需要传递简历信息的页面
            "resume.html",
            "register_info.html",
            "resume_detail.html",
            "additional.html",
            "driver_two.html",
            "part_time.html",
            "update_id.html",
        ]
        resume_id = user.get("resume_id", "")
        if html_name in resume_pages:
            """简历的简要信息"""
            if resume_id == "":
                resume = dict()
            else:
                resume = DriverResume.find_by_id(o_id=resume_id, to_dict=True)
            # kwargs['work'] = dict()
            if html_name in ["resume.html", "resume_detail.html"]:
                """这个页面是显示简历全部信息的地方,需要额外详细的简历信息"""
                page_title = "我的简历"
                kwargs['page_title'] = page_title
                info = DriverResume.get_full_info(resume_id=resume_id)
                message = info['message']
                if message == "success":
                    resume = info['data']
                else:
                    ms = "获取简历详细信息错误,错误原因:{}".format(message)
                    logger.exception(msg=ms)
            else:
                pass
            # set_trace()
            kwargs['resume'] = resume
        elif html_name == "driver_three.html":  # 车辆信息
            page_title = "自有车辆"
            kwargs['page_title'] = page_title
            v_id = get_arg(request, "v_id", "")
            if isinstance(v_id, str) and len(v_id) == 24:
                vehicle = Vehicle.find_by_id(o_id=v_id, to_dict=True)
            else:
                vehicle = dict()
            kwargs['vehicle'] = vehicle
        elif html_name == "add_info_jilu.html":  # 添加荣誉
            page_title = "曾获荣誉"
            kwargs['page_title'] = page_title
            if resume_id == "":
                return abort(403)
            else:
                h_id = get_arg(request, "h_id", "")
                if isinstance(h_id, str) and len(h_id) == 24:
                    honor = Honor.find_by_id(o_id=h_id, can_json=True)
                else:
                    honor = dict()
                kwargs['honor'] = honor
        elif html_name == "resume_info.html":  # 添加工作经验
            page_title = "工作履历"
            kwargs['page_title'] = page_title
            if resume_id == "":
                return abort(403)
            else:
                w_id = get_arg(request, "w_id", "")
                if isinstance(w_id, str) and len(w_id) == 24:
                    work = WorkHistory.find_by_id(o_id=w_id, can_json=True)
                else:
                    work = dict()
                kwargs['work'] = work
        elif html_name == "educational_experience.html":  # 添加教育经历
            page_title = "教育经历"
            kwargs['page_title'] = page_title
            if resume_id == "":
                return abort(403)
            else:
                e_id = get_arg(request, "e_id", "")
                if isinstance(e_id, str) and len(e_id) == 24:
                    education = Education.find_by_id(o_id=e_id, can_json=True)
                else:
                    education = dict()
                kwargs['education'] = education
        elif html_name == "intermediary.html":
            """
            上传营业执照等申请中介审核的页面
            1. 如果审核尚未通过.允许访问本页面.
                1. 未申请的,允许发起申请.
                2. 申请中的,锁定输入.不允许编辑.但是可以撤回.
                3. 申请驳回的,允许编辑再次申请
            2. 审核通过,跳转到help_job.html页面
            """
            page_title = "申请认证"
            kwargs['page_title'] = page_title
            if user.get("authenticity") == 1:
                return redirect("/wx/html/help_job.html?u_id={}".format(user['_id']))
        elif html_name == "my_resource.html":  # 中介/销售/黄牛 查看自己的推荐的资源
            u_id = get_arg(request, "u_id", "")
            user = None
            if isinstance(u_id, str) and len(u_id) == 24:
                user = WXUser.find_by_id(o_id=u_id, to_dict=True, can_json=True)
            else:
                pass
            # 测试时为了获取资源,生产环境请注销
            # if user is None:
            #     user = WXUser.find_by_id(o_id=ObjectId("5b56c0f87b3128ec21daa693"), to_dict=True, can_json=False)
            if user is None:
                """没有合法的u_id参数就重定向"""
                referrer = request.referrer
                if referrer is None or referrer == "":
                    return abort(404)
                else:
                    return redirect(referrer)
            else:
                kwargs['user'] = user
                now = datetime.datetime.now()
                y = get_arg(request, "y", now.year)
                m = get_arg(request, "m", now.month)
                b = mongo_db.get_datetime_from_str("{}-{}-1 0:0:0".format(y, m))
                f = {"relate_time": {"$gte": b, "$lte": now}}
                page_index = get_arg(request, "index", 1)
                res = WXUser.page_resource(u_id=kwargs['user']['_id'], filter_dict=f, page_index=page_index)
                total_record = res.get("total_record", 0)
                total_page = res.get("total_page", 0)
                data = res.get("data", list())
                current_page = res.get("current_page", 1)
                pages = res.get("pages", list())
                page_title = "我的资源"
                # pages = [1, 2, 3, 4]  # 生产环境注销
                # total_record = 50  # 生产环境注销
                # total_page = 5  # 生产环境注销
                # page_index = 2  # 生产环境注销
                kwargs['data'] = data
                kwargs['current_page'] = current_page
                kwargs['pages'] = pages
                kwargs['page_index'] = page_index
                kwargs['page_title'] = page_title
                kwargs['total_record'] = total_record
                kwargs['total_page'] = total_page
                kwargs['y'] = y
                kwargs['m'] = m
        elif html_name == "help_job.html":
            """
            u_id = "5b56c0f87b3128ec21daa693"
            展示关联二维码二维码页面, 中介/销售/黄牛专属页面,任何人访问这个页面的时候,必须带上u_id参数.
            否则原路导向回去或者403
            用户访问此页面时,检测用户是否已绑定
            """
            page_title = "委托求职"
            kwargs['page_title'] = page_title
            s_id = get_arg(request, "s_id", "")
            s_id = s_id if s_id != "" else get_arg(request, "u_id", "")
            if isinstance(s_id, str) and len(s_id) == 24:
                sales = WXUser.find_by_id(o_id=s_id, to_dict=True, can_json=True)
                if isinstance(sales, dict):
                    """
                    带s_id参数
                    1. 验证过,允许访问
                    2. 尚未通过审核,允许跳转到页面,但提示未审核,立即跳转. 
                    """
                    kwargs['sales'] = sales
                else:
                    """不合法的u_id参数"""
                    return abort(403)
            else:
                """无u_id参数"""
                return abort(403)
            """访问页面之前,可能需要加载一些参数"""
        else:
            pass
        print(kwargs)  # 打印参数
        print("html_name is {}".format(html_name))
        return render_template(html_name, **kwargs)
    else:
        return abort(404)


def share_wx_func():
    """分享微信的单独页面,用于外链"""
    return render_template("share_wx.html")


"""集中注册函数"""


"""hello"""
wx_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""分享微信的单独页面,用于外链"""
wx_blueprint.add_url_rule(rule="/share_wx", view_func=share_wx_func, methods=['get'])
"""保存或者获取文件(mongodb存储)"""
wx_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['post', 'get'])
"""保存或者获取简历相关的图片(mongodb存储)"""
wx_blueprint.add_url_rule(rule="/resume_image/<action>/<table_name>", view_func=resume_image_func, methods=['post', 'get'])
"""下载微信服务器上的素材并保存(mongodb存储)"""
wx_blueprint.add_url_rule(rule="/auto_download/<table_name>", view_func=download_image_func, methods=['post'])
"""获取用户授权页面"""
wx_blueprint.add_url_rule(rule="/auth_demo/<key>", view_func=auth_demo, methods=['post', 'get'])
"""页面授权示范页"""
wx_blueprint.add_url_rule(rule="/page_auth_demo", view_func=page_auth_demo, methods=['post', 'get'])
"""生产环境,获取用户code"""
wx_blueprint.add_url_rule(rule="/get_code_and_redirect", view_func=get_code_and_redirect, methods=['post', 'get'])
"""生产环境,获取用户微信信息"""
wx_blueprint.add_url_rule(rule="/draw_user_info", view_func=draw_user_info, methods=['post', 'get'])
"""生产环境,获取JS-SDK初始化用的脚本"""
wx_blueprint.add_url_rule(rule="/js_sdk_init", view_func=wx_js_func, methods=['post', 'get'])
"""JS-SDK初始化用脚本的演示页面"""
wx_blueprint.add_url_rule(rule="/js_sdk_init_demo", view_func=wx_js_api_demo, methods=['get'])
"""发送/校验短信"""
wx_blueprint.add_url_rule(rule="/sms/<key>", view_func=sms_func, methods=['post', 'get'])
"""用户自己操作(查看/修改)自己的(微信)用户信息"""
wx_blueprint.add_url_rule(rule="/self_info/<key>", view_func=self_info_func, methods=['post', 'get'])
"""用户撤回申请中介/兼职的申请"""
wx_blueprint.add_url_rule(rule="/back_apply", view_func=back_apply, methods=['post', 'get'])
"""操作(查看/添加/修改,但是不能删除)简历基本信息"""
wx_blueprint.add_url_rule(rule="/resume/opt", view_func=resume_opt_func, methods=['post', 'get'])
"""操作(查看/添加/修改/删除)简历扩展信息"""
wx_blueprint.add_url_rule(rule="/resume/extend", view_func=resume_extend_info_func, methods=['post', 'get'])
"""手动建立用户和中介/兼职/销售的委托关系"""
wx_blueprint.add_url_rule(rule="/build_relate", view_func=build_relate, methods=['post', 'get'])
"""通用页面视图"""
wx_blueprint.add_url_rule(rule="/html/<html_name>", view_func=common_view_func, methods=['post', 'get'])