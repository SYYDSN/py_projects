# -*- coding: utf-8 -*-
import requests
import json
from log_module import get_logger


"""发送消息给钉订机器人"""


logger = get_logger()
# 钉订小助手
url_assistant = "https://oapi.dingtalk.com/robot/send?access_token=f346ad6b04dec14dfee9298f9e34aca4605efe4deb2" \
                "0b1ee8b18adfc54af5ca3"


def send_signal(send_data: dict) -> bool:
    """
    发送建仓/平仓交易信号
    :param send_data:
    :return:
    """
    res = False
    data = json.dumps(send_data)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url_assistant, data=data, headers=headers)
    status_code = r.status_code
    if status_code == 200:
        r = r.json()
        if r['errmsg'] == 'ok':
            """success"""
            res = True
        else:
            ms = '发送消息到钉订机器人失败，错误原因：{}， 参数{}'.format(res['errmsg'], data)
            logger.exception(ms)
            raise ValueError(ms)
    else:
        ms = '钉订机器人没有返回正确的响应，错误代码：{}'.format(status_code)
        logger.exception(ms)
        raise ValueError(ms)
    return res


def add_money(group_name: str, sales_name: str, customer_name: str, money: (str, float)) -> bool:
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