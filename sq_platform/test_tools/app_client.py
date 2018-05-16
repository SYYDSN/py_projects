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


def test_check_version():
    """测试检查新版本"""
    url = "http://127.0.0.1:5000/api/check_version"
    r = requests.post(url)
    print(r.json())


def test_get_security_rank_list():
    """测试用户安全指数排名接口"""
    auth_token = "f40bc71e130c48f4bcebff1169dfe22a" # app段登录标识 me
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
    auth_token = "f40bc71e130c48f4bcebff1169dfe22a"  # app段登录标识
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_daily_info", headers=headers)
    print(res.json())


def test_get_user_info():
    """
    测试获取用户信息
    :return:
    """
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    # url = "http://safego.org:5000/api/get_vio_query_shortcuts"
    url = "http://127.0.0.1:5000/api/get_user_info"
    res = requests.post(url, headers=headers)
    print(res.json())


def test_get_vio_query_shortcuts():
    """
    测试获取违章查询器列表
    :return:
    """
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    # url = "http://safego.org:5000/api/get_vio_query_shortcuts"
    url = "http://127.0.0.1:5000/api/get_vio_query_shortcuts"
    res = requests.post(url, headers=headers)
    print(res.json())


def test_query_violation():
    """
    测试违章查询
    :return:
    """
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    # auth_token = "47a55e628931458fb70773badbe063ba"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    # args = {"_id": "5af55414e39a7b7691355f41"}   #
    args = {"_id": "5af938984660d345c070c1c7"}   #
    url = "http://safego.org:5000/api/query_violation"
    url = "http://127.0.0.1:5000/api/query_violation"
    res = requests.post(url, data=args, headers=headers)
    print(res.json())


def test_upload_user_permit_image():
    """测试用户上传行车证图片"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    img_path = "/home/walle/图片/img_mingcheng.png"
    # img_path = "/home/walle/图片/general_dict.png"
    file = open(img_path, 'rb')
    files = {"permit_image": file}
    url = "http://127.0.0.1:5000/api/upload_permit_image"
    # url = "http://safego.org:5000/api/upload_permit_image"
    res = requests.post(url, files=files, headers=headers)
    print(res.json())


def test_edit_user_permit_image():
    """测试用户编辑行车证图片"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    img_path = "/home/walle/图片/img_mingcheng.png"
    # img_path = "/home/walle/图片/general_dict.png"
    file = open(img_path, 'rb')
    files = {"permit_image": file}
    args = {"_id": "5af92f1c4660d33d13be1933", "plate_number": "沪A12345"}  # 行车证id
    url = "http://127.0.0.1:5000/api/upload_permit_image"
    # url = "http://safego.org:5000/api/upload_permit_image"
    res = requests.post(url, files=files, data=args, headers=headers)
    print(res.json())


def test_delete_user_vehicle_info():
    """测试用户删除行车证"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    args = {"_id": "5a9f90324660d33e27146332"}
    url = "http://127.0.0.1:5000/api/delete_vehicle_info"
    # url = "http://safego.org:5000/api/delete_vehicle_info"
    res = requests.post(url, data=args, headers=headers)
    print(res.json())


def test_upload_user_driving_license():
    """测试用户上传驾驶证信息"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    img_path = "/home/walle/图片/2017-10-31 08-39-52屏幕截图.png"
    file = open(img_path, 'rb')
    files = {"license_image": file}
    res = requests.post("http://127.0.0.1:5000/api/upload_license_image", files=files, headers=headers)
    print(res.json())


def test_update_user_driving_license():
    """测试更新用户驾驶证信息"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
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


def test_get_car_license():
    """测试获取用户行车证信息"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    auth_token = "12b9b21c959140f3af79ce56bf30a7e1"  # app段登录标识 有问题的测试手机
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_vehicle_info", headers=headers)
    print(res.json())


def test_get_user_driving_license():
    """测试获取用户驾驶证信息"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    res = requests.post("http://127.0.0.1:5000/api/get_license_info", headers=headers)
    print(res.json())


def test_add_driving_data():
    """测试用户上传行车数据的压缩文件"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    files = {"driving_data": open("/home/walle/work/temp/2018_03_02_12_41_35.zip", "rb")}
    res = requests.post("http://127.0.0.1:5000/api/add_driving_data", headers=headers, files=files)
    print(res.json())


def test_gps_push():
    """测试是是上传gps数据"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
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
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
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
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://safego.org:5000/api/get_alert_message"
    r = requests.post(url, headers=headers)
    print(r.json())


def test_get_report_detail():
    """测试获取安全报告详情"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431" # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/get_report_detail"
    # url = "http://safego.org:5000/api/get_report_detail"
    r = requests.post(url, headers=headers, data={"hello": "world"})
    j = r.json()
    if 'data' in j:
        rs = j['data']
        for k, v in rs.items():
            print(k, v)
    else:
        print(j)


def test_get_safety_report_history():
    """测试获取安全报告历史"""
    auth_token = "a98d8bb4840c42e3993ccc6d6c79d431"  # app段登录标识 me
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/get_safety_report_history"
    # url = "http://safego.org:5000/api/get_safety_report_history"
    r = requests.post(url, headers=headers, data={"hello": "world"})
    j = r.json()
    if 'data' in j:
        rs = j['data']
        for item in rs:
            for k, v in item.items():
                print(k, v)
    else:
        print(j)


if __name__ == "__main__":
    # args = {
    #     "url": "http://127.0.0.1:5000/api/get_daily_info",
    #     "method": "post",
    #     "user_id": "59cda886ad01be237680e28e"
    # }
    """测试检查新版本"""
    test_check_version()
    """测试获取用户信息"""
    # test_get_user_info()
    """测试获取每日报告"""
    # test_get_daily_info()
    """测试获取违章查询器列表"""
    # test_get_vio_query_shortcuts()
    """测试违章查询"""
    # test_query_violation()
    """测试获取用户行车证信息"""
    # test_get_car_license()
    """测试用户上传行车证图片"""
    # test_upload_user_permit_image()
    """测试用户删除行车证"""
    # test_delete_user_vehicle_info()
    """测试用户编辑行车证图片"""
    # test_edit_user_permit_image()
    """测试用户上传驾驶证"""
    # test_upload_user_driving_license()
    """测试更新用户驾驶证信息"""
    # test_update_user_driving_license()
    """测试获取用户驾驶证信息"""
    # test_get_user_driving_license()
    """测试用户安全指数排名接口"""
    # test_get_security_rank_list()
    """测试用户上传行车数据的压缩文件"""
    # test_add_driving_data()
    """测试获取安全报告详情"""
    # test_get_report_detail()
    """测试获取安全报告历史"""
    # test_get_safety_report_history()
    pass