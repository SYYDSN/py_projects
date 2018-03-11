#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
from log_module import get_logger
import datetime
import re


"""交易模块,包含交易信息"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()


class Transaction(mongo_db.BaseDoc):
    """管理平台的交易记录表信息"""
    _table_name = "transaction_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['system'] = str    # 哪个系统平台的数据? 默认是shengfx888.com
    type_dict['ticket'] = int    # 系统为每个订单安排的号码,按时间顺序递增，同一系统内永不重复
    type_dict['login'] = int    # 客户交易账号，同一系统内永不重复,是判断佣金的重要判断数据
    """system+ticket联合, system+login联合有唯一性"""
    type_dict['nick_name'] = str  # 英文名,对应表单中的英文名
    type_dict['real_name'] = str  # 英文名,对应表单中的MT名,一般是真名
    type_dict['command'] = str    # 交易指令 
    """
    交易指令分多种类型.他们的含义分别如下:
    1. buy        买入型订单  已成交，利息/手续费一栏中，手续费不为0
    2. sell       卖出型订单  已成交，利息/手续费一栏中，手续费不为0
    3. buy limit  买入型订单  买入型订单，指定在某一价格买入产品，现价高于指定价格，到达指定价格后，订单转为buy ,未成交，利息/手续费一栏中，手续费为0。如果该订单被取消则注释栏为cancelled.
    4. sell limit 卖出型订单  指定在某一价格卖出产品，现价低于指定价格，到达指定价格后，订单转为sell,未成交，利息/手续费一栏中，手续费为0。如果该订单被取消则注释栏为cancelled
    5. buy stop   买入型订单  买入型订单，指定在某一价格买入产品，现价高于指定价格，到达指定价格后，订单转为buy,未成交，利息/手续费一栏中，手续费为0。如果该订单被取消则注释栏为cancelled
    6. sell stop  卖出型订单  指定在某一价格卖出产品，现价低于指定价格，到达指定价格后，订单转为sell,未成交，利息/手续费一栏中，手续费为0。如果该订单被取消则注释栏为cancelled
    7. balance    出入金     代表客户增加或减少账户资金，盈亏一栏为正数代表入金，负数代表出金
    8. credit     赠金       正数代表给客户账户增加资金，注释一栏为Credit In
    """
    type_dict['symbol'] = str  # 交易的产品的品种
    """交易的产品有多种,注意他们计算手数的计量方式不同,只有HK50mini (恒指迷你手)  一手相当于普通产品0.1手,其他的都是正常计量"""
    type_dict['lot'] = int  # 交易手数
    type_dict['enter_price'] = float  # 建仓价 订单进场价格 对于LIMIT，STOP类型订单，是等待到这个价格自动入场
    type_dict['exit_price'] = float  # 平仓价 订单出场价格 现在市场价格
    type_dict['take_profit'] = float  # 止盈价格
    type_dict['stop_losses'] = float  # 止损价格
    type_dict['swap'] = float  # 利息,过夜费,当天进出场订单无利息，持仓过夜会产生利息，负数为从客户账户扣款，正数代表客户账户增加资金.成交订单，持仓过夜才会可能产生利息
    type_dict['commission'] = float # 佣金/手续费,产生手续费的订单是有效订单.成交订单，才会产生手续费，一般为负数
    type_dict['open_time'] = datetime.datetime  # 开仓时间
    type_dict['close_time'] = datetime.datetime  # 平仓时间
    type_dict['time'] = datetime.datetime  # 不存在过程的交易的时间，比如出如金
    type_dict['profit'] = float  # 盈亏/利润. 正数为客户盈利，负数为客户亏损.平仓订单盈亏有意义，挂单（LIMIT，STOP），以及持仓中订单的盈亏暂不统计
    type_dict['spread_profit'] = float  # 点差/价格利润
    type_dict['comment'] = str  # 注释
    type_dict['description'] = str  # 对注释的补充说明
    """
    注释有多种,现部分举例如下:
    1. cancelled     订单取消.
    2. from #28860   部分平仓的订单的剩余部分   28860是父订单号  这个订单是28860订单的一部分，产生于28860,没有完全平掉,那剩下的部分就会生成一条这样的注释.   
    3. to #28844     部分平仓的订单            28844是剩余未平仓订单转化成的  
    4. tp            止盈触发
    5. sl            止损触发
    6. so:49.7%      爆仓                    保证金低于50%（49.7%），被强制平仓
    7. deposit       入金/加金
    8. withdraw      出金
    9. credit        赠金
    """

    def __init__(self, **kwargs):
        if "comment" in kwargs and "description" not in kwargs:
            description = ''
            comment = kwargs['comment']
            if comment.lower() == "cancelled":
                description = "订单取消"
            elif re.match(r'^from.*', comment.lower()):
                description = "部分平仓的订单的剩余部分"
            elif re.match(r'^to.*', comment.lower()):
                description = "部分平仓的订单"
            elif re.match(r'^.tp.*', comment.lower()):
                description = "止盈触发"
            elif re.match(r'^.sl.*', comment.lower()):
                description = "止损触发"
            elif re.match(r'^so.*', comment.lower()):
                description = "爆仓"
            elif re.match(r'^deposit.*', comment.lower()):
                description = "入金/加金"
            elif re.match(r'^withdraw.*', comment.lower()):
                description = "出金"
            elif re.match(r'^credit.*', comment.lower()):
                description = "赠金"
            else:
                pass
            kwargs['description'] = description
        else:
            pass
        super(Transaction, self).__init__(**kwargs)

    @classmethod
    def last_ticket(cls) -> (None, int):
        """
        获取最后一个出入金记录的ticket，用于判断最后一个交易号
        :return:
        """
        filter_dict = {"command": "balance"}
        sort_dict = {"ticket": -1}
        record = cls.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict, projection=["ticket"])
        if record is None:
            pass
        else:
            return record['ticket']


if __name__ == "__main__":
    print(Transaction.last_ticket())
    pass