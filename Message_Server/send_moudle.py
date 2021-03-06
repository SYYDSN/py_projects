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
    "努力拼搏 消息助手": "e7692ed3a1b7e667b67c9af21d5d1d89009ae828c6b2048bac904b1fdadc0629",
    "努力拼搏 入金宣传表": "e7692ed3a1b7e667b67c9af21d5d1d89009ae828c6b2048bac904b1fdadc0629", # 和消息助手一样的
    "客户消息通知群 消息助手": "54704700f073548352e5fbe802704b19f6abd10c289731c7a5ed6aa44a5bd858",
    "group_001": "5f737e7c49a989d615cd6f2cc0236c0be3d2a8ea147fcaae6cee983d4e3e648c",  # 分组出入金消息
    "group_002": "9f1722d8d1bd1c16258d430f9cd5e0c4af1febecfad1bb3ed39ead0b8f0acdea",  # 分组出入金消息
    "group_005": "c035b57d094e021474bcc4fb6d0183677fe48a07f6e8fc53c611ffc182d3c4f7",  # 分组出入金消息
    "入金宣传": "be6e9de55c5777862fb37a62bcfcc6a1af6590ed8fb80e82392667bb01808526",  # 入金宣传
    "素材群": "497a9b8dcbde3bc6bcc55867c0963cf17f71bea2530ed7c3b606e85c4b18d1c2",   # 素材群
    "高管沟通群": "6c58b6174a3523ccc942db00bfdb4f978a0859b274469b22701de667b7c65d16",   # 高管沟通群
    "管理沟通群": "b0d40fa1e3d589eae169ab4e3a7f13628b47e836d35a75f891fb83473bdc428b"   # 管理沟通群
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
        now = datetime.datetime.now()
        r = None
        try:
            r = requests.post(robot_url, data=data, headers=headers)
        except Exception as e:

            title = "调用钉钉机器人接口异常!{}".format(now)
            content = "{}, 错误原因: {}".format(title, str(e))
            send_mail(title=title, content=content)
            logger.exception(e)
            print(e)
        finally:
            if r is not None:
                status_code = r.status_code
            else:
                status_code = -1
            if status_code == 200:
                r = r.json()
                if r['errmsg'] == 'ok':
                    """success"""
                    res = True
                else:
                    ms = '发送消息到钉钉机器人失败，错误原因：{}， 参数{}'.format(r['errmsg'], data)
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


if __name__ == "__main__":
    pass
