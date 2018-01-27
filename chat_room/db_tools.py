# -*- coding:utf8 -*-
__author__ = 'Administrator'
import datetime, os, db_module
import logging

# 打印sql语句
sql_file = open(file="logs" + os.sep + "{0} sql_string.log".format(datetime.datetime.now().strftime("%Y%m%d")),
                mode="a", encoding="utf-8")


def printSqlStr(line, sql):
    astr = "{0} debug info ".format(str(datetime.datetime.now())) + __file__ + " line {0} execute sql: {1}".format(line,
                                                                                                                   sql)
    global sql_file
    print(astr, file=sql_file)
    sql_file.flush()


def print_func_sql(func_name, sql):
    """打印函数的sql语句"""
    astr = "{0} debug info ".format(str(datetime.datetime.now())) + __file__ + " function {0} execute sql: {1}".format(func_name,
                                                                                                                   sql)
    global sql_file
    print(astr, file=sql_file)
    sql_file.flush()


# 记录聊天内容
def talks(the_type, messages=[]):
    ses = db_module.sql_session()
    data = []
    if the_type == "save":
        if len(messages) == 0:
            print("没有消息写入数据库")
        else:
            for x in messages:
                print(x)
                user_level = x["user_level"]
                message = x["message"].replace("'", "￡")
                message_id = x["message_id"]
                come_from = x['come_from']
                atime = x["time"]
                name = x["name"]
                ip = x["ip"]
                page_url = x["page_url"]
                sql = "insert into chartroom_talks(user_level,message_id,message,come_from,time,name,page_url,ip,save_date) values({0},'{1}','{2}','{3}','{4}','{5}','{6}','{7}',now())".format(
                    user_level, message_id, message, come_from, atime, name, page_url, ip)
                printSqlStr(34, sql)
                ses.execute(sql)
            ses.commit()
    elif the_type == "delete":
        if len(messages) == 0:
            print("没有消息需要删除")
        else:
            temp = ''
            for x in messages:
                temp += "'" + x + "',"
            temp = temp.rstrip(",")
            sql = "delete from chartroom_talks where message_id in ({0})".format(temp)
            print(sql)
            printSqlStr(47, sql)
            ses.execute(sql)
            ses.commit()
    else:
        sql = "select user_level,message_id,message,come_from,time,name,page_url,ip from chartroom_talks order by save_date desc limit 0,40"
        printSqlStr(52, sql)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            pass
        else:
            data = [
                {"user_level": x[0], "message_id": x[1], "message": x[2].replace("￡", "'"), "come_from": x[3],
                 "time": x[4], "name": x[5],
                 "page_url": x[6], "ip": x[7]} for x in raw]
    ses.close()
    data.reverse()
    return {"data": data}


# 日志记录工具，按天切分
def get_logger_everyday(name):
    path = os.path.join(os.path.split(__file__)[0], "logs")
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass
    #when表示时间的间隔，interval表示是否循环，backupCount表示备份文件的数目
    fh = logging.handlers.TimedRotatingFileHandler(
        filename="logs" + os.sep + name +"_"+datetime.datetime.now().strftime("%Y%m%d")+ ".log",
        when="D",interval=1,backupCount=10,encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    # 日志部分
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        handlers=[fh]
                        )
    my_logger = logging.getLogger(name)
    return my_logger