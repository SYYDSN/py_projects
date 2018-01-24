# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
import pymssql,threading,time,random
import datetime,urllib.request,json
#####################################实现挂单功能##################################################################
#定义一个全局变量，用来存储行情信息
hangqing_list=[]
print("web socket服务器运行在9009端口.....")
#2获取行情数据。用于ws服务器。
#创建数据库连接
conn=None
try:
    conn=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
except:
    message="连接失败"
    print("连接失败")
cursor=conn.cursor()
#####################################
conn3=None
try:
    conn3=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
except:
    message="连接失败"
    print("连接失败")
###################
conn2=None
try:
    conn2=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
except:
    message="连接失败"
    print("连接失败")

##########################一个检测sql是否连接的方法#########################
def check_pymssql():
    global  conn
    sql="select COUNT(*) from changjiang_hangqing"
    try:
        cursor=conn.cursor()
        cursor.execute(sql)
    except:
        try:
            conn=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
            cursor=conn.cursor()
            cursor.execute(sql)
            print("重新连接成功")
            cursor.close()
        except:
            print("重新连接失败，等待5秒后重新连接")
            time.sleep(5)
            check_pymssql()
    #print("数据库检测正常")
####################################################################

#一个获取行情数据的方法，用于ws服务器。
def get_hangqing():
    check_pymssql()
    #查询行情。注意下面的union关键字用来连接两个查询结果，查询结果的列顺序是：0产品id，1 产品代码，2 产品名称（修改过的），3 产品价格，4 涨跌（点数）
    sql="select Product.p_Id as 'ID',Sys_Code as Code,Product.p_Name  as '名称',admin_hangqing_02.Sys_New as '价格',admin_hangqing_02.SYs_Change as '涨跌'    from admin_hangqing_02,Product where Product.p_Code=admin_hangqing_02.Sys_Code and (Sys_Code='USD' or Sys_Code='SPCI' or Sys_Code='1' or Sys_Code='CONC') union select Product.p_Id as 'ID',product_code as Code,Product.p_Name as '名称',changjiang_hangqing.current_price as '价格',changjiang_hangqing.up_down as '涨跌' from Product,changjiang_hangqing where  Product.p_Code=changjiang_hangqing.product_code and Product.can_user=1"

    #print("查询行情 "+sql)
    cursor.execute(sql)
    result=cursor.fetchall()
    result=[list(x) for x in result]
    to_single_call(result)  ########################################################触发挂单和临晨强制平仓##############################################################################
    auto_stop_win_lost(result) ##################################################触发止赢止损############################################################################################
    result.insert(0,['产品ID',"产品代码","产品名称","报价","涨跌"])
    global hangqing_list
    hangqing_list=result
    return result
########################################挂单自动改为喊单的方法,第一个参数是数据库指针，第二个参数是价格字典的列表【{"产品id":"产品价格"}】
ping_flag=''  #定义一个变量，用于标识是否需要强制平掉挂单（每天凌晨4点的时候，会强制把处于wait状态的挂单改为drop状态）
def to_single_call(price_list=[]):
    sql1="select s_Id,s_ProductId,s_JinChang,s_compare,s_Direction from SingleCall_Ahead where s_Status='wait'"
    log=open("singleCall_Ahead_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")          #日志
    cursor3=conn3.cursor()
    cursor3.execute(sql1)
    result1=cursor3.fetchall()
    if len(result1)==0:
        pass
    else:
        result1=[list(x) for x in result1]  #0。挂单id  1.产品id  2.进场价 3.挂单时报价  4，交易方向
        #['产品ID',"产品代码","产品名称","报价","涨跌"]
        price_list=dict(zip([x[0] for x in price_list],[x[3] for x in price_list]))  #构建一个以产品id为key，报价为value的dict
        count=0 #进场单计数器
        count1=0  #改变状态的挂单的计数器

        for x in result1:
            #print(x)
            #print(price_list)
            if x[4]=="挂多":
                if float(price_list.get(x[1]))>=float(x[2]) and float(x[2])>=float(x[3]):  #如果现在的价格高于进场价，并且进场价大于等于挂单时的价格，认定此单可立即进场。
                    sql_up="update SingleCall_Ahead set s_Status='gone' where s_Id={0}".format(x[0])
                    print("sql_up is "+sql_up)
                    print(datetime.datetime.now(),file=log)
                    print("sql_up is "+sql_up,file=log)
                    cursor3.execute(sql_up)
                    count+=1
                elif float(price_list.get(x[1]))<=float(x[2]) and float(x[2])<float(x[3]):  #如果现在的价格小于等于进场价，并且进场价小于挂单时的价格，认定此单可立即进场。
                    sql_up="update SingleCall_Ahead set s_Status='gone' where s_Id={0}".format(x[0])
                    print("sql_up is "+sql_up)
                    print(datetime.datetime.now(),file=log)
                    print("sql_up is "+sql_up,file=log)
                    cursor3.execute(sql_up)
                    count1+=1
                else:
                    pass
            elif x[4]=="挂空":
                if float(price_list.get(x[1]))<=float(x[2]) and float(x[2])<=float(x[3]):  #如果现在的价格低于进场价，并且进场价小于等于挂单时的价格，认定此单可立即进场。
                    sql_down="update SingleCall_Ahead set s_Status='gone' where s_Id={0}".format(x[0])
                    print("sql_up is "+sql_down)
                    print(datetime.datetime.now(),file=log)
                    print("sql_up is "+sql_down,file=log)
                    cursor3.execute(sql_down)
                    count+=1
                elif float(price_list.get(x[1]))>=float(x[2]) and float(x[2])>float(x[3]):  #如果现在的价格低于进场价，并且进场价大于挂单时的价格，认定此单可立即进场。
                    sql_down="update SingleCall_Ahead set s_Status='gone' where s_Id={0}".format(x[0])
                    print("sql_up is "+sql_down)
                    print(datetime.datetime.now(),file=log)
                    print("sql_up is "+sql_down,file=log)
                    cursor3.execute(sql_down)
                    count1+=1
                else:
                    pass
            else:
                print("方向不明的挂单:",end=" ")
                print(x)
                print("方向不明的挂单:",file=log)
                print(x,file=log)
        conn3.commit()
        if count==0:
            pass
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" 共有"+str(count+count1)+"个单子入场")
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" 共有"+str(count+count1)+"个单子入场",file=log)

    #凌晨强制平仓


    clock=datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d")+" "+"04:00:00","%Y-%m-%d %H:%M:%S")  ###########定义强制平单时间#######################
    now=datetime.datetime.now()
    delta=(now-clock).total_seconds()
    if delta<0:#如果当前时间比定时早
        pass
    else:
        global ping_flag
        #print("ping_flag is ",str(ping_flag))
        #print("now is "+now.strftime("%Y-%m-%d"))
        #print(ping_flag!=now.strftime("%Y-%m-%d") and ping_flag!='')
        if ping_flag!=now.strftime("%Y-%m-%d") and ping_flag!='':
            #print("if")
            sql_drop="select s_Id from SingleCall_Ahead where s_Status='wait' and DATEDIFF(ss,'{0}',s_Bigin)<0".format(clock.strftime("%Y-%m-%d %H:%M:%S"))  #平单的sql
            cursor3.execute(sql_drop)
            temp_drop=cursor3.fetchall()
            if len(temp_drop)==0:
                pass
            else:
                count2=0
                result_drop=[list(x)[0] for x in temp_drop]
                for x in result_drop:
                    sql_drop2="update SingleCall_Ahead set s_Status='drop' where s_Id={0}".format(x)  #修改记录状态
                    cursor3.execute(sql_drop2)
                    count2+=1
                conn3.commit()
                print("共计"+str(count2)+"条挂单失效")
            ping_flag=now.strftime("%Y-%m-%d")  #给ping_flag赋值，表示今天强制平单过了。
        elif ping_flag=='':
            #print("XXXXX")
            #nonlocal ping_flag  #选择语句切断了生存周期，所以要用global声明一下
            ping_flag=0
        else:
            pass
    log.close()
    cursor3.close()
    #print(now)
#to_single_call(cursor,get_hangqing()[1:])
#############################################################################
"""
#自定义一个子线程的类用来发送数据
class My_Thread(threading.Thread):            #必须继承threading.Thread类。定时器用多线程是因为py的定时器和js的概念不同，在py 的定时器中一般有while语句，处于while 1 状态的代码会一直执行下去而阻断后继代码的执行，所以必须让定时器代码以子线程的方式运行，防止定时器阻止主代码继续运行下去。
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.thread_stop = False   #定义此变量用于辅助确认停止线程。。
    def run(self):                                #此方法将被start()调用，此方法不能有任何参数。
        while not self.thread_stop:               #判断此线程是否处于stop状态。
            data=get_hangqing()
            print(data)
            time.sleep(1)                        #停止1秒。
    def stop(self):                                #停止线程的方法。
        self.thread_stop=True                     #修改标志位以停止线程。
"""

#定义一个类，用来接收挂单的请求。
def single_call_ahead(input,owner_id,product_id,direction,jin_price,stop_win,stop_lost):
    cursor2=conn2.cursor()
    #方法参数0，老师id，1.产品id 2.交易方向 。3.进场价格 4.止赢价格  5.止损价格   注意，要插入的表有一个触发器，在满足条件的时候会把特定的数据插入SingleCall表中。
    print(input)
    #线查询这个老师是否已有挂单或者喊单 根据这个老师的id从SingleCall里统计状态处于open和SingleCall_Ahead里处于wait状态的统计数字，如果大于0，就判断为已有单子了，因为任意老师只允许一个喊单或者挂单
    #同样，在平仓的时候，挂单也可以平仓，一般都是挂单错误或者失去机会的时候主动关闭挂单.
    sql1="select sum(t2.c) from ((select COUNT(*) as c from SingleCall where s_OwnerId={0} and s_Status='open') union (select COUNT(*) as c from SingleCall_Ahead where s_OwnerId={0} and s_Status='wait')) as t2".format(owner_id)
    print("single call ahead select string is "+sql1)
    cursor2.execute(sql1)
    result1=cursor2.fetchone()[0]
    log=open("singleCall_Ahead_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")           #日志
    #print(result1)
    if input=="add":#如果是增加挂单的情况
        if result1>0:
            return {"message":"已有喊单或者挂单"}
        else:
            global  hangqing_list
            price_list=hangqing_list.copy()
            price_list.pop(0)
            price_list=dict(zip([x[0] for x in price_list],[x[3] for x in price_list]))  #构建一个以产品id为key，报价为value的dict
            #sql语句列顺序 0.老师id 1。产品id 2.产品名称 3.交易方向 4.进场价格 5.挂单开始时间 6.止赢价格 7.止损价格 8.挂单状态 9.当前年 10.当前月
            sql="insert into SingleCall_Ahead([s_OwnerId],[s_ProductId],[s_ProductName],[s_Direction],[s_JinChang],[s_compare],[s_Bigin],[s_StopProfit],[s_StopDrop],[s_Status],[s_CurrentYear],[s_CurrentMonth]) " \
                "values({0},{1},{2},'{3}',{4},{5},{6},{7},{8},'{9}',{10},{11})".format(owner_id,product_id,"(select p_Name from Product where p_Id={0})".format(product_id),direction,jin_price,price_list[product_id],"getdate()",stop_win,stop_lost,"wait","datepart(yyyy,getdate())","datepart(m,getdate())" )
            print("single_call_ahead sql insert string is "+sql)
            print(datetime.datetime.now(),file=log)
            print("single_call_ahead sql insert string is "+sql,file=log)
            cursor2.execute(sql)
            conn2.commit()
            return {"message":"success"}
    elif input=="cancel":#如果是取消挂单
        sql2="select s_Id from SingleCall_Ahead where s_OwnerId={0} and s_Status='wait'".format(owner_id)
        cursor2.execute(sql2)
        one=cursor2.fetchone()
        result2=one[0] if one else 0
        #print(result2)
        if result2==0:
            return {"message":"没有挂单信息"}
        else:
            sql2="update SingleCall_Ahead set s_Status='drop' where s_Id={0}".format(result2)
            cursor2.execute(sql2)
            print("Single call ahead cancel string is "+sql2)
            conn2.commit()
            print(datetime.datetime.now(),file=log)
            print("Single call ahead cancel string is "+sql2,file=log)
            return {"message":"取消成功"}
    elif input=="check":#检查是否有喊单或挂单
        sql1="select sum(t2.c) from ((select COUNT(*) as c from SingleCall where s_OwnerId={0} and s_Status='open') union (select COUNT(*) as c from SingleCall_Ahead where s_OwnerId={0} and s_Status='wait')) as t2".format(owner_id)
        print("single call ahead check select string is "+sql1)
        cursor2.execute(sql1)
        result1=cursor2.fetchone()[0]
        print(result1)
        if result1>0:
            return {"message":"已有喊单或者挂单"}
        else:
            return {"message":"success"}
    else:
        pass
    log.close()
    cursor2.close()
#有关自动止赢止损的思路：
#原则上，只要周期性查询数据库SingleCall表中有止赢或者止损并且处于open状态的单子即可，但出于降低数据库压力考虑。应该只在需要时查询数据库更新这个需要止赢止损的单据的列表,暂时采用轮训的方式，在每次查询报价时触发查询。
#那么，可以采取如下的办法：
#1.程序启动时查询一次SingleCall表
#2.挂单触发喊单时，触发查询。
#3. 老师喊单时，触发查询
#4.老师平仓时，触发查询。
#5. 止赢止损时，触发查询。
###################
conn3=None
try:
    conn3=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
except:
    message="连接失败"
    print("连接失败")
def auto_stop_win_lost(price_list=[]):         #自动止盈止损
    #参数price_list是报价的数组，格式如下['产品ID',"产品代码","产品名称","报价","涨跌"]，实际只用到了数组中的产品id和报价两项
    global conn3
    cursor3=conn3.cursor()
    sql="select COUNT(*) from changjiang_hangqing"
    try:
        cursor3.execute(sql)
        result=cursor3.fetchone()[0]
    except:
        conn3=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
        cursor3=conn3.cursor()
    log=open("singleCall_Ahead_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")           #日志
    #先查出所有还在关注老师的粉丝的信息备用。
    sql="select uat_Uid,u_MobilePhone,(case when isnull((case when ISNULL(u_Nickname,'')='' then u_Name else u_Name end),'')='' " \
        "then CONVERT(nvarchar(6),u_Id)+'号用户' else (case when ISNULL(u_Nickname,'')='' then u_Name else u_Name end) end), " \
        "uat_Tid from UserAttentionTeacher,userinfo where u_Id=uat_Uid and uat_EndTime is null"
    cursor3.execute(sql)
    fans_list=[list(x) for x in cursor3.fetchall()]   #从用户关注老师的表里查询出来的列顺序是 0.用户id  1.用户手机  2.用户的昵称/真实名字/xx号用户 3.老师id
    #查询所有有止赢或者止损的单据,止赢止损不能为null，并且如果值是0的话，在比对的时候就要掠过
    sql="select s_Id,s_ProductId,s_Direction,s_StopProfit,s_StopDrop,t_Nickname,t_Id from SingleCall,teacherinfo where SingleCall.s_OwnerId=teacherinfo.t_Id and s_Status='open' and not (s_StopDrop is  null and s_StopDrop is null)"
    #查询的结果的列顺序是：0.喊单id  1.产品id  2.方向 空/多  3.止赢 float 4。止损 float 5.老师昵称 6.老师ID
    #print("auto_stop_win_lost's select string :"+sql)
    cursor3.execute(sql)
    result=cursor3.fetchall()
    #print(result)
    if len(result)>0:
        result=[list(x) for x in result]  #查询到的有止赢止损的喊单的集合。列顺序是：0.喊单id  1.产品id  2.方向 空/多  3.止赢 float 4。止损 float  5.老师昵称  6.老师ID
        #price_list=price_list[1:]   #测试的时候用，正式的时候根据插入位置的不同，可能不需要这一步
        price_dict=dict(zip([x[0] for x in price_list],[x[3] for x in price_list])) #制作一个key=产品代码，value=产品价格的dict
        pro_count=0
        for x in result:#x列顺序 0.喊单id int 1.产品id int  2.方向 空/多 str 3.止赢 float 4。止损 float
            current_price=price_dict.get(x[1])
            if x[2]=="多":#如果是多单
                if x[3]==None or x[3]==0:
                    stop_win=float("inf") #如果没有设置止赢或者止赢为0的话，就把止赢设置为正无穷大
                else:
                    stop_win=x[3]
                if x[4]==None or x[4]==0:
                    stop_lost=float("-inf") #如果没有设置止损或者止损为0的话，就把止损设置为负无穷小
                else:
                    stop_lost=x[4]
                if stop_win<=current_price or stop_lost>=current_price:#多单止赢止损
                    pro_count+=1
                    temp_sql="update SingleCall set s_End=getdate(),s_PingCang={1},s_Status='close' where s_Id={0}".format(x[0],current_price)
                    if stop_win<=current_price:
                        key="多单止赢"
                    else:
                        key="多单止损"
                    print(key)
                    print("auto_stop_win_lost's stop string :"+temp_sql)
                    print(datetime.datetime.now(),file=log)
                    print(key)
                    print("auto_stop_win_lost's stop string :"+temp_sql,file=log)
                    cursor3.execute(temp_sql)
                    conn3.commit()#平仓
                    #给老师的粉丝发短信##################################################
                    teacher_nick=x[5]
                    teacher_id=x[6]
                    a_fans_list=[[n[1],n[2]] for n in fans_list if n[3]==teacher_id]#取出粉丝的手机号码和昵称
                    print(a_fans_list)
                    send_sms_to_fans(teacher_nick,a_fans_list)
                else:
                    pass
            elif x[2]=="空":#如果是空单
                if x[3]==None or x[3]==0:
                    stop_win=float("-inf") #如果没有设置止赢或者止赢为0的话，就把止赢设置为负无穷小
                else:
                    stop_win=x[3]
                if x[4]==None or x[4]==0:
                    stop_lost=float("inf") #如果没有设置止损或者止损为0的话，就把止损设置为正无穷大
                else:
                    stop_lost=x[4]
                if stop_win>=current_price or stop_lost<=current_price:#空单止赢止损
                    pro_count+=1
                    temp_sql="update SingleCall set s_End=getdate(),s_PingCang={1},s_Status='close' where s_Id={0}".format(x[0],current_price)
                    if stop_win>=current_price:
                        key="空单止赢"
                    else:
                        key="空单止损"
                    print(key)
                    print("auto_stop_win_lost's stop string :"+temp_sql)
                    print(datetime.datetime.now(),file=log)
                    print(key)
                    print("auto_stop_win_lost's stop string :"+temp_sql,file=log)
                    cursor3.execute(temp_sql)
                    conn3.commit() #平仓
                    #给老师的粉丝发短信###############################################
                    teacher_nick=x[5]
                    teacher_id=x[6]
                    a_fans_list=[[n[1],n[2]] for n in fans_list if n[3]==teacher_id]  #取出粉丝的手机号码和昵称
                    print(a_fans_list)
                    send_sms_to_fans(teacher_nick,a_fans_list)
                else:
                    pass
            else:
                pass

        cursor3.close()
        if pro_count==0:
            pass
        else:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"共计"+str(pro_count)+"个单子被止赢/止损")
    else:
        #print("没有止赢/止损的喊单")
        pass
    log.close()
def send_sms_to_fans(teacger_nick,fans_list):
    print("start send_sms_to_fans")
    #发短信给老师的粉丝,第一个参数是老师的昵称，第二个参数是该名老师的粉丝手机号码列表，列表内每个元素的都是用户的手机号码和昵称组成的数组
    url="http://91dashi.cn:5000/post_sms" #请求的网址。对应ws服务器的对应url
    s=''
    s2=''
    print("fans_list")
    print(fans_list)
    log=open("singleCall_Ahead_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")           #日志
    for x in fans_list:
        print(x)

        data={"templateId":16249,"phone":x[0],"sms":x[1]+","+teacger_nick}
        adata=(urllib.parse.urlencode(data)).encode() #先用urllib.parse.urlencode()方法转换对象为key=val的格式（就像get方法的参数那样），要求是原始对象是dict格式的。然后从encode（）方法转为字节码。因为py3的post只能发送字节码对象
        #print(adata)

        req=urllib.request.Request(url,adata) #创建一个请求对象
        print(req.data)

        res=urllib.request.urlopen(req) #打开页面
        result=res.read() #读取返回结果。
        flag=str(datetime.datetime.now().isoformat())+" send "+result.decode() #接收回来的数据要解码，不要忘记了。
        #print(flag)
        if flag.endswith("成功"):
            s+=str(x)+","
        else:
            s2=str(x)+",返回信息："+flag+"；"
    if s.rstrip(",").strip()!="":
        print("以下号码发送成功："+s)
        print(datetime.datetime.now,file=log)
        print("以下号码发送成功："+s,file=log)
    elif s2.rstrip("；").strip()!="":
        print("以下是发送失败的号码："+s2)
        print(datetime.datetime.now,file=log)
        print("以下号码发送成功："+s2,file=log)
    else:
        pass
    log.close()
#send_sms_to_fans("张三",[15618317376,13162206967])
