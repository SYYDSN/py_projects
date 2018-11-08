# -*- coding: utf-8 -*-
import datetime


"""自定义jinja2的过滤器"""


def __short_num(num: float) -> float:
    """不保留小数"""
    return int(num)


def __short_num1(num: float) -> float:
    """保留1位小数"""
    return round(num, 1)


def __short_num2(num: float) -> float:
    """保留2位小数"""
    return round(num, 2)


def __short_date(d: datetime.datetime) -> str:
    """
    日期格式化,返回'x月x日'这样的格式
    :param d:
    :return:
    """
    if d:
        return "{}月{}日".format(d.month, d.day)
    else:
        return ""


def __short_date2(d: datetime.datetime) -> str:
    """
    日期格式化,返回'xxxx年x月x日'这样的格式
    :param d:
    :return:
    """
    if d:
        return "{}年{}月{}日".format(d.year,d.month, d.day)
    else:
        return ""


def __startswith(string: str, pre: str) -> bool:
    """
    检查一个字符串是否以特定的字符串序列开头?
    :param string: 待检测字符串
    :param pre:
    :return:
    """
    return string.startswith(pre)


def __endswith(string: str, end: str) -> bool:
    """
    检查一个字符串是否以特定的字符串序列结尾?
    :param string: 待检测字符串
    :param end:
    :return:
    """
    return string.endswith(end)


def __str_time(val: datetime.datetime, fmt: str = None) -> str:
    """
    自定义的jinja2的格式化时间的方式.
    :param val:
    :param fmt:
    :return:
    """
    if isinstance(val, datetime.datetime):
        fmt = "%F" if fmt is None else fmt
        res = '' if val is None else val.strftime(fmt)
    else:
        res = val
    return res


def __is_list(val) -> bool:
    """
    自定义的jinja2的过滤器, 判断一个对象是否是数组
    :param val:
    :return:
    """
    if isinstance(val, list):
        return True
    else:
        return False


def __get_age(birth: datetime.datetime) -> str:
    """
    根据出生年月计算年龄
    :param birth:
    :return:
    """
    if isinstance(birth, datetime.datetime):
        now = datetime.datetime.now().year
        y = birth.year
        m = birth.month
        return "{} 岁({}年{}月)".format(now - y, y, m)
    else:
        return ''


def mount_plugin(app):
    """注册自定义的过滤器和测试器"""
    app.jinja_env.filters['short_num'] = __short_num
    app.jinja_env.filters['short_num1'] = __short_num1
    app.jinja_env.filters['short_num2'] = __short_num2
    app.jinja_env.filters['short_date'] = __short_date
    app.jinja_env.filters['short_date2'] = __short_date2
    app.jinja_env.tests['startswith'] = __startswith
    app.jinja_env.tests['endswith'] = __endswith
    app.jinja_env.filters['str_time'] = __str_time
    app.jinja_env.filters['is_list'] = __is_list
    app.jinja_env.filters['get_age'] = __get_age


if __name__ == "__main__":
    pass