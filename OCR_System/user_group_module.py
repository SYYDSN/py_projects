# -*- coding:utf8 -*-
import db_module
import sqlalchemy.exc
import re
from uuid import uuid4
import server_module
import user_module


table_name = "user_group_info"

db_module.get_columns(table_name, True)  # 第一次启动时加载


def sn_alias():
    """获取用的sn和company_alias的对应关系，返回dict"""
    sql = "select group_sn, company_alias from user_group_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    result = {}
    if len(raw) == 0:
        pass
    else:
        result = {x[0]: x[1] for x in raw}
    return result


def query_sn_like():
    pass


def add_user_group(**kwargs):
    """增加公司,参数必须是键值对的形式,"""
    message = {"message": "success"}
    session = db_module.sql_session()
    try:
        create_date = db_module.current_datetime()
        request_token = uuid4().hex  # 取request_token
        server_account = server_module.select_server(1)  # 从服务器列表选择一个服务器和一个sftp用户id 返回的是键值对
        kwargs['create_date'] = create_date
        kwargs['request_token'] = request_token
        kwargs.update(server_account)
        sql = db_module.structure_sql("add", table_name, **kwargs)  # 跟新user_group_info表
        session.execute(sql)
        session.commit()
        server_module.update_account_status(server_account['account_sn'], 1)
    except sqlalchemy.exc.IntegrityError as e1:
        """
        re.findall(r"for key '(.+?)'",str) 是从str中找到匹配以for key 'PRIMARY'")
        句子中的PRIMARY,findall方法返回的是数组
        """
        print(e1.args)
        error_cause = re.findall(r"for key '(.+?)'", e1.args[-1])[0]
        if error_cause == "company_name":
            message["message"] = "此公司已存在"
        elif error_cause == "company_alias":
            message["message"] = "公司简称重复"
        else:
            print(error_cause)
            message['message'] = "注册失败，请查看日志"
    except Exception as e2:
        print(e2)
        print("未知错误")
        message['message'] = "语句执行失败"
    finally:
        session.close()
    return message


def edit_user_group(**kwargs):
    """修改公司资料,参数必须是键值对的形式"""
    message = {"message": "success"}

    user_group_id = kwargs.pop("group_sn", None)
    if user_group_id is None or not user_group_id.isdigit():
        message["message"] = "无效的用户ID"
    else:
        user_group_id = int(user_group_id) if isinstance(user_group_id, str) else user_group_id
        sql = db_module.structure_sql("edit", table_name, query_terms="where group_sn={}".format(user_group_id),
                                      **kwargs)
        session = db_module.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = '编辑公司信息失败'
        finally:
            session.close()
    return message


def change_user_group_status(the_type, user_group_id):
    """启用/禁用/删除公司 ,第一个参数是up/down/delete ，启用或者禁用，第二个是公司id"""
    message = {"message": "success"}
    if db_module.validate_arg(user_group_id) and db_module.validate_arg(user_group_id):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update {} set group_status=1 where group_sn={}".format(table_name, user_group_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from {} where group_sn='{}'".format(table_name, user_group_id)
        else:
            verb = "禁用"
            sql = "update {} set group_status=0 where group_sn={}".format(table_name, user_group_id)
        session = db_module.sql_session()
        try:
            if the_type.strip().lower() == "up":
                sql_sub = "update account_info set account_status=1 where account_sn=(select account_sn from " \
                      "{} where group_sn={})".format(table_name, user_group_id)
            else:
                sql_sub = "update account_info set account_status=0 where account_sn=(select account_sn from " \
                      "{} where group_sn={})".format(table_name, user_group_id)
            session.execute(sql_sub)
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = "{}账户失败".format(verb)
        finally:
            session.close()
    else:
        message['message'] = "公司ID错误"
    return message


def get_user_group_info(user_group_id):
    """根据公司id获取信息"""
    message = {"message": "success"}
    if db_module.validate_arg(user_group_id):
        session = db_module.sql_session()
        columns = db_module.get_columns(table_name)
        sql = "select " + ",".join(columns) + " from {} where group_sn={}".format(table_name, user_group_id)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "此ID不存在"
            else:
                result = db_module.str_format(result)
                result = dict(zip(columns, result))
                message['result'] = result
        except Exception as e:
            print(e)
            message['message'] = '查询失败'
        finally:
            session.close()
    else:
        message['message'] = "参数错误"
    return message


def user_group_count(available=True):
    """统计所有公司的数量，available参数表示是否统计被禁用的账户，默认为统计
    返回int对象
    """
    redis_client = db_module.MyRedis.redis_client()
    key = "{}_count".format(table_name)
    result = redis_client.get(key)
    if not result:
        session = db_module.sql_session()
        if available:
            sql = "select count(1) from {}".format(table_name)
        else:
            sql = "select count(1) from {} where group_status=1".format(table_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set(key, result, ex=5 * 60)
    else:
        result = int(result)
    return result


def page(index=1, length=30):
    """分页查询公司，后台管理用，index是页码，length是每页多少条记录"""
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            session = db_module.sql_session()
            columns = db_module.get_columns(table_name)
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
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message


def check_author(author):
    '''
    检查服务器author
    :param author:
    :return:
    '''
    ses = db_module.sql_session()
    sql = "select group_sn, server_sn from user_group_info where request_token='{}'".format(author)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw:
        return raw[0]
    else:
        return None


def get_server_ip(author):
    """通过服务器author获取服务器ip"""
    ses = db_module.sql_session()
    sql = "select group_sn, server_sn from user_group_info where request_token='{}'".format(author)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    if raw is None:
        raise ValueError("没有找到对应的客户，客户sn为{}".format(author))
    else:
        group_sn, server_sn = raw[0], raw[1]
    sql = "select sn, ip from server_info where sn={}".format(server_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        raise ValueError("没有找到对应的服务ip，客户sn为为{}".format(author))
    else:
        return group_sn, raw[1], raw[0]

# print(get_server_ip('8af044f186374563b30dfd5f3da2b5e3'))