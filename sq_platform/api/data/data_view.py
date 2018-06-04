# -*- coding:utf-8 -*-
import json
import os
from bson.objectid import ObjectId
from flask import Blueprint, abort
from bson.dbref import DBRef
import error_module
from mongo_db import to_flat_dict
from api.data import item_module
from api.data.file_module import unzip_all_user_file
from api.data.item_module import User
from log_module import get_logger
import celery_module
from tools_module import *

api_data_blueprint = Blueprint("api_data_blueprint", __name__, url_prefix="/api", template_folder="templates")

data_dir_path = os.path.join(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0], "static", 'data_file')  # 存储传感器数据文件的路径
if not os.path.exists(data_dir_path):
    os.makedirs(data_dir_path)
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif')  # 运行上传的文件的类型
logger = get_logger()


@api_data_blueprint.route("/token", methods=['post', 'get'])
def test_token():
    """toke测试"""
    token = request.headers.get("auth-token")
    result = {"token": token}
    return json.dumps(result)


@api_data_blueprint.route("/query_error_code", methods=['post', 'get'])
def query_error_code():
    """查询错误代码"""
    error_code = get_arg(request, "error_code", 0)
    message = error_module.ErrorCode.query_error_code(error_code)
    return json.dumps(message)


@api_data_blueprint.route("/gps_push", methods=['post'])
@login_required_app
# @log_request_args
def gps_push(user_id):
    """接收设备发来的实时gps信息"""
    args = get_args(request)
    log_type = "data_view.gps_push"
    info_dict = args.copy()
    message = {"message": "success"}
    token = ''
    try:
        token = args.pop('auth_token')
    except KeyError as e:
        pass
    finally:
        pass
    # calculated_user_id = AppLoginToken.get_id_by_token(token)
    if user_id:
        args['user_id'] = DBRef(collection="user_info", database="platform_db", id=user_id)
        info_dict = args.copy()
        info_dict['result'] = 'before begin'
        info_dict['result'] = 'unknown error'
        """发送给socketio服务器"""
        celery_module.send_last_pio_celery.delay(to_flat_dict(args))
        try:
            args['real_time'] = 1
            result = item_module.GPS.insert_queue(args)
            if result:
                info_dict['result'] = 'success'
            else:
                message = error_module.pack_message(message, 3004, **args)
        except ValueError as e:
            logger.exception("Error: ")
            error_col, error_val = e.args[0].split(" ")[-1].split(":")
            message = error_module.pack_message(message, 6001, **args)
            message['message'] = "{}的值 {} 重复".format(error_col, error_val)
            info_dict['result'] = message['message']
        except Exception as e:
            logger.exception("Error: {}".format(e), exc_info=True, stack_info=True)
            print(e)
            message = error_module.pack_message(message, 5000, **args)
            info_dict['result'] = str(e)
        finally:
            return json.dumps(message)
    else:
        message = pack_message(message, 3009, auth_token=token, user_id=args.get('user_id'))
        info_dict['result'] = message['message']
        return json.dumps(message)


@api_data_blueprint.route("/gps_push_async", methods=['get', 'post'])
@login_required_app
# @log_request_args
def gps_push_async(user_id):
    """接收设备发来的gps信息 异步队列模式"""
    message = {"message": "success"}
    args = get_args(request)
    if args is not None:
        """检查用户身份"""
        token = ''
        try:
            token = args.pop('auth_token')
        except KeyError as e:
            pass
        finally:
            pass
        # calculated_user_id = AppLoginToken.get_id_by_token(token)
        if str(user_id) == args.get('user_id'):
            result = celery_module.save_gps.delay(**args)
            if result is not None and result.status == "SUCCESS":
                if result.info['message'] == "success":
                    pass
                else:
                    message = error_module.pack_message(message, 6001, **args)
            else:
                message = error_module.pack_message(message, 6000, **args)
        else:
            message = pack_message(message, 3009, token=token, user_id=args.get('user_id'))
    else:
        message = error_module.pack_message(message, 3000, args=args)
    return json.dumps(message)


@api_data_blueprint.route("/sensor_push", methods=['get', 'post'])
@login_required_app
# @log_request_args
def sensor_push(user_id):
    """接收设备的传感器发来的信息"""
    args = get_args(request)
    message = {"message": "success"}
    token = ''
    try:
        token = args.pop('auth_token')
    except KeyError as e:
        pass
    finally:
        pass
    # calculated_user_id = AppLoginToken.get_id_by_token(token)
    if str(user_id) == args.get('user_id'):
        sensor = item_module.Sensor(**args)
        try:
            result = sensor.insert()
            if isinstance(result, ObjectId):
                pass
            else:
                message = error_module.pack_message(message, 3004, **args)
        except ValueError as e:
            logger.exception("Error:")
            message = error_module.pack_message(message, 6001, **args)
            error_col, error_val = e.args[0].split(" ")[-1].split(":")
            message['message'] = "{}的值 {} 重复".format(error_col, error_val)
        finally:
            return json.dumps(message)
    else:
        message = pack_message(message, 3009, token=token, user_id=args.get('user_id'))
        return json.dumps(message)


@api_data_blueprint.route("/sensor_push_async", methods=['get', 'post'])
@login_required_app
# @log_request_args
def sensor_push_async(user_id):
    """接收设备的传感器发来的信息 异步队列模式"""
    message = {"message": "success"}
    args = get_args(request)
    if args is not None:
        """检查用户身份"""
        token = ''
        try:
            token = args.pop('auth_token')
        except KeyError as e:
            pass
            print(e)
        finally:
            pass
        # calculated_user_id = AppLoginToken.get_id_by_token(token)
        if str(user_id) == args.get('user_id'):
            result = celery_module.save_gps.delay(**args)
            if result is not None and result.status == "SUCCESS":
                if result.info['message'] == "success":
                    pass
                else:
                    message = error_module.pack_message(message, 6001, **args)
            else:
                message = error_module.pack_message(message, 6000, **args)
        else:
            message = pack_message(message, 3009, token=token, user_id=args.get('user_id'))
    else:
        message = error_module.pack_message(message, 3000, args=args)
    return json.dumps(message)


@api_data_blueprint.route("/<key>_device_info", methods=['get', 'post'])
@login_required_app
# @log_request_args
def process_device_info(user_id, key):
    """处理手机（及其附带的传感器的）信息的增删改查"""
    message = pack_message(error_code=3012, key=key)
    if key == "add":
        """添加一个移动设备的信息，原则上说，如果型号和model相同就认为是同一款手机，但是也不排除同一型号的手机，由于发布时间不同
        厂家私自更改配置的情况"""
        args = get_args(request)
        print(args)
        try:
            args.pop("token")
        except KeyError as e:
            print(e)
        finally:
            if args is None or len(args) == 0:
                message = pack_message()
            else:
                message = {"message": "success"}
                dbref = None
                try:
                    obj = item_module.PhoneDevice(**args)
                    dbref = obj.save_self_and_return_dbref()
                except error_module.RepeatError as e:
                    print(e)
                    message['inserted_id'] = ''
                except Exception as e:
                    logger.exception("process_device_info exception:")
                    print(e)
                    message = pack_message(error_code=5000, **args)
                finally:
                    if dbref is None:
                        pass
                    else:
                        """更新用户信息"""
                        res = User.add_phone_device(user_id=user_id, dbref_obj=dbref)
                        if res:
                            pass
                        else:
                            message = pack_message(error_code=5000, user_id=user_id, **args)
    else:
        """没法识别的key类型"""
        pass

    return json.dumps(message)


@api_data_blueprint.route("/add_driving_data", methods=['post', 'get'])
@login_required_app
@log_request_args
def process_driving_data(user_id):
    """以文件方式保存传感器和gps数据"""
    message = {"message": "success"}
    arg_name = 'driving_data'
    files = request.files
    ms = "{}: user_id: {}, files: {}".format(datetime.datetime.now(), user_id, files)
    logger.info(ms)
    if request.method.lower() == "post" and arg_name in files.keys():
        file = files[arg_name]
        file_name = file.filename.lower()
        prefix_path = os.path.join(data_dir_path, str(user_id))
        if not os.path.exists(prefix_path):
            os.makedirs(prefix_path)
        data_path = os.path.join(data_dir_path, str(user_id), file_name)
        if file is None:
            message = pack_message(message, 3000, arg_name=arg_name)
        else:
            try:
                file.save(data_path)
                celery_module.unzip_file.delay(zip_path=data_path)
            except Exception as e:
                print(e)
                ms = "process_driving_data Error:{}".format(e)
                logger.exception(ms)
                message = pack_message(message, 5001, error_info=str(e))
    else:
        message = pack_message(None, 3000, arg_name=arg_name, files=files)
    return json.dumps(message)


@api_data_blueprint.route("/unzip_all_file", methods=['post', 'get'])
def process_all_zip_file():
    """测试解压缩程序是否正餐工作的非生产函数"""
    key = get_arg(request, "key")
    if key != "dfdK@-03":
        return abort(404)
    else:
        arg = get_arg(request, "delay", False)
        if arg:
            celery_module.unzip_all_file.delay()
            return json.dumps({"message": "异步执行"})
        else:
            unzip_all_user_file()
            return json.dumps({"message": "同步执行"})


if __name__ == "__main__":
    try:
       None.split()
    except Exception as e:
        print(e)
        logger.exception("Error")
        print(e)