# -*- coding:utf-8 -*-
from flask import Blueprint, abort, request, url_for, redirect, render_template
from api.data.item_module import *
from tools_module import *
from api.user import sms
import json
import datetime
import hashlib
import os
import sys
from error_module import pack_message, RepeatError
from mongo_db import BaseDoc
from log_module import get_logger
from api.user import violation_module
from uuid import uuid4
from api.user.app_module import check_version as check_client_version
from api.data.item_module import *
from manage.company_module import Company
from api.user import security_module


api_user_blueprint = Blueprint("api_user_blueprint", __name__, url_prefix="/api", template_folder="templates")
logger = get_logger()
head_img_dir_path = os.path.join(sys.path[0], "static", 'image', 'head_img')
if not os.path.exists(head_img_dir_path):
    os.makedirs(head_img_dir_path)
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')  # 运行上传的文件的类型


def get_img_dir_path(dir_name):
    """获取图片的存储目录"""
    path = os.path.join(sys.path[0], "static", 'image', dir_name)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


@api_user_blueprint.route("/reg", methods=['get', 'post'])
@log_request_args
def app_user_reg():
    """app端用户注册"""
    message = {"message": "success"}
    user_name = get_arg(request, 'username')
    user_password = get_arg(request, 'password')
    phone_num = get_arg(request, 'phone_num')
    random_code = get_arg(request, 'tel_verify_code')   # 短信验证码
    invite_code = get_arg(request, 'invite_code')   # 邀请码
    phone_num = user_name if phone_num == "" else phone_num
    validate_result = sms.validate_sms(phone_num, random_code)
    if validate_result['message'] != "success":
        """短信验证失败"""
        message = validate_result
    else:
        """组装添加客户的数据"""
        user_password = hashlib.md5(phone_num[5:].encode()).hexdigest() if user_password == "" else user_password
        create_date = datetime.datetime.now()
        """先记录注册信息"""
        ip = get_real_ip(request)
        RegRecord.insert_one(reg_date=create_date, ip=ip, phone_num=phone_num)
        args = {"user_name": user_name, "user_password": user_password, "phone_num": phone_num,
                "create_date": create_date, "invite_code": invite_code}
        try:
            result = User.register(**args)
            if isinstance(result, BaseDoc):
                """注册验证码依然有效，直至超时"""
                # sms.clear_sms_code(phone_num)  # 清除短信
                pass
            else:
                message = pack_message(message, 3007, **args)
        except ValueError as e:
            logger.exception(sys._getframe().f_code.co_name)
            error_col, error_val = e.args[0].split(" ")[-1].split(":")
            name_dict = {"phone_num": "手机号码", "user_name": "用户名"}
            if error_col in name_dict:
                col_name = name_dict[error_col]
                if col_name == "手机号码":
                    message['message'] = "{}已注册，请直接登录".format(col_name)
                elif col_name == "用户名":
                    message['message'] = "{} {} 已被占用，请使用其他用户名".format(col_name, error_val)
            else:
                message['message'] = "{} {} 重复".format(error_col, error_val)
        except Exception as e:
            print(e)
            logger.exception("app_user_reg Error: {}".format(e))
        finally:
            pass
    logger.info("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))
    return json.dumps(message)


@api_user_blueprint.route("/login", methods=['get', 'post'])
@log_request_args
def app_user_login():
    """app端用户登录"""
    message = {"message": "success"}
    user_name = get_arg(request, 'username')
    user_password = get_arg(request, 'password')
    phone_num = get_arg(request, 'phone_num')
    """为了兼容老系统做的修改"""
    phone_num = user_name if phone_num == '' else phone_num
    random_code = get_arg(request, 'tel_verify_code', 0)   # 短信验证码
    login_type = get_arg(request, 'login_type', '')   # 登录类型
    """有多种登录类型：
    TY_PHONE：以手机登录
    """
    if login_type.upper() == "TY_PHONE":
        try:
            random_code = int(random_code)
            """先检查是不是物联网卡，不是的话，走普通通道，是的话，走特殊通道"""
            if check_iot_phone(phone_num):
                """是物联网卡"""
                result = User.iot_user_login(phone_num=phone_num)
                if result is None:
                    message = pack_message(message, 3001, phone_num=phone_num, random_code=random_code)
                else:
                    message.update(result)
            else:
                """普通手机卡"""
                validate_result = sms.validate_sms(phone_num, random_code)
                if validate_result['message'] != "success":
                    """短信验证失败"""
                    message = pack_message(message, 3002, phone_num=phone_num, random_code=random_code)
                else:
                    """根据手机号码查询用户"""
                    result = User.find_one(phone_num=phone_num)
                    if isinstance(result, User):
                        """登录验证码依然有效，直至超时"""
                        # sms.clear_sms_code(phone_num)  # 清除短信
                        message['data'] = result.to_flat_dict()
                        token = AppLoginToken.create_token(result.get_id())
                        message['token'] = token
                    else:
                        """还未注册"""
                        message = pack_message(message, 3004, phone_num=phone_num, random_code=random_code)
        except ValueError:
            """参数类型错误"""
            message = pack_message(message, 3001, phone_num=phone_num, random_code=random_code)
        finally:
            pass
    else:
        """未识别的参数"""
        message = pack_message(message, 3002, phone_num=phone_num, random_code=random_code)
    logger.info("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))
    return json.dumps(message)


@api_user_blueprint.route("/logout", methods=['get', 'post'])
@login_required_app
@log_request_args
def app_user_logout(user_id):
    """app端用户登出"""
    message = {"message": "success"}
    try:
        User.user_logout(user_id)
    except Exception as e:
        ms = "Error function={},args={}".format(sys._getframe().f_code.co_name, {"user_id": user_id, "e": e})
        logger.info(ms)
    finally:
        return json.dumps(message)


@api_user_blueprint.route("/get_sms", methods=['get', 'post'])
@log_request_args
def api_send_sms():
    """用户发送短信"""
    message = {"message": "success"}
    phone_num = get_arg(request, "phone_num")
    if phone_num == "":
        phone_num = get_arg(request, "username")
    if check_phone(phone_num):
        message = sms.send_sms(phone_num)
    else:
        message = pack_message(message, 3013, phone_num=phone_num)
    logger.info("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))
    return json.dumps(message)


@api_user_blueprint.route("/get_verify_code", methods=['get', 'post'])
def get_verify_code():
    """获取短信验证码，保留是为了对老系统的兼容"""
    return redirect(url_for('api_send_sms'))


@api_user_blueprint.route("/check_version", methods=['get', 'post'])
def check_version():
    """检查版本信息"""
    os_type = get_arg(request, "os_type", "android")
    message = {"message": "success"}
    result = check_client_version(os_type)
    if result is None:
        pass
    else:
        result['url'] = "{}{}".format(request.host_url, result['url'])
        message.update(result)
    return json.dumps(message)


@api_user_blueprint.route("/<key>_user_info", methods=['get', 'post'])
@login_required_app
@log_request_args
def process_user_info(key, user_id):
    """根据token获取/编辑用户信息"""
    message = {"message": "success"}
    if key == "get":
        host_url = request.host_url
        message = User.get_info_dict_by_id(user_id)
        if message['message'] == "success":
            message['data']['head_img_url'] = host_url + str(message['data']['head_img_url'])
        logger.info("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))
    elif key == "edit" or key == "update":
        """编辑用户信息"""
        args = get_args(request)
        try:
            if "auth_token" in args:
                args.pop("auth_token")
            else:
                args.pop("token")
        except KeyError:
            pass
        try:
            args.pop("_id")
        except KeyError:
            pass
        filter_dict = {"_id": user_id}
        user = User.find_by_id(user_id)
        result = user.find_one_and_update(filter_dict=filter_dict, update=args)
        if result is None:
            """插入失败"""
            message = pack_message(message, 6001, args=args, user_id=user_id)
    else:
        message = pack_message(message, 3003, key=key)
    return json.dumps(message)


@api_user_blueprint.route("/upload_<key>", methods=['post'])
@login_required_app
@log_request_args
def update_image(user_id, key):
    """
    用户上传文件
    注意!!!!
    其他路由都不能以upload_开头了,这是个历史问题
    """
    if request.method.lower() == "post":
        message = {"message": "success"}
        upload_files = request.files
        """sys._getframe().f_code.co_name 当前运行函数的名称"""
        ms = "{} 上传文件，key={},files={}, user_id={}".format(sys._getframe().f_code.co_name, key, upload_files, user_id)
        logger.info(ms)
        try:
            file = upload_files[key]
            raw_file_name = file.filename.lower()
            suffix = raw_file_name.split(".")[-1]
            if suffix in ALLOWED_EXTENSIONS:
                """允许的文件类型"""
                file_name = "{}.{}".format(uuid4().hex, suffix)
                img_dir_path = get_img_dir_path(key)
                full_path = os.path.join(img_dir_path, file_name)
                file.save(full_path)
                update_dict = None
                result = None
                if key == "avatar":
                    """用户上传头像"""
                    part_url = "static/image/{}/{}".format(key, file_name)
                    img_url = request.host_url + part_url
                    message['data'] = img_url
                    user = User.find_by_id(user_id)
                    filter_dict = {"_id": user_id}
                    update_dict = {"$set": {"head_img_url": part_url}}
                    print("------------")
                    print(filter_dict)
                    print(update_dict)
                    print("---------")
                    result = user.find_one_and_update(filter_dict=filter_dict, update=update_dict)
                    print(result)
                elif key == "permit_image":
                    """如果是行车证照片的话，需要创建/修改一个对应的行车证信息"""
                    part_url = "static/image/{}/{}".format(key, file_name)
                    img_url = request.host_url + part_url
                    message['data'] = img_url
                    result = "Ok"  # 仅仅为了下面的if不报错而已
                    _id = get_arg(request, "_id")  # 获取请求的行车证信息的id
                    _id = _id.strip() if isinstance(_id, str) else _id
                    """创建一个行车证信息"""
                    if _id is None or _id == "":
                        """这是上传图片添加行车证的情况"""
                        permit_image_url = request.host_url + part_url
                        car_license_kwargs = {"permit_image_url": part_url,
                                              "user_id": user_id}
                        print("new permit_image args: {}".format(_id))
                        r = CarLicense.instance(**car_license_kwargs)  # 插入一个行车证信息
                        if r is not None:
                            _id = r.get_id()
                            res = dict()
                            res['_id'] = str(_id)
                            res['permit_image_url'] = permit_image_url
                            message['data'] = res
                        else:
                            ms = "CarLicense.instance函数没有正确的返回,参数:{}".format(car_license_kwargs)
                            logger.exception(ms)
                            print(ms)
                            message = pack_message(message, 5000, **car_license_kwargs)
                    else:
                        """这是修改一个行车证图片的情况"""
                        print("修改行车证图片,_id={}".format(_id))
                        if not isinstance(_id, ObjectId):
                            _id = ObjectId(_id)
                        filter_dict = {"_id": _id}
                        permit_image_url = request.host_url + part_url
                        update = {"$set": {"permit_image_url": part_url}}
                        r = CarLicense.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update, upsert=False)
                        if r is not None:
                            res = dict()
                            res['_id'] = str(_id)
                            res['permit_image_url'] = permit_image_url
                            message['data'] = res
                        else:
                            ms = "CarLicense.find_one_and_update_plus函数没有正确的返回,参数:{} {}".format(filter_dict, update)
                            logger.exception(ms)
                            print(ms)
                            message = pack_message(message, 3004, _id=_id, error_cause=ms, permit_image_url=permit_image_url)
                elif key == "license_image":
                    """上传驾驶证照片信息,驾驶证的照片地址是User的直接属性"""
                    part_url = "static/image/{}/{}".format(key, file_name)
                    img_url = request.host_url + part_url
                    message['data'] = img_url
                    result = "Ok"  # 仅仅为了下面的if不报错而已
                    user = User.find_by_id(user_id)
                    if isinstance(user, User):
                        res = user.update_driving_license(image_url=part_url)
                        if res['message'] == "success":
                            image_url = img_url  # 返回驾驶证图片的绝对地址
                            _id = str(user_id)
                            data = {"_id": _id, "image_url": image_url}
                            message['data'] = data
                        else:
                            ms = "update_image func Error: key={},img_url={}".format(key, img_url)
                            logger.exception(ms)
                    else:
                        message = pack_message(message, 3004, user_id=str(user_id))
                else:
                    """不是用户上传头像,行车证和驾驶证照片"""
                    part_url = "static/image/{}/{}".format(key, file_name)
                    img_url = request.host_url + part_url
                    message['data'] = img_url
                    result = "Ok"  # 仅仅为了下面的if不报错而已
                    print(result)

                if result is None:
                    message = pack_message(message, 6001, user_id=user_id, update_dict=update_dict)
            else:
                message = pack_message(message, 3001, file_name=raw_file_name, allow_file_suffix=ALLOWED_EXTENSIONS)
        except KeyError as e:
            print(e)
            logger.exception("Error! case: {}".format(e))
            message = pack_message(message, 3000, avatar=str(None))
        except Exception as e:
            print(e)
            logger.exception("Error! case: {}".format(e))
            message = pack_message(message, 5000, avatar=str(None))
        finally:
            print("update_image function : ", end="")
            print(message)
            return json.dumps(message)
    else:
        return abort(405)


@api_user_blueprint.route("/<key>_violation_shortcut", methods=['get', 'post'])
@login_required_app
@log_request_args
def process_vio_query_generator(user_id, key):
    """创建一个违章查询器,token是身份检查装饰器传来的值"""
    message = {"message": "success"}
    raw_args = get_args(request)
    args = raw_args.copy()
    if args is None:
        message = pack_message(message, 3000, args=raw_args)
    else:
        try:
            if "auth_token" in args:
                args.pop("auth_token")
            else:
                args.pop("token")
        except KeyError:
            pass
        args['user_id'] = user_id
        if key == "add":
            """添加查询器"""
            if "car_type" not in args or args['car_type'] == "":
                args['car_type'] = "02"
            try:
                generator = violation_module.VioQueryGenerator.create(**args)
                generator_id = generator.insert()
                message['data'] = str(generator_id)
            except KeyError:
                logger.exception("args: {}".format(str(raw_args)))
                message = pack_message(message, 3000, **raw_args)
            except RepeatError:
                logger.exception("args: {}".format(str(raw_args)))
                message = pack_message(message, 3007, **raw_args)
        elif key == "delete":
            """删除查询器"""
            try:
                object_id = args['_id']
                message = violation_module.VioQueryGenerator.delete_one(object_id=object_id, user_id=user_id)
            except KeyError as e:
                print(e)
                logger.error("参数错误", exc_info=True, stack_info=True)
                message = pack_message(message, 3000, _id=None)
        else:
            message = pack_message(message, 3012, **raw_args)
    return json.dumps(message)


@api_user_blueprint.route("/get_vio_query_shortcuts", methods=['get', 'post'])
@login_required_app
@log_request_args
def get_vio_query_shortcuts(user_id):
    """查询当前用户的所有的查询器"""
    message = {"message": "success"}

    try:
        data = violation_module.VioQueryGenerator.generator_list(user_id)
        message['data'] = data
    except Exception as e:
        print(e)
        message = pack_message(message, 3010, user_id=user_id)
    finally:
        return json.dumps(message)


@api_user_blueprint.route("/query_violation", methods=['post', 'get'])
@login_required_app
@log_request_args
def query_violation(user_id):
    """查询违章记录"""
    message = {"message": "success"}
    args = get_args(request)
    """记录违章查询参数"""
    if args is None:
        message = pack_message(message, 3000, args=args)
    else:
        generator_id = args["_id"]  # 查询器id
        try:
            message = violation_module.VioQueryGenerator.get_prev_query_result(user_id, generator_id)
        except Exception as e:
            message = pack_message(None, 5000, **{"user_id": user_id, "generator_id": generator_id})
            ms = "Server Error: args:user_id={},generator_id={}".format(user_id, generator_id)
            logger.exception(ms, exc_info=True, stack_info=True)
            print(e)
        finally:
            pass
    ms = "违章查询的结果是:{}".format(message)
    logger.info(ms)
    print(ms)
    return json.dumps(message)


@api_user_blueprint.route("/<key>_license_info", methods=['post'])
@login_required_app
@log_request_args
def process_license_info(user_id, key):
    """
    查询/编辑驾驶证信息
    :param user_id: 用户id,ObjectId类型
    :param key:     操作类型,比如update/get 之类的动词
    :return:        json序列化的字典.
    """
    message = {"message": "success"}
    args = get_args(request)
    args = dict() if args is None else args
    """净化参数"""
    if "auth_token" in args:
        args.pop("auth_token")
    if "token" in args:
        args.pop("token")

    if key == "get":
        """查询驾驶证信息"""
        res = User.find_driving_license(user_id)
        if res is None:  # 错误的用户id
            ms = "process_license_info Error: 用户id错误, user_id={}".format(user_id)
            logger.exception(ms)
            message = pack_message(message, 3004, user_id=user_id, key=key)
        else:
            if 'image_url' in res:
                res['image_url'] = request.host_url + res['image_url']
            message['data'] = res
    elif key == "update":
        """更新驾驶证信息"""
        args['user_id'] = user_id
        res = User.set_driving_license(**args)
        if res['message'] == "success":
            pass
        else:
            message = pack_message(message, 6001, **args)
    else:
        message = pack_message(message, 3003, key=key)
    return json.dumps(message)


@api_user_blueprint.route("/<key>_vehicle_info", methods=['post', 'get'])
@login_required_app
@log_request_args
def process_vehicle_info(user_id, key):
    """获取/编辑行车证信息"""
    message = {"message": "success"}
    args = get_args(request)
    args = dict() if args is None else args
    """净化参数"""
    if "auth_token" in args:
        args.pop("auth_token")
    if "token" in args:
        args.pop("token")

    _id = args.get("_id")  # 获取请求的行车证信息的id
    ms = "process_vehicle_info func key:{}, user_id:{}, args:{}".format(key, str(user_id), json.dumps(args))
    print(ms)
    logger.info(ms)
    args['user_id'] = user_id
    if key == "get":
        """获取行车证信息"""
        host_url = request.host_url
        if _id is None:
            """返回行车证信息的列表"""
            obj_list = User.get_usable_license(user_id=user_id)
            for obj in obj_list:
                """按照app段需求整理转换字段名"""
                if 'permit_image_url' in obj:
                    obj['permit_image_url'] = host_url + obj['permit_image_url']
            message['data'] = obj_list
        else:
            """返回单个行车证信息"""
            obj = CarLicense.find_by_id(_id, can_json=True)
            obj = obj.to_flat_dict()
            if obj is None:
                pass
            else:
                """按照app段需求整理转换字段名"""
                if 'permit_image_url' in obj:
                    obj['permit_image_url'] = host_url + obj['permit_image_url']
                else:
                    pass
                message['data'] = obj
    elif key == "edit":
        """编辑行车证信息"""
        if _id is None:
            message = pack_message(message, 3000, _id=_id)
        else:
            args.pop("_id")
            filter_dict = {"_id": _id}
            update = args
            print("filter_dict={}".format(str(filter_dict)))
            print("update={}".format(str(update)))
            result = CarLicense.find_alone_and_update(filter_dict=filter_dict, update=update)
            if result is None:
                message = pack_message(message, 6001, filter_dict=filter_dict, update=update)
            else:
                pass
    elif key == "delete":
        """删除行车证信息"""
        l_id = get_arg(request, "_id")
        user = User.find_by_id(user_id)
        if isinstance(user, User):
            res = None
            try:
                res = user.delete_car_license(l_id=l_id)
            except Exception as e:
                # 删除失败
                ms = "删除行车证失败,l_id:{},错误原因:{}".format(l_id, e)
                logger.exception(ms)
                filter_dict = dict()
                filter_dict['l_id'] = l_id
                filter_dict['error_cause'] = str(e)
                message = pack_message(message, 5000, **filter_dict)
            finally:
                if not res:
                    error_cause = "没有返回正确的结果,请查询系统日志"
                    logger.exception(error_cause)
                    message = pack_message(message, 5000, error_cause=error_cause)
        else:
            e = "错误的用户id:{}".format_map(user_id)
            message = pack_message(message, 3000, error_cause=e)
    else:
        message = pack_message(message, 3012, key=key)
    print(message)
    return json.dumps(message)


@api_user_blueprint.route("/get_vio_query_history", methods=['post', 'get'])
@login_required_app
@log_request_args
def get_vio_query_history_func(user_id):
    """获取行车证中，和违章查询器有关的输入字段的历史"""
    message = {"message": "success"}
    data = violation_module.VioQueryGenerator.get_input_history(user_id)
    message['data'] = data
    return json.dumps(message)


@api_user_blueprint.route("/query_geo_coordinate", methods=['post', 'get'])
def query_geo_coordinate_func():
    """根据城市和地址查询经纬度"""
    city = get_arg(request, "city", None)
    address = get_arg(request, "address", None)
    message = {"message": "success"}
    if city is None or address is None:
        message = pack_message(message, 3000, city=city, address=address)
    else:
        data = Position.query(city, address)
        message['data'] = data
    return json.dumps(message)


@api_user_blueprint.route("/privacy_policy")
def privacy_policy_func():
    """app端隐私条款"""
    return render_template("app/privacy_policy.html")


@api_user_blueprint.route("/get_security_index", methods=['post', 'get'])
@login_required_app
def get_security_index_func(user_id) -> str:
    """
        根据用户id查询安全指数
        :param user_id: 用户id,由login_required_app装饰器返回.
    """
    """获取安全指数暂定格式如下:
        mes = {
            "message": "success",             # 返回状态标识, 字符串,
            "data": {
                "sum_time": 90,               # 全部时间, float类型.单位:分钟
                "sum_mile": 90,               # 全部历程, float类型.单位:公里
                "avg_speed": 78,              # 平均速度, float类型.单位:公里/小时
                "avg_cost": 77,               # 平均时间, float类型.单位:分钟.目前此返回值的实际意义待定.
                "indexes": [                  # 安全指数的集合,数组/列表形式,子元素为键值对对象.每个子元素代表一个安全指数的实例.
                    {
                        "idx_1": 62.0,        # 疲劳驾驶(指数),int类型,百分制.
                        "idx_2": 76.0,        # 驾驶行为(指数),int类型,百分制.
                        "idx_3": 84.0,        # 生活习惯(指数),int类型,百分制.
                        "idx_4": 67.0,        # 情绪状态(指数),int类型,百分制.
                        "idx_5": 75.0,        # 驾驶时长(指数),int类型,百分制.
                        "idx_6": 79.0         # 驾驶里程(指数),int类型,百分制.
                    },
                    {
                        "idx_1": 67.0,
                        "idx_2": 72.0,
                        "idx_3": 73.0,
                        "idx_4": 59.0,
                        "idx_5": 57.0,
                        "idx_6": 75.0
                    },
                    .....

                ]
            }
        }
    """
    message = {"message": "success"}
    count = get_arg(request, "count", None)  # 返回几个报告? 默认是2个.,非必须参数.
    try:
        count = int(count)
    except ValueError as e:
        print(e)
        count = 2
    except TypeError as e:
        print(e)
        count = 2
    finally:
        data = security_module.SecurityLevel.get_security_indexes(user_id, count)
        message['data'] = data
    return json.dumps(message)


@api_user_blueprint.route("/get_security_rank_list", methods=['post', 'get'])
@login_required_app
def get_security_rank_list_func(user_id) -> str:
    """
        根据用户id查询安全等级排名
        :param user_id: 用户id,由login_required_app装饰器返回.
        :return:
        成功：{"message": "success"， “data”：[dict, dict,]}
        失败：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
    """
    """字典说明:
        public int rank; 排名
        public int scr_synt; 驾驶综合分数
        public String driver_name; 司机姓名
        public String url_avatar； 司机头像地址
    example:
    {
    'rank': '441', 
    'url_avatar': 'http://127.0.0.1:5000/static/image/head_img/default_01.png', 
    'scr_synt': '70', 
    'driver_name': '李四'
    }
    """
    message = {"message": "success"}
    # user_id = ObjectId('5ab0ad831315e00e3cb61c62')  # 新振兴李侠
    prefix = Company.get_prefix_by_user_id(user_id)
    host_url = request.host_url
    try:
        begin_date = datetime.datetime.now().strftime("%F")
        """个人排名数据"""
        my_report = security_module.SecurityReport.query_report2(prefix=prefix, user_id=user_id, report_type="rank", size=1)
        """精简个人排名数据"""
        mes = security_module.SecurityReport.query_report2(prefix=prefix, report_type="rank", size=15, begin_date=begin_date)
        """团队排名数据"""
        res = list()
        my_rank = dict()
        if len(mes) == 0:
            pass
        else:
            """查询头像地址"""
            ids = [ObjectId(x['_source']["id"]) for x in mes]
            if user_id not in ids:
                ids.append(user_id)
            imgs = User.find_plus(filter_dict={"_id": {"$in": ids}}, projection=['head_img_url'], to_dict=True,
                                  can_json=True)
            imgs = {x["_id"]: x["head_img_url"] for x in imgs}

            if len(my_report) == 0:
                pass
            else:
                my_report = my_report[0]['_source']
                my_rank['rank'] = my_report['drive_rank']
                my_rank['scr_synt'] = my_report['drive_score']
                my_rank['driver_name'] = my_report['username'] if my_report.get('real_name') is None else \
                    my_report.get('real_name')
                my_rank['url_avatar'] = "{}{}".format(host_url, imgs[my_report['id']])
            for x in mes:
                s = x['_source']
                t = dict()
                t['rank'] = s['drive_rank']
                t['scr_synt'] = s['drive_score']
                t['driver_name'] = s['username'] if s.get('real_name') is None else s.get('real_name')
                t['url_avatar'] = "{}{}".format(host_url, imgs[s['id']])
                res.append(t)
        message['data'] = res       # top10
        message['myself'] = my_rank  # 个人排名数据
    except Exception as e:
        logger.exception(e)
        message = pack_message(message, 5000, user_id=user_id)
    return json.dumps(message)


@api_user_blueprint.route("/get_report_detail", methods=['post', 'get'])
@login_required_app
def get_report_detail_func(user_id) -> str:
    """
    根据安全报告id查询安全报告详细内容.
    :param user_id: 用户id,由login_required_app装饰器返回.用于和report配合确认身份.(防止查别人的报告详细)
    return:
       mes = {'message': 'success',                                # 返回状态标识, 字符串,
              'data':                                              # 安全报告详细内容
                      {
                      'begin_date': '2017-11-12',                  # 报告的开始日期,
                      'end_date': '2017-11-12',                    # 报告的结束日期,
                      'create_date': '2017-11-13 12:00:05.340',  # 报告的生成日期,
                      'sum_mile': 7406.0,                          # 行驶里程, float类型.单位:公里.
                      'sum_time': 688,                             # 行驶时间, float类型.单位:分钟.
                      'scr_synt': 72,                              # 综合分数, float类型,百分制
                      'idx_slep': 0,                               # 睡眠 0好 1坏
                      'idx_mood': 0,                               # 情绪 0好 1坏
                      'idx_heal': 0,                               # 健康 0好 1坏



                      'cnt_make_call': 1,                          # 打电话次数
                      'cnt_play_phon': 3,                          # 看手机
                      'cnt_fati_driv': 1,                          # 疲劳驾驶次数
                      'cnt_shar_turn': 1,                          # 急转弯次数. int类型.
                      'cnt_rapi_acce': 0,                          # 急加速次数. int类型.
                      'cnt_over_sped': 6,                          # 超速次数. int类型.
                      'cnt_sudd_brak': 6,                          # 急刹车次数. int类型.
                      'poly': [                                    # 本次报告相关的行车轨迹的数组.
                               {
                                'pr': '',                          # 字符串,坐标数据是来自gps还是lbs(基于位置的服务/基站)?默认空.
                                'tm': '2017-12-12 12:12:12',       # 时间,字符串格式,精确到毫秒级
                                'lo': 121.234522,                  # 经度,浮点.
                                'la': 31.345672,                   # 纬度,浮点.
                                'al': 0.0,                         # 高度/海拔,单位:米, 浮点,默认值0.0, 暂不提供.
                                'sp': 0.0,                         # 速度 ,单位:公里/小时,浮点,默认0.0,暂不提供.
                                'br': 0.0                          # 方位,浮点,默认0.0, 暂不提供.
                               },
                               ......
                                 ]
                      }
            }
    """
    message = {"message": "success"}
    begin = datetime.datetime.now()
    report_id = get_arg(request, "report_id", None)  # 报告id,必须参数.
    if report_id is None:
        pass
    data = security_module.SecurityReport.get_report_detail(report_id, user_id)
    """查询ai模块"""
    prefix = Company.get_prefix_by_user_id(user_id)
    prefix = "sf" if prefix is None else prefix
    try:
        user_id = '5a3b3cd5db122cd9fbc21c40'
        report = security_module.SecurityReport.query_report2(prefix=prefix, user_id=user_id, size=1)
        if len(report) == 0:
            pass
        else:
            """把报告内容附加到档案中"""
            report = report[0]['_source']
    except Exception as e:
        print(e)
        logger.exception("get_report_detail_func Error:")
        message = pack_message(message, 3010, user_id=user_id)
    finally:
        data['scr_synt'] = report['drive_score']  # 安全得分
    url_root = request.url_root
    url_poly = data['url_poly']
    url_poly = "{}static/image/poly_image/{}".format(url_root, url_poly)
    data['url_poly'] = url_poly
    poly = Track.get_tracks_list(user_id=user_id, for_app=True)
    data['poly'] = poly['track_list']
    message['data'] = data
    end = datetime.datetime.now()
    seconds = (end - begin).microseconds
    resp = json.dumps(message)
    ms = "get_report_detail func is running args: user_id={}, report_id={}, begin={}, end={}, seconds={}".\
        format(user_id, report_id, begin, end, seconds)
    print(ms)
    logger.info(ms)
    return resp


@api_user_blueprint.route("/get_safety_report_history", methods=['post', 'get'])
@login_required_app
def get_safety_report_history_func(user_id) -> str:
    """
    安全报告历史查询,此接口将会替代 << 安全报告列表查询 >>接口的功能
    :param user_id:
    :return:
    """
    message = {"message": "success"}
    host_url = request.host_url
    end_date = get_arg(request, "end_date", None)
    begin_date = get_arg(request, "begin_date", None)
    if end_date is None:
        end_date = datetime.datetime.today()
    else:
        end_date = datetime.datetime.today() if mongo_db.get_datetime_from_str(end_date) is None \
            else mongo_db.get_datetime_from_str(end_date)
    begin_date = None if begin_date is None else mongo_db.get_datetime_from_str(begin_date)
    report_history = list()
    try:
        report_history = security_module.SecurityReport.get_report_history(user_id=user_id, end_day=end_date,
                                                                       begin_day=begin_date, can_json=True)
    except Exception as e:
        logger.exception("get_safety_report_history_func Error:")
        error_info = "错误消息:{}".format(e)
        message['message'] = error_info
        print(e)
    finally:
        url_root = request.url_root
        for x in report_history:
            url_poly = x['url_poly']
            url_poly = "{}static/image/poly_image/{}".format(url_root, url_poly)
            x['url_poly'] = url_poly
        message['data'] = report_history
        return json.dumps(message)


@api_user_blueprint.route("/get_ship_weather", methods=['post', 'get'])
@login_required_app
def get_ship_weather_func(user_id) -> str:
    """
    根据用户的id,找到用户最后的位置坐标,然后比对最接近的路线.查询该路线的天气.
    测试阶段,目前只能返回固定的线路的天气.
    :param user_id: 用户id
    :return:
    """
    message = {"message": "success"}
    route_id = ObjectId("5a052d294660d327825df124")
    weather_list = RouteWeather.get_route_weather(route_id)
    message['data'] = weather_list
    return json.dumps(message)


@api_user_blueprint.route("/track_thumb.html", methods=['get'])
@login_required_app
def track_thumb_func():
    """
    给app用的,原本用来截图轨迹的路径的,测试中发现截图速度太慢,这个暂时停用.
    :return:
    """
    report_id = get_arg(request, "report_id", None)  # 安全报告id
    end_date = datetime.datetime.strptime("2017-10-24", "%Y-%m-%d")
    tracks = Track.get_tracks_list("59895177de713e304a67d30c", end=end_date)['track_list']
    tracks = [x["loc"] for x in tracks]
    return render_template("app/track_thumb.html", tracks=tracks)


@api_user_blueprint.route("/get_daily_info", methods=['get', 'post'])
@login_required_app
def get_daily_info_func(user_id) -> str:
    """
    获取每日报告扼要
    用户获取最后一次安全报告中的简要信息
    :return: json化的字典
    """
    message = {"message": "success"}
    prefix = Company.get_prefix_by_user_id(user_id)
    prefix = "sf" if prefix is None else prefix
    try:
        user_id = '5a3b3cd5db122cd9fbc21c40'
        report = security_module.SecurityReport.query_report2(prefix=prefix, user_id=user_id)
        archive = dict()
        if len(report) == 0:
            pass
        else:
            """把报告内容附加到档案中"""
            _source = report[0]['_source']
            archive['_id'] = _source['id']  # id
            archive['td_miles'] = int(float(_source['drive_distance'].rstrip("km")))  # 总里程    公里, 注意,这是个str
            archive['td_fuels'] = _source['oil_cost']  # 油耗     升/百公里
            archive['synt'] = _source['drive_score']  # 驾驶得分
            archive['td_rank'] = _source['drive_rank']  # 排名
        message['data'] = archive
    except Exception as e:
        print(e)
        logger.exception("get_daily_info_func Error:")
        message = pack_message(message, 3010, user_id=user_id)
    finally:
        return json.dumps(message)


@api_user_blueprint.route("/<key>_alert_message", methods=['post', 'get'])
@login_required_app
def process_alert_message_func(user_id, key):
    """app端查询推送的消息,示范接口,具体细节未落实"""
    mes = dict({"message": "success"})
    if key == "get":
        """
        查询推送的消息
        data = {
            "ticker": "demo滚动消息",                                # 收到消息的时候,通知栏的一次滚动消息
            "title": "推动消息demo标题",                              # 标题
            "detail": "推送消息demo的详细内容",                        # 内容
            "url": "http://pltf.safeogo.rg/api/alert_message"       # 详情页面
        }
        """
        now = datetime.datetime.now()
        filter_dict = {
            "effective_time": {"$gte": now}
        }
        alert = Message.find_one_plus(filter_dict=filter_dict, instance=True)
        if isinstance(alert, Message):
            mes_id = alert.get_id()
            data = alert.to_flat_dict()
            """标记已读"""
            filter_dict = {"_id": mes_id}
            update_dict = {"$set": {"effective_time": datetime.datetime.now()}}
            Message.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
        else:
            data = dict()
        mes['data'] = data
    elif key == "add":
        args = get_args(request)
        if "title" in args and "detail" in args:
            try:
                alert = Message(**args)
                alert.save()
            except Exception as e:
                print(e)
                logger.exception("process_alert_message_func Error:", exc_info=True, stack_info=True)
                mes = pack_message(mes, 6001, **args)
            finally:
                pass
    else:
        mes = pack_message(mes, 3003, key=key)
    return json.dumps(mes)


@api_user_blueprint.route("/online_surplus", methods=['post', 'get'])
@login_required_app
@log_request_args
def process_online_surplus_func(user_id):
    """在线时长的接口"""
    mes = {"message": "success"}
    """上传在线时常.单位:分钟"""
    online_time = get_arg(request, "duration", None)
    if online_time is None:
        """获取在线时间"""
        f = {"_id": user_id}
        r = User.find_one_plus(filter_dict=f, projection=['online_time'], instance=False)
        if r is None:
            mes['data'] = 0
        else:
            mes['data'] = 0 if r.get("online_time") is None else r['online_time']
    else:
        """上传在线时间"""
        try:
            online_time = float(online_time)
        except ValueError as e:
            print(e)
            logger.exception("错误的在线时长:{}".format(online_time))
            mes = pack_message(mes, 3001, duration=online_time)
        finally:
            if isinstance(online_time, float):
                f = {"_id": user_id}
                u = {"$set": {"online_time": online_time}}
                User.find_one_and_update_plus(filter_dict=f, update_dict=u)
            else:
                mes = pack_message(mes, 5000, duration=online_time)
    return json.dumps(mes)