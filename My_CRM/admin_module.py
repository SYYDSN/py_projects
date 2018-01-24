# -*- coding:utf-8 -*-
import db_module


"""管理员模块"""


def check_login(user_name, user_password_md5):
    """检验登录"""
    user_name = user_name.strip()
    user_password_md5 = user_password_md5.strip()
    message = {"message": "success"}
    if not db_module.validate_arg(user_name, "_"):
        message['message'] = "用户名非法"
    else:
        ses = db_module.sql_session()
        sql = "select user_password from admin_info where admin_status=1"
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is None:
            message['message'] = "用户名不存在"
        else:
            raw = raw[0]
            if raw != user_password_md5:
                message['message'] = "密码错误"
            else:
                pass
    return message
