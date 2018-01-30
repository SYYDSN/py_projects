# -*-coding:utf8-*-
import db_module
import sqlalchemy.exc
import re


"""用户模块，是user_group_module的子模块"""


table_name = "user_info"


def add_user(**kwargs):
    """增加用户,参数必须是键值对的形式,"""
    message = {"message": "success"}
    session = db_module.sql_session()
    try:
        create_date = db_module.current_datetime()
        kwargs['create_date'] = create_date
        sql = db_module.structure_sql("add", table_name, **kwargs)
        session.execute(sql)
        session.commit()
    except sqlalchemy.exc.IntegrityError as e1:
        """
        re.findall(r"for key '(.+?)'",str) 是从str中找到匹配以for key 'PRIMARY'")
        句子中的PRIMARY,findall方法返回的是数组
        """
        print(e1.args)
        error_cause = re.findall(r"for key '(.+?)'", e1.args[-1])[0]
        if error_cause == "user_name":
            message["message"] = "用户名已存在"
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


def edit_user(**kwargs):
    """修改用户资料,参数必须是键值对的形式"""
    message = {"message": "success"}

    user_id = kwargs.pop("user_id", None)
    if user_id is None or not user_id.isdigest():
        message["message"] = "无效的用户ID"
    else:
        user_id = int(user_id) if isinstance(user_id, str) else user_id
        sql = db_module.structure_sql("edit", table_name, query_terms="where user_id={} and user_status!=0".format(user_id),
                                      **kwargs)
        session = db_module.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = '编辑用户信息失败'
        finally:
            session.close()
    return message


def change_user_status(the_type, user_id):
    """启用/禁用/删除用户 ,第一个参数是up/down/delete ，启用或者禁用，第二个是用户id"""
    message = {"message": "success"}
    if db_module.validate_arg(user_id) and db_module.validate_arg(user_id):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update {} set user_status=1 where sn={} and user_status!=0".format(table_name, user_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from {} where sn='{}' and user_status!=0".format(table_name, user_id)
        else:
            verb = "禁用"
            sql = "update {} set user_status=0 where sn={} and user_status!=0".format(table_name, user_id)
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
        message['message'] = "执行错误"
    return message


def check_user_identity(user_name, user_password):
    """根据用户账户密码获取用户资料，一般是用户登录用"""
    message = {"message": "success"}
    if db_module.validate_arg(user_name):
        session = db_module.sql_session()
        columns = db_module.get_columns(table_name)
        sql = "select " + ",".join(columns) + " from {} where user_name='{}'".format(table_name, user_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()
            if result is None:
                message['message'] = "此ID不存在"
            else:
                result = db_module.str_format(result)
                result = dict(zip(columns, result))
                if user_password.lower() != result['user_password']:
                    message['message'] = "密码错误"
                else:
                    message['result'] = result
        except Exception as e:
            print(e)
            message['message'] = '查询失败'
        finally:
            session.close()
    else:
        message['message'] = "参数错误"
    return message


def user_count(available=True):
    """统计所有公司的数量，available参数表示是否统计被禁用的账户，默认为统计
    返回int对象
    """
    redis_client = db_module.MyRedis.redis_client()
    key = "{}_count".format(table_name)
    result = redis_client.get(key)
    if not result:
        session = db_module.sql_session()
        if available:
            sql = "select count(1) from {} where user_type!=0".format(table_name)
        else:
            sql = "select count(1) from {} where user_status=1 and user_type!=0".format(table_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set(key, result, ex=5 * 60)
    else:
        result = int(result)
    return result


def view_all():
    """查询所有用户的信息,以list形式返回"""
    result = list()
    ses = db_module.sql_session()
    columns = db_module.get_columns(table_name)
    sql = "select " + ",".join(columns) + " from {} where user_type!=0".format(table_name)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = [db_module.str_format(x) for x in raw]
        result = dict(zip(columns, result))
    return result


def down_all(user_group_id):
    """根据公司的id一次性停用此公司下所有用户，包括根用户,成功返回布尔值True"""
    status = True
    ses = db_module.sql_session()
    sql = "update {} set user_status=0 where group_sn={}".format(table_name, user_group_id)
    try:
        ses.execute(sql)
        ses.commit()
    except Exception as e:
        print(e)
        status = False
    finally:
        ses.close()
    return status


def drop_all(user_group_id):
    """根据公司的id一次性删除此公司下所有用户，包括根用户,成功返回布尔值True"""
    status = True
    ses = db_module.sql_session()
    sql = "delete from {} where group_sn={}".format(table_name, user_group_id)
    try:
        ses.execute(sql)
        ses.commit()
    except Exception as e:
        print(e)
        status = False
    finally:
        ses.close()
    return status


def up_root(user_group_id):
    """根据公司的id启用已被禁用的根用户,如果启用失败，成功返回布尔值True"""
    status = True
    ses = db_module.sql_session()
    sql = "update {} set user_status=1 where user_type=0 and group_sn={}".format(table_name, user_group_id)
    try:
        ses.execute(sql)
        ses.commit()
    except Exception as e:
        print(e)
        status = False
    finally:
        ses.close()
    return status

