# -*-coding:utf8-*-
import db_module

"""批次模块"""

table_name = "batch_info"
columns = db_module.get_columns(table_name, True)


def batch_count():
    """统计所有批次的数量
    返回int对象
    """
    redis_client = db_module.MyRedis.redis_client()
    result = redis_client.get("batch_count")
    if not result:
        session = db_module.sql_session()
        sql = "select count(1) from {}".format(table_name)
        try:
            proxy_result = session.execute(sql)
            result = proxy_result.fetchone()[0]
        finally:
            session.close()
            redis_client.set("batch_count", result, ex=5 * 60)
    else:
        result = int(result)
    return result


def sn_batch():
    """获取sn和batch_name的对应关系，返回dict"""
    sql = "select batch_sn, batch_name from batch_info"
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


def batch_sn_list(the_type="customer", sn=0):
    """获取客户/供应商的sn的列表，返回数组"""
    query = "where customer_sn={}".format(sn)
    if the_type == "supplier":
        query = "where supplier_sn={}".format(sn)
    sql = "select batch_sn from {} {}".format(table_name, query)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    result = list()
    if len(raw) == 0:
        pass
    else:
        result = [x[0] for x in raw]
    return result


def __save_batch(batch_dict, group_sn):
    """批量存储批次信息"""
    now = db_module.current_datetime()

    """先插请求表,返回请求sn"""
    print(batch_dict)
    print(group_sn)
    request_sn = 0
    ses = db_module.sql_session()
    if len(batch_dict) > 0:
        sql = "insert into request_info(customer_sn, begin_date) values({},'{}')".format(group_sn, now)
        print(sql)

        proxy = ses.execute(sql)
        ses.commit()
        request_sn = proxy.lastrowid

    for k, v in batch_dict.items():
        x = dict()
        x['batch_name'] = k
        x['batch_md5'] = v
        x['request_sn'] = request_sn
        x['begin_datetime'] = now
        x['prev_datetime'] = now
        x['customer_sn'] = group_sn
        sql = db_module.structure_sql("add", "batch_info", **x)
        ses.execute(sql)
        print(sql)
        ses.commit()
    ses.close()
    return request_sn


def exist(batch_dict, group_sn):
    """检查当前请求的批次文件是否已存储过？"""
    batch_dict = {(k.split(".zip")[0] if k.endswith(".zip") else k): v for k, v in batch_dict.items()}
    sql = "select batch_name, batch_md5 from batch_info where customer_sn={}".format(group_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        return __save_batch(batch_dict, group_sn)
    else:
        raw = {x[0]: x[1] for x in raw}
        new_dict = dict()
        for k, v in batch_dict.items():
            if k in raw and v == raw[k]:
                pass
            else:
                new_dict[k] = v
        if len(new_dict) > 0:
            return __save_batch(new_dict, group_sn)
        else:
            return 0


def close_request_recode(request_sn):
    """关闭请求的记录"""
    end = db_module.current_datetime()
    sql = db_module.structure_sql("edit", "request_info", "where request_sn={}".format(request_sn), end_date=end)
    ses = db_module.sql_session()
    ses.execute(sql)
    ses.commit()
    ses.close()


def get_customer_sn(batch_sn: int) -> int:
    """根据批次sn获取此批次所属的客户的sn
    batch_sn: 批次sn
    return int  客户sn，没有对应的客户或者批次sn错误返回None
    """
    sql = "select customer_sn from batch_info where batch_sn={}".format(batch_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        return raw[0]


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
                    raise ValueError("没有查询道用户id")
                else:
                    term = "customer_sn"
                    key_word = raw[0]
            columns = db_module.get_columns(table_name)
            if term != "" and key_word != "" and term in columns:
                sql = "select " + ",".join(columns) + (" from {} where {}='{}' order by begin_datetime desc "
                                                       "limit {},{}".format(table_name, term, key_word,
                                                                            (index - 1) * length, length))
            else:
                sql = "select " + ",".join(columns) + (" from {} order by begin_datetime desc "
                                                       "limit {},{}".format(table_name, (index - 1) * length, length))
            try:
                proxy_result = session.execute(sql)
                result = proxy_result.fetchall()
                if len(result) != 0:
                    result = [db_module.str_format(x) for x in result]
                    raw_data = [dict(zip(columns, x)) for x in result]
                    data = list()
                    for x in raw_data:
                        batch_sn = x['batch_sn']
                        sql = "select count(1),sum(is_return) from image_info where batch_sn={}".format(batch_sn)
                        proxy = session.execute(sql)
                        raw = proxy.fetchone()
                        temp = x
                        if raw is None:
                            temp["image_count"] = "0/0"
                        else:
                            temp["image_count"] = "{} / {}".format(0 if raw[1] is None else raw[1],
                                                                   0 if raw[0] is None else raw[0])
                        data.append(temp)
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


def change_to_checked(batch_sn, to_checked):
    """审核/反审核批次
    batch 批次号
    to_checked  为to_checked的状态，取值为1和0 标识审核通过和不通过
    return {"message": "success"}
    """
    messgae = {"message": "success"}
    sql = "update batch_info set to_checked={} where batch_sn={}".format(to_checked, batch_sn)
    ses = db_module.sql_session()
    try:
        ses.execute(sql)
        ses.commit()
    except Exception:
        messgae['message'] = "插入失败"
    finally:
        ses.close()
        return messgae


if __name__ == "__main__":
    batch_info = {"file4.zip": "ccccc", "file5.zip": "dddddd", "file6.zip": "eeeeeee"}
    print(__save_batch(batch_info, 1))
