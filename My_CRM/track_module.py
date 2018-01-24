# -*- coding:utf-8 -*-
import db_module

"""跟进模块"""

table_name = "base_track_info"
customer_table = "customer_info"
track_table = "track_info"
columns = db_module.get_columns(table_name, True)
customer_columns = db_module.get_columns(customer_table, True)
track_columns = db_module.get_columns(track_table, True)


def count(employee_sn):
    """统计"""
    sql = "select count(1) from {} where employee_sn={}".format(customer_table, employee_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    result = raw[0]
    return result


def get_track_type():
    """获取跟踪类型"""
    temp = ",".join(track_columns)
    sql = "select sn,type_name from track_type_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    result = {str(x[0]): x[1] for x in raw}
    return result


def page(employee_sn, index=1, length=30, term=''):
    """分页查询注册用户，后台管理用，
    employee_sn  员工sn
    index是页码，
    length是每页多少条记录
    term 是查询条件表达式 类是 user_sn>10 暂时不用
    return  数组
    """
    result = []
    try:
        index = int(index)
        length = int(length)
    except ValueError:
        index = ""
    if db_module.validate_arg(term, "_") and index != "":
        """参数检查通过"""
        skip = (index - 1) * length
        limit = length
        join_cols = ["a.{}".format(x) for x in customer_columns]
        sql = "select {},b.track_status,b.customer_level from {} a left join {} b on a.user_sn=b.sn where employee_sn={} and a.in_pool=0 order by create_date desc limit {},{}". \
            format(",".join(join_cols), customer_table, table_name, employee_sn, skip, limit)

        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            new_col = customer_columns.copy()
            new_col.extend(["track_status", "customer_level"])
            data = list()
            for x in raw:
                temp = [y if y is not None else '' for y in x]
                if x[-2] is None or x[-2] == '':
                    begin_track(x[0], employee_sn)
                data.append(temp)
            result = [dict(zip(new_col, x)) for x in data]
    else:
        pass
    return result


def begin_track(customer_sn, employee_sn):
    """
    开始跟踪
    :param customer_sn:
    :param employee_sn:
    :return: None
    """
    """先检查是否有基本跟进信息"""
    ses = db_module.sql_session()
    sql = "select count(1) from {} where sn={}".format(table_name, customer_sn)
    proxy = ses.execute(sql)
    has_it = proxy.fetchone()[0]
    if has_it == 0:
        args = {"begin_date": db_module.current_datetime(), "sn": customer_sn}
        sql = db_module.structure_sql("add", table_name, **args)
        ses.execute(sql)
        ses.commit()
    """插入一条跟进信息"""
    args = {"customer_sn": customer_sn, "employee_sn": employee_sn, "track_type_sn": 14, "create_date":
        db_module.current_datetime()}
    sql = db_module.structure_sql("add", track_table, **args)
    ses.execute(sql)
    args = {"track_status": 14}
    sql = db_module.structure_sql("edit", table_name, "where sn={}".format(customer_sn), **args)
    ses.execute(sql)
    ses.commit()
    ses.close()
