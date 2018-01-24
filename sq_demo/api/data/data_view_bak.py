# -*- coding:utf-8 -*-
from flask import Blueprint, abort, request
from api.data import item_module
from tools_module import *
import json
from bson.objectid import ObjectId
from mongo_db import BaseDoc

api_data_blueprint = Blueprint("api_data_blueprint", __name__, url_prefix="/api", template_folder="templates")


@api_data_blueprint.route("/gps_push", methods=['get', 'post'])
def gps_push():
    """接收设备发来的gps信息"""
    args = get_args(request)
    gps = item_module.GPS(**args)
    message = {"message": "success"}
    try:
        result = gps.insert()
        if isinstance(result, ObjectId):
            pass
        else:
            message['message'] = '插入失败'
    except ValueError as e:
        error_col, error_val = e.args[0].split(" ")[-1].split(":")
        message['message'] = "{}的值 {} 重复".format(error_col, error_val)
    finally:
        return json.dumps(message)


@api_data_blueprint.route("/sensor_push", methods=['get', 'post'])
def sensor_push():
    """接收设备的传感器发来的信息"""
    args = get_args(request)
    sensor = item_module.Sensor(**args)
    message = {"message": "success"}
    try:
        result = sensor.insert()
        if isinstance(result, ObjectId):
            pass
        else:
            message['message'] = '插入失败'
    except ValueError as e:
        error_col, error_val = e.args[0].split(" ")[-1].split(":")
        message['message'] = "{}的值 {} 重复".format(error_col, error_val)
    finally:
        return json.dumps(message)
