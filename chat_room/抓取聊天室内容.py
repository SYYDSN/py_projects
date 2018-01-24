__author__ = 'Administrator'
import threading,time
from datetime import datetime
import urllib.request,threading
from html.parser import HTMLParser

class myHTMLParser(HTMLParser):
    def __init__(self):
        self.title=''
        self.reading_title=0
        HTMLParser.__init__(self)
    def handle_starttag(self,tag,attrs):
        for x in attrs:
            if "id" in x and "Y_PubMes_Div" in x and tag=="div":
                #print(attrs)
                self.reading_title=1
    def handle_data(self,data):
        if self.reading_title:
            self.title+=data
    def handle_endtag(self,tag):
        if tag=="div":
            self.reading_title=0
    def gettitle(self):
        self.title=[x.strip() for x in self.title.split("\r") if x.strip()!=""]

        return self.title

"""
my_parser=myHTMLParser()
req=urllib.request.urlopen("http://www.shiyou8.cn/index.php?fid=1001")
my_parser.feed(req.readall().decode())
for line in my_parser.gettitle():
    print(line)

class myt(threading.Thread):
    def __init__(self):


        threading.Thread.__init__(self)
    def run(self):

        while 1:
            p=myHTMLParser()
            req=urllib.request.urlopen("http://www.shiyou8.cn/index.php?fid=1001")
            p.feed(req.readall().decode())
            for line in p.gettitle():
                print(line)
            time.sleep(1)

t=myt()
t.start()
"""
import httplib2
h=httplib2.Http(".cache")
response,content=h.request("http://www.shiyou8.cn/index.php?fid=1001")
#print(response.status)
#print(content.decode())
while 1:
    my_parser=myHTMLParser()
    response,content=h.request("http://www.shiyou8.cn/index.php?fid=1001")
    my_parser.feed(content.decode())
    print(response.status)
    print( my_parser.gettitle())
    time.sleep(10)