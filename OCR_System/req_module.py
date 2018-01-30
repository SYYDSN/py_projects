# -*-coding:utf8-*-
import db_module
import json

"""req记录模块"""


def begin(to_sn, command, request_message):
    """记录请求开始"""
    ses = db_module.sql_session()
    arg_dict = {"from_sn": 2, "to_sn": to_sn, "command": command,
                "request_message": json.dumps(request_message),
                "request_time": db_module.current_datetime()}
    sql = db_module.structure_sql("add", "req", **arg_dict)
    proxy = ses.execute(sql)
    sn = proxy.lastrowid
    ses.commit()
    ses.close()
    return sn


def end(req_sn, response_message):
    """记录请求结束"""
    ses = db_module.sql_session()
    sql = "update req set response_message='{}' where sn={}".format(json.dumps(response_message), req_sn)
    ses.execute(sql)
    ses.commit()
    ses.close()


def check():
    """启动时检查未完成的req"""
    sql = "select req.sn,server_info.ip, command, request_message from req, server_info where " \
          "server_info.sn=req.to_sn and  from_sn=3 and response_message is null"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        return list()
    else:
        return [{"sn": x[0], "ip": x[1], "command": x[2], "request_message": json.loads(x[3])} for x in raw]
