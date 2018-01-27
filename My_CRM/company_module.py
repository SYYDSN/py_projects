# -*- coding:utf-8 -*-
import db_module
import hashlib

"""公司管理模块"""

table_name = "company_info"


def check_login(user_name, user_password_md5):
    """检验登录"""
    user_name = user_name.strip()
    user_password_md5 = user_password_md5.strip()
    message = {"message": "success"}
    if not db_module.validate_arg(user_name, "_"):
        message['message'] = "用户名非法"
    else:
        ses = db_module.sql_session()
        sql = "select sn,user_password from {} where user_status=1 and user_name='{}'".format(table_name, user_name)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is None:
            message['message'] = "用户名不存在"
        else:
            md5_str = raw[1]
            if md5_str != user_password_md5:
                message['message'] = "密码错误"
            else:
                message['data'] = {"sn": raw[0], "user_name": user_name, "user_password": user_password_md5}
    return message


def get_names():
    """获取所有sn和公司名的对应关系，返回dict"""
    sql = "select sn,company_name from {}".format(table_name)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        return dict()
    else:
        result = {x[0]: x[1] for x in raw}
        return result


def company_count(parent_sn=0):
    """统计所有数量,parent_sn 是父公司sn
    返回int对象
    """
    session = db_module.sql_session()
    result = 0
    sql = "select count(1) from {} where parent_sn={}".format(table_name, parent_sn)
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchone()[0]
    finally:
        session.close()
    return result


def add_company(**kwargs):
    """创建公司"""
    message = {"message": "success"}
    kwargs['create_date'] = db_module.current_datetime()
    user_password = kwargs['user_password']
    user_password = hashlib.md5(user_password.strip().encode()).hexdigest()
    kwargs['user_password'] = user_password
    sql = db_module.structure_sql("add", table_name, **kwargs)
    ses = db_module.sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()
    return message


def edit_company(**kwargs):
    """编辑公司信息"""
    message = {"message": "success"}
    sn = kwargs.pop("sn")
    user_password = kwargs['user_password']
    user_password = hashlib.md5(user_password.strip().encode()).hexdigest()
    kwargs['user_password'] = user_password
    term = "where sn={}".format(sn)
    sql = db_module.structure_sql("edit", table_name, term, **kwargs)
    ses = db_module.sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()
    return message


def delete_company(**kwargs):
    """删除公司信息"""
    message = {"message": "success"}
    sn = kwargs.pop("sn")
    term = "where sn={}".format(sn)
    sql = db_module.structure_sql("delete", table_name, term, **kwargs)
    ses = db_module.sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()
    return message


def page(index=1, length=30, term='', key_word=''):
    """分页查询，后台管理用，index是页码，length是每页多少条记录
    term是查询的条件 相当于 where case=value中的case
    key_word查询条件的值 相当于 where case=value中的value
    """
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            session = db_module.sql_session()
            columns = db_module.get_columns(table_name)
            if term != "" and key_word != "" and term in columns:
                sql = "select " + ",".join(columns) + (" from {} where {}='{}' order by create_date desc "
                                                       "limit {},{}".format(table_name, term, key_word, (index - 1) * length, length))
            else:
                sql = "select " + ",".join(columns) + (" from {} order by create_date desc "
                                                   "limit {},{}".format(table_name, (index - 1) * length, length))
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
        finally:
            pass
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message


if __name__ == "__main__":
    add_company(company_name="df", user_name="root", user_password="123456")