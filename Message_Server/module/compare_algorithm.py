from bson.objectid import ObjectId

"""
用于验证算法时的脚本
1. 老师增加初始资金, 收益率, 胜率, 交易手数上下限,
2. 计算盈亏的算法
3. 收益率的计算
4. 交易手数的波动.会根据盈亏的情况: 盈利区域稳健量小, 亏损趋于激进量大,性格差异反映在手数上下限尚
5. 入金机制. 老师本金小于下一次喊单所需的资金(400倍杠杆)时,触发入金. 增加一个入金表.记录老师入金数据.
"""

a = {
    "_id" : ObjectId("5b4d7c46f313841fc0ecb808"),
    "creator_name" : "高巍",
    "datetime" : "2018-07-17T05:18:36.000Z",
    "app_id" : "5a45b8436203d26b528c7881",
    "app_name" : "分析师交易记录",
    "create_time" : "2018-07-17T13:19:02.365Z",
    "creator_id" : "5b4c01fffd259807ff92ad65",
    "direction" : "卖出",
    "each_cost" : 100.0,
    "each_profit" : 44.0,
    "each_profit_dollar" : 144.0,
    "enter_price" : 1241.33,
    "entry_id" : "5a45b90254ca00466b3c0cd1",
    "op" : "data_update",
    "p_coefficient" : 100.0,
    "product" : "黄金",
    "profit" : 144.0,
    "receive_time" : "2018-07-17T20:13:51.416Z",
    "record_id" : "5b4d7c46c88215247aa2d245",
    "send_time_enter" : "2018-07-17T13:19:02.767Z",
    "t_coefficient" : -1.0,
    "the_type" : "普通",
    "token_name" : "策略助手 小迅",
    "update_time" : "2018-07-17T20:13:52.206Z",
    "updater_id" : "5b4c01fffd259807ff92ad65",
    "updater_name" : "高巍",
    "exit_price" : 1239.89,
    "send_time_exit" : "2018-07-17T20:13:51.531Z"
}

b = {
    "_id" : ObjectId("5b4d7c46a7a7513eacde2e0b"),
    "p_coefficient" : 100.0,
    "direction" : "卖出",
    "each_profit_dollar" : 144.0,
    "re_calculate" : False,
    "native_direction" : "卖出",
    "t_coefficient" : -1.0,
    "each_profit" : 44.0,
    "native" : True,
    "create_time" : "2018-07-17T13:19:02.365Z",
    "the_type" : "普通",
    "product" : "黄金",
    "enter_price" : 1241.33,
    "native_id" : "5b4d7c46c88215247aa2d245",
    "each_cost" : 100.0,
    "teacher_id" : ObjectId("5b4c01fffd259807ff92ad65"),
    "profit" : 144.0,
    "close_time" : "2018-07-17T20:13:52.206Z",
    "exit_price" : 1239.89,
    "exit_reason" : None,
    "update_time" : "2018-07-17T20:13:52.206Z"
}