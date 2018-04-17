# -*-encoding: utf-8 -*-
from module.transaction_module import Transaction
from mongo_db import get_datetime_from_str


f = {
    "login": 8300092,
    "$or": [
        {"close_time": {
        "$gte": get_datetime_from_str("2018-3-1 0:0:0"),
        "$lt": get_datetime_from_str('2018-4-1 0:0:0')
    }},
{"time": {
        "$gte": get_datetime_from_str("2018-3-1 0:0:0"),
        "$lt": get_datetime_from_str('2018-4-1 0:0:0')
    }}
    ]
}
s = {"close_time": -1}
r = Transaction.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
num = list()
# today = 0
# prev = None
# for i in r:
#     swap = 0 if i.get("swap") is None else i['swap']
d = dict()
for i in r:
    key = i['time'] if i.get('close_time') is None else i['close_time']
    key = key.strftime("%F")
    if key not in d:
        d[key] = [i]
    else:
        d[key].append(i)
keys = list(d.keys())
keys.sort(key=lambda obj: get_datetime_from_str(obj), reverse=True)
sell_and_buy = list()
balance = list()
for k in keys:
    v = d[k]
    cur1 = 0
    cur2 = 0
    for i in v:
        command = i['command']
        p = i['profit']
        s = 0 if i.get("swap") is None else i['swap']
        c = 0 if i.get("commission") is None else i['commission']
        t = p + s + c
        if command in ['buy', 'sell']:
            cur1 += t
        else:
            cur2 += t
    print(k, cur1 + cur2)
    sell_and_buy.append(cur1)
    balance.append(cur2)
print("总盈亏：${}".format(str(round(sum(sell_and_buy), 2))))
print("总入金:${}".format(sum(balance)))