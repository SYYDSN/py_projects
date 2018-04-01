#  -*- coding: utf-8 -*-
from log_module import get_logger
import requests
import json
import mongo_db
import datetime

logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class Signal(mongo_db.BaseDoc):
    """交易信号"""
    """
    数据示范
    data = {'op': 'data_create',
            'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
                     'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
                     '_widget_1520843763126': 1190, 'formName': '发信号测试',
                     '_widget_1514518782504': '2018-03-29T21:40:19.000Z', 'label': '', '_widget_1514518782592': 120,
                     'createTime': '2018-03-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
                     '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
                     'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'}, '_widget_1520843228626': 1000,
                     '_id': '5abd5d81493acc231b27af1c', 'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
                     '_widget_1514518782603': [{'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
                     'updateTime': '2018-03-29T21:41:21.491Z', '_widget_1514518782514': '原油',
                     'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
                     }
            }
    """
    _table_name = "signal_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId

    def __init__(self, **kwargs):
        op = kwargs.pop('op', None)
        data = kwargs.pop('data', None)
        if op is None:
            ms = "op必须"
            logger.exception(ms)
            raise ValueError(ms)
        elif data is None:
            ms = "data必须"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            arg_dict = dict()
            arg_dict['op'] = op
            delete_time = mongo_db.get_datetime_from_str(data.pop('deleteTime', None))
            if delete_time is not None:
                arg_dict['delete_time'] = delete_time
            arg_dict['app_name'] = data.pop('formName', None)  # 表单名称，重要区别依据，应该是唯一的
            updater = data.pop('updater', None)
            if updater is not None:
                arg_dict['updater_name'] = updater['name']
                arg_dict['updater_id'] = updater['_id']
            deleter = data.pop('deleter', None)
            if deleter is not None:
                arg_dict['deleter_name'] = deleter['name']
                arg_dict['deleter_id'] = deleter['_id']
            creator = data.pop('creator', None)
            if creator is not None:
                arg_dict['creator_name'] = creator['name']
                arg_dict['creator_id'] = creator['_id']
            for k, v in data.items():
                if v is not None:
                    arg_dict[k] = v
            arg_dict = self.replace_column(arg_dict)
            super(Signal, self).__init__(**arg_dict)

    @staticmethod
    def replace_column(init_dict: dict) -> dict:
        """
        替换初始化参数的列名，这么做的原因是让初始化字典易懂。此函数应该被覆盖
        :param init_dict:
        :return:
        """
        return init_dict

    def send(self):
        """
        输出发送到丁丁机器人的消息字典，此函数应该被覆盖
        日期时间	_widget_1514518782504	string
        产品	_widget_1514518782514	string
        订单类型	_widget_1516245169208	string
        交易方向	_widget_1514518782557	string
        建仓价格	_widget_1514518782592	number
        离场位置.止盈	_widget_1514518782603._widget_1514518782614	number
        离场位置.止损	_widget_1514518782603._widget_1514518782632	number
        平仓价格	_widget_1514887799231	number
        离场理由	_widget_1514887799261	string
        盈亏点数	_widget_1514518782842	number
        每手赢利/美金	_widget_1520843763126	number
        每手实际盈利	_widget_1522117404041	number
        点值系数	_widget_1520843228626	number
        交易系数	_widget_1514887799459	number
        每手成本	_widget_1522134222811	number
        :return:
        """
        if self.op == "data_create":
            """进场信号"""
            the_type = "建仓提醒"
            auth = self.creator_name
        elif self.op == "data_update":
            the_type = "平仓提醒"
            auth = self.updater_name
        else:
            the_type = '提醒'
            auth = self.deleter_name

        product = self.__dict__['_widget_1514518782514']
        direction = self.__dict__['_widget_1514518782557']
        enter_price = self.__dict__['_widget_1514518782592']
        exit_price = self.__dict__.get('_widget_1514887799231')
        profit = self.__dict__.get('_widget_1514518782842')  # 获利
        event_date = mongo_db.get_datetime_from_str(self.__dict__['_widget_1514518782504'])
        if isinstance(event_date, datetime.datetime):
            event_date = event_date.strftime("%Y年%m月%d日 %H:%M:%S")
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
        title = the_type
        if the_type == "建仓提醒":
            text = "#### {}\n > {}老师在{}点位{}{}  \n\r > {}".format(the_type, auth, enter_price, direction, product,
                                                              event_date)
        else:
            text = "#### {}\n > {}老师平仓{}{}订单 \n\r > 在{}点 <br> \n\r > 总获利 {} \n\r > <br> {}".format(the_type, auth,
                                                                                                   direction, product,
                                                                                                   exit_price, profit,
                                                                                                   event_date)
        markdown = dict()
        markdown['title'] = title
        markdown['text'] = text
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}

        """发送消息到钉订群"""
        url = "https://oapi.dingtalk.com/robot/send?access_token=" \
              "1f84ff5a4e5515d505ca0c31074788609b4ceac2a5e579aa91df8f197fb894cd"
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(out_put)
        r = requests.post(url, data=data, headers=headers)
        status_code = r.status_code
        if status_code == 200:
            res = r.json()
            if res['errmsg'] == 'ok':
                """success"""
                self.__dict__['send'] = True
                self.save_plus()
            else:
                ms = '发送消息到钉订机器人失败，错误原因：{}， 参数{}'.format(res['errmsg'], data)
                logger.exception(ms)
                raise ValueError(ms)
        else:
            ms = '钉订机器人没有返回正确的响应，错误代码：{}'.format(status_code)
            logger.exception(ms)
            raise ValueError(ms)


if __name__ == "__main__":
    data = {'op': 'data_update',
            'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
                     'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
                     '_widget_1520843763126': 1190, 'formName': '发信号测试',
                     '_widget_1514518782504': '2018-03-29T21:40:19.000Z', 'label': '', '_widget_1514518782592': 120,
                     'createTime': '2018-03-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
                     '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
                     'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'}, '_widget_1520843228626': 1000,
                     '_id': '5abd5d81493acc231b27af1c', 'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
                     '_widget_1514518782603': [{'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
                     'updateTime': '2018-03-29T21:41:21.491Z', '_widget_1514518782514': '原油',
                     'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
                     }
            }
    d = Signal(**data)
    d.send()
