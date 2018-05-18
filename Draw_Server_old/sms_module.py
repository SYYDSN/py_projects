# -*- coding: utf-8 -*-
from uuid import uuid1
import datetime
import json
import requests
import urllib.request
import hmac
import hashlib
import base64
from log_module import get_logger
import random
from werkzeug.contrib.cache import RedisCache


logger = get_logger()
cache = RedisCache()
REGION = "cn-hangzhou"  # 暂时不支持多region
# ACCESS_KEY_ID = "LTAI3gQfeexbJGdU"
ACCESS_KEY_ID = "LTAIWn0xLJBMOors"
# ACCESS_KEY_SECRET = "bMWC9VJc6Ek9Q63davYpkSTQEPifzJ"
ACCESS_KEY_SECRET = "4uqurgDcvgkrsZ3vPe19ie9UW4xTbP"
TEMPLATE_CODE = "SMS_109375360"
MIN_CODE = 1111
MAX_CODE = 9999


def __save_sms_code(phone: str, sms_code: str) -> None:
    """
    把短信和手机号码的对应关系存入缓存,2分钟内只能发一次.短信有效周期15分钟
    :param phone: 
    :param sms_code: 
    :return: 
    """
    key = "sms_code_{}".format(phone)
    old = {"sms_code": sms_code, "create_date": datetime.datetime.now()}
    cache.set(key, old, timeout=60 * 15)
    

def check_sms_code(phone: str, sms_code: str) -> bool:
    """
    检查手机短信密码是否正确,正确返回True,这个用来验证短信验证码的
    old = {'sms_code","1245","create_date":"2017-11-11 11:1:10"}
    验证码和生成的时间
    :param phone: 
    :param sms_code: 
    :return: 
    """
    result = False
    if isinstance(phone, (str, int)) and isinstance(sms_code, (str, int)):
        phone = phone if isinstance(phone, str) else str(phone)
        sms_code = sms_code if isinstance(sms_code, str) else str(sms_code)
        if check_phone(phone):
            key = "sms_code_{}".format(phone)
            old = cache.get(key)
            if old is None:
                pass
            else:
                old_sms_code = old['sms_code']
                if old_sms_code == sms_code:
                    result = True
                    cache.delete(key)  # 注册成功删验证码
                else:
                    pass
        else:
            pass
    else:
        pass
    return result


def send_sms(phone: str) -> dict:
    """
    检查一个号码是否刚刚发过短信?如果是2分钟内发过短信的,就不允许再发送.否则.就发送短信
    :param phone: 
    :return: 状态字典.
    """
    message = {"message": "success"}
    if check_phone(phone):
        key = "sms_code_{}".format(phone)
        old = cache.get(key)
        if old is None:
            pass
        else:
            old_create_date = old['create_date']
            delta = (datetime.datetime.now() - old_create_date).total_seconds()
            if delta > (60 * 2):
                pass
            else:
                message['message'] = "发送过于频繁,请等待{}秒再试".format(60 * 2 - int(delta))
    else:
        message['message'] = "手机号码错误:{}".format(phone)
    """检查是否可以发短信"""
    if message['message'] == "success":
        """可以发送短信"""
        flag = __send_sms(phone)
        if flag:
            pass
        else:
            message['message'] = "短信发送失败"
    else:
        pass
    return message


def __get_sms_code() -> str:
    """
    获取验证码
    :return:
    """
    num = str(random.randint(MIN_CODE, MAX_CODE))
    return num


def check_phone(phone):
    """检查手机号码的合法性，合法的手机返回True"""
    if phone is None:
        return False
    elif isinstance(phone, str) or isinstance(phone, int):
        phone = str(phone).strip()
        if len(phone) == 11 and phone.startswith("1"):
            try:
                int(phone)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return False


def special_url_encode(url: str) -> bytes:
    """
    针对签名的特殊编码,阿里接口专用
    :param url:
    :return:
    """
    res = urllib.request.quote(url, safe="")
    res = res.replace("+", "%20")
    res = res.replace("*", "%2A")
    res = res.replace("%7E", "~")
    return res


def __send_sms(phone: str) -> bool:
    """
    发送短信
    :param phone: 手机号码
    :return:
    """
    sms_code = __get_sms_code()
    if not check_phone(phone):
        return False
    else:
        delta = datetime.timedelta(hours=8)
        time_str = (datetime.datetime.now() - delta).strftime("%Y-%m-%d %H:%M:%S ")
        print(time_str)
        args = {
            "SignatureMethod": "HMAC-SHA1", "SignatureNonce": uuid1().hex,
            "AccessKeyId": ACCESS_KEY_ID, "SignatureVersion": "1.0",
            "Timestamp": time_str,
            "Action": "SendSms", "Version": "2017-05-25",
            "RegionId": "cn-hangzhou", "PhoneNumbers": phone,
            "SignName": "盛汇", "TemplateCode": "SMS_109375360",
            "TemplateParam": json.dumps({"code": str(sms_code)})
                }
        arg_str = ""
        args = [(k, v) for k, v in args.items()]
        args.sort(key=lambda obj: obj[0])
        for arg in args:
            print(arg)
            arg_str += "&{}={}".format(special_url_encode(arg[0]), special_url_encode(arg[1]))
        arg_str = arg_str.lstrip("&")  # sortQueryString
        print(arg_str)  # 第三步：构造待签名的请求串完成.
        string_to = "GET&{}&{}".format(special_url_encode("/"), special_url_encode(arg_str))  # 待签名串
        print(string_to)
        sign = hmac.new("{}&".format(ACCESS_KEY_SECRET).encode("utf-8"), string_to.encode("utf-8"), hashlib.sha1).digest()
        sign = base64.b64encode(sign).decode()
        sign = "Signature={}&".format(special_url_encode(sign))
        arg_str = sign + arg_str
        send_result = False
        try:
            r = requests.get("http://dysmsapi.aliyuncs.com/?{}".format(arg_str))
            if r.status_code == 200:
                ok = r.text.split("<Code>", 1)[-1].split("</Code>")[0]
                if ok.lower() == "ok":
                    """发送成功"""
                    __save_sms_code(phone, sms_code)  # 保存结果
                    print("sms code: {}".format(sms_code))
                    send_result = True
                else:
                    ms = "sms send error, return content:{}".format(r.text)
                    print(ms)
                    logger.exception(ms)
            else:
                ms = "sms send error, server code:{}".format(r.status_code)
                logger.exception(ms)
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            return send_result


if __name__ == "__main__":
    pass