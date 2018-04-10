#  -*- coding: utf-8 -*-
from log_module import get_logger
from send_moudle import *
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
            arg_dict['receive_time'] = datetime.datetime.now()
            arg_dict['op'] = op
            create_time = mongo_db.get_datetime_from_str(data.pop('createTime', None))
            if isinstance(create_time, datetime.datetime):
                create_time = self.transform_time_zone(create_time)  # 调整时区
                arg_dict['create_time'] = create_time
            update_time = mongo_db.get_datetime_from_str(data.pop('updateTime', None))
            if isinstance(update_time, datetime.datetime):
                update_time = self.transform_time_zone(update_time)  # 调整时区
                arg_dict['update_time'] = update_time
            delete_time = mongo_db.get_datetime_from_str(data.pop('deleteTime', None))
            if isinstance(delete_time, datetime.datetime):
                delete_time = self.transform_time_zone(delete_time)  # 调整时区
                arg_dict['delete_time'] = delete_time
            event_date = datetime.datetime.now()
            if isinstance(event_date, datetime.datetime):
                arg_dict['event_date'] = event_date

            arg_dict['record_id'] = data.pop('_id', None)   # 事件唯一id,用于判断是不是同一个交易?
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
            arg_dict['token_name'] = "策略助手 小迅"
            for k, v in data.items():
                if v is not None:
                    arg_dict[k] = v
            super(Signal, self).__init__(**arg_dict)

    @staticmethod
    def transform_time_zone(a_time) -> datetime.datetime:
        """
        转换时区，把时间+8个小时
        :param a_time:
        :return:
        """
        return a_time + datetime.timedelta(hours=8)  # 调整时区

    def replace_column(self) -> None:
        """
        替换初始化参数的列名，这么做的原因是让初始化字典易懂。此函数应该被覆盖
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
        product = self.__dict__.pop('_widget_1514518782514', None)
        if product is not None:
            self.set_attr("product", product)
        direction = self.__dict__.pop('_widget_1514518782557', None)  # 交易方向
        if direction is not None:
            self.set_attr("direction", direction)
        enter_price = self.__dict__.pop('_widget_1514518782592', None)
        try:
            enter_price = float(enter_price) if enter_price is not None else enter_price
        except Exception as e:
            logger.exception(e)
            print(e)
        finally:
            if isinstance(enter_price, float):
                self.set_attr("enter_price", enter_price)
            else:
                pass
        exit_price = self.__dict__.pop('_widget_1514887799231', None)
        try:
            exit_price = float(exit_price) if exit_price is not None else exit_price
        except Exception as e:
            logger.exception(e)
            print(e)
        finally:
            if isinstance(exit_price, float):
                self.set_attr("exit_price", exit_price)
            else:
                pass
        profit = self.__dict__.pop('_widget_1514518782842', None)  # 获利
        if profit is not None:
            self.set_attr("profit", profit)
        each_profit = self.__dict__.pop('_widget_1522117404041', None)  # 每手获利
        if profit is not None:
            self.set_attr("each_profit", each_profit)

    def send(self):
        """
        输出发送到丁丁机器人的消息字典，此函数应该被覆盖
        :return:
        """
        self.replace_column()
        print(self.__dict__)
        create_time = self.get_attr("create_time")
        update_time = self.get_attr("update_time")
        delete_time = self.get_attr("delete_time")
        op = self.get_attr("op")
        enter_price = self.get_attr("enter_price")
        exit_price = self.get_attr("exit_price")
        now = datetime.datetime.now()
        if self.op == "data_create" and enter_price is not None:
            """进场信号"""
            the_type = "建仓提醒"
            auth = self.get_attr("creator_name")
            event_date = create_time
        elif self.op == "data_update" and enter_price is not None and exit_price is not None:
            the_type = "平仓提醒"
            auth = self.get_attr("updater_name")
            event_date = update_time
        elif self.op == "data_update":
            the_type = '修改订单'
            auth = self.get_attr("updater_name")
            event_date = now
        elif self.op == "data_delete":
            the_type = '删除订单'
            auth = self.get_attr("deleter_name")
            event_date = self.get_attr("delete_time", now)
        else:
            the_type = '异常'
            auth = self.get_attr("updater_name")
            event_date = now
            ms = "位置的操作:{}".format(self.__dict__)
            logger.exception(ms)
        if isinstance(event_date, datetime.datetime):
            event_date = event_date.strftime("%m月%d日 %H:%M:%S")
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
        if the_type == "异常":
            pass
        else:
            if the_type == "建仓提醒":
                text = "#### {}\n > {}老师{}{} \n\r >建仓价格：{} \n\r > {}".format(title,
                                                                              auth,
                                                                              self.get_attr("direction", ''),
                                                                              self.get_attr("product", ''),
                                                                              enter_price,
                                                                              event_date)
            elif the_type == "平仓提醒":
                text = "#### {}\n > {}老师平仓{}方向{}订单 \n\r > 建仓：{} <br> \n\r > 平仓：{} <br> \n\r > 每手实际盈利 {} \n\r > <br> {}".format(
                    title, auth, self.get_attr("direction", ""),
                    self.get_attr("product", ""), enter_price, exit_price,
                    self.get_attr("each_profit", ''),
                    event_date)
            elif the_type == "修改订单":
                text = "#### {}\n > {}老师平仓{}方向{}订单 \n\r > 建仓：{} <br> \n\r > 平仓：{} <br> \n\r" \
                       " > 每手实际盈利 {} \n\r > <br> {}".format(
                    title, auth, self.get_attr("direction", ""),
                    self.get_attr("product", ""),
                    "" if enter_price is None else enter_price,
                    "" if exit_price is None else exit_price,
                    self.get_attr("each_profit", ''),
                    event_date)
            else:
                """这应该是删除订单"""
                text = "#### {}\n > {}老师删除 {} 订单 \n\r > {}".format(title,
                                                                             auth,
                                                                             self.get_attr("product", ''),
                                                                             event_date)
            markdown = dict()
            markdown['title'] = title
            markdown['text'] = text
            out_put['markdown'] = markdown
            out_put['at'] = {'atMobiles': [], 'isAtAll': False}

            """发送消息到钉订群"""
            # res = send_signal(out_put, token_name=self.get_attr("token_name"))
            res = 1
            if res:
                if the_type == "删除订单":
                    self.__dict__['send_time_delete'] = datetime.datetime.now()
                elif the_type == "修改订单":
                    self.__dict__['send_time_prev_update'] = datetime.datetime.now()
                elif the_type == "建仓提醒":
                    self.__dict__['send_time_enter'] = datetime.datetime.now()
                elif the_type == "平仓提醒":
                    self.__dict__['send_time_exit'] = datetime.datetime.now()
                else:
                    pass
                u = self.__dict__
                u.pop("_id", None)
                record_id = u.pop("record_id", None)
                if record_id is None:
                    pass
                else:
                    f = {"record_id": record_id}
                    u = {"$set": u}
                    conn = mongo_db.get_conn(self._table_name)
                    r = conn.find_one_and_update(filter=f, update=u, upsert=True)
                    print(r)
            else:
                pass

    def welcome(self):
        """
        发送欢迎消息
        :return:
        """
        out_put = dict()
        markdown = dict()
        out_put['msgtype'] = 'markdown'
        markdown['title'] = "机器人开通"
        markdown['text'] = "> {}已开通 \n > {}".format(self.get_attr("token_name"), datetime.datetime.now().strftime(
            "%Y年%m月%d日 %H:%M:%S"))
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        res = send_signal(out_put, token_name=self.get_attr("token_name"))
        print(res)


if __name__ == "__main__":
    data = {'op': 'data_create',
            'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
                     'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
                     '_widget_1520843763126': 1190, 'formName': '发信号测试',
                     '_widget_1514518782504': '2018-03-29T21:40:19.000Z', 'label': '', '_widget_1514518782592': 120,
                     'createTime': '2018-03-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
                     '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
                     'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'}, '_widget_1520843228626': 1000,
                     '_id': '7abd5d81493acc231b27af1c', 'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
                     '_widget_1514518782603': [{'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
                     'updateTime': '2018-03-29T21:41:21.491Z', '_widget_1514518782514': '原油',
                     'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
                     }
            }
    d = Signal(**data)
    d.send()
    # d.welcome()
    pass
