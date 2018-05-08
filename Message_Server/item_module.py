#  -*- coding: utf-8 -*-
from log_module import get_logger
from send_moudle import *
import mongo_db
import datetime
from mail_module import send_mail

logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class Signal(mongo_db.BaseDoc):
    """交易信号"""
    """
    以create_time字段排序
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
    type_dict['datetime'] = datetime.datetime  # 表单的日期时间字段。
    type_dict['receive_time'] = datetime.datetime  # 接收消息时间
    type_dict['create_time'] = datetime.datetime  # 创建时间
    type_dict['update_time'] = datetime.datetime  # 修改时间
    type_dict['delete_time'] = datetime.datetime  # 删除时间
    type_dict['record_id'] = str  # 事件唯一id,用于判断是不是同一个交易?
    type_dict['app_name'] = str  # 表单名称，重要区别依据，应该是唯一的
    type_dict['the_type'] = str  # 订单类型
    type_dict['updater_name'] = str  # 修改者
    type_dict['updater_id'] = str  # 修改者id
    type_dict['deleter_name'] = str  # 删除者
    type_dict['deleter_id'] = str  # 删除者id
    type_dict['creator_name'] = str  # 创建者
    type_dict['creator_id'] = str  # 创建者id
    type_dict['product'] = str  # 产品名称
    type_dict['direction'] = str  # 方向
    type_dict['exit_reason'] = str  # 离场理由
    type_dict['enter_price'] = float  # 建仓价
    type_dict['exit_price'] = float  # 平仓价
    type_dict['profit'] = float  # 获利/盈亏
    type_dict['each_profit'] = float  # 每手实际获利
    type_dict['each_profit_dollar'] = float  # 每手获利/美金
    type_dict['each_cost'] = float  # 每手成本
    type_dict['t_coefficient'] = float  # （交易）系数
    type_dict['p_coefficient'] = float  # （点值）系数
    type_dict['token_name'] = str  # 固定  "策略助手 小迅"

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
            t_s = data.pop("_widget_1514518782603", dict())  # 止盈止损
            if "_widget_1514518782614" in t_s:
                take_profit = t_s.get('_widget_1514518782614')
                if take_profit is not None and isinstance(take_profit, (int, float)):
                    arg_dict['take_profit'] = take_profit  # 止盈
            if "_widget_1514518782632" in t_s:
                stop_losses = t_s.get('_widget_1514518782632')
                if stop_losses is not None and isinstance(stop_losses, (int, float)):
                    arg_dict['stop_losses'] = stop_losses   # 止损
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
            each_profit = data.pop("_widget_1522117404041", None)
            if isinstance(each_profit, (int, float)):
                arg_dict['each_profit'] = each_profit
            profit = data.pop("_widget_1514518782842", None)
            if isinstance(profit, (int, float)):
                arg_dict['profit'] = profit
            enter_price = data.pop("_widget_1514518782592", None)
            if isinstance(enter_price, (int, float)):
                arg_dict['enter_price'] = enter_price
            exit_price = data.pop("_widget_1514887799231", None)
            if isinstance(exit_price, (int, float)):
                arg_dict['exit_price'] = exit_price
            product = data.pop("_widget_1514518782514", None)
            if isinstance(product, str) and product.strip() != "":
                arg_dict['product'] = product
            direction = data.pop("_widget_1514518782557", None)
            if isinstance(direction, str) and direction.strip() != "":
                arg_dict['direction'] = direction
            exit_reason = data.pop("_widget_1514887799261", None)
            if isinstance(exit_reason, str) and exit_reason.strip() != "":
                arg_dict['exit_reason'] = exit_reason
            date_time = data.pop("_widget_1514518782504", None)
            date_time = mongo_db.get_datetime_from_str(date_time)
            if isinstance(date_time, datetime.datetime):
                arg_dict['datetime'] = date_time
            the_type = data.pop("_widget_1516245169208", None)
            if isinstance(the_type, str) and the_type.strip() != "":
                arg_dict['the_type'] = the_type
            each_cost = data.pop("_widget_1522134222811", None)  # 每手成本
            if isinstance(each_cost, (int, float)):
                arg_dict['each_cost'] = each_cost
            each_profit_dollar = data.pop("_widget_1520843763126", None)  # 每手盈利/美金
            if isinstance(each_profit_dollar, (int, float)):
                arg_dict['each_profit_dollar'] = each_profit_dollar
            t_coefficient = data.pop("_widget_1514887799459", None)  # （交易）系数
            if isinstance(t_coefficient, (int, float)):
                arg_dict['t_coefficient'] = t_coefficient
            p_coefficient = data.pop("_widget_1520843228626", None)  # （点值）系数
            if isinstance(p_coefficient, (int, float)):
                arg_dict['p_coefficient'] = p_coefficient

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
        输出发送到钉钉机器人的消息字典，此函数应该被子类覆盖
        :return:
        """
        # self.replace_column()
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

            """发送消息到钉钉群"""
            res = send_signal(out_put, token_name=self.get_attr("token_name"))
            # res = 1
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
                date_time = u.pop("datetime", None)
                creator_name = u.pop("creator_name", None)
                if date_time is None or creator_name is None:
                    ms = "不合法的喊单信号：{}".format(u)
                    logger.exception(ms)
                    title = "喊单信号不符合规范"
                    send_mail(title=title, content=ms)
                else:
                    f = {"datetime": date_time, "creator_name": creator_name}
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


def create_teacher(**kwargs):
    """
    生成真实的老师的字典
    """
    d = dict()
    d['direction'] = kwargs['_widget_1525161353528']
    d['product'] = kwargs['_widget_1525161353525']
    d['teacher_id'] = kwargs['_widget_1525161353522']['_id']
    d['teacher_name'] = kwargs['_widget_1525161353522']['name']
    return d


class VirtualTeacher(mongo_db.BaseDoc):
    """
    虚拟老师
    {
      'op': 'data_create',
      'data': {
        'creator': {
          'name': '徐立杰',
          '_id': '5a684c9b42f8c1bffc68f4b4'
        },
        'deleteTime': None,
        'updater': {
          'name': '徐立杰',
          '_id': '5a684c9b42f8c1bffc68f4b4'
        },
        'appId': '5a446c355a8c99236975be09',
        '_widget_1525161353511': [
          {
            '_widget_1525161353528': '正向',
            '_widget_1525161353525': '黄金',
            '_widget_1525161353522': {
              'name': '高特',
              '_id': '5a1e680642f8c1bffc5dbd6b'
            }
          },
          {
            '_widget_1525161353528': '反向',
            '_widget_1525161353525': '恒指',
            '_widget_1525161353522': {
              'name': '常阳',
              '_id': '5a1e680642f8c1bffc5dbd69'
            }
          },
          {
            '_widget_1525161353528': '正向',
            '_widget_1525161353525': '全部',
            '_widget_1525161353522': {
              'name': '高巍',
              '_id': '5aab3ea4340c1749505a2819'
            }
          }
        ],
        'createTime': '2018-05-08T22:13:32.952Z',
        'label': '',
        '_widget_1525161353498': 'robot1',
        'formName': '机器人分析师控制台',
        '_id': '5af2210c58b42122eba5abf0',
        'submitPrompt': {
          'content': ''
        },
        'deleter': None,
        'updateTime': '2018-05-08T22:13:32.952Z',
        'entryId': '5ae81d8bdd481029da358eaf'
      }
    }

    {
      'op': 'data_update',
      'data': {
        'creator': {
          'name': '徐立杰',
          '_id': '5a684c9b42f8c1bffc68f4b4'
        },
        'deleteTime': None,
        'updater': {
          'name': '徐立杰',
          '_id': '5a684c9b42f8c1bffc68f4b4'
        },
        'appId': '5a446c355a8c99236975be09',
        '_widget_1525161353511': [
          {
            '_widget_1525161353528': '正向',
            '_widget_1525161353525': '原油',
            '_widget_1525161353522': {
              'name': '语昂',
              '_id': '5a1e680642f8c1bffc5dbd6f'
            }
          },
          {
            '_widget_1525161353528': '反向',
            '_widget_1525161353525': '恒指',
            '_widget_1525161353522': {
              'name': '常阳',
              '_id': '5a1e680642f8c1bffc5dbd69'
            }
          },
          {
            '_widget_1525161353528': '正向',
            '_widget_1525161353525': '全部',
            '_widget_1525161353522': {
              'name': '高巍',
              '_id': '5aab3ea4340c1749505a2819'
            }
          }
        ],
        'createTime': '2018-05-08T22:13:32.952Z',
        'label': '',
        '_widget_1525161353498': 'robot1',
        'formName': '机器人分析师控制台',
        '_id': '5af2210c58b42122eba5abf0',
        'submitPrompt': {
          'content': ''
        },
        'deleter': None,
        'updateTime': '2018-05-08T22:15:53.546Z',
        'entryId': '5ae81d8bdd481029da358eaf'
      }
    }
    {
      'op': 'data_remove',
      'data': {
        'formName': '机器人分析师控制台',
        '_id': '5af2210c58b42122eba5abf0',
        'appId': '5a446c355a8c99236975be09',
        'deleter': {
          'name': '徐立杰',
          '_id': '5a684c9b42f8c1bffc68f4b4'
        },
        'deleteTime': '2018-05-08T22:16:13.417Z',
        'entryId': '5ae81d8bdd481029da358eaf'
      }
    }

    """
    _table_name = "virtual_teacher_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 此id从信号获得
    type_dict['creator_name'] = str
    type_dict['creator_id'] = str
    type_dict['create_time'] = datetime.datetime
    type_dict['updater_name'] = str
    type_dict['updater_id'] = str
    type_dict['update_time'] = datetime.datetime
    type_dict['deleter_name'] = str
    type_dict['deleter_id'] = str
    type_dict['delete_time'] = datetime.datetime
    type_dict['teachers'] = list()

    def __init__(self, **kwargs):
        super(VirtualTeacher, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **kwargs):
        """接收简道云的信号时，请用此方法替代init"""
        if "_id" in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])
        if "createTime" in kwargs:
            create_time = cls.transform_time_zone(kwargs.pop('createTime', None))
            if create_time is not None:
                kwargs['create_time'] = create_time
        if "updateTime" in kwargs:
            update_time = cls.transform_time_zone(kwargs.pop('updateTime', None))
            if update_time is not None:
                kwargs['update_time'] = update_time
        if "deleteTime" in kwargs:
            delete_time = cls.transform_time_zone(kwargs.pop('deleteTime', None))
            if delete_time is not None:
                kwargs['delete_time'] = delete_time
        creator = kwargs.pop("creator", None)
        if creator is not None:
            creator_name = creator.pop('name', None)
            if creator_name is not None:
                kwargs['creator_name'] = creator_name
            creator_id = creator.pop('_id', None)
            if creator_id is not None:
                kwargs['creator_id'] = creator_id
        updater = kwargs.pop("updater", None)
        if updater is not None:
            updater_name = updater.pop('name', None)
            if updater_name is not None:
                kwargs['updater_name'] = updater_name
            updater_id = updater.pop('_id', None)
            if updater_id is not None:
                kwargs['updater_id'] = updater_id
        deleter = kwargs.pop("deleter", None)
        if deleter is not None:
            deleter_name = creator.pop('name', None)
            if deleter_name is not None:
                kwargs['deleter_name'] = deleter_name
            deleter_id = creator.pop('_id', None)
            if deleter_id is not None:
                kwargs['deleter_id'] = deleter_id
        if "_widget_1525161353511" in kwargs:
            teachers = kwargs.pop("_widget_1525161353511", None)
            if teachers is not None:
                teachers = [create_teacher(**x) for x in teachers]
                kwargs['teachers'] = teachers
        return cls(**kwargs)

    @staticmethod
    def create_teacher(**kwargs):
        """
        生成喊单的老师的字典
        """
        d = dict()
        d['direction'] = kwargs['_widget_1525161353528']
        d['product'] = kwargs['_widget_1525161353525']
        d['teacher_id'] = kwargs['_widget_1525161353522']['_id']
        d['teacher_name'] = kwargs['_widget_1525161353522']['name']
        return d

    @staticmethod
    def transform_time_zone(a_time: (str, datetime.datetime)) -> (datetime.datetime, None):
        """
        转换时区，把时间+8个小时
        :param a_time:
        :return:
        """
        if isinstance(a_time, str):
            a_time = mongo_db.get_datetime_from_str(a_time)
        if not isinstance(a_time, datetime.datetime):
            return None
        else:
            return a_time + datetime.timedelta(hours=8)  # 调整时区


if __name__ == "__main__":
    """一个模拟的老师发送交易信号的字典对象，用于初始化Signal类"""
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
    """初始化喊单信号并发送"""
    d = Signal(**data)
    d.send()
    pass
