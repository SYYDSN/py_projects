# -*- coding: UTF-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import time
from hashlib import md5
import requests
import random
from mongo_db import cache
from log_module import get_logger
import datetime


logger = get_logger()


class SmsApp(object):
    url = "http://www.api.zthysms.com/sendSms.do"
    username = "soooqooohy"
    password = "KDXKeo"
    verify_code = ''
    mobile = ''
    content = ''
    xh = ''

    def __init__(self):
        None

    def sms(self, mobile, verify_code):
        self.mobile = mobile
        self.verify_code = verify_code

        self.content = "您的验证码是:".encode('utf-8') + str(self.verify_code).encode('utf-8') + ",请在30分钟内验证【苏秦网络.保驾犬】".encode(
            'utf-8')

        tkey = time.strftime('%Y%m%d%H%M%S')
        pmd5 = md5(self.password.encode()).hexdigest() + tkey
        omd5 = md5(pmd5.encode()).hexdigest()

        param = "url=" + self.url + "&username=" + self.username + "&password=" + omd5 + "&tkey=" + tkey + "&mobile=" + self.mobile + "&content=" + self.content.decode() + "&xh=" + self.xh;
        result = requests.post(self.url, data={'username': self.username,
                                               'password': omd5,
                                               'tkey': tkey,
                                               'mobile': self.mobile,
                                               'content': self.content,
                                               'xh': self.xh})
        if result.status_code == 200:
            print(mobile, verify_code)
        else:
            print(result.status_code)
        return result.text


def __send_sms(phone_num):
    """发送手机短信"""
    message = {"message": "success"}
    validate_code = random.randint(1111, 9999)
    sms_client = SmsApp()
    result = sms_client.sms(phone_num, validate_code)
    status_code = result.split(",")[0]
    if status_code == "1":
        key = "sms_{}".format(phone_num)
        cache.set(key, validate_code, timeout=60 * 30)
    elif status_code == "20":
        message['message'] = "余额不足"
    else:
        message['message'] = "短信发送失败:错误代码{}".format(status_code)
    return message


def send_sms(phone_num):
    """发送短信并检查短信发送的请求是否合法，用户发送短信时请调用次方法"""
    """一天最多允许发送10次短信"""
    max_time = 10  # 24小时内的最大短信发送次数
    interval = 60  # 短信发送间隔
    message = {"message": "success"}
    key = "sms_send_time_{}".format(phone_num)  # 用于计数的key的前缀
    recode_list = list()
    for i in range(max_time):
        sub_key = "{}_{}".format(key, str(i))
        val = cache.get(sub_key)
        if val is None:
            break
        else:
            recode_list.append(val)
    if len(recode_list) == 0:
        message = __send_sms(phone_num)
        if message['message'] == "success":
            """计数"""
            temp_key = "{}_{}".format(key, str(len(recode_list)))
            cache.set(temp_key, datetime.datetime.now(), timeout=60 * 24)
    elif 0 < len(recode_list) < max_time:
        now = datetime.datetime.now()
        prev = recode_list[-1]
        seconds = (now - prev).total_seconds()
        """检查发送间隔"""
        if seconds < interval:
            message['message'] = "短信发送频繁，请等待{}秒后再试".format(int(interval - seconds))
        else:
            message = __send_sms(phone_num)
            if message['message'] == "success":
                """计数"""
                temp_key = "{}_{}".format(key, str(len(recode_list)))
                cache.set(temp_key, datetime.datetime.now(), timeout=60 * 24)
    else:
        message['message'] = "已超本日短信最大发送次数"
    return message


def validate_sms(phone_num, validate_code):
    """验证用户输入的短信验证码是否正确"""
    message = {"message": "success"}
    key = "sms_{}".format(phone_num)
    raw_code = cache.get(key)
    if raw_code is None:
        message['message'] = "验证失败"
    elif isinstance(validate_code, int):
        if validate_code != raw_code:
            message['message'] = "验证码错误"
        else:
            pass
    elif isinstance(validate_code, str) and validate_code.isdigit():
        if int(validate_code) != raw_code:
            message['message'] = "验证码错误"
        else:
            pass
    else:
        message['message'] = "未知错误"
    return message


def clear_sms_code(phone_num):
    """清除手机对应的验证码"""
    key = "sms_{}".format(phone_num)
    cache.delete(key)


if __name__ == '__main__':
    phoneNum = '15618317376'
    pass