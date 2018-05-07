# -*- coding: utf-8 -*-


l1 = [{"_id": "aaa", "name": "jack"}, {"_id": "aaa", "name": "tom"}]


def get_dict(l: list, key: str = "_id", value_keys: list = None) -> dict:
    """
    从数组生成字典,数组的item必须是dict对象, 注意返回的格式
    :param l:  原始数组
    :param key: 选择item的哪个key的值作为key?
    :param value_keys: 选择item的哪些key的value组成value? None表示全部
    :return: {key1: [value11, value12...], key2: [value21, value22...], ....}
    """
    r = dict()
    for x in l:
        k = x[key]
        t = r.get(key)
        if t is None:
            t = list()
        if isinstance(value_keys, list):
            t.append({k: v for k, v in x if k in value_keys})
        else:
            t.append(x)
        r[k] = t
    return r