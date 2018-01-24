# -*-coding:utf8-*-
import db_module


table_name = "user_info"
columns = db_module.get_columns(table_name, True)


def add_user(**kwargs):
    """添加用户"""
    kwargs['create_date'] = db_module.current_datetime()
    message = {"message": "success"}
    sql = db_module.structure_sql("add", table_name, **kwargs)
    ses = db_module.sql_session()
    try:
        ses.execute(sql)
        ses.commit()
    except Exception as e:
        print(e)
        message['message'] = '注册失败'
    finally:
        ses.close()
        return message