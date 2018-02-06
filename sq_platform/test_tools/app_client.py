# -*- coding: utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(project_dir)
if project_dir not in sys.path:
    sys.path.append(project_dir)
import requests
import datetime
from mongo_db import get_obj_id
from api.data import item_module


def test_get_security_rank_list():
    """测试用户安全指数排名接口"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_security_rank_list", headers=headers)
    print(res.json())


def test_req(**kwargs) -> None:
    """测试app客户端的请求"""
    url = kwargs['url']
    user_id = get_obj_id(kwargs['user_id'])
    tk = item_module.AppLoginToken.find_one_plus(filter_dict={"user_id": user_id}, instance=True)
    now = datetime.datetime.now()
    end = tk.get_attr("end_date")
    if (end - now).total_seconds() > 0:
        print(end)
        auth_token = tk.get_attr("token")
        headers = {"auth_token": auth_token}
        r = requests.post(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(data)
        else:
            print(r.status_code)
    else:
        print("token过期")


def test_get_daily_info():
    """
    测试获取每日报告
    :return:
    """
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_daily_info", headers=headers)
    print(res.json())


def test_query_violation():
    """
    测试违章查询
    :return:
    """
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    auth_token = "f4a624cff79d47448fcd41f071297db2"  # app段登录标识
    headers = {"auth_token": auth_token}
    args = {"_id": "59ffb9b5e39a7b293e11d3ca"}
    res = requests.post("http://127.0.0.1:5000/api/query_violation", data=args, headers=headers)
    print(res.json())


def test_upload_user_driving_license():
    """测试用户上传驾驶证信息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    auth_token = "f4a624cff79d47448fcd41f071297db2"  # app段登录标识
    headers = {"auth_token": auth_token}
    img_path = "/home/walle/图片/img_mingcheng.png"
    img_path = "/home/walle/图片/general_dict.png"
    file = open(img_path, 'rb')
    files = {"license_image": file}
    res = requests.post("http://127.0.0.1:5000/api/upload_license_image", files=files, headers=headers)
    print(res.json())


def test_upload_user_permit_image():
    """测试用户上传行车证信息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    img_path = "/home/walle/图片/img_mingcheng.png"
    # img_path = "/home/walle/图片/general_dict.png"
    file = open(img_path, 'rb')
    files = {"permit_image": file}
    args = {"_id": "5a5837cae39a7b2a5da57970"}
    res = requests.post("http://127.0.0.1:5000/api/upload_permit_image", files=files, data=args, headers=headers)
    print(res.json())


def test_update_user_driving_license():
    """测试更新用户驾驶证信息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    args = {
                "license_id": "dfdf54545我的驾驶证id43430as",                 # 驾驶证id
                "license_class": "C1",           # 驾驶证类型/准驾车型
                "address": "上海市嘉定区安亭镇昌吉东路156号",                       # 地址
                "gender": "男",                         # 性别
                "nationality": "中国",                   # 国家
                "birth_date": "1976-12-11",                 # 出生日期
                "first_issued_date": "2000-1-1",   # 首次领证日期
                "valid_date": "2020-12-30"                  # 驾照有效期
            }
    res = requests.post("http://127.0.0.1:5000/api/update_license_info", data=args, headers=headers)
    print(res.json())


def test_get_user_driving_license():
    """测试获取用户驾驶证信息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    auth_token = "f4a624cff79d47448fcd41f071297db2"  # app段登录标识
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_license_info", headers=headers)
    print(res.json())


def test_gps_push():
    """测试是是上传gps数据"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    args = {
    "ct" : "上海市",
    "dt" : "嘉定区",
    "speed" : 0.0,
    "longitude" : 121.172826,
    "be" : 0.0,
    "fl" : "false",
    "app_version" : "1.2.4.0122 Debug",
    "pv" : "上海市",
    "ac" : 15.0,
    "ts" : "2018-01-23 13:25:08.000",
    "latitude" : 31.296939,
    "ad" : "310114",
    "altitude" : 0.0,
    "amap" : "amap",
    "pr" : "lbs"
}
    res = requests.post("http://127.0.0.1:5000/api/gps_push", headers=headers, data=args)
    print(res.json())


def test_add_alert_message():
    """测试发送推送消息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/add_alert_message"
    data = {
        "ticker": "这是一条测试消息",
        "title": "this is a title",
        "detail": "我是正文",
        "url": ""
    }
    r = requests.post(url, data=data, headers=headers)
    print(r.json())


def test_get_alert_message():
    """测试接收推送消息"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://safego.org:5000/api/get_alert_message"
    r = requests.post(url, headers=headers)
    print(r.json())


def test_get_report_detail():
    """测试获取安全报告详情"""
    auth_token = "19be87a739504c6a92bba4c16c89058a"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/get_report_detail"
    url = "http://safego.org:5000/api/get_report_detail"
    r = requests.post(url, headers=headers, data={"hello": "world"})
    j = r.json()
    rs = j['data']
    for k, v in rs.items():
        print(k, v)


if __name__ == "__main__":
    # args = {
    #     "url": "http://127.0.0.1:5000/api/get_daily_info",
    #     "method": "post",
    #     "user_id": "59cda886ad01be237680e28e"
    # }
    # """测试获取每日报告"""
    # test_get_daily_info()
    # """测试违章查询"""
    # test_query_violation()
    # test_req(**args)
    # """测试用户上传行车证"""
    # test_upload_user_permit_image()
    # """测试用户上传驾驶证"""
    # test_upload_user_driving_license()
    # """测试更新用户驾驶证信息"""
    # test_update_user_driving_license()
    # """测试获取用户驾驶证信息"""
    # test_get_user_driving_license()
    # """测试用户安全指数排名接口"""
    # test_get_security_rank_list()
    test_get_report_detail()
    # test_gps_push()
    pass