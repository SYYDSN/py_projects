# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
import db_module, datetime


# 采集聊天记录写入数据库作为机器人对话的备选语句。dialog_list是聊天记录的数组，{ 'time': '00:00:10', 'name': '挑战者','message': 'xxxx'}这样组成的dict的list
def insert_dialog_to_database(dialog_list):
    alist = [x["message"].strip() for x in dialog_list if
             (x["message"].strip('') != '' and len(x["message"].strip('')) < 255)]
    ses = db_module.sql_session()
    count = 0
    # 先读取数据库里所有已存在的对话记录
    sql = "select s_string from Robot_Dialog_Collector"
    proxy = ses.execute(sql)
    result = proxy.fetchall()
    if len(result) == 0:
        for x in alist:
            sql_insert = "insert into Robot_Dialog_Collector(s_string) values('{0}') ".format(x)
            ses.execute(sql_insert)
            count += 1
        CONN.commit()
    else:
        query_list = [x[0] for x in result]
        for x in alist:
            if x in query_list:
                pass
            else:
                sql_insert = "insert into Robot_Dialog_Collector(s_string) values('{0}') ".format(x)
                ses.execute(sql_insert)
                count += 1
        ses.commit()
    ses.close()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 本次操作结束的的日期
    # print(now_str+"本次插入"+str(count)+"条对话记录到Robot_Dialog_Collector")
