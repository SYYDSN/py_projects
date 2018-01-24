# -*- encoding: utf8 -*-
__author__ = 'Administrator'

import re, urllib.request,getpass,sys,http.cookiejar,urllib.parse,urllib.error,httplib2,time,datetime,math,threading
from bs4 import BeautifulSoup
NEWS=[]     #全局变量，存储金10的新闻[{"time":time,"message":message},{}]
CAIJING_RILI=[]  #全局变量，存放财经日历的数据
CAIJING_RILI_3=[] #全局变量，存放财经日历3星以上的数据
CAIJING_RILI_3M2=[] #全局变量，存放财经日历3星以上+美国2星以上的的数据
NEXT_UPDATE_TIME=''  #下次更新金10数据日历的时间。格式为 "2015-01-01 01:20"
###############################################################################
#获取页面的内容，这是个通用方法
def get_page(url="http://rili.jin10.com/"):
    #连接到页面获取数据,url为网址，返回的是页面的内容
    headers={'Referer':url,"Connection":"Keep-Alive",
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'}
    req=urllib.request.Request(url,headers=headers)
    flag=True
    while flag:
        try:
            resp=urllib.request.urlopen(req)
            flag=False
            print(str(datetime.datetime.now())+" 获取日历成功")
        except:
            print(str(datetime.datetime.now())+" 连接中断")
            time.sleep(30)
    try:
        a=resp.readall().decode()
    except AttributeError as e:
        print(e)
        print("系统可能是python 3.5 编译环境")
        a=resp.read().decode()
    #print(a) #输出抓取到的原始页面内容
    return a
###############################################################################
#解析金石日历页面此方法不通用，date_str是时间格式字符串“”2016-01-01“格式,代表着获取哪一天的数据，默认是今天
def parse_page_jin10_rili(event_type='time_list',date_str=''):
    #f=open("parse_page_jin10_rili_log"+str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().month)+"-"+str(datetime.datetime.now().day)+".txt",mode="a",encoding="utf-8")   #日志
    if date_str=='':
        now=datetime.datetime.now()
    else:
        now=datetime.datetime.strptime(date_str,"%Y-%m-%d")
    url="http://rili.jin10.com/index.php?date={0}".format(now.strftime("%Y%m%d"))
    #f.write(now.strftime("%Y-%m-%d %H:%M:%S")+"抓取地址:"+url+'\n')
    global NEXT_UPDATE_TIME
    next_time=NEXT_UPDATE_TIME
    #f.write("下次更新时间："+next_time+"\n")
    #f.flush()
    #f.close()
    #print(url)
    a=get_page(url)
    soup=BeautifulSoup(a,"html5lib")  #指定Beautiful Soup 库所用的解析器
    data_list=[]  #存放所有数据日历
    data_list_3=[] #存放所有3星以上的数据日历
    data_list_3m2=[]    #存放三星+美国2星的数据日历
    if event_type=="time_list":
        event_time=''  #数据日历每条记录的发布时间
        #locals()["event_time"]=12
        for x in soup.table.find_all("tr"):
            if x.text.strip().startswith("时间"):
                pass
            else:
                #print("------------------------------")
                #拆分每一行的记录
                temp=x.text.strip().split("\n")
                #去掉空行
                temp=[x.strip() for x in temp if x.strip()!=""]
                #取时间
                if temp==['今日无重要经济数据']:
                    print(temp)
                elif re.search(r"^\d{1}\d?:\d{1}\d?$",temp[0]):#匹配时间
                    #print(temp[0])
                    event_time=temp[0]
                    #print("event_time is "+str(event_time))
                else:
                    temp.insert(0,event_time) #给没有时间的插入时间。
                #取星级
                imgs=x.find_all("img")
                #print(imgs)
                for y in imgs:
                    temp_img_src=y["src"]
                    if re.search(r"http://cdn.jin10.com/newrili/img/\d.png",temp_img_src):  #这幅图片代表的是星级,注意，这个网址有可能会变动
                        level=int((temp_img_src.split("/")[-1]).split(".")[0])
                        temp.insert(2,level)
                    else:
                        pass
                #print(temp)
                #2016-03-24修正列长度为7，类似 ['22:30', '美国至3月18日当周EIA天然气库存(亿立方英尺)', 2, '-10', '---', '待公布', '未公布', '金银']
                if len(temp)!=8:
                    #print("error: ",end='')
                    #print(temp)
                    temp.insert(4,"--")  #如果这行数据日历没有预测值的话，就添加一个，防止数组越界。
                    #print(temp)
                else:
                    data_list.append(temp)
                #print("temp is "+str(temp))
                if temp==['今日无重要经济数据'] or "今日无重要经济数据" in temp:
                    pass
                    #print(temp)
                elif int(temp[2])>=3:
                    data_list_3.append(temp)
                    data_list_3m2.append(temp)
                elif int(temp[2])>=2 and temp[1].split(" ")[0]=="美国":
                    data_list_3m2.append(temp)
                else:
                    pass
    else:
        pass
    #data_list 数据列数顺序 0.时间 1.信息（包含国家） 2.重要等级 3.前值 4.预测值 5.公布值

    global CAIJING_RILI,CAIJING_RILI_3,CAIJING_RILI_3M2
    #print(data_list)
    #print(data_list_3)
    #print(data_list_3m2)
    CAIJING_RILI=data_list
    CAIJING_RILI_3=data_list_3
    CAIJING_RILI_3M2=data_list_3m2
 ###################返回筛选的数据日历的方法#####################################
def pack_data_calendar():
    #data_list 数据列数顺序 0.时间 1.信息（包含国家） 2.重要等级 3.前值 4.预测值 5.公布值
    #如果有三星的消息，那就拿三星的数据，如果没有三星以上的数据，那就拿美国的2星的。
    #筛选标准如下：
    #1.三星和三星以上的数据，有多少拿多少。
    #2.如果三星以上的数据不足5条，那就从美国的2星的数据里面填充剩下的。
    #return globals()["CAIJING_RILI"].copy()  #测试用，测试完就需要注销
    if len(globals()["CAIJING_RILI_3"])>=5:
        return globals()["CAIJING_RILI_3"].copy()
    elif len(globals()["CAIJING_RILI_3M2"])>=10:
        return globals()["CAIJING_RILI_3M2"].copy()
    else:
        return globals()["CAIJING_RILI"].copy()
###############################################################################

#获取下一次更新的时间间隔。返回,date_str是时间格式字符串“”2016-01-01“格式,代表着获取哪一天的数据，默认是今天
def get_next_update_timeout(date_str=''):
    data_list=pack_data_calendar()
    if date_str=='':
        now=datetime.datetime.now()
    else:
        now=datetime.datetime.strptime(date_str,"%Y-%m-%d")
    date_str=now.strftime("%Y-%m-%d")
    #print(data_list)
    #数据列数顺序 0.时间 1.信息（包含国家） 2.重要等级 3.前值 4.预测值 5.公布值
    #[['07:50', '日本 12月未季调商品贸易帐(亿日元)', '-3797', '1170', '1402'], 。。。。]
    if len(data_list)==0 or data_list[0][1].startswith("今日无"):#如果今天没有任何数据，比如是周末
        next_update_date=datetime.datetime.strptime(date_str+" "+"23:59:59","%Y-%m-%d %H:%M:%S")
    else:
        #寻找关键字所在的索引
        try:
            index=data_list[-1].index("待公布")
            next_time=[x for x in data_list if x[index]=="待公布"][0][0]
            next_update_date=datetime.datetime.strptime(date_str+" "+next_time,"%Y-%m-%d %H:%M")
        except ValueError as e:
            print(e)
            next_update_date=datetime.datetime.strptime(date_str+" "+"23:59:59","%Y-%m-%d %H:%M:%S")

    delta=(next_update_date-now).total_seconds()  #判断还有多少秒就到更新时间了。
    if delta>=0:#如果更新时间晚于或者等于现在的时间，
        delta+=5 #再延时5秒
    else:#如果更新时间已超时，很可能是由于金10网站没有及时更新造成的，那就在现在的基础上延时5秒再试
        delta=5
    delta=math.ceil(delta)   #向上取整
    #print(delta)
    global NEXT_UPDATE_TIME
    NEXT_UPDATE_TIME=(now+datetime.timedelta(seconds=delta)).strftime("%Y-%m-%d %H:%M:%S")
    xx=globals()["NEXT_UPDATE_TIME"]
    print("下次更新时间: "+xx)
    return delta
#get_next_update_timeout()
###############################################################################
#更新金石数据日历的线程
class My_Updater1(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop=False
    def run(self):
        while not self.thread_stop:
            parse_page_jin10_rili()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"更新完毕")
            time.sleep(get_next_update_timeout())
    def stop(self):
        self.thread_stop=True
###############################################################################
My_Updater1().start()   #运行此线程
#parse_page_jin10_rili(date_str="2016-01-22")
#print(CAIJING_RILI)
###############################################################################
#获取金石日历数据的方法,post和ws都可以使用。
def get_jin10_calendar():
    return pack_data_calendar() #数据列数顺序 0.时间 1.信息（包含国家） 2.重要等级 3.前值 4.预测值 5.公布值

#time.sleep(3)
#print(get_jin10_calendar())
###############################################################################
#比较数据日历，返回结果为布尔值，表示两则是否相等,第一个参数是上一次的日历，第二个我参数是这一次的数据日历
def compare_data_calendar(obj1,obj2):#数据列数顺序 0.时间 1.信息（包含国家） 2.重要等级 3.前值 4.预测值 5.公布值
    flag=True
    if len(obj1)==0:
        flag=False
        print(str(datetime.datetime.now())+"第一次加载数据日历")
    else:
        list1=[x[5] for x in obj1 if len(x)==7]
        list2=[x[5] for x in obj2 if len(x)==7]

        for i in range(len(list1)-1):
            if list1[i]==list2[i]:
                pass
            else:
                print(str(datetime.datetime.now())+"日历不匹配，需要更新")
                flag=False
                break
        #print(str(datetime.datetime.now())+"日历匹配，无需更新")
    return flag
#比较数据新闻，如果想等就返回空数组，否则就返回一个增量数组
def compare_news(old_news,new_news):#数据格式{'time': '16:59', 'message': '香港特区政府：12月香港对内地净出口量为129.266吨，前值79.003吨。'}
    data_list=[]
    if len(old_news)==0:
        return new_news
    elif len(new_news)==0:
        return old_news
    else:
        for x in new_news:
            if x not in old_news:
                data_list.append(x)
        return data_list
###############################################################################
#接受金10主页发送来的数据。
def listen_jin10_index(info_list=[]):
    #前端发送来的数据格式{'time': '16:59', 'message': '香港特区政府：12月香港对内地净出口量为129.266吨，前值79.003吨。'}
    #print(info_list)
    info_list=[x for x in info_list if x['message'].strip()!='']
    info_list=info_list if len(info_list)<=30 else info_list[0:30]
    info_list2=[]
    for x in info_list:
        if re.search(r"^\d{1}\d{1}:\d{1}\d{1}:\d{1}\d{1}$",x["time"]):#把16:00:00这样的时间修改为16:00
            info_list2.append({"time":x["time"][0:5],"message":x["message"]})
        else:
            info_list2.append(x)
    global NEWS
    #print("info_list:")
    #print(info_list)
    NEWS=info_list2
############获取金10 新闻的方法#############################################
def get_jin10_news():
    return globals()["NEWS"].copy()
###############################################################################
#不一定在给定时间延时60秒执行更新的时候，金石网站那里也及时更新了数据。
