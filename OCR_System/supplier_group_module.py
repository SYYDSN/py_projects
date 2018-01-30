# -*-coding:utf-8-*-
import db_module
import server_module
import sqlalchemy.exc
from uuid import uuid4
import re


"""供应商模块"""

cache = db_module.cache
table_name = "supplier_group_info"
db_module.get_columns(table_name, first=True)


def check_author(token):
    """检查供应商的token,成功返回供应商sn"""
    key = "supplier_token"
    token_dict = cache.get(key)
    if token_dict is None:
        sql = "select request_token,group_sn from supplier_group_info where group_status=1"
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        print(raw)
        if len(raw) == 0:
            return False
        else:
            token_dict = {x[0]: x[1] for x in raw}
            cache.set(key, token_dict, timeout=60 * 60)
    if token in token_dict:
        return token_dict[token]
    else:
        return None


def get_supplier_list():
    """获取全部可用的供应商列表"""
    ses = db_module.sql_session()
    sql = "select group_sn,company_alias from supplier_group_info where group_status=1"
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    result = [{"group_sn": x[0], "supplier_alias": x[1]} for x in raw]
    return result


def supplier_group_count(available=True):
    """统计所有供应商的数量，available参数表示是否统计被禁用的账户，默认为统计
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
    """分页查询供应商，后台管理用，index是页码，length是每页多少条记录"""
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


def add_supplier_group(**kwargs):
    """增加供应商,参数必须是键值对的形式,"""
    message = {"message": "success"}
    session = db_module.sql_session()
    try:
        create_date = db_module.current_datetime()
        request_token = uuid4().hex  # 取request_token
        server_account = server_module.select_server(2)  # 从服务器列表选择一个服务器和一个sftp用户id 返回的是键值对
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


def change_supplier_group_status(the_type, supplier_group_id):
    """启用/禁用/删除供应商 ,第一个参数是up/down/delete ，启用或者禁用，第二个是供应商id"""
    message = {"message": "success"}
    if db_module.validate_arg(supplier_group_id) and db_module.validate_arg(supplier_group_id):
        if the_type.strip().lower() == "up":
            verb = "启用"
            sql = "update {} set group_status=1 where group_sn={}".format(table_name, supplier_group_id)
        elif the_type.strip().lower() == "delete":
            verb = "删除"
            sql = "delete from {} where group_sn='{}'".format(table_name, supplier_group_id)
        else:
            verb = "禁用"
            sql = "update {} set group_status=0 where group_sn={}".format(table_name, supplier_group_id)
        session = db_module.sql_session()
        try:
            if the_type.strip().lower() == "up":
                sql_sub = "update account_info set account_status=1 where account_sn=(select account_sn from " \
                      "{} where group_sn={})".format(table_name, supplier_group_id)
            else:
                sql_sub = "update account_info set account_status=0 where account_sn=(select account_sn from " \
                      "{} where group_sn={})".format(table_name, supplier_group_id)
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


def edit_supplier_group(**kwargs):
    """修改供应商资料,参数必须是键值对的形式"""
    message = {"message": "success"}

    group_id = kwargs.pop("group_sn", None)
    if group_id is None or not group_id.isdigit():
        message["message"] = "无效的用户ID"
    else:
        ugroup_id = int(group_id) if isinstance(group_id, str) else group_id
        sql = db_module.structure_sql("edit", table_name, query_terms="where group_sn={}".format(group_id),
                                      **kwargs)
        session = db_module.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = '编辑供应商信息失败'
        finally:
            session.close()
    return message
