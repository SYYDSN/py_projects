# -*-coding:utf8-*-
from db_module import *


def admin_login(user_name, user_password):
    """管理员登录，默认 admin Eai123456 """
    message = {"message": "success"}
    if isinstance(user_name, str) and isinstance(user_password, str):
        user_name = user_name.lower()
        user_password = user_password.lower()
        ses = sql_session()
        sql = "select sn,user_name,user_password from admins where user_name='{}'".format(user_name)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is None:
            message['message'] = "用户名不存在"
        else:
            if user_password == raw[2]:
                message['user_sn'] = raw[0]
                message['user_name'] = user_name
                message['user_password'] = user_password
            else:
                message['message'] = '密码错误'
    else:
        message = {"message": "用户名或者密码缺失"}
    return message

