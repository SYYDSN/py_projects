# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
import datetime,urllib.request,time,json,random,pymssql




#用于抓取长江行情的数据写入数据库
#创建数据库连接
conn=None
try:
    conn=pymssql.connect(host='121.42.204.235',user='sa',password='SHxdkj2015',database='jy_db',charset='utf8')
except:
    message="连接失败"
    print("连接失败")
cursor=conn.cursor()

count=0
errorcount=0

data_dict_old={"date":"","data":[]}; #全局变量存放上次获取的数据的时间和数据，用来和最新的数据比较，看看是否是重复的数据。


#获取行情报价的函数，由于有sleep方法，所以必须放在代码的最后，将来会修改这个方法，避免sleep影响到
def get_data():
    while 1:
        time.sleep(1) #等待间隔
        data_dict_new={"date":"","data":[]};#存放本地获取的数据的时间和数据，用来和最新的数据比较，看看是否是重复的数据。
        log=open("hangqing_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt","a")          #日志
        try:
            re=urllib.request.urlopen("http://180.166.148.187:16853/hqweb/hq/736.jsp?uid={0}".format(random.random()))
            s=re.readall().decode("gbk")  #读取消息，注意gbk的字符集
            global count
            count=count+1
            print(s)
            print("连接正常，正在读取数据....")
        except:
            global errorcount
            errorcount+=1
            print(datetime.datetime.now().isoformat()," error connection's count=",count,file=log)
            print("连接被断开，正在重新连接....")
        temp_list=s.split("\n")
        recode_date=temp_list.pop().strip()   #弹出最后一行的日期
        data_dict_new["date"]=recode_date
        data_list=[] #一个数组，用来存储不同产品同一时刻的报价
        #print(len(temp_list))
        count=1
        for line in temp_list:
            if len(line)<20:    #如果数组的长度太短，证明可能是空行或者无效字符
                pass
            else:
                #print(str(count)+str(line))
                #print("lengthis "+str(len(line)))
                count+=1
                temp=[x.strip() for x in line.split(",")]
                #print(temp)
                #按照 0产品代码，1产品名称，2收盘价，3开盘价，4最高价，5最低价，6最新价，9涨跌，10，昨结，11，涨跌幅 插入数据
                #插入后的顺序 0产品代码，1产品名称，2收盘价，3开盘价，4最高价，5最低价，6最新价，7涨跌，8，昨结，9，涨跌幅
                #涨跌幅的计算公式 涨跌幅=（(昨收-现价）/昨收)*100%
                temp_list2=[temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[9],temp[10],str(round(((float(temp[2] if float(temp[2])!=0.00 else temp[3])-float(temp[6]))/float(temp[2] if float(temp[2])!=0.00 else temp[6]))*100,2))+"%"]  #保存单个产品的报价
                #print(temp_list2)
                data_list.append(temp_list2)
        data_dict_new["data"]=data_list
        #新的数据字典装载完毕。
        old_date=0
        new_date=1
        try:
            global data_dict_old
            old_date=datetime.datetime.strptime(data_dict_old.get("date"),"%Y-%m-%d %H:%M:%S")
            new_date=datetime.datetime.strptime(data_dict_new.get("date"),"%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("数据的时间没有找到或者格式错误")
        if old_date<new_date:
            datas=data_dict_new.get("data")
            for data in datas:
                sql="insert into changjiang_hangqing values('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},'{9}','{10}')".format(
                    data[0],data[1],float(data[2]),float(data[3]),float(data[4]),float(data[5]),float(data[6]),float(data[7]),
                    float(data[8]),data[9],data_dict_new.get("date"))
                #print("插入changjiang_hangqing的sql语句是："+sql)
                cursor.execute(sql)
            conn.commit()
            data_dict_old=data_dict_new  #把刚刚获取的数据写入作为全局变量的旧数据。用于下一次的比较。
            #ws_client.send(json.dumps(data_dict_old))  #把更新后的数据发送到ws服务器 已注销
        else:
            print("跳过已存在的数据")
            pass
#运行程序写入行情报价
get_data()


