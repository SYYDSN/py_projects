# -*-coding:utf-8-*-
import db_module

table_name = "userinfo"
columns = db_module.get_columns(table_name, True)

def all_user():
    ses = db_module.sql_session()
    col_str = ",".join(columns)
    sql = "select {} from {} order by u_CreateTime desc".format(col_str, table_name)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    result = [dict(zip(columns, db_module.str_format(x))) for x in raw]
    return result


