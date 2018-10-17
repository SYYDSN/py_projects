# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from mongo_db import *
import datetime
from send_moudle import send_signal


"""
记录交易平台发过来的事件消息的模块
目前记录的事件包含:
1. 提交入金
2. 入金成功
3. 出金处理
4. 待审核客户
"""


class PlatformEvent(BaseDoc):
    """
    交易平台发送来的事件信息.
    """
    _table_name = "platform_event"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['title'] = str
    type_dict['mt4_account'] = str
    type_dict['user_name'] = str
    type_dict['user_parent_name'] = str
    type_dict['order'] = str                 # 出入金单号
    type_dict['money'] = float               # 有符号浮点,
    type_dict['status'] = str
    type_dict['time'] = datetime.datetime    # 事件时间
    type_dict['create_time'] = datetime.datetime    # 创建

    @classmethod
    def instance(cls, **kwargs):
        if "create_time" not in kwargs:
            kwargs['create_time'] = datetime.datetime.now()
        instance = cls(**kwargs)
        return instance

    def get_message_dict(self, test_mode: bool = False) -> dict:
        """
        获取需要用钉钉机器人发送的消息，字典格式
        title 是要发送的消息的标题。共5种： 待审核客户，出金申请，入金申请，出金成功，入金成功
        text 是要发送的消息的内容字典和token，是符合markdown语法的字符串。
        :param test_mode: 是否打开测试模式？ 打开后会在消息里显示'测试消息'字样
        :return:
        """
        data = dict()
        title = self.get_attr("title", "")
        p = self.get_attr("user_parent_name", "")
        u = self.get_attr("user_name", "")
        t = self.get_attr("time", "")
        if isinstance(t, datetime.datetime):
            t = t.strftime("%Y年%m月%d日 %H时%M分")
        if title == "待审核客户":
            if test_mode:
                data['title'] = "消息测试 {}".format(title)
            else:
                data['title'] = title
            text = "#### {} \n > {}的客户{}正等待审核. \n > {}".format(title, p, u, t)
            data['text'] = text
        elif title == "提交入金":
            if test_mode:
                data['title'] = "消息测试 {}".format(title)
            else:
                data['title'] = title
            m = self.get_attr("money", "")
            text = "#### {} \n > {}的客户{}提交入金申请 \n > 金额: {}美元 \n > {}".format(title, p, u, m, t)
            data['text'] = text
        elif title == "入金成功":
            if test_mode:
                data['title'] = "消息测试 {}".format(title)
            else:
                data['title'] = title
            m = self.get_attr("money", "")
            text = "#### {} \n > {}的客户{}入金{}美元![胜利][胜利][胜利],继续加油[加油][加油][加油] \n > {}".format(title, p,
                                                                                            u, m, t)
            data['text'] = text
        elif title == "出金处理":
            title = "出金提醒"
            if test_mode:
                data['title'] = "消息测试 {}".format(title)
            else:
                data['title'] = title
            m = self.get_attr("money", "")
            text = "#### {} \n > {}的客户{}提交出金{}美元 \n > {}".format(title, p, u, m, t)
            data['text'] = text
        else:
            ms = "错误的实例对象：{}".format(str(self.get_dict()))
            logger.exception(ms)
            print(ms)
        return {"sales": p if isinstance(p, str) else str(p), "args": data}
        # name_map = {
        #     "出金提醒": "客户消息通知群 消息助手",
        #     "入金成功": "客户消息通知群 消息助手",
        #     "提交入金": "努力拼搏 消息助手",
        #     "待审核客户": "努力拼搏 消息助手"
        # }
        # if title not in name_map:
        #     ms = "错误的title:{}".format(title)
        #     logger.exception(ms)
        # else:
        #     robot_name = name_map[title]
        #     return {"robot_name": robot_name, "args": data}

    def send_message(self, test_mode: bool = False) -> bool:
        """
        向钉钉机器人发送消息
        :param test_mode: 是否打开测试模式？
        :return: 是否发送成功？
        """
        res = False
        resp = self.get_message_dict(test_mode=test_mode)
        markdown = resp['args']
        # robot_name = resp['robot_name']
        """1. 发送到努力拼搏群"""
        robot_name = "努力拼搏 消息助手"
        data = dict()
        data['msgtype'] = "markdown"
        data['markdown'] = markdown
        data['at'] = {'atMobiles': [], 'isAtAll': False}
        res1 = send_signal(send_data=data, token_name=robot_name)
        """2. 发送分组消息"""
        sales = resp['sales']
        robot_name2 = None
        if sales.startswith("001"):
            robot_name2 = "group_001"
        elif sales.startswith("002"):
            robot_name2 = "group_002"
        elif sales.startswith("005"):
            robot_name2 = "group_005"
        else:
            pass
        if robot_name2 is None:
            ms = "未意料的销售人员前缀,sales={}".format(sales)
            logger.exception(ms)
            res2 = True
        else:
            res2 = send_signal(send_data=data, token_name=robot_name2)
        res = res1 and res2
        return res


if __name__ == "__main__":
    """统计指定时间区间的数据"""
    # begin = get_datetime_from_str("2018-7-10 0:0:0")
    # end = get_datetime_from_str("2018-7-11 0:0:0")
    # f = dict()
    # f["time"] = {"$lt": end, "$gte": begin}
    # f['title'] = {"$in": ['入金成功', '提交入金']}
    # f['title'] = {"$in": ['待审核客户']}
    # rs = PlatformEvent.find_plus(filter_dict=f, to_dict=True)
    # money = 0
    # for x in rs:
    #     print(x)
    #     # print(x['title'], x['time'], x['user_parent_name'], x['money'])
    #     # money += x['money']
    # print("{}笔入金,共计:{}".format(len(rs), money))
    """测试发送消息"""
    init_args = {
        "_id" : ObjectId("5b3ee960a7a75160e480ed06"),
        "user_parent_name" : "001002",
        "time" : get_datetime_from_str("2018-07-06T12:00:31.000Z"),
        "status" : "审核已通过",
        "mt4_account" : "200370",
        "money" : -100.0,
        "user_name" : "张三",
        "order" : "1576",
        "title" : "提交入金"
    }
    obj = PlatformEvent(**init_args)
    obj.send_message(test_mode=True)
    pass