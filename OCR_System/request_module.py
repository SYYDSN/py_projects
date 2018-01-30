# -*- coding:utf-8 -*-
import db_module
import sqlalchemy.exc
import datetime
import re
import json
from threading import Lock
from user_group_module import get_user_group_info
from mail_module import send_mail


"""作业请求管理"""

table_name = "request_info"
db_module.get_columns(table_name, True)  # 第一次启动时加载


def get_customer_sn(request_sn):
    """根据请求sn获取用户的sn"""
    sql = "(select group_sn from user_group_info where group_sn=(select customer_sn from {} " \
          "where request_sn={}))".format(table_name, request_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        return raw[0]


def change_status(the_type, user_id):
    """启用/禁用/删除账户 ,第一个参数是up/down/delete ，启用或者禁用，第二个是用户id"""
    message = {"message": "success"}
    if db_module.validate_arg(user_id) and db_module.validate_arg(the_type):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update user_info set user_status=1 where user_id='{}'".format(user_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from user_info where user_id='{}'".format(user_id)
        else:
            verb = "禁用"
            sql = "update user_info set user_status=0 where user_id='{}'".format(user_id)
        session = db_module.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = "{}账户失败".format(verb)
        finally:
            session.close()
    else:
        message['message'] = "用户ID错误"
    return message


def request_count():
    """统计所有发票的数量
    返回int对象
    """
    redis_client = db_module.MyRedis.redis_client()
    result = redis_client.get("request_count")
    if not result:
        session = db_module.sql_session()
        sql = "select count(1) from request_info"
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set("request_count", result, ex=5 * 60)
    else:
        result = int(result)
    return result


def page(index=1, length=30, term='', key_word=''):
    """分页查询发票，后台管理用，index是页码，length是每页多少条记录
    term是查询的条件 相当于 where case=value中的case
    key_word查询条件的值 相当于 where case=value中的value
    """
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            session = db_module.sql_session()
            """如果是按照用户简称查询的话,需要转换为按照用户的sn查询"""
            if term == "customer_alias":
                sql = "select group_sn from user_group_info where company_alias like '%{0}%' " \
                      "or company_name like '%{0}%'".format(key_word)
                proxy = session.execute(sql)
                raw = proxy.fetchone()
                if raw is None:
                    raise ValueError("没有查询道用户id")
                else:
                    term = "customer_sn"
                    key_word = raw[0]
            columns = db_module.get_columns(table_name)
            if term != "" and key_word != "" and term in columns:
                sql = "select " + ",".join(columns) + (" from request_info where {}='{}' order by end_date desc "
                                                       "limit {},{}".format(term, key_word, (index - 1) * length, length))
            else:
                sql = "select " + ",".join(columns) + (" from request_info order by end_date desc "
                                                   "limit {},{}".format((index - 1) * length, length))
            try:
                proxy_result = session.execute(sql)
                result = proxy_result.fetchall()
                if len(result) != 0:
                    result = [db_module.str_format(x) for x in result]
                    data = [dict(zip(columns, x)) for x in result]
                else:
                    data = []
                message['data'] = data
            except Exception as e:
                print(e)
                message['message'] = "查询错误"
            finally:
                session.close()
        except TypeError:
            message['message'] = "参数错误"
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message
