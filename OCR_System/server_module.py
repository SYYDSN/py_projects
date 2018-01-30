# -*-coding:utf-8-*-
import db_module


"""服务器及账户的配置信息"""

server_columns = db_module.get_columns("server_info", first=True)


def update_account_status(account_sn, account_status):
    """更新account_info表中的账户状态，"""
    ses = db_module.sql_session()
    sql = "update account_info set account_status={} where account_sn={}".format(account_status, account_sn)
    ses.execute(sql)
    ses.commit()
    ses.close()


def select_server(account_type):
    """自动选择服务器的及ftp的账户的sn
    account_type 是账户类型，1代表客户，2代表供应商
    """
    sql = "SELECT sn,(SELECT COUNT(1) FROM account_info WHERE server_sn=server_info.sn AND account_type={} AND " \
          "account_status=0) as e FROM server_info order by e desc".format(account_type)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    server_sn = raw[0]
    sql = "select account_sn from account_info where server_sn={} and account_type={} and account_status=0 " \
          "order by account_sn".format(server_sn, account_type)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    account_sn = raw[0]
    ses.close()
    return {"server_sn": server_sn, "account_sn": account_sn}


def get_server_info(the_sn, the_type):
    """根据sn获取用户的server和account信息
    the_sn, 用户sn或者供应商sn
    the_type，类型，1代表用户，其他代表供应商
    返回的是字典格式的对象
    """
    sn = str(the_sn)
    the_type = str(the_type)
    if sn.isdigit():
        table_name = "user_group_info" if the_type == "1" else "supplier_group_info"
        sql = "select server_sn, account_sn,request_token from {} where group_sn={}".format(table_name, sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        server_sn, account_sn, token = raw
        sql = "select ip, port from server_info where sn={}".format(server_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ip, port = raw
        sql = "select account_name, account_password from account_info where account_sn={}".format(account_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        account_name, account_password = raw
        ses.close()
        return {"ip": ip, "port": port, "account_name": account_name,
                "account_password": account_password, "token": token}
    else:
        raise ValueError("{} 不是一个可int化的对象".format(the_sn))

