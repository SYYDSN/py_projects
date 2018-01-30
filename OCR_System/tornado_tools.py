# -*-coding:utf8-*-
import werkzeug.contrib.cache


"""tornado_server的工具模块"""


WS_DICT = dict()  # 全局变量


def get_online_dict():
    """获取在线的ws用户id和ws_handler的字典"""
    global WS_DICT
    return WS_DICT


def get_online_list():
    """获取在线的ws用户id"""
    return list(get_online_dict().keys())


def add_online_id(the_id, ws_hanlder):
    """把一个在线ws的id和ws_handler加入ws_dict"""
    ws_dict = get_online_dict()
    if the_id not in ws_dict.keys():
        ws_dict[the_id] = ws_hanlder
    else:
        pass


def remove_online_id(the_id):
    """把一个ws_id从全局列表中删除"""
    ws_dict = get_online_dict()
    if the_id not in ws_dict.keys():
        pass
    else:
        ws_dict.pop(the_id)