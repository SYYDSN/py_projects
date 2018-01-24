__author__ = 'Administrator'
import threading,time
from datetime import datetime
from datetime import timedelta
import urllib.request,threading,re
from html.parser import HTMLParser

"""
第二版日晖聊天室解析器和抓取方法
前端所用的js代码如下（在开发者工具的命令行中运行）：
var int = setInterval(function () {
var html=$("#liaotianlist").parent().html();
  console.log(html);
$.post("http://127.0.0.1:81/data_listen",{"data":html},function(data){
 console.log(data);
 });
}, 5000);
"""
DICT_LIST=[]        #全局变量，用于实时存储日晖聊天室的消息
BLACK_LIST=[]       #全局变量，禁言黑名单
#HTML文档解析器
class myHTMLParser(HTMLParser):
    def __init__(self):
        self.title=''
        self.reading_title=0
        HTMLParser.__init__(self)
    def handle_starttag(self,tag,attrs):
        for x in attrs:
            if "id" in x and "liaotianlist" in x and tag=="ul":
                #print(attrs)
                self.reading_title=1
    def handle_data(self,data):
        if self.reading_title:
            if self.title=='' and not data.isspace():
                self.title+=data
            else:
                if self.title.endswith("|") and not data.isspace():
                    self.title+=data
                else:
                    if not data.isspace():
                        if re.search(r"\d{1}\d?:\d{1}\d?:\d{1}\d?",data):
                            self.title+=","+data
                        else:
                            self.title+="|"+data
                        #print(data)
                        #print(data.isspace())
                        #print(self.title)
                    else:
                        pass
            #print("data is "+data)
        else:
            pass
    def handle_endtag(self,tag):
        if tag=="ul":
            self.reading_title=0
    def gettitle(self):
        temp=[x for x in self.title.split("\r") if x.strip()!=""]

        temp=[x.split("|") for x in temp[0].split(",")]
        temp2=[]
        for x in temp:
            #print(x)
            if len(x)>1:#数组中只有一条数据的时候就放弃。
                try:
                    v=x[2]
                except:
                    v=""
                t=[x[0],x[1].strip(":").strip("："),v]
                #print(t)
                temp2.append(t)
            else:
                pass
        self.title=temp2
        return self.title
#接受前段发来的脚本，抓取聊天室数据，写入全局变量，
def get_data(request):
    """b=request.form.get("data") 这个是flask下取出post数据的方法。tornado不是这个方法取出post数据的，所以要注销。
    #print(request.form)
    if b=='' or b==None:
        return "no data" #如果没有数据
    else:
        pass
    """
    global  DICT_LIST
    b=request    #tornado专用，main_server已取出data作为参数传进来了。
    my_parser=myHTMLParser()
    my_parser.feed(b)
    messages=my_parser.gettitle()
    #print("l is ")
    #print(messages)

    #规范并处理数据，统一成{ 'time': '00:00:10', 'name': '挑战者','message': 'xxxx'}这样组成的dict的list形势
    dict_list=[]  #准备最终结果集合。
    for x in messages:
        #处理敏感字，
        if "巡管" in x[1] or "老师" in x[1] or x[2].strip()=='' or "http://" in x[2] or "止损" in x[2] or "赌" in x[2] or "日晖" in x[2] or "游客uOi1" in x[1] or "不要等到错过今天的机会" in x[2] or "测试" in x[2] or "原油" in x[1] or "微信" in x[2] or "qq" in x[2] or "QQ" in x[2]:
            pass
        else:
            dict_list.append(dict(zip(['time','name','message'],x)))
    global DICT_LIST
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" 前端数据接收成功！")  #临时注销，方便观察输出

    DICT_LIST=dict_list
    #print("原始消息")
    #print(dict_list)
    return "ok"
#从全局变量获取抓取到的日晖聊天室消息，并发送给91聊天室。
def get_chat_room_message():
    #print("get_chat_room_message")
    #print(DICT_LIST)
    current_date=datetime.now().strftime("%Y-%m-%d")  #当前日期
    prev_date=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")  #昨天日期
    current_time=datetime.strptime(datetime.now().strftime("%H:%M:%S"),"%H:%M:%S") #当前时间
    #print(prev_date)
    #给聊天室抓回来的消息加上准确的时间，这一行为的目的并非要解决真正的消息排序，而是仅仅为了解决早上发消息会排在第一天抓取到的晚上的消息的前面的bug。
    # 以前的格式是：【消息显示的时间，发消息的人的名字，消息内容】
    #在末尾增加一列精确的时间，这个时间由消息显示的时间和当前时间比对后得出，比对的原则如下;
    #聊天室抓取到的消息是已经排序过的，最晚的消息在数组的末尾。我们就迭代这个数组，从最后一个元素开
    # 始和当前时间比对，如果比当前时间早，那就把最后一个消息的精确时间设为  当天的日期+消息的时间。如果消息时间比当前时间晚，那就是 当前日期-1天+消息时间
    #
    global DICT_LIST
    if len(DICT_LIST)!=0:
        atime=datetime.strptime(DICT_LIST[len(DICT_LIST)-1]["time"],"%H:%M:%S")
        compare_time=atime  #定义一个用于每条记录的时间变量 时间类型，此变量将会在每次比对后被更新。
        delta=atime-current_time  #时间差，如果为负值就是抓取消息的最后一条的时间比当前时间早，那就可以把最后一条消息的日期设置为current_date，如果是正直，那就是最后一条消息的时间比当前时间晚，那就把最后有一条消息的日期设置为current_date-
        if delta.total_seconds()<=0:
            last_message_date=datetime.strptime(current_date+" "+DICT_LIST[len(DICT_LIST)-1]["time"],"%Y-%m-%d %H:%M:%S")
            compare_date=datetime.now()  #定义一个用于每条记录的日期变量 日期类型，此变量将会在每次比对后被更新。
        else:
            last_message_date=datetime.strptime(prev_date+" "+DICT_LIST[len(DICT_LIST)-1]["time"],"%Y-%m-%d %H:%M:%S")
            compare_date=datetime.now()-timedelta(days=1)  #定义一个用于每条记录的日期变量 日期类型，此变量将会在每次比对后被更新。
        DICT_LIST[len(DICT_LIST)-1].update({"datetime":last_message_date})#给最后一条消息的的记录追加一个键值对。
        for i in range(len(DICT_LIST)-2,-1,-1):  #-2的原因是最后一条数据已经被拿出来做比对了。
            #用每一条消息的时间和最后一条消息的时间做比对，如果是负值，就是日期就和最后一条消息的日期相同，否则，日期就比最后一条消息的日期早一天
            temp_time=datetime.strptime(DICT_LIST[i]["time"],"%H:%M:%S")
            if (temp_time-compare_time).total_seconds()<0:
                pass
            else:
                compare_date=compare_date-timedelta(days=1) #更新用于比对的日期
            temp_datetime=datetime.strptime(compare_date.strftime("%Y-%m-%d")+" "+DICT_LIST[i]["time"],"%Y-%m-%d %H:%M:%S")  #这条消息的精确时间就等于用于比对的日期+消息的时间.
            DICT_LIST[i].update({"datetime":temp_datetime})
            #delta=atime-ctime  #时间差，如果为负值就是atime比较早,还要继续往前找更早的
    #print(DICT_LIST)
    # f=open("ChartRoom_log"+str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day)+".txt",mode="a",encoding="utf-8")   #日志
    # print(datetime.now(),file=f)
    # for x in DICT_LIST:
    #     print(x,file=f)
    # f.close()
    return DICT_LIST.copy()
#get_chat_room_message()
