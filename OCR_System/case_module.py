# -*-coding:utf8-*-
import db_module


"""赔案模块"""

table_name = "case_info"
columns = db_module.get_columns(table_name, True)


def case_count():
    """统计所有批次的数量
    返回int对象
    """
    redis_client = db_module.MyRedis.redis_client()
    result = redis_client.get("case_count")
    if not result:
        session = db_module.sql_session()
        sql = "select count(1) from {}".format(table_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set("case_count", result, ex=5 * 60)
    else:
        result = int(result)
    return result


def page(index=1, length=30, term='', key_word=''):
    """分页查询批次，后台管理用，index是页码，length是每页多少条记录
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
                    message['message'] = "没有查询道用户id"
                    message['data'] = []
                    return message
                else:
                    term = "customer_sn"
                    key_word = raw[0]
            """如果是使用批次号查询的话，需要转换为使用batch_sn查询"""
            if term == "batch_name":
                sql = "select batch_sn from batch_info where batch_name like '%{0}%'".format(key_word)
                proxy = session.execute(sql)
                raw = proxy.fetchone()
                if raw is None:
                    message['message'] = "没有查询到批次"
                    message['data'] = []
                    return message
                else:
                    term = "batch_sn"
                    key_word = raw[0]
            columns = db_module.get_columns(table_name)
            if term != "" and key_word != "" and term in columns:
                sql = "select " + ",".join(columns) + (" from {} where {}='{}' order by case_sn desc "
                                                       "limit {},{}".format(table_name, term, key_word, (index - 1) * length, length))
            else:
                sql = "select " + ",".join(columns) + (" from {} order by case_sn desc "
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

