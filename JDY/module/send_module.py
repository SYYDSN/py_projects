# -*- coding: utf-8 -*-
import requests
import json
from mail_module import send_mail
from log_module import get_logger
import datetime


"""发送消息给钉钉机器人"""


logger = get_logger()
# 钉钉机器人的链接的token
url_map = {
    "财务群钉钉小助手": "ffec4541136ac31d597f128761e84ae84152d0a196cf7f89c5ae303a6d07f052",  # 财务群
    "策略助手 小迅": "f007c608f52b78620a52372764d17b42367e22bef78d6966925fee4fe7f715f6",     # 直播操作建议群
    "推广助手": "9028ccfe1733a13ae6fe97d0f519ba9a53431709231a9bfa33a413f125d8cb56",           # 资源群
    "战报": "b1500b22ff1b8aa35f17a822f37e2b23127c7ad76e7947fbb83fb1391ade69df",   # 电销部门业务群
    "01": "c92cc34ef302a06ba0f3f6c86a1a2a6cb68ab96391a8288f58019d251adec616",   # 一部群
    "02": "20414f8599ff5bc375416013619f26b8787e111d30f7c12f16c782f49b323f3c",   # 二部群
    "03": "e74e25cca0798f5dd8a909059a427a5bae5662b85bd6d04a24b10c1a8176380e",   # 二部群
    "04": "619a8a5f9cd7973d50f1d2c9851f006ce7020f8a1a52f67b1e8669cdff252829",   # 二部群
    "05": "ae36fc1e32276489fc395c9071db3f9d787751f8ff87de9f46e6bc5e4791a6e7",   # 二部群
}


def send_signal(send_data: dict, token_name: str = None) -> bool:
    """
    发送信号
    :param send_data:发动的信息字典
    :param token_name:  token映射的key，对应url_map的key
    :return:
    """
    res = False
    token = url_map.get(token_name)
    if token is None:
        ms = "不存在的token_name:{}".format(token_name)
        now = datetime.datetime.now()
        title = "{}{}".format(ms, now)
        send_mail(title=title)
        logger.exception(ms)
        raise ValueError(ms)
    else:
        data = json.dumps(send_data)
        headers = {'Content-Type': 'application/json'}
        base_url = "https://oapi.dingtalk.com/robot/send?access_token="
        robot_url = "{}{}".format(base_url, token)
        r = requests.post(robot_url, data=data, headers=headers)
        status_code = r.status_code
        if status_code == 200:
            r = r.json()
            if r['errmsg'] == 'ok':
                """success"""
                res = True
            else:
                ms = '发送消息到钉钉机器人失败，错误原因：{}， 参数{}'.format(r['errmsg'], data)
                now = datetime.datetime.now()
                title = "发送消息到钉钉机器人失败{}".format(ms, now)
                send_mail(title=title, content=ms)
                logger.exception(ms)
                raise ValueError(ms)
        else:
            ms = '钉钉机器人没有返回正确的响应，错误代码：{}'.format(status_code)
            now = datetime.datetime.now()
            send_mail(title="{}{}".format(now, ms))
            logger.exception(ms)
            raise ValueError(ms)
    return res


def add_money(group_name: str, sales_name: str, customer_name: str, money: (str, float)) -> None:
    """
    发送加金恭喜消息
    :param group_name: 销售组名
    :param sales_name: 销售员名
    :param customer_name: 客户名
    :param money: 加金数额 （美元）
    :return:
    """
    """
            {
                 "msgtype": "markdown",
                 "markdown": {
                     "title":"杭州天气",
                     "text": "#### 杭州天气 @156xxxx8827\n" +
                             "> 9度，西北风1级，空气良89，相对温度73%\n\n" +
                             "> ![screenshot](http://image.jpg)\n"  +
                             "> ###### 10点20分发布 [天气](http://www.thinkpage.cn/) \n"
                 },
                "at": {
                    "atMobiles": [
                        "156xxxx8827", 
                        "189xxxx8325"
                    ], 
                    "isAtAll": false
                }
             }
            """
    out_put = dict()
    out_put['msgtype'] = 'markdown'
    title = "恭喜加金"
    text = "{}-{}-客户-{}xx,成功入近{}美金。[胜利][胜利][胜利]，继续加油！[加油][加油][加油] <br> ".format(group_name, sales_name,
                                                                                customer_name[0], money)
    markdown = dict()
    markdown['title'] = title
    markdown['text'] = text
    out_put['markdown'] = markdown
    out_put['at'] = {'atMobiles': [], 'isAtAll': False}


def send_reg_info(group_by: str, info: dict) -> dict:
    """
    发送注册信息的钉订消息到各个大部群
    :param group_by:
    :param info:
    :return:
    """
    mes = {"message": "success"}
    if group_by.startswith("01"):
        key = "01"
    elif group_by.startswith("02"):
        key = "02"
    elif group_by.startswith("03"):
        key = "03"
    elif group_by.startswith("04"):
        key = "04"
    elif group_by.startswith("05"):
        key = "05"
    else:
        key = None
    if key is None:
        title = "无效的分组信息: {}, {}".format(group_by, datetime.datetime.now())
        send_mail(title=title)
        print(title)
        return mes
    else:
        token = url_map[key]
        data = json.dumps(info)
        headers = {'Content-Type': 'application/json'}
        base_url = "https://oapi.dingtalk.com/robot/send?access_token="
        robot_url = "{}{}".format(base_url, token)
        try:
            r = requests.post(robot_url, data=data, headers=headers, timeout=5)
            status = r.status_code
            if status != 200:
                raise ValueError("{} 服务器返回了错误的代码:{}".format(robot_url, status))
        except Exception as e:
            mes['message'] = "error"
            mes['reason'] = e
        finally:
            return mes


if __name__ == "__main__":
    pass
