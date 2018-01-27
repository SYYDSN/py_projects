# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
import pymssql,threading,time,datetime,sys,calendar,json,random
import random,math,hashlib
import chat_room_manage,my_sql
ROBOT_ALIAS=[] #全局变量，机器人的化名库
ROBOT_STEP_TIMES={}  #机器人发言间隔的倍率库。是key=robot_id,value=倍率 的一个字典
ALL_MODEL_ID=[]    #全局变量，用来查询模式是处于工作状态还是停止状态。
#定义一个在启动机器人的时候，获取别名库的方法
def get_public_alias():
    flag=True
    sql=sql="select robot_alias from Robot_Alias"
    while flag:
        try:
            conn=my_sql.get_conn()
            cursor=conn.cursor()
            cursor.execute(sql)
            raw=cursor.fetchall()
            if len(raw)==0:
                pass
            else:
                result=[x[0] for x in raw]
                global ROBOT_ALIAS
                ROBOT_ALIAS=result
            cursor.close()
            conn.close()
            flag=False
        except:
            time.sleep(3)
#######################聊天室机器人的类################
class Robot(threading.Thread):
    #创建机器人类的几个参数，
    # 机器人名字，字符串 不可重复
    #发言循环方式：字符串 定时循环发送，包括1，按固定/随机时间间隔 2,按每月几个固定时间点/段  3.按每周周几固定时间点/段
    #begin_time发言开始时间 dict类型，这是一个指定相对时间的发言，比如每周的周二上午9点或者每月的第二个星期五等等，
    #{day:0,weekday:1,week:4,month:4,time:09:30:00} {几号/周几，周几还是几号，第几个星期，第几个月，何时}，4月第四个星期的星期2的上午9点半  weekday的值只有0和1，0代表day指的是day in month，1代表day指的是day in week
    #{day:2,weekday:0,week:0,month:4,time:09:30:00}     4月2号上午9点半
    #{day:2,weekday:1,week:1,month:4,time:09:30:00}   4月第一个星期二上午9点半
    #{day:2,weekday:1,week:4,month:0,time:09:30:00}    每个月的第四个星期2的上午9点半
    #{day:0,weekday:1,week:4,month:4,time:09:30:00}   四月的第四个星期的每天早上0点半
    #{day:0,weekday:0,week:0,month:4,time:09:30:00}   四月的每天早上9点半
    #{day:2,weekday:1,week:0,month:0,time:09:30:00}   每周2早上9点半
    #{day:0,weekday:0,week:0,month:0,time:09:30:00}   每天早上9点半
    #{day:2,weekday:1,week:3,month:4,time:09:30:00}  四月的第三个星期2的上午9点半
    #{day:2,weekday:0,week:3,month:4,time:09:30:00}  四月2日的上午9点半，这时的week参数比忽略了。
    # end_time发言结束时间，相对时间，以小时为单位，默认是2小时
    # step 发言间隔，秒为单位，如果是一个数字，那就是固定间隔时间，如果是2个或者2个以上以英文逗号隔开的数字就表示是一个介于这两个数字之间的哦随机时间间隔。如果开始时间是数组，会在运行的时候忽略这个参数。
    # 每次机器人以begin_time开始发言，以step为间隔，以end_time为结束时间，如果到时候对话数组还有未发的对话，那就终止发送，如果对话发送完毕后还未到结束时间，那也终止发送。
    #
    #归属此机器人的发言 有序集合 会按照发言循环方式逐条发言
    def __init__(self,robot_id,name,begin_time,end_time=2,step=5,str_list=[]):
        threading.Thread.__init__(self)
        self.id=robot_id        #机器人id
        self.name=name
        self.begin=begin_time
        self.alias_list=[]
        get_public_alias()  #查询数据库更新化名库
        global ROBOT_ALIAS
        """
        #随机选择不大于10个化名
        if len(ROBOT_ALIAS)==0:
            self.alias_list=[" 张三","李四","王五"]
        else:
            raw_alias_list=[ROBOT_ALIAS[random.randint(0,(len(ROBOT_ALIAS)-1 if 0<len(ROBOT_ALIAS)<10 else 9))] for x in range(len(ROBOT_ALIAS))]
            self.alias_list=list(set(raw_alias_list))  #使用set去重复
        """
        raw_alias_list=ROBOT_ALIAS
        self.alias_list=list(set(raw_alias_list))
        try:
            self.end_time=int(end_time)*60*60
        except ValueError:
            print("非法的结束时间:"+str(end_time))
            sys.exit(1)
        self.step=step
        self.str_list=str_list   #发言库，未发消息的容器
        self.str_list2=[]      #发言库，已发消息的容器
        self.flag_month=False
        self.flag_weekday=False
        self.thread_stop=False

    def stop(self):
        self.thread_stop=True
        print("robot {0} is stop".format(self.name))
    def run(self):
        while not self.thread_stop:

            now=datetime.datetime.now()
            delta=(datetime.datetime.strptime(str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "+self.begin['time'],"%Y-%m-%d %H:%M:%S")-now).total_seconds()  #如果这个值小于等于零，就证明已经到了或者晚于开始时间了。
            if int(self.begin['weekday'])==1:  #如果传过来的开始时间注明了day是day in week
                #计算当天的month，week，和day
                current_year=now.year
                current_month=now.month
                current_day=now.day
                current_weekday=now.isoweekday()   #星期几？从1到7，7为最后一天。
                c=calendar.Calendar()

                #比较月份
                if int(self.begin["month"])==0 or  int(self.begin["month"])>12:#不用比较月份
                    self.flag_month=True
                elif int(self.begin["month"])>0 and int(self.begin["month"])<13 and int(self.begin["month"])==current_month:
                    self.flag_month=True
                else:
                    self.flag_month=False
                #比较星期几
                if self.flag_month:
                    if self.begin['day']==0:
                        self.flag_weekday=True
                    elif self.begin['day']>0 and self.begin['day']<8:
                        #当前月的所有星期组成的数组。可以根据日期在数组的位置判断是第几周的周几
                        day_week_list=c.monthdayscalendar(current_year,current_month)
                        flag_for=True
                        count_week=0   #周计数器，用来确认是第几个星期几
                        for i in range(len(day_week_list)):
                            if flag_for:
                                temp_week_range=day_week_list[i]
                                 #如果这一周有指定的星期
                                if temp_week_range[int(self.begin["day"]-1)]!=0:
                                    count_week+=1
                                else:
                                    pass
                                #如果这一周有指定的星期并且周序数也和指定的数值相同。
                                if temp_week_range[int(self.begin["day"]-1)]!=0 and count_week==int(self.begin['week']):
                                    for j in temp_week_range:
                                        if j==current_day and (temp_week_range.index(j)+1)==current_weekday:
                                            self.flag_weekday=True
                                            flag_for=False
                                            break
                                        else:
                                            self.flag_weekday=False
                                else:
                                    pass
                            else:
                                break
                    else:
                        self.flag_weekday=False
                else:
                    self.flag_weekday=False
            elif int(self.begin['weekday'])==0:  #如果传过来的开始时间注明了day是day in month
                current_month=now.month
                current_day=now.day
                #比较月份
                if int(self.begin["month"])==0 or  int(self.begin["month"])>12:#不用比较月份
                    self.flag_month=True
                elif int(self.begin["month"])>0 and int(self.begin["month"])<13 and int(self.begin["month"])==current_month:
                    self.flag_month=True
                else:
                    self.flag_month=False
                #比较几号
                if self.flag_month:
                    if self.begin['day']==0:
                        self.flag_weekday=True
                    elif self.begin['day']>0 and self.begin['day']<32 and current_day==int(self.begin["day"]):
                        self.flag_weekday=True
                    else:
                        self.flag_weekday=False
                else:
                    self.flag_weekday=False
            else:
                self.flag_weekday,self.flag_month=False,False
            #如果比较都通过了，那就比较时间
            if self.flag_month and self.flag_weekday:
                begin_time=datetime.datetime.strptime(str(now.year)+"-"+str(now.month)+"-"+str(now.day)+" "+str(self.begin['time']),"%Y-%m-%d %H:%M:%S")
                current_time=now
                #如果当前时间等于晚于开始时间但是早于结束时间，那就开始发言
                if (begin_time-current_time).total_seconds()<=0 and ((begin_time-current_time).total_seconds()+float(self.end_time)*60*60)>=0:
                    self.send_message()  #发言
                else:
                    print("不在发言时间内")
            else:
                print(now,end=" ")
                print("发言日期不匹配")
            #最后一个延时，如果延时放在最后，会导致启动机器的时候所有机器人一起说第一句话,所以，在模拟个人行为的时候，这个延时应该放在头部。本例是模拟一类人发言，所以放在头部
            #判断分隔符
            flag_split=","
            if str(self.step).find(flag_split)!=-1:
                pass
            elif str(self.step).find("，")!=-1:
                flag_split="，"
            else:
                flag_split=""
            if flag_split=="":#如果时间间隔字符串找不到分隔符，那就假设它是一个数字
                try:
                    time.sleep(int(self.step))
                except ValueError:
                    print("时间间隔设置错误，错误的值是："+str(self.step))
            else:
                try:
                    step_list=str(self.step).split(flag_split)[0:2]  #只取数组前两位
                    temp_step=random.randint(int(step_list[0]),int(step_list[1]))
                    global ROBOT_STEP_TIMES
                    time.sleep(math.ceil((1.0 if ROBOT_STEP_TIMES.get(self.id) is None else ROBOT_STEP_TIMES.get(self.id))*temp_step))                        #发言间隔的延时
                except ValueError:
                    print("时间间隔设置错误，错误的值是："+str(self.step))


    def send_message(self):#机器人发送消息的方法
        if len(self.str_list)==0:
            self.reload_messages(True)
        else:
            the_str=self.str_list.pop(random.randint(0,len(self.str_list)-1)) #随机弹出一句
            #print(self.name+"说:",end="")                   #测试发言
            #print(the_str)
            self.str_list2.append(the_str)
            now=datetime.datetime.now()
            #发送数据到聊天室
            #print({"name":self.alias_list[random.randint(0,len(self.alias_list)-1)],"time":now.strftime("%H:%M:%S"),"message":the_str,"datetime":now,"come_from":"robot"})
            chat_room_manage.listen_robot({"name":self.alias_list[random.randint(0, len(self.alias_list) - 1 if (len(self.alias_list) - 1) > 1 else 1)], "time":now.strftime("%H:%M:%S"), "message":the_str, "datetime":now, "come_from": "robot", "user_level":3})


    def reload_messages(self,flag=True):#一个在发言完毕，重新加载发言库的方法，此方法也可被调用更新发言库。
        #参数flag表示是否清空已发留言库。
        conn=None
        try:
            conn=my_sql.get_conn()
            #print("Robot数据库连接成功")
        except:
            print("Robot数据库连接失败")
        cursor=conn.cursor()
        sql="select s_string from Robot_Dialog where  robot_id={0}".format(self.id)
        #print(sql)
        cursor.execute(sql)
        raw=cursor.fetchall()
        if len(raw)==0:
            pass
        else:
            result=[x[0] for x in raw]
            if not flag:
                for x in result:
                    if x in self.str_list2:
                        result.remove(x) #在查到的对话中清除掉已发过的对话
                    else:
                        pass
            else:
                self.str_list2.clear()  #清除发言的历史
            self.str_list=result
        cursor.close()
        conn.close()



#测试，创建一个机器人(self,robot_id,name,begin_time,end_time=2,step=5,str_list=[]):
# robot1=Robot(1,"jack",{"day":1,"weekday":1,"week":2,"month":0,"time":"01:00:00"},step="1,5")
# robot1.start()
# robot2=Robot(1,"tom",{"day":11,"weekday":0,"week":0,"month":1,"time":"01:00:00"},end_time=1.5,step="1,5")
# robot2.start()
# time.sleep(6)
# robot1.stop()
# time.sleep(6)
# robot2.stop()
# for x in range(100):
#     Robot(1,"游客"+str(random.randint(10,200)),{"day":11,"weekday":0,"week":0,"month":1,"time":"09:00:00"},end_time=1.5,step="1,5").start()
class Robot_Manage():
    def __init__(self):
        self.robots={}  #以robot_id为key，Robot对象为值的字典
        self.conn=None
        try:
            self.conn=my_sql.get_conn()
            print("Robot数据库连接成功")
        except:
            print("Robot数据库连接失败")
    def init_robots(self):
        cursor=self.conn.cursor()
        #查询数据库所有处于运行状态的机器人
        sql="SELECT robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time," \
            "end_time,step,robot_owner,robot_status FROM Robot_config where robot_status='run'"
        cursor.execute(sql)
        raw=cursor.fetchall()
        if len(raw)==0:
            print("没有配置为运行的机器人")
            cursor.close()
            return {"message":"没有配置为运行的机器人"}
        else:
            result=[list(x) for x in raw]
            cursor.close()
            for x in result:
                self.run_robot(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8])#s参数(self,robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step)
            return {"message":"success"}
    def edit_robot(self,event_type,args_dict):
        #event_type代表事件类型，add，edit，delete等
        #arg_list是参数字典,包含的参数如下：
        #robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step,robot_owner,robot_status
        cursor=self.conn.cursor()
        args_dict=args_dict if args_dict is not None else {}
        print(args_dict)
        robot_id=int(args_dict.get("robot_id")[0].decode()) if args_dict.get("robot_id") is not None else 0
        robot_name=args_dict.get("robot_name")[0].decode() if args_dict.get("robot_name") is not None else ''
        begin_day=int(args_dict.get("begin_day")[0].decode()) if args_dict.get("begin_day") is not None else 0
        begin_weekday=int(args_dict.get("begin_weekday")[0].decode()) if args_dict.get("begin_weekday") is not None else 0
        begin_week=int(args_dict.get("begin_week")[0].decode()) if args_dict.get("begin_week") is not None else 0
        begin_month=int(args_dict.get("begin_month")[0].decode()) if args_dict.get("begin_month") is not None else 0
        begin_time=args_dict.get("begin_time")[0].decode() if args_dict.get("begin_time") is not None else "00:00:00"
        end_time=float(args_dict.get("end_time")[0].decode()) if args_dict.get("end_time") is not None else 2.0
        step=args_dict.get("step")[0].decode() if args_dict.get("step") is not None else "60"
        robot_owner=args_dict.get("robot_owner")[0].decode() if args_dict.get("robot_owner") is not None else 1
        robot_status=args_dict.get("robot_status")[0].decode() if args_dict.get("robot_status") is not None else "stop"

        sql="select count(*) from Robot_config where robot_name='{0}'".format(robot_name)
        cursor.execute(sql)

        if event_type=="add":
            sql="select count(*) from Robot_config where robot_name='{0}'".format(robot_name)
            cursor.execute(sql)
            if cursor.fetchone()[0]>0:
                return {"message":"已存在同名机器人"}
            else:
                sql="insert into Robot_config(robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time," \
            "end_time,step,robot_owner,robot_status) values('{1}',{2},{3},{4},{5},'{6}'," \
            "{7},'{8}','{9}','{10}')".format(robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step,robot_owner,robot_status)
                print("insert into Robot_config :"+sql)
                cursor.execute(sql)
                self.conn.commit()
                sql="select robot_id from Robot_config where robot_name='{0}'".format(robot_name)
                cursor.execute(sql)
                robot_id=cursor.fetchone()[0]
                return {"message":"{0} 机器人添加成功".format(robot_name),"robot_id":robot_id}
        elif event_type=="edit":
            sql="select count(*) from Robot_config where robot_id={0}".format(robot_id)
            cursor.execute(sql)
            if cursor.fetchone()[0]==0:
                return {"message":"{0} 机器人配置文件不存在".format(robot_name)}
            else:
                sql="update Robot_config set robot_name='{1}',begin_day={2},begin_weekday={3},begin_week={4},begin_month={5},begin_time='{6}',end_time={7},step='{8}',robot_owner='{9}',robot_status='{10}' where robot_id={0}".format(robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step,robot_owner,robot_status)
                cursor.execute(sql)
                self.conn.commit()
                if robot_id in self.robots.keys():#如果这个机器人正在运行中。
                    self.stop_robot(robot_id,robot_name)
                    self.run_robot(robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step)
                else:
                    pass
                return {"message":"{0} 机器人修改成功".format(robot_name)}
        elif event_type=="delete":
            if cursor.fetchone()[0]==0:
                return {"message":"{0} 机器人配置文件不存在".format(robot_name)}
            else:
                sql="delete from Robot_config where robot_id={0}".format(robot_id)
                cursor.execute(sql)
                self.conn.commit()
                return {"message":"{0} 机器人删除成功".format(robot_name)}
        elif event_type=="run":
            return self.run_robot(robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step)
        elif event_type=="stop":
            return self.stop_robot(robot_id,robot_name)
        elif event_type=="view_robots":#查询所有的机器人
            sql="SELECT robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step,robot_owner,robot_status FROM Robot_config"
            cursor.execute(sql)
            raw=cursor.fetchall()
            if len(raw)==0:
                result=[["robot_id","robot_name","begin_day","begin_weekday","begin_week","begin_month","begin_time","end_time","step","robot_owner","robot_status"]]    #插入标题栏
                return {"message":"success","data":result}#返回所有的机器人配置清单
            else:
                result=[list(x) for x in raw]
                result.insert(0,["robot_id","robot_name","begin_day","begin_weekday","begin_week","begin_month","begin_time","end_time","step","robot_owner","robot_status"])    #插入标题栏
                return {"message":"success","data":result}#返回所有的机器人配置清单
        else:
            pass
        cursor.close()
    #启动机器人的方法
    def run_robot(self,robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step):#启动机器人的方法
        if robot_id in self.robots.keys():
            return {"message":"{0} 机器人已在运行中".format(robot_name)}
        else:
            robot=Robot(robot_id,robot_name,{"day":begin_day,"weekday":begin_weekday,"week":begin_week,"month":begin_month,"time":begin_time},end_time=end_time,step=step)
            self.robots[robot_id]=robot
            robot.start()
            sql="update Robot_config set robot_status='run' where robot_id={0}".format(robot_id)
            cursor=self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print(sql)
            print("{0} 机器人启动成功".format(robot_name))
            return {"message":"{0} 机器人启动成功".format(robot_name)}
    #停止机器人的方法
    def stop_robot(self,robot_id,robot_name):
        if robot_id not in self.robots.keys():
            pass
            #return {"message":"{0} 机器人没有运行".format(robot_name)} 这一句不可靠
            sql="update Robot_config set robot_status='stop' where robot_id={0}".format(robot_id)
            cursor=self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print(sql)
            print("{0} 机器人停止成功".format(robot_name))
            return {"message":"{0} 机器人停止成功".format(robot_name)}
        else:
            robot=self.robots.get(robot_id)
            robot.stop()
            self.robots.pop(robot_id)
            sql="update Robot_config set robot_status='stop' where robot_id={0}".format(robot_id)
            cursor=self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
            print(sql)
            print("{0} 机器人停止成功".format(robot_name))
            return {"message":"{0} 机器人停止成功".format(robot_name)}


RM=Robot_Manage()
RM.init_robots()
#重置机器人管理器容器，返回机器人的dict
def init_robots():
    return RM.init_robots()
#机器人管理器的各种操作
def robot_handler(event_type,args_dict):
    return RM.edit_robot(event_type,args_dict)

try:
    CONN=my_sql.get_conn()
except:
    print("数据库连接失败")
#获取发言库的发言
def backup_dialog(job_id,page_number):
    #job_id为用户工号，page_number为要查询的页码，如果为0的话，说明是第一次载入页面，就要计算总计多少页了。
    if job_id=="":
        return {"message":"工号 {0}  不存在".format(job_id)}
    else:
        pass
    cursor=CONN.cursor()
    page_count=0
    every_page=10  #每页多少条
    if int(page_number)==0:
        sql="select count(*) from Robot_Dialog where owner_id='{0}'".format(job_id)
        print(sql)
        cursor.execute(sql)
        page_count=cursor.fetchone()[0]
    else:
        pass
    #先要知道共计有多少发言
    #分页查询发言库
    page_number=1 if int(page_number)==0 else int(page_number)
    sql="select top {0} s_id,s_string,robot_id,owner_id from Robot_Dialog where s_id not in (select top {1} s_id from Robot_Dialog)".format(every_page,(int(page_number)-1)*every_page)  #0.发言id 1，发言 2.机器人id 3.工号
    print("backup_dialog page_query public data sql str :"+sql)
    cursor.execute(sql)
    raw=cursor.fetchall()
    if len(raw)==0:
        result=[]
    else:
        result=[list(x) for x in raw]
    cursor.close()
    return {"message":"success","page_count":math.ceil(page_count/every_page),"data":result}   #返回的三个结果 1.标志位，2，共多少分页，不是第一次查询的话，就返回0，data 是返回的查询结果集。列顺序：0.发言id，1机器人id，2.工号 3.发言内容
#获取机器人的发言列表 参数为机器人的id
def get_robot_dialog_list(robot_id):
    global CONN
    cursor=CONN.cursor()
    sql="select s_id,s_string from Robot_Dialog where robot_id={0}".format(robot_id)
    print("backup_dialog page_query private data sql str :"+sql)
    cursor.execute(sql)
    raw=cursor.fetchall()
    if len(raw)==0:
        result=[]
    else:
        result=[list(x) for x in raw]
    cursor.close()
    return {"message":"success","data":result}   #返回的2个结果 1.标志位，2，data 是返回的查询结果集。0.对话id 1.对话内容
#更新机器人的发言库
def update_robot_dialog(robot_id,owner_id,str_list,delete_list):
    #第一个参数是机器人的id，第二个参数是发言的数组
    global CONN
    cursor=CONN.cursor()
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if len(str_list)==0 and len(delete_list)==0:
        return {"message":"没有数据插入"}
    else:
        pass
    #先把delete_list列表中的str跟robot脱离关系。
    if len(delete_list)==0:
        pass
    else:
        for x in delete_list:
            sql="update Robot_Dialog set robot_id=0 where s_id={0}".format(x)
            cursor.execute(sql)
        CONN.commit()
        print("从{0}的配置列表中删除了{1}条语句".format(robot_id,len(delete_list)))
    #插入语句
    for x in str_list:
        sql="insert into Robot_Dialog(s_string,robot_id,owner_id,create_date) values('{0}',{1},'{2}','{3}')".format(x,robot_id,owner_id,now)
        print(sql)
        cursor.execute(sql)
    CONN.commit()
    cursor.close()
    return {"message":"插入成功"}
#对机器人化名库的操作
def robot_alias(event_type,alias_list=[],delete_list=[]):
    global CONN
    cursor=CONN.cursor()
    if event_type=="view":#查看全部化名
        sql="select s_id,robot_alias from Robot_Alias"
        cursor.execute(sql)
        raw=cursor.fetchall()
        if len(raw)==0:
            return {"message":"没有数据"}
        else:
            result=[list(x) for x in raw]
            return {"message":"success","data":result}
    elif event_type=="update": #增加，或者删除化名
        #先删除
        if len(delete_list)==0:
            pass
        else:
            for x in delete_list:
                sql="delete from Robot_Alias where s_id={0}".format(int(x))
                cursor.execute(sql)
            CONN.commit()
        #再添加
        if len(alias_list)==0 and len(delete_list)==0:
            return {"message":"没有数据需要更新"}
        elif len(alias_list)==0 and len(delete_list)>0:
            return {"message":"已删除{0}个化名".format(len(delete_list))}
        else:
            for x in alias_list:
                sql="insert into Robot_Alias(robot_alias) values('{0}')".format(x)
                cursor.execute(sql)
            CONN.commit()
            return {"message":"化名添加成功"}
    else:
        return {"message":"未知操作"}
    cursor.close()

#定义检测周末的方法
def is_weeked(date=datetime.datetime.now()):
    pass
#定义一个更新机器人化名库的方法
def update_alias_list():
    global CONN
    global ROBOT_ALIAS
    cursor=CONN.cursor()
    sql="select robot_alias from Robot_Alias"
    cursor.execute(sql)
    raw=cursor.fetchall()
    if len(raw)==0:
        pass
    else:
        result=[x[0] for x in raw]
        ROBOT_ALIAS=result
    cursor.close()
#一个检测桥页登录的方法
def bridge_login(account,password_md5):
    if account=='' or password_md5=='':
        return {"message":"需要登录"}
    else:
        print(account)
        print(password_md5)
        conn_flag=True
        conn=None
        while conn_flag:
            try:
                conn=my_sql.get_conn()
                conn_flag=False
            except:
                conn_flag=True
                print("数据库连接失败，15秒后重试")
                time.sleep(15)
        cursor=conn.cursor()
        sql="select t_Id,t_AccountPassword from teacherinfo where t_AccountName='{0}'".format(account)
        cursor.execute(sql)
        result=cursor.fetchone()
        if result is None:
            return {"message":"用户名不存在"}
        else:
            result=list(result)
            password_md5_db=result[1]
            password_md5_db=hashlib.md5(password_md5_db.encode()).hexdigest()
            if password_md5.lower()==password_md5_db.lower():
                return {"message":"success","teacher_id":result[0]}
            else:
                return {"message":"密码错误"}
#查询没有机器人配置的模式信息
def query_only_model(cursor):
    sql="select m_id,m_name from Robot_Model where m_id not in (select m_id from Robot_and_Model)"
    cursor.execute(sql)
    r=cursor.fetchall()
    cursor.close()
    if len(r)==0:
        return {}
    else:
        return [list(x) for x in r]  #[模式id,模式名称].....]

#查询所有机器人模式和所属的机器人的配置信息
def get_all_model_and_robot(cursor):
    sql="select Robot_and_Model.m_id,m_name,r_id,robot_name,r_times,robot_status from Robot_and_Model,Robot_Model,Robot_config where Robot_and_Model.m_id=Robot_Model.m_id and robot_id=r_id" #只能查出来有机器人配置信息的模式
    cursor.execute(sql)
    id_name_list=[]  #[{"模式id":id,"模式名称":name}........]
    robot_dict={}  #{"模式id":{"所属模式名称"：模式名称，“s所属机器人集合”:[{"机器人id"：机器人id，"机器人名称"：机器人名称，"间隔倍率":间隔倍率,"状态"：状态},{}...]},......]}
    result1=cursor.fetchall()
    other_dict=query_only_model(cursor)
    if len(result1)==0 and len(other_dict)==0:
        return {"message":"没有数据"}
    else:
        print(result1)
        #result=[list[x] for x in result1] #列顺序 0.模式id 1.模式名称 2.机器人id 3.机器人名称 4.间隔倍率 5.状态
        result=[]
        for x in result1:
            print(x)
            result.append(list(x))
        #制作一个数据字典，存储查询结果
        id_list=[]
        if len(id_name_list)>0:
            id_list=[n[0] for n in id_name_list]
        else:
            pass
        for x in result:
            if len(id_name_list)==0:
                 id_name_list.append({"id":x[0],"name":x[1]}) #操作模式名称和id的容器
            elif x[0] in [k["id"] for k in id_name_list]:
                pass
            else:
                id_name_list.append({"id":x[0],"name":x[1]}) #操作模式名称和id的容器
            if len(robot_dict)==0 or x[0] not in robot_dict.keys():
                robot_dict[x[0]]={"model_name":x[1],"robots":[{"robot_id":x[2],"robot_name":x[3],"robot_times":x[4],"robot_status":x[5]}]}
            elif x[0] in robot_dict.keys():
                robot_dict[x[0]]["robots"].append({"robot_id":x[2],"robot_name":x[3],"robot_times":x[4],"robot_status":x[5]})
            else:
                print("查询机器人和模式信息时发生未知错误")
        #检查没有机器人配置的清单。
        if len(other_dict)==0:
            pass
        else:
            for x in other_dict:
                if x[0] in [k["id"] for k in id_name_list]:#已有这个模式了
                    pass
                else:
                    id_name_list.append({"id":x[0],"name":x[1]}) #操作模式名称和id的容器
    print({"model_list":id_name_list,"robot_dict":robot_dict})
    cursor.close()
    global ALL_MODEL_ID
    return {"model_list":id_name_list,"robot_dict":robot_dict,"run_model_list":ALL_MODEL_ID.copy()}

#查询所有机器人的配置信息，robot_model的子方法
def get_all_robot(cursor):
    result_last=[]
    sql="select robot_id,robot_name from Robot_config"
    cursor.execute(sql)
    result=cursor.fetchall()
    if len(result)==0:
        pass
    else:
        result_last=[list(x) for x in result]
    cursor.close()
    return result_last
#删除机器人工作模式的方法
def delete_model(conn,model_id):
    sql1="delete from Robot_and_Model where m_id={0}".format(model_id)
    sql2="delete from Robot_Model where m_id={0}".format(model_id)
    cursor=conn.cursor()
    cursor.execute(sql1)
    cursor.execute(sql2)
    conn.commit()
    cursor.close()
    return {"message":"success"}
#添加/修改模式  第一个参数是dbc，第二个参数是模式名， 第三个参数是模式id，第四个参数是机器人的配置数组，【{"model_id":"","robot_id":robot_id,"times":times}，{"model_id":"","robot_id":robot_id,"times":times}，。。。。。】
def add_model(conn,model_name='',model_id='',robot_list=[]):
    #如果model_id=‘’说明是增加模式，否则视为修改模式
    if model_name=='':
        return {"message":"模式名称必须"}
    else:
        cursor=conn.cursor()
        if model_id=='':#如果是新增模式
            sql="select m_id from Robot_Model where m_name='{0}'".format(model_name)
            cursor.execute(sql)
            result=cursor.fetchone()
            if result is not None:
                return {"message":"已存在同名用户"}
            else:
                pass
            random_int=random.randint(1,10000000)
            sql="insert into Robot_Model(m_name,random_number) values('{0}',{1})".format(model_name,random_int)
            cursor.execute(sql)
            conn.commit()
            sql="select m_id from Robot_Model where m_name='{0}' and random_number={1}".format(model_name,random_int)
            cursor.execute(sql)
            result=cursor.fetchone()
            if len(result)==0:
                cursor.close()
                return {"message":"模式名称插入失败"}
            else:
                model_id=int(result[0])
                if len(robot_list)==0:
                    cursor.close()
                    return {"message":"模式新增完成"}
                else:
                    for x in robot_list:
                        print(x)
                        sql="insert into Robot_and_Model(m_id,r_id,r_times) values({0},{1},{2})".format(model_id,x["robot_id"],x["times"])
                        print(sql)
                        cursor.execute(sql)
                    conn.commit()
                    cursor.close()
                    return {"message":"模式新增完成"}
        else:    #如果是修改模式
            sql="delete from Robot_and_Model where m_id={0}".format(model_id)
            cursor.execute(sql)
            conn.commit()  #删除此模式原来的机器人配置
            if len(robot_list)==0:
                cursor.close()
                return {"message":"模式修改完成"}
            else:
                for x in robot_list:
                    sql="insert into Robot_and_Model(m_id,r_id,r_times) values({0},{1},{2})".format(model_id,x["robot_id"],x["times"])
                    print(sql)
                    cursor.execute(sql)
                conn.commit()
                cursor.close()
                return {"message":"模式修改完成"}
#一个专门重新计算间隔的类
class New_Step:
    def __init__(self,ids_times_dict):
        self.ids_times_dict=ids_times_dict
        self.temp_list=[]
    def new_step(self,id,step):
        step=step
        print("step is ",end='')
        print(step)
        if step.find(",")!=-1:
            self.temp_list=step.split(",")[0:2]
        elif step.find("，")!=-1:
            self.temp_list=step.split("，")[0:2]
        else:
            self.temp_list=[step,step]
        k=self.ids_times_dict.get(str(id))
        print(self.temp_list)
        print(len(self.temp_list))
        result=str(math.floor(int(self.temp_list[0])*float(k)))+","+str(math.floor(int(self.temp_list[1])*float(k)))
        return result
#print(New_Step({'8': 0.5, '3': 0.5, '6': 0.5}).new_step(3,"15,20"))
#一个把字典的key展开成为(key1,key2.....)这样格式的方法，用于给数据库的 in 方法配置参数
def in_arg(keys):
    s='('
    for i in  keys:
        s+=str(i)+","
    s=s.rstrip(",")
    s+=")"
    return s
#停止正在运行的所有机器人
def stop_all_robot(cursor):
    cursor=cursor
    sql="select robot_id,robot_name from Robot_config where robot_status='run'"
    cursor.execute(sql)
    result_raw=cursor.fetchall()
    cursor.close()
    if len(result_raw)==0:
        global ALL_MODEL_ID
        ALL_MODEL_ID=[]
        return {"message":"没有正在运行的机器人"}
    else:
        result=[list(x) for x in result_raw]
        for x in result:
            robot_handler("stop",{"robot_id":[str(x[0]).encode()],"robot_name":[str(x[1]).encode()]})
        global ALL_MODEL_ID
        ALL_MODEL_ID=[]
        global RM
        RM=Robot_Manage()
        RM.init_robots()
        return {"message":"success"}

#控制机器人模式的开始和停止 ,第一个参数是jdb，第二个参数代表是启动还是停止，第三个参数是一个id和间隔倍率组成的字典，
def control_model(cursor,model_id,type,ids_times={}):
    if len(ids_times)==0:
        return {"message":"此模式没有配置机器人"}
    else:
        cursor=cursor
        res=[]#返回的结果集
        new_step=New_Step(ids_times)
        #启动和停止机器人所需的参数如下：#0.robot_id,1.robot_name,2.begin_day,3.begin_weekday,4.begin_week,5.begin_month,6.begin_time,7.end_time,8.step,9.robot_owner,10.robot_status
        #这是方法去参数的形式：robot_id=int(args_dict.get("robot_id")[0].decode()) if args_dict.get("robot_id") is not None else 0
        #{"key"(str):[value(bytes)],"key"(str):[value(bytes)],"key"(str):[value(bytes)],"key"(str):[value(bytes)].........}
        sql="select robot_id,robot_name,begin_day,begin_weekday,begin_week,begin_month,begin_time,end_time,step,robot_owner,robot_status from Robot_config where robot_id in {0}".format(in_arg(ids_times.keys()))
        print(ids_times)
        print(sql)
        cursor.execute(sql)
        result_raw=cursor.fetchall()
        if len(result_raw)==0:
            return {"message":"信息有误，没有相关的机器人配置"}
        else:
            result=[list(x) for x in result_raw]
            robot_config_dict=[{x[1]:{"robot_id":[str(x[0]).encode()],"robot_name":[str(x[1]).encode()],"begin_day":[str(x[2]).encode()],"begin_weekday":[str(x[3]).encode()],"begin_week":[str(x[4]).encode()],"begin_month":[str(x[5]).encode()],"begin_time":[str(x[6]).encode()],"end_time":[str(x[7]).encode()],"step":[str(new_step.new_step(x[0],x[8])).encode()],"robot_owner":[str(x[9]).encode()],"robot_status":[str(x[10]).encode()]}} for x in result]
            #停止现在运行的所有机器人。
            stop_all_robot(cursor)
            #print("模式的机器人配置信息:",end='')
            #print(robot_config_dict)
            for x in robot_config_dict:
                for key in x.keys():
                    print(key)
                    robot_config=x[key]
                    res.append(robot_handler(type,robot_config))
                    print(res)
        cursor.close()
        global ALL_MODEL_ID
        if type=='run':
            ALL_MODEL_ID.append(model_id)
        else:
            pass
            #ALL_MODEL_ID.remove(model_id)  #前面的 stop_all_robot(cursor)已经清楚了所有的正在运行的模式
        return {"message":"success"}

#分析师后台多机器人和机器人模式的各种操作
def robot_model(input_arg,arg_dict={}):
    conn_flag=True
    result_last=None  #最后的结果集容器
    conn=None
    while conn_flag:
        try:
            conn=my_sql.get_conn()
            conn_flag=False
        except:
            conn_flag=True
            print("数据库连接失败，15秒后重试")
            time.sleep(15)
    cursor=conn.cursor()
    if input_arg=="query_model":
        result_last=get_all_model_and_robot(cursor)
    elif input_arg=="all_robot":
        result_last=get_all_robot(cursor)
    elif input_arg=="delete_model":
        result_last=delete_model(conn,arg_dict.get("model_id"))
    elif input_arg=="add_model":
        result_last=add_model(conn,arg_dict.get("model_name"),arg_dict.get("model_id"),arg_dict.get("robot_list"))
    elif input_arg=="run_model":
        result_last=control_model(cursor,arg_dict.get("model_id"),arg_dict.get("model_action"),arg_dict.get("ids_times"))
    elif input_arg=="stop_all_robot":
        result_last=stop_all_robot(cursor)
    else:
        pass

    cursor.close()
    conn.close()
    return json.dumps(result_last)
#print(robot_model("query_model"))



