#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger
from module.teacher_module import *
from send_moudle import *
import mongo_db
from flask import request
from tools_module import get_real_ip
import datetime
import calendar
import random
from mail_module import send_mail

logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""产品参数"""
product_map = {
    "加元": {"p_arg": 100000, "cost": 80},  # p_arg/p_coefficient 点值,cost(每手)成本
    "澳元": {"p_arg": 100000, "cost": 80},
    "日元": {"p_arg": 1000, "cost": 80},
    "英镑": {"p_arg": 100000, "cost": 80},
    "欧元": {"p_arg": 100000, "cost": 70},
    "恒指": {"p_arg": 10, "cost": 100},
    "原油": {"p_arg": 1000, "cost": 100},
    "白银": {"p_arg": 5000, "cost": 250},
    "黄金": {"p_arg": 100, "cost": 100}
}


def _generator_signal(raw_signal: dict, change: dict) -> dict:
    """
    根据原始喊单信号和方向,生成新的(正向/反向/任意)(单个)信号字典
    :param raw_signal:
    :param change: Teacher.direction
    :return:
    """
    now = datetime.datetime.now()
    res = raw_signal.copy()
    op = res.get("op")
    record_id = res['record_id']
    record_id = ObjectId(record_id) if isinstance(record_id, str) and len(record_id) == 24 else record_id
    res['record_id'] = record_id
    native_direction = res.pop('direction')  # 原始订单的方向
    res['native_direction'] = native_direction
    teacher_name = res.pop('creator_name')  # 老师名
    res['teacher_name'] = teacher_name
    teacher_id = res.pop('creator_id')  # 老师id
    teacher_id = ObjectId(teacher_id) if isinstance(teacher_id, str) and len(teacher_id) == 24 else teacher_id
    res['teacher_id'] = teacher_id
    teacher = Teacher.find_by_id(o_id=teacher_id, to_dict=True)
    res['change'] = change
    res['enter_time'] = res.pop("create_time")
    res['exit_time'] = res.pop("update_time")
    enter_price = res['enter_price']
    exit_price = res.get('exit_price')
    product = res['product']

    if change == "raw":
        teacher = Teacher.find_by_id(o_id=teacher_id, to_dict=True)
        res['native'] = True
        res['direction'] = native_direction
    else:
        res["_id"] = ObjectId()
        teacher = random.choice(Teacher.direction_map()[change])
        teacher_id = teacher['_id']
        res['teacher_id'] = teacher_id
        res['teacher_name'] = teacher['name']
        res['native'] = False
        if change == "follow":
            res['direction'] = native_direction
        elif change == "reverse" and native_direction == "买入":
            res['direction'] = "卖出"
        elif change == "reverse" and native_direction == "卖出":
            res['direction'] = "买入"
        else:
            res['direction'] = random.choice(["买入", "卖出"])
        res['t_coefficient'] = 1 if res['direction'] == "买入" else -1
        a_coefficient = random.randint(-4, 4)  # 开仓价随机系数
        res['a_coefficient'] = a_coefficient
        """当前没有点差"""
        new_enter_price = enter_price + (1 / product_map[product]['p_arg']) * a_coefficient
        res['enter_price'] = new_enter_price
    """生成手数并计算是否需要加金"""
    lots_range = teacher['lots_range']
    lots = random.randint(lots_range[0], lots_range[1])
    res['lots'] = lots
    min_money = (lots * product_map[product]['cost']) / 400  # 400倍杠杆
    deposit = teacher.get("deposit", 0)
    deposit_amount = teacher.get("deposit_amount", 0)
    if deposit < min_money:
        """触发加金"""
        money = Deposit.generator_deposit(min_money=min_money)
        deposit += money
        deposit_amount += money
        temp = {"_id": ObjectId(), "t_id": teacher_id, "num": money, "time": now}
        t_f = {"_id": teacher_id}
        t_u = {"$set": {"deposit": deposit, "deposit_amount": deposit_amount}}
        client = mongo_db.get_client()
        t1 = client[mongo_db.db_name][Deposit.get_table_name()]
        t2 = client[mongo_db.db_name][Teacher.get_table_name()]
        with client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction():
                t1.insert_one(temp)
                t2.find_one_and_update(filter=t_f, update=t_u, upsert=True)
    else:
        pass

    if op == "data_update" and isinstance(enter_price, (int, float)) and isinstance(exit_price, (int, float)):
        """
        平仓信号,现在生成
        1. a/b系数。
        2. 可能的方向重设
        3. 进场/离场价格
        剩下的：
        1. 手数生成
        2. 资金计算
        3. 盈利率计算
        4. 胜负计算（用于计算胜率）
        则留到close_case环节处理。
        """
        res['need_calculate'] = True
        b_coefficient = random.randint(-4, 4)  # 平仓价随机系数
        res['b_coefficient'] = b_coefficient
        new_exit_price = exit_price + (1 / product_map[product]['p_arg']) * b_coefficient
        res['exit_price'] = new_exit_price
    else:
        pass
    return res


def generator_signal_and_save(raw_signal: dict) -> list:
    """
    根据原始喊单信号,生成新的(正向/反向/任意)信号字典(生成的同时如果是离场信号的话就要计算盈利).
    最后返回这四个信号字典的数组
    注意raw_signal必须有record_id字段,过早的信号没有这个字段.
    :param raw_signal: 原始信号字典.
    :return:
    """
    t_map = Teacher.direction_map()
    t_list = [_generator_signal(raw_signal, x) for x in t_map.keys()]
    need_calculate = t_list[0].get('need_calculate')
    if not need_calculate:
        """不需要计算,也就是进场记录,直接保存就好了"""
        for x in t_list:
            x.pop("_id")
            f = {"record_id": x.pop("record_id"), "change": x.pop("change")}
            u = {"$set": x}
            r = Trade.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
            if r is None:
                ms = "保存trade失败! f:{}, u: {}".format(f, u)
                logger.exception(msg=ms)
                print(ms)
            else:
                pass
    else:
        f = {"record_id": t_list[0]['record_id']}
        rs = Trade.find_plus(filter_dict=f, to_dict=True)
        rs = {x['change']: x for x in rs}
        for x in t_list:
            change = x['change']
            old = rs.get(change)
            if old is None:
                """没有对应的开单记录,无需修改喊单信号字段"""
                pass
            else:
                """
                有对应的开单记录,需要修改:
                1. enter_price 开盘价
                2. a__coefficient a参数
                3. _id
                """
                x['_id'] = old['_id']
                x['enter_price'] = old['enter_price']
                try:
                    x['a_coefficient'] = old['a_coefficient']
                except Exception as e:
                    print(e)
                    print(x)
                    print(old)
            """
            计算开始,需要计算的内容:
            # 1. lots 随机一个交易手数,在下单的时候计算.
            2. deposit   当前存款
            3. deposit_amount 历史总存款.
            # 4.  入金事件在下单的时候计算.
            5. each_profit 本次交易的每手盈利
            6. profit 本次交易的盈利 each_profit * lots
            7. profit_amount 历史交易总盈利
            8. profit_ratio 和 win_ratio 盈利率和胜率
            """
            """计算盈利总额,盈利率"""
            teacher_id = x['teacher_id']
            teacher = Teacher.find_by_id(o_id=teacher_id, to_dict=True)
            deposit = teacher.get('deposit', 0)
            profit_amount = teacher.get('profit_amount', 0)
            deposit_amount = teacher.get('deposit_amount', 0)
            case_count = teacher.get('case_count', 0)
            win_count = teacher.get('win_count', 0)
            if change == "raw":
                each_profit = x['each_profit']
            else:
                exit_price = x['exit_price']
                enter_price = x['enter_price']
                p_c = x['p_coefficient']
                t_c = x['t_coefficient']
                each_profit_dollar = (exit_price - enter_price) * t_c * p_c
                each_cost = x['each_cost']
                each_profit = each_profit_dollar - each_cost
                x['each_profit_dollar'] = each_profit_dollar
                x['each_profit'] = each_profit
            try:
                lots = x['lots']
            except Exception as e:
                print(e)
                print(x)
            the_profit = lots * each_profit  # 本次交易盈利
            x['the_profit'] = the_profit
            if the_profit >= 0:
                win_count += 1
            else:
                pass
            case_count += 1
            win_ratio = round((win_count / case_count) * 100, 2)
            deposit += the_profit
            profit_amount += the_profit
            print(x)
            print(teacher)
            profit_ratio = round((profit_amount / deposit_amount) * 100, 2)  # 盈利率
            client = mongo_db.get_client()
            t1 = client[mongo_db.db_name][Trade.get_table_name()]
            t2 = client[mongo_db.db_name][Teacher.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    t1_f = {"_id": x.pop("_id")}
                    t1_u = {"$set": x}
                    r1 = t1.find_one_and_update(filter=t1_f, update=t1_u, upsert=True)
                    t2_f = {"_id": teacher_id}
                    t2_u = {"$set": {
                        'deposit': deposit,
                        'deposit_amount': deposit_amount,
                        'profit_amount': profit_amount,
                        'profit_ratio': profit_ratio,
                        "case_count": case_count,
                        "win_count": win_count,
                        "win_ratio": win_ratio,
                    }}
                    r2 = t2.find_one_and_update(filter=t2_f, update=t2_u, upsert=True)


class RawSignal(mongo_db.BaseDoc):
    """
    原始信号的记录,目前用来监听简道云发送过来的消息
    """
    _table_name = "raw_signal_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class RawRequestInfo(mongo_db.BaseDoc):
    """
    原始请求信号的记录,注意，没有记录请求中的files参数,可用来监听任意request,
    目前的用途:
    1. 监听交易平台发过来的消息  2018-6-29
    """
    _table_name = "raw_request_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['ip'] = str
    type_dict['path'] = str
    type_dict['args'] = dict
    type_dict['form'] = dict
    type_dict['json'] = dict
    type_dict['headers'] = dict
    type_dict['event_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "event_date" not in kwargs:
            kwargs['event_date'] = datetime.datetime.now()
        super(RawRequestInfo, self).__init__(**kwargs)

    @classmethod
    def get_init_dict(cls, req: request) -> dict:
        """
        从request中获取初始化字典.
        :param req:
        :return:
        """
        args = dict()
        args['ip'] = get_real_ip(req)
        args['path'] = req.path
        args['method'] = req.method.lower()
        args['args'] = {k: v for k, v in req.args.items()}
        args['form'] = {k: v for k, v in req.form.items()}
        args['json'] = req.json
        args['headers'] = {k: v for k, v in req.headers.items()}
        return args

    @classmethod
    def instance(cls, req: request):
        """
        生成一个实例
        :param req: flask.request
        :return: 实例
        """
        args = cls.get_init_dict(req=req)
        instance = cls(**args)
        return instance

    @classmethod
    def record(cls, req: request) -> ObjectId:
        """
        记录原始的请求
        :param req:
        :return:
        """
        instance = cls.instance(req)
        return instance.save_plus()


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
    """
    原始操作类型
    1. data_create 一定是开单操作
    2. data_update 可能是离场操作,但也可能是修改订单
    """
    type_dict['op'] = str  # 原始操作类型
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
    type_dict['profit'] = float  # 获利/盈亏,旧字段,将废弃,
    type_dict['each_profit'] = float  # 每手实际获利
    type_dict['each_profit_dollar'] = float  # 每手获利/美金
    type_dict['each_cost'] = float  # 每手成本
    type_dict['t_coefficient'] = float  # （交易）系数
    type_dict['p_coefficient'] = float  # （点值）系数
    type_dict['token_name'] = str  # 固定  "策略助手 小迅"

    def __init__(self, **kwargs):
        super(Signal, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **kwargs):
        """
        从简道云发送过来的信号中创建对象
        :param kwargs:
        :return:
        """
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
                create_time = cls.transform_time_zone(create_time)  # 调整时区
                arg_dict['create_time'] = create_time
            update_time = mongo_db.get_datetime_from_str(data.pop('updateTime', None))
            if isinstance(update_time, datetime.datetime):
                update_time = cls.transform_time_zone(update_time)  # 调整时区
                arg_dict['update_time'] = update_time
            delete_time = mongo_db.get_datetime_from_str(data.pop('deleteTime', None))
            if isinstance(delete_time, datetime.datetime):
                delete_time = cls.transform_time_zone(delete_time)  # 调整时区
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
            return cls(**arg_dict)

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
                    """记录原始信号并生成虚拟信号"""
                    try:
                        Trade.sync_from_signal(signal=self)
                    except Exception as e:
                        print(e)
                        logger.exception(e)
                        title = "{}同步AI操盘手出错".format(datetime.datetime.now())
                        content = "cause: {}".format(e)
                        send_mail(title=title, content=content)
                    finally:
                        pass
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

    @classmethod
    def supplement_teacher_id(cls) -> None:
        """
        把记录中,缺乏老师id的部分补上.
        :return:
        """
        f = {"creator_name": {"$exists": True}}
        all_record = cls.find_plus(filter_dict=f, to_dict=True, can_json=False)
        teacher_dict = dict()
        for record in all_record:
            name = record['creator_name']
            t_id = record.get('creator_id')
            if name not in teacher_dict and t_id is not None:
                teacher_dict[name] = t_id
            else:
                pass
        for record in all_record:
            name = record['creator_name']
            t_id = record.get('creator_id')
            if name in teacher_dict and t_id is None:
                t_id = teacher_dict[name]
                f = {"_id": record['_id']}
                u = {"$set": {"creator_id": t_id}}
                cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)


class MonthEstimate(mongo_db.BaseDoc):
    """
    老师的喊单成绩评估按月评估的记录
    """
    _table_name = "Month_estimate_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['teacher_id'] = str
    type_dict['teacher_name'] = str
    type_dict['date_str'] = str  # 评估的年月 2018-04格式
    type_dict['info_dict'] = dict
    """
    info_dict是信息字典 ,包含以下多类信息
    {
        "all": {"win_per": "所有产品月总胜率,百浮点,直接加%即可", "profit": "所有产品总盈利,美元,浮点"},
        "黄金": {"win_per": "黄金月胜率,浮点,直接加%即可", "profit": "黄金月总盈利,美元,浮点"},
        ....
    }
    """
    type_dict['create_date'] = datetime.datetime

    @classmethod
    def get_instance(cls, teacher_id: str, date_str: str, return_type: str = "doc") -> object:
        """
        获取实例,是在查询老师的月评估时推荐替代init的方法
        :param teacher_id: 老师id
        :param date_str:  2018-04
        :param return_type: 返回类型 instance/doc/json  实例/doc/可以json的dict
        :return:
        """
        dates = date_str.split("-")
        the_year = int(dates[0])
        the_month = int(dates[-1])
        now = datetime.datetime.now()
        cur_year = now.year
        cur_month = now.month
        flag = -1
        if the_year < cur_year:
            flat = 1
        elif the_year == cur_year and the_month < cur_month:
            flag = 1
        else:
            flag = -1
        res = dict()
        if flag != 1:
            pass
        else:
            """先从数据库查,查不到再计算"""
            f = {"teacher_id": teacher_id, "date_str": date_str}
            estimate = cls.find_one_plus(filter_dict=f, instance=False, can_json=False)
            if isinstance(estimate, dict):
                """查询成功"""
                pass
            else:
                """查询失败,生成一下"""
                begin = mongo_db.get_datetime_from_str("{}-{}-01 0:0:0".format(the_year, the_month))
                max_day = calendar.monthrange(the_year, the_month)[-1]
                end = mongo_db.get_datetime_from_str("{}-{}-{} 23:59:59.999".format(the_year, the_month, max_day))
                f = {"creator_id": teacher_id, "update_time": {"$gte": begin, "$lte": end}}
                rs = Signal.find_plus(filter_dict=f, to_dict=True, can_json=False)
                p_dict = dict()
                for r in rs:
                    p_name = r['product']
                    each_profit = r['each_profit'] if isinstance(r['each_profit'], (int, float)) else float(r['each_profit'])
                    p = p_dict.get(p_name)
                    if p is None:
                        p = list()
                    p.append(each_profit)
                    p_dict[p_name] = p
                """计算产品胜率"""
                res = dict()
                all_win_count = 0
                all_count = 0
                all_profit = 0
                for p_name, v in p_dict.items():
                    l1 = len(v)
                    wins = [x for x in v if x >= 0]
                    l2 = len(wins)
                    p_win_per = round((l2 / l1) * 100, 1)
                    profit = sum(wins)
                    all_count += l1
                    all_win_count += l2
                    all_profit += profit
                    p = res.get(p_name)
                    if p is None:
                        p = dict()
                    p['win_per'] = p_win_per
                    p['profit'] = profit
                    res[p_name] = p
                res['all'] = {"win_per": round((all_win_count / all_count) * 100, 1), "profit": all_profit}
                init = dict()
                init['_id'] = ObjectId()
                init['teacher_id'] = teacher_id
                init['date_str'] = date_str
                init['create_date'] = now
                init['info_dict'] = res
                cls.insert_one(**init)
                estimate = init
            return estimate


class Trade(Signal):
    """
    （老师的喊单）交易, 包括虚拟老师和真实老师的都会保存在这里.
    """
    _table_name = "trade"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['native'] = bool  # 这个记录是原生的吗?
    type_dict['record_id'] = ObjectId # 原记录的id,指向Signal的record_id属性
    type_dict['native_direction'] = str  # 原始订单的方向
    type_dict['change'] = str  # 改变方式  raw/follow/reverse/random
    type_dict['direction'] = str  # 方向（实际方向）
    type_dict['create_time'] = datetime.datetime  # 创建时间
    type_dict['enter_time'] = datetime.datetime  # 开单时间
    type_dict['exit_time'] = datetime.datetime  # 平仓时间
    type_dict['update_time'] = datetime.datetime  # 平仓时间,为了兼容报表的冗余字段
    type_dict['the_type'] = str  # 订单类型
    type_dict['teacher_name'] = str  #
    type_dict['teacher_id'] = ObjectId  #
    type_dict['product'] = str  # 产品名称
    type_dict['exit_reason'] = str  # 离场理由
    type_dict['enter_price'] = float  # 建仓价
    type_dict['exit_price'] = float  # 平仓价
    type_dict['each_profit_dollar'] = float  # 每手毛利美金
    type_dict['each_cost'] = float  # 每手成本
    type_dict['each_profit'] = float  # 每手实际获利美金
    type_dict['lots'] = int  # 交易手数
    type_dict['the_profit'] = float  # 本次交易总盈利
    type_dict['t_coefficient'] = float  # （交易）系数 -1/1
    type_dict['p_coefficient'] = float  # （点值）系数
    type_dict['a_coefficient'] = float  # 开仓价随机系数
    type_dict['b_coefficient'] = float  # 平仓价随机系数
    type_dict['need_calculate'] = bool  # 平仓信号特有。提醒系统计算盈利

    def __init__(self, **kwargs):
        super(Signal, self).__init__(**kwargs)

    @classmethod
    def re_build(cls) -> None:
        """
        从老师的原始喊单信号派生出来虚拟信号并保存,初始化的时候使用.会清空旧的数据
        :return:
        """
        f = {"record_id": {"$exists": True}, "create_time": {"$gte": mongo_db.get_datetime_from_str("2018-6-1")}}
        s = {"create_time": -1}
        rs = Signal.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
        Deposit.delete_many(filter_dict={"_id": {"$exists": True}})
        cls.delete_many(filter_dict={"_id": {"$exists": True}})
        for x in rs:
            cls.sync_from_signal(x)

    @classmethod
    def sync_from_signal(cls, signal: (dict, Signal)):
        """
        根据实际开仓信号,参照老师列表.生成真实老师和虚拟老师的喊单记录,存入trade表
        :param signal:
        :return:
        """
        signal = signal.get_dict() if isinstance(signal, Signal) else signal
        generator_signal_and_save(raw_signal=signal)


if __name__ == "__main__":
    """一个模拟的老师发送交易信号的字典对象，用于初始化Signal类"""
    # create_data = {'op': 'data_create',
    #         'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
    #                  'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
    #                  '_widget_1520843763126': 1190, 'formName': '发信号测试',
    #                  '_widget_1514518782504': '2018-07-29T21:40:19.000Z', 'label': '', '_widget_1514518782592': 120,
    #                  'createTime': '2018-07-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
    #                  '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
    #                  'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'}, '_widget_1520843228626': 1000,
    #                  '_id': '7abd5d81493acc231b27af1c', 'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
    #                  '_widget_1514518782603': [{'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
    #                  'updateTime': '2018-07-29T21:41:21.491Z', '_widget_1514518782514': '原油',
    #                  'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
    #                  }
    #         }
    # update_data = {'op': 'data_update',
    #                'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
    #                         'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
    #                         '_widget_1520843763126': 1190, 'formName': '发信号测试',
    #                         '_widget_1514518782504': '2018-07-29T21:40:19.000Z', 'label': '',
    #                         '_widget_1514518782592': 120,
    #                         'createTime': '2018-07-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
    #                         '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
    #                         'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
    #                         '_widget_1520843228626': 1000,
    #                         '_id': '7abd5d81493acc231b27af1c',
    #                         'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
    #                         '_widget_1514518782603': [
    #                             {'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
    #                         'updateTime': '2018-07-29T21:41:21.491Z', '_widget_1514518782514': '原油',
    #                         'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
    #                         }
    #                }
    # # """初始化喊单信号并发送"""
    # d = Signal.instance(**create_data)
    # # d.send()
    # """查看老师的月胜率"""
    # # print(MonthEstimate.get_instance("5a1e680642f8c1bffc5dbd6f", "2018-06"))
    # """生成一个虚拟信号"""
    # # signal1 = Signal.find_by_id(ObjectId("5b485ebbf313841fc0eaf2ad"))
    # Trade.sync_from_signal(d, signal_type="建仓提醒")
    close_case = Signal.find_by_id(o_id=ObjectId("5b63b3dac5aee8250b3b18fe"), to_dict=True)
    # Trade.sync_from_signal(close_case)
    Trade.re_build()
    pass
