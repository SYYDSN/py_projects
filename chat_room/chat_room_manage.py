# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
import threading, time, random, json, sys, datetime, os, threading, time, Chat_Room
import Dialog_Collector
import sys, db_module
import db_tools
import sys
from ext_tools import get_logger_everyday


PREV_DIALOG_LIST = []  # 全局变量，保存本次比较前的上一次对话[guest_id,user_id,user_name,teacher_id,dialog_message,dialog_type,now_str,page_url,ip]用于保存私聊内容  0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
DIALOG_LIST = []  # 全局变量，保存最新的对话信息[guest_id,user_id,user_name,teacher_id,dialog_message,dialog_type,now_str,page_url,ip]用于保存私聊内容  0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
USER_INFO = []  # 全局变量，用来存储聊天室用户的身份信息的{"guest_id",“user_id","ws_id","page_url","status"} 0。客户匿名id，1.注册用户id  2 ws_id 3.聊天室地址 4.是否在线？online offline 此对象中的userid将永远为0，我们将使用匿名id配合匿名id和用户id的对应关系来判断登录情况。
GUEST_ID_AND_USER_ID = []  # 全局变量，存储登录用户信息。{"guest_id":guest_id,"user_id":user_id}
CUSTOMER_AND_SALES = []  # 全局变量，保存聊天室登录的客户和销售人员的对应关系
ROBOT_LIST = []  # 全局变量，存储机器人的发言。
logger = get_logger_everyday(__name__)


def get_conn():
    return db_module.sql_session()


# 打印sql语句
sql_file = open(file="logs" + os.sep + "{0} sql_string.log".format(datetime.datetime.now().strftime("%Y%m%d")),
                mode="a", encoding="utf-8")


def printSqlStr(line, sql):
    astr = "{0} debug info ".format(str(datetime.datetime.now())) + __file__ + " line {0} execute sql: {1}".format(line,
                                                                                                                   sql)
    global sql_file
    print(astr, file=sql_file)
    sql_file.flush()


# 一个访问ip过滤器，用于过滤有问题ip,以下几种情况需要过滤ip
# 1。恶意行为主要表现为快速的同一地址注册，发言等。这种行为可以自动进行屏蔽。
# 2.发广告，不良信息的，这些需要人为甄别。然后决定是否手动屏蔽
class ip_filter:
    def __init__(self):
        self.ip_list = []  # 这个数组是给手动屏蔽ip准备的容器，里面是ip的字符串
        ses = get_conn()
        sql = "select i_ip from ChartRoom_Black_Ip_List"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            self.ip_list = [x[0] for x in raw]
        self.prev_ip_info = []  # 一个字典的数组，没一个字典{"ip":ip,"prev_time":time,"the_type":reg} 其中type可能的类型reg：注册 dialog：发言 等  这个字典数组专门为自动屏蔽准备的

    def listen(self, ip, the_type):  # 此方法被调用时会计算同一ip重复某样操作的次数
        pass  # 未完成


# 检测用户名是否重复的方法
def check_user_repeat(user_name=''):
    ses = get_conn()
    message = {}
    check_sql = "select COUNT(1) from userinfo where u_AccountName='{0}'".format(user_name.strip())
    proxy = ses.execute(check_sql)
    raw = proxy.fetchone()[0]
    if raw > 0:
        message = {"message": "{0}这个用户名已经被占用，请重新输入一个用户名".format(user_name)}
    else:
        message = {"message": "success"}
    ses.close()
    return message


# 聊天室用户注册的方法
def user_reg(user_name='', user_password='', user_phone='', nick_name='', ip='未知'):
    message = {"message": "success"}
    if user_name == '' or user_password == '' or user_phone == '':
        message = {"message": "缺少必要信息"}
    else:
        ses = get_conn()
        check_sql = "select COUNT(1) from userinfo where u_phone='{0}'".format(user_phone.strip())
        proxy = ses.execute(check_sql)
        raw = proxy.fetchone()[0]
        if raw > 0:
            ses.close()
            message = {"message": "{0}已经注册过，请直接登录或联系客服".format(user_phone)}
        else:
            check_sql = "select COUNT(1) from userinfo where u_AccountName='{0}'".format(user_name.strip())
            proxy = ses.execute(check_sql)
            raw = proxy.fetchone()[0]
            if raw > 0:
                ses.close()
                message = {"message": "用户名{0}已被占用，请更改用户名后重试".format(user_name)}
            else:
                sql = "insert into userinfo(u_AccountName,u_AccountPassword,u_phone,u_RealName,u_CreateTime,u_CanUse,u_Level) values('{0}','{1}','{2}','{3}',now(),1,5)".format(
                    user_name, user_password, user_phone, nick_name)
                print(sql)
                db_tools.print_func_sql(sys._getframe().f_code.co_name, sql)
                ses.execute(sql)
                ses.commit()
                ses.close()
    return message


#############################一个检测老师管理员登录的方法#########################################
def check_login(username='', password=''):
    if username == '' or username is None or password == '' or password is None:
        return {"message": "error"}
    else:
        sql = "select t_Id,t_AccountPassword from teacheradmin where t_AccountName='{0}' and can_login=1".format(
            username.lower())
        print(sql)
        ses = get_conn()
        proxy = ses.execute(sql)
        query_result = proxy.fetchone()
        ses.close()
        query_result = (0 if query_result is None else query_result)
        print("用户名查询结果：")
        print(query_result)
        if query_result == 0:
            return {"message": "用户不存在"}
        else:
            result = query_result[1]  # 密码
            if result.lower() == password.lower():
                print("check login ok")
                return {"message": "success", "teacher_name": username, "teacher_id": query_result[0]}
            else:
                print("check login error username is {0},password is {1}".format(username, password))
                return {"message": "密码错误"}


##################################获取老师后台用户列表############################################
def query_teacher_admin(username='', password=''):
    if check_login(username, password)["message"] == "success":  # 检查用户身份和权限。
        ses = get_conn()
        sql = "select t_AccountName,t_AccountPassword,phone,can_login from teacheradmin where t_AccountName!='admin_user'"  # 0用户名，1.密码 2.手机 3.是否可登录
        proxy = ses.execute(sql)
        result = proxy.fetchall()
        ses.close()
        result = [list(x) for x in result]
        return json.dumps(result)  # 返回查询到的
    else:
        print("用户名或密码错误")
        return {"message": "error"}


##################管理后台老师的各种操作####################################
def edit_teacher_user(event_type, objname, password=""):
    ses = get_conn()
    message = {"message": "success"}
    print(event_type)
    if event_type == "reset_password":  # 重设密码 123456
        sql = "update teacheradmin set t_AccountPassword='E10ADC3949BA59ABBE56E057F20F883E' where t_AccountName='{0}'".format(
            objname)
        try:
            ses.execute(sql)
            ses.commit()
        except Exception as e:
            logger.exception("Error: ")
            message['message'] = "执行错误"
        finally:
            ses.close()
    elif event_type == "check_objname":  # 检查用户是否重复
        sql = "select count(*) from teacheradmin  where t_AccountName='{0}'".format(objname)
        print(sql)
        try:
            proxy = ses.execute(sql)
            result = proxy.fetchone()[0]
            ses.close()
            if result > 0:
                message["message"] = "find!"
            else:
                message["message"] = "not find!"
        except Exception as e:
            logger.exception("Error: ")
            message['message'] = "执行错误"
        finally:
            ses.close()
    elif event_type == "add_user":  # 添加用户
        print(objname)
        print(password)
        if password == '':
            ses.close()
            message = {"message": "密码不能为空"}
        else:
            sql1 = "select count(*) from teacheradmin  where t_AccountName='{0}'".format(objname)
            proxy = ses.execute(sql1)
            result = proxy.fetchone()[0]
            if result > 0:
                ses.close()
                message = {"message": "用户已存在"}
            else:
                sql = "insert into teacheradmin(t_AccountName,t_AccountPassword) values('{0}','{1}')".format(objname,
                                                                                                             password)
                print(sql)
                ses.execute(sql)
                ses.commit()
                ses.close()
                message = {"message": "success"}
    elif event_type == "change_name":  # 修改老师昵称
        sql = "update teacheradmin set t_Name='{0}' where t_AccountName='{1}'".format(password,
                                                                                      objname)  # 注意这里的password实际上是老师的t_Name。
        print(sql)
        ses.execute(sql)
        ses.commit()
        ses.close()
        message = {"message": "success"}
    elif event_type == "stop_login":  # 停用账户
        sql = "update teacheradmin set can_login=0 where t_AccountName='{0}'".format(objname)
        print(sql)
        ses.execute(sql)
        ses.commit()
        ses.close()
        message = {"message": "success"}
    elif event_type == "delete":  # 删除账户
        sql = "delete teacheradmin where t_AccountName='{0}'".format(objname)
        print(sql)
        ses.execute(sql)
        ses.commit()
        ses.close()
        message = {"message": "success"}
    elif event_type == "change_password":  # 修改密码
        sql = "update teacheradmin set t_AccountPassword='{1}' where t_AccountName='{0}'".format(objname, password)
        print(sql)
        ses.execute(sql)
        ses.commit()
        ses.close()
        message = {"message": "success"}
    elif event_type == "find_name":  # 查看这个老师是否设定了名字，如果设定了就返回名字，否则返回0
        sql = "select t_Name from teacheradmin  where t_AccountName='{0}'".format(objname)
        print(sql)
        proxy = ses.execute(sql)
        result = proxy.fetchone()
        if result is None:
            ses.close()
            message = {"message": 0}
        else:
            ses.close()
            message = {"message": result[0]}
    elif event_type == "add_remark_name":  # 如果是添加后台发言的化名化名
        ses.close()
    else:
        ses.close()
    try:
        ses.close()
    except Exception as e:
        pass
    return {"message": "I don't know"}  # 应该有多种操作情况的，这里留着以后添加


# 聊天室对话的方法，负责对话系统。每次客户发送消息要做两件事：1.写入全局数组，2.写入数据库

def dialog(guest_id, user_id, user_level, user_name, teacher_id, dialog_message, dialog_type, page_url,
           ip):  # 0.用户匿名id 1.注册后登录的用户id 2.用户级别 3用户昵称/名字 4.老师id ，5，消息内容 6.消息类型（私聊还是公开），7.聊天室地址 8.ip
    # conn=get_conn()
    # cursor=conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dialog_type = "allow" if dialog_type == "teacher" else "ban"  # 如果是老师发言就直接允许了。
    # 0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
    temp = [guest_id, user_id, user_level, user_name, teacher_id, dialog_message, dialog_type, now_str, page_url, ip]
    if temp[6] == "allow":
        pass  # 此方法已废弃
    else:
        pass
    global DIALOG_LIST
    DIALOG_LIST.append(temp)
    print("全局对话容器：")
    print(DIALOG_LIST)
    # print("dialog mothod ",end='')
    # print(temp)
    # sql="insert into chartroom_dialog(guest_id,user_id,user_name,teacher_id,dialog_message,dialog_type,dialog_date,page_url,ip) values({0},{1},'{2}',{3},'{4}','{5}','{6}','{7}','{8}')".format(guest_id,user_id,user_name,teacher_id,dialog_message,dialog_type,now_str,page_url,ip)
    # print("dialog's sql is  "+sql)
    # cursor.execute(sql)
    # conn.commit()
    # cursor.close()
    # conn.close()
    return {"message": "success"}


# 一个检查全局私聊数组的方法，如果数组过大，就截断数组.
def check_Dialog_list():
    global DIALOG_LIST
    max_length, current_length = 200, len(DIALOG_LIST)
    if current_length > max_length:
        DIALOG_LIST.clear()
        get_room_question()
        print("已重设数组长度")
    else:
        pass
        # print("数组长度在许可范围内")


# 定时比较聊天对话，如果发送变更，就写入数据库。否则就什么都不做
class save_dialog_thread(threading.Thread):
    def __init__(self):
        global PREV_DIALOG_LIST
        self.prev_dialog = PREV_DIALOG_LIST
        self.thread_stop = False
        threading.Thread.__init__(self)

    def stop(self):
        self.thread_stop = True

    def run(self):
        while not self.thread_stop:
            pass


# 一个获取聊天室客户提问信息的方法，在启动程序的时候从历史记录中查找前20条信息。
def get_room_question():  # 启动和重置DIALOG_LIST的方法。
    global DIALOG_LIST
    ses = get_conn()
    if len(DIALOG_LIST) == 0:
        ## 0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
        sql = "select guest_id ,user_id,user_name,teacher_id ,dialog_message,dialog_type,dialog_date,page_url,ip from chartroom_dialog where TIMESTAMPDIFF(SECOND,dialog_date,now())<43200 and (dialog_type='allow' or dialog_type='ban' or dialog_type='teacher') order by dialog_date desc limit 0,20"  # 距今12小时内的前20条记录。
        print("get_room_question is " + sql)
        proxy = ses.execute(sql)
        result = [[x[0], x[1], x[2], x[3], x[4], x[5], x[6].strftime("%Y-%m-%d %H:%M:%S"), x[7], x[8]] for x in
                  proxy.fetchall()]
        result.reverse()
        DIALOG_LIST = result
    else:
        pass
    # print("get_room_question")
    # print(DIALOG_LIST)
    ses.close()


get_room_question()  # 是启动的时候要运行一次  。


# 返回聊天室提问/发言信息的方法
def get_question():
    global DIALOG_LIST
    # print("get_question:")
    # print(DIALOG_LIST)
    return DIALOG_LIST.copy()


# 定义一个混合聊天室信息和被允许的发言信息的方法：
def mix_message():
    # 挑选聊天室客户发言中，被允许的发言跟抓取来的发言混合。
    # 其中，客户发言的格式  # 0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
    # 抓取的消息的格式：{time:time,name:name,message:message}
    result1 = get_question()  # 获取或有的发言，包含allow和ban的
    result2 = []  # 存储被允许的发言
    room_list = Chat_Room.get_chat_room_message()  # 不copy的话会修改原始Char_Room.DICT_LIST数据。这里存储的是抓取到的聊天室信息的拷贝结果
    # 取出被允许的发言
    for x in result1:
        if x[6] == "allow":
            # 发言的格式  # 0.用户匿名id 1.注册后登录的用户id 2.用户级别 3.用户昵称/名字 4.老师id ，5，消息内容 6.消息类型（私聊还是公开），7.消息日期8.聊天室地址 9.ip
            result2.append(
                {"time": datetime.datetime.strptime(x[7], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S"), "name": str(x[3]),
                 "message": x[5], "datetime": datetime.datetime.strptime(x[7], "%Y-%m-%d %H:%M:%S"),
                 "user_level": x[2]})  # {time"发言时间,name:"发言人名字",message:"发言内容",datetime:"用于排序的时间"}
            """
            #发言的格式  # 0.用户匿名id 1.注册后登录的用户id 2.用户昵称/名字 3.老师id ，4，消息内容 5.消息类型（私聊还是公开），6.消息日期 7.聊天室地址 8.ip
            if x[2]!=0 and x[2]!=None and x[2]!='': #如果发言里面有用户名就显示用户名
                result2.append({"time":datetime.datetime.strptime(x[6],"%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S"),"name":str(x[2]),"message":x[4],"datetime":datetime.datetime.strptime(x[6],"%Y-%m-%d %H:%M:%S")})#{time"发言时间,name:"发言人名字",message:"发言内容",datetime:"用于排序的时间"}
            else:  #否则就显示游客xxx
                result2.append({"time":datetime.datetime.strptime(x[6],"%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S"),"name":"游客"+str(x[0]),"message":x[4],"datetime":datetime.datetime.strptime(x[6],"%Y-%m-%d %H:%M:%S")})#{time"发言时间,name:"发言人名字",message:"发言内容",datetime:"用于排序的时间"}
            """
        else:
            pass
            # 混合发言


            # print("x is ")
            # print(x)
    if len(room_list) > 0:  # 如果抓取到的有信息
        pass  # room_list不在有用
    else:
        room_list = result2
    # print("before")
    # print(room_list)
    room_list3 = []
    # 把用以比对的时间转换成str格式，防止json在序列化的时候出错。
    # {time"发言时间,name:"发言人名字",message:"发言内容",datetime:"用于排序的时间"}
    for x in room_list:
        temp = x
        try:
            xx = x["datetime"]
            if isinstance(x["datetime"], str):  # 如果这个用于比对的精确时间已经转化为字符串，那就直接插入，否则就要把datetime转为str再插入
                room_list3.append(temp)
            else:
                date_str = x["datetime"].strftime("%Y-%m-%d %H:%M:%S")
                temp.update({"datetime": date_str})
                room_list3.append(temp)
        except KeyError:
            print(x)
            pass

    # room_list=[x.update({"datetime":x["datetime"].strftime("%Y-%m-%d %H:%M:%S")}) for x in room_list]
    # 检测数组长度，保持数组长度。
    # room_list3=room_list3[len(room_list3)-40:len(room_list3)] if len(room_list3)>40 else room_list3#不截断数组。
    # 处于保险起见，再次检测数据类型,仅作调试用，用于比对
    # f=open("error_log_for_mix_message"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")   #日志
    for x in room_list3:
        try:
            temp = x["datetime"]
        except KeyError:
            # print("key error ! ",end=" ",file=f)
            # print(datetime.datetime.now(),file=f)
            # print("error item ",end=": ",file=f)
            # print(x)
            # print("-------------")
            pass
        if isinstance(temp, str):
            pass
        else:
            # print("type error ! ",end=" ",file=f)
            # print(datetime.datetime.now(),file=f)
            # print("error item ",end=": ",file=f)
            # print(x)
            # print("-------------")
            pass
    # f.close()
    # print("所有发言内容")
    # print(result1)
    # print("被允许的发言")
    # print(result2)
    # print("混合后的发言")
    # print(room_list3)
    # Dialog_Collector.insert_dialog_to_database(room_list3) #把聊天记录中的对话跟数据库中的Robot_Dialog_Collector的对话做对比，把新的对话插入数据库给机器人做备选对话库
    # 混合机器人发言
    global ROBOT_LIST
    temp_dialog_list = room_list3.copy()
    mix_dialog_list = [{"message": x["message"], "time": x["time"], "name": x["name"],
                        "datetime": datetime.datetime.strptime(x["datetime"], "%Y-%m-%d %H:%M:%S"),
                        "come_from": "dialog", "user_level": x["user_level"]} for x in temp_dialog_list]
    # 聊天室的datetime是str类型，机器人的发言的datetime是datetime类型。
    mix_dialog_list.extend(ROBOT_LIST.copy())
    # print(ROBOT_LIST.copy())
    if mix_dialog_list is None:
        return []
    else:
        mix_dialog_list.sort(key=lambda obj: obj["datetime"], reverse=False)
        last_dialog = [{"message": x["message"], "time": x["time"], "name": x["name"], "come_from": x["come_from"],
                        "user_level": x["user_level"]} for x in mix_dialog_list]
        # print("last_dialog")
        # print(last_dialog)
        return last_dialog


def listen_robot(info={}):
    # 接收机器人发送过来的消息，info是一条消息记录，【"name":name.time:time,message:message】
    # 加工成【"name":name.time:time,message:message，datetime:datetime】插入全局变量
    global ROBOT_LIST
    ROBOT_LIST.append(info)


# 一个修改留言状态的方法。
def change_question_status(guest_id, dialog_time, status=0):
    # print("change_question_status's ags is "+guest_id+" "+dialog_time+" "+status)
    if status == 0:
        return {"message": "没有参数"}
    elif status == "allow" or status == "ban":
        dialog_date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 由于不再写入数据库，这一步省掉
        # conn=get_conn()
        # sql="update chartroom_dialog set dialog_type='{2}',dialog_date='{3}' where guest_id={0} and dialog_date='{1}'".format(guest_id,dialog_time,status,dialog_date_str)
        # cursor=conn.cursor()
        # print("change_question_status : "+sql)
        # cursor.execute(sql)
        # conn.commit()
        # cursor.close()
        # conn.close()
        # 0。客户匿名id，1.注册用户id 2.用户昵称/名字 3.员工id ，4消息内容 5.消息类型。6.消息日期。7.聊天室地址 8.ip
        # 改变全局数组中对应记录的状态
        # flag=False
        # 新的列顺序 0。客户匿名id，1.注册用户id 2.用户级别 3用户昵称/名字 4.员工id ，5消息内容 6.消息类型。7.消息日期。8.聊天室地址 9.ip
        for x in DIALOG_LIST:
            # print(guest_id+" : "+str(x[0])+" type:"+str(type(x[0]))+"      "+dialog_time+" : "+str(x[5])+" type:"+str(type(x[5])))
            if str(x[0]) == str(guest_id) and str(x[7]) == str(dialog_time):  # 如果全局对话容器中这条消息的匿名id和时间都完全匹配
                # print("find x")
                print(x)
                temp = [x[0], x[1], x[2], x[3], x[4], x[5], status, x[7], x[8], x[9]]
                print("change x")
                print(temp)
                DIALOG_LIST.remove(x)
                DIALOG_LIST.append(temp)
                flag = True
                break
            else:
                pass
        # print("内存数组比对结果："+str(flag))
        return {"message": "success"}
    else:
        return {"message": "无法理解的操作"}


# 一个用户登录聊天室的login方法
def chartroom_user_login(user_name, user_password, ip):  # 0.用户名 1.用户密码 3。ip
    if user_name is None:
        return {"message": "错误"}
    else:
        pass

    ses = get_conn()
    username = user_name.split(" ")[0] if user_name.find(" ") else user_name  # 检查用户名是否有空格，防止and 注入攻击
    message = ''
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 从数据库查询的用户信息的列顺序 0.用户id 1，用户密码，2.用户真实名/昵称 3.用户手机4.用户级别
    sql1 = "select u_Id,u_AccountPassword,u_RealName,u_phone,u_Level from userinfo where u_AccountName='{0}' and u_CanUse=1".format(
        username)
    # time.sleep(1)
    print(sql1)
    proxy = ses.execute(sql1)
    print(sql1)
    t = proxy.fetchone()

    if t is None:
        message = {"message": "用户不存在或未被启用"}
    else:
        result1 = list(t)
        user_id = int(result1[0])
        password = str(result1[1])
        real_name = '' if result1[2] is None else result1[2]
        phone = str(result1[3])
        user_level = '' if str(result1[4]).lower() == "null" or result1[4] is None  else str(result1[4])  # 用户级别
        if user_password != str(password):
            message = {"message": "密码错误"}
        else:
            # 0.匿名id 1.用户id 2.员工密码，3消息内容，4.消息类型 5.消息日期 6。页面地址，7 ip  #插入客户登录聊天室信息
            sql2 = "insert into chartroom_dialog(guest_id,user_id,teacher_id,dialog_message,dialog_type,dialog_date,page_url,ip) values({0},{1},{2},'{3}','{4}','{5}','{6}','{7}')".format(
                0, user_id, 0, "", "login", now_str, "营销直播室", ip)
            print(sql2)
            ses.execute(sql2)
            ses.commit()
            sql = "select day_count from chartroom_user_day_count where u_id={0}".format(user_id)
            proxy = ses.execute(sql)
            result = proxy.fetchone()
            pro_time = -1 if result is None else result[0]
            message = {"message": "success", "user_id": str(user_id), "user_name": username, "real_name": real_name,
                       "level": user_level, "u_phone": phone, "pro_time": pro_time}  # 消息类型，用户id，用户名，用户级别 。已注册用户的登录天数
    ses.close()
    return message


# 聊天室用户修改个人资料
def edit_user_info(user_id, real_name, nick_name, new_password):
    if user_id == "":
        return {"message": "请先登录"}
    else:
        if new_password == '':
            sql = "update userinfo set u_RealName='{1}' where u_Id={0}".format(int(user_id), nick_name)
        else:
            sql = "update userinfo set u_RealName='{1}',u_AccountPassword='{2}' where u_Id={0}".format(int(user_id),
                                                                                                         nick_name,
                                                                                                         new_password)
        ses = get_conn()
        printSqlStr(579, sql)
        ses.execute(sql)
        try:
            ses.commit()
            ses.close()
            return {"message": "success"}
        except:
            ses.close()
            return {"message": "修改失败"}


# 聊天室用户修改绑定的后继号码
def change_user_phone(user_id, phone):
    if user_id == "":
        return {"message": "请先登录"}
    else:
        sql = "update userinfo set u_phone='{1}',u_validate=1 where u_Id={0}".format(int(user_id), phone)
        ses = get_conn()
        print("change_user_phone " + sql)
        try:
            ses.execute(sql)
            ses.commit()
            ses.close()
            return {"message": "success"}
        except:
            ses.close()
            return {"message": "修改失败"}


# 聊天室用户管理。、 type是操作类型，args是参数字典
def edit_chatroom_user(type='view_all', args={}):
    ses = get_conn()
    message = ''
    if type == "view_all":
        sql = "select u_Id,u_AccountName,u_AccountPassword,u_RealName,u_phone,u_Level,u_Sex from userinfo"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            message = {"message": "没有用户"}
        else:
            result = [list(x) for x in raw]
            # .列顺序 0.id 1.帐户名 2密码，3.真实名字 4.手机 5.级别 6，性别 7 创建时间
            message = {"message": "success", "data": result}
    elif type == "view_level":  # 查看客户分级信息
        sql = "select u_Id,u_level_number,u_Name from userlevel where u_level_number!=0"  # 0 级别id  1 级别顺序 2 级别名字
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            message = {"message": "没有客户级别信息"}
        else:
            result = [list(x) for x in raw]
            result.sort(key=lambda obj: obj[1], reverse=False)
            message = {"message": "success", "data": result}

    elif type == "add":
        phone = args.get("phone")
        if phone is None:
            message = {"message": "没有手机号码"}
        else:
            sql = "select count(1) from userinfo where u_phone='{0}'".format(phone)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()[0]
            if raw == 0:
                account_name = '' if args.get("account_name") is None else args.get("account_name")
                account_password = '' if args.get("account_password") is None else args.get("account_password")
                real_name = '' if args.get("real_name") is None else args.get("real_name")
                phone = '' if args.get("phone") is None else args.get("phone")
                level = 0 if args.get("level") is None else args.get("level")
                sex = '' if args.get("sex") is None else args.get("sex")
                sql = "insert into userinfo(u_AccountName,u_AccountPassword,u_RealName,u_phone,u_Level,u_Sex,u_CreateTime) values('{0}','{1}','{2}','{3}',{4},'{5}',{6})".format(
                    account_name, account_password, real_name, phone, level, sex, 'now()')
                print(sql)
                ses.execute(sql)
                ses.commit()
                message = {"message": "success"}
            else:
                message = {"message": "已存在相同手机用户"}
    elif type == "check_username":
        account = '' if args.get("account_name") is None else args.get("account_name")
        if account is None:
            message = {"message": "没有手机号码"}
        else:
            sql = "select count(1) from userinfo where u_AccountName='{0}'".format(account)
            print(sql)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()[0]
            if raw == 0:
                message = {"message": "success"}
            else:
                message = {"message": "find!"}
    elif type == "delete":
        u_id = args.get("u_id")
        if u_id is None:
            message = {"message": "缺少用户id"}
        else:
            sql = "delete from  userinfo where u_id={0}".format(u_id)
            print(sql)
            ses.execute(sql)
            ses.commit()
            message = {"message": "success"}
    elif type == "edit":
        u_id = args.get("u_id")
        if u_id is None:
            message = {"message": "缺少用户id"}
        else:
            sql = "select count(1) from userinfo where u_id={0}".format(u_id)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()[0]
            if raw == 0:
                message = {"message": "用户id不存在"}
            else:
                account_name = '' if args.get("account_name") is None else args.get("account_name")
                # account_password='' if args.get("account_password") is None else args.get("account_password")
                # real_name='' if args.get("real_name") is None else args.get("real_name")
                phone = '' if args.get("phone") is None else args.get("phone")
                level = 0 if args.get("level") is None else args.get("level")
                # sex='' if args.get("sex") is None else args.get("sex")
                # sql="update userinfo set u_AccountName='{0}',u_AccountPassword='{1}',u_RealName='{2}',u_BusinessAccount='{3}',u_Level={4},u_Sex='{5}',u_LastTime=now() where u_Id={6}".format(account_name,account_password,real_name,phone,level,sex,u_id)
                sql = "update userinfo set u_AccountName='{0}',u_phone='{1}',u_Level={2},u_LastTime=now() where u_Id={3}".format(
                    account_name, phone, level, u_id)
                ses.execute(sql)
                ses.commit()
                message = {"message": "success"}
    elif type == "change_phone":
        u_id = args.get("u_id")
        if u_id is None:
            message = {"message": "缺少用户id"}
        else:
            sql = "select count(1) from userinfo where u_id={0}".format(u_id)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()[0]
            if raw == 0:
                message = {"message": "用户id不存在"}
            else:
                phone = '' if args.get("phone") is None else args.get("phone")
                sql = "update userinfo set u_phone='{0}',u_LastTime=now() where u_Id={1}".format(phone, u_id)
                print(sql)
                ses.execute(sql)
                ses.commit()
                message = {"message": "success"}
    elif type == "reset_password":
        u_id = args.get("u_id")
        if u_id is None:
            message = {"message": "缺少用户id"}
        else:
            sql = "select count(1) from userinfo where u_id={0}".format(u_id)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()[0]
            if raw == 0:
                message = {"message": "用户id不存在"}
            else:
                sql = "update userinfo set u_AccountPassword='888888' where u_Id={0}".format(u_id)
                ses.execute(sql)
                ses.commit()
                message = {"message": "success"}
    else:
        message = {"message": "无法理解的操作"}
    ses.close()
    return message


level_and_prefix_dict = {}


# 查询用户等级和级别名称，图标名字的对应关系。
def level_and_prefix():
    global level_and_prefix_dict
    if len(level_and_prefix_dict) == 0:
        ses = get_conn()
        sql = "select u_Id,u_Name,u_img_path from userlevel"  # 级别id  级别名称  级别图标前缀
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        data = {x[0]: {"id": x[0], "name": x[1], "path": x[2]} for x in raw}
        level_and_prefix_dict = data
        return data
    else:
        return level_and_prefix_dict



# print(level_and_prefix())
# 编辑维护聊天室的老师风采的资料
def teachers(the_type, t_name='', t_nickname='', t_description='', t_password="123456", t_title="宏赟分析师", t_id=0,
             t_can_use=1):
    ses = get_conn()
    message = {"message": "success"}
    if the_type == "add":
        sql = " insert into teachinfo(t_name,t_nickname,t_title,t_description,t_password,t_CreateTime,t_can_use,t_Level,t_in_class) values('{0}','{1}','{2}','{3}','{4}',now(),1,1,1)".format(
            t_name, t_nickname, t_title, t_description, t_password, db_module.current_datetime())
        print(sql)
        ses.execute(sql)
        ses.commit()
    elif the_type == "edit":
        if t_id == 0:
            message = {"message": "老师id不存在"}
        else:
            sql = " update teachinfo set t_name='{0}',t_nickname='{1}',t_description='{2}',t_can_use={3},t_title='{4}',t_password='{5}' where t_id={6}".format(
                t_name, t_nickname, t_description, t_can_use, t_title, t_password, t_id)
            print(sql)
            ses.execute(sql)
            ses.commit()
    elif the_type == "delete":
        if t_id == 0:
            message = {"message": "老师id不存在"}
        else:
            sql = "delete from teachinfo where t_id={0}".format(t_id)
            print(sql)
            ses.execute(sql)
            ses.commit()
    elif the_type == "all":  # 查看所有老师的信息，用于营销直播室的老师风采
        sql = "select t_id,t_account,t_name,t_nickname,t_title,t_description from teachinfo where t_can_use=1 order by t_CreateTime desc"  # id 名字 昵称 介绍
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        raw = [{"t_id": x[0], "t_account": x[1], "t_name": x[2], "t_nickname": x[3], "t_title": x[4],
                "t_description": x[5]} for x in raw]
        message["data"] = raw
    elif the_type == "reset_password":
        sql = "update teachinfo set t_password='{0}' where t_id={1}".format(t_password, t_id)
        ses.execute(sql)
        ses.commit()
    else:
        message = {"message": "未知的teachers操作"}
    ses.close()
    return message


# 保存/读取课程表
def edit_class(the_type, class_data):
    message = {"message": "success"}
    ses = get_conn()
    if the_type == "save":
        ses.execute("truncate table class_table")
        ses.commit()
        print(class_data)
        for x in class_data:
            sql = "insert into class_table(begin_time,end_time,Monday,Tuesday,Wednesday,Thursday,Friday) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(
                x[0], x[1], x[2], x[3], x[4], x[5], x[6])
            print(sql)
            ses.execute(sql)
        ses.commit()
    elif the_type == "view":
        sql = "select begin_time,end_time,Monday,Tuesday,Wednesday,Thursday,Friday from class_table"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        raw = [list(x) for x in raw]
        message["class_data"] = json.dumps(raw)
    else:
        pass
    ses.close()
    return message


# 对每日策略的操作
def tips(the_type, args_dict):
    ses = get_conn()
    message = {"message": "success"}
    if the_type == "add":  # 如果是增加策略
        e_title = args_dict.get("e_title")
        e_content = args_dict.get("e_content")
        e_author = args_dict.get("e_author")
        if e_author is None or e_content is None or e_author is None or e_author == "" or e_content == "" or e_author == "":
            message = {"message": "信息不完整"}
        else:
            sql = "insert into Everyday_Tip(e_title,e_content,e_author,e_datetime) values('{0}','{1}','{2}',now())".format(
                e_title, e_content, e_author)
            print(sql)
            ses.execute(sql)
            ses.commit()
    elif the_type == "view_new":  # 查看最新的策略
        sql = "select e_title,e_content,e_author,e_datetime from Everyday_Tip order by e_datetime desc limit 0,5"
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        if raw is None:
            message["data"] = {}
        else:
            message["data"] = {"e_title": raw[0], "e_content": raw[1], "e_author": raw[2],
                               "e_datetime": raw[3].strftime("%Y-%m-%d %H:%M:%S")}
    elif the_type == "top5":  # 查看最新的策略
        sql = "select e_title,e_content,e_author,e_datetime from Everyday_Tip order by e_datetime desc limit 0,5"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            message["data"] = []
        else:
            alist = []
            for x in raw:
                alist.append({"e_title": x[0], "e_content": x[1], "e_author": x[2],
                              "e_datetime": x[3].strftime("%Y-%m-%d %H:%M:%S")})
            message["data"] = alist
    elif the_type == "edit":  # 编辑策略
        e_id = args_dict.get("e_id")
        e_title = args_dict.get("e_title")
        e_content = args_dict.get("e_content")
        e_author = args_dict.get("e_author")
        if e_id is None or e_id == 0 or e_id == '':
            message = {"message": "未知的id"}
        else:
            sql = "update Everyday_Tip set e_title='{0}',e_content='{1}',e_author='{2}' where e_id={3}".format(e_title,
                                                                                                               e_content,
                                                                                                               e_author,
                                                                                                               e_id)
            ses.execute(sql)
            ses.commit()
    elif the_type == "view_all":  # 查询所有的策略，一般在启动页面时加载数据使用
        sql = "select e_id,e_title,e_content,e_author,e_datetime from Everyday_Tip order by e_datetime desc limit 0,50"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            message["data"] = {}
        else:
            alist = []
            for x in raw:
                alist.append({"e_id": x[0], "e_title": x[1], "e_content": x[2], "e_author": x[3],
                              "e_datetime": x[4].strftime("%Y-%m-%d %H:%M:%S")})
            message["data"] = alist
    elif the_type == "delete":  # 删除策略
        e_id = args_dict.get("e_id")
        if e_id is None or e_id == 0 or e_id == '':
            message = {"message": "未知的id"}
        else:
            sql = "delete from Everyday_Tip where e_id={0}".format(e_id)
            ses.execute(sql)
            ses.commit()
    else:
        message = {"message": "未知的操作"}
    ses.close()
    return message
