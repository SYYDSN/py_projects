# -*- encoding: utf-8 -*-
__author__ = 'Administrator'

import requests, json
import pymssql
import datetime

conn = pymssql.connect(host='121.42.204.235', user='sa', password='SHxdkj2015', database='jy_db', charset='utf8')
cursor = conn.cursor()
yesterday = datetime.datetime.now() - datetime.timedelta(days=3)
yesterday_str = str(yesterday.year) + "-" + str(yesterday.month) + "-" + str(yesterday.day)
sql = "select 'phone' as [from],c_phone as number, '无' as name,c_date as get_date,'http://'+CRM_Website.w_url as URL_ID,c_url as info from CRM_customer_phone,CRM_Website where convert(date,c_date)='{0}'  and c_site_id=w_id union select 'QQ' as [from],c_qq as number," \
      "c_nike as name,c_date as get_date,'http://'+CRM_Website.w_url as URL_ID,c_url as info from CRM_customer_qq,CRM_Website where convert(date,c_date)='{0}' and c_site_id=w_id union select 'user' as [from],u_MobilePhone as number,u_Name as name,u_CreateTime " \
      "as get_date,u_RegisteredQuote as URL_ID,'null' as info from userinfo where convert(date,u_CreateTime)='{0}'".format(yesterday_str)
cursor.execute(sql)
raw=cursor.fetchall()
astr="<table><tr><tH>类别</th></th>号码</th></th>名字/昵称</th></th>获取时间</th></th>入口地址</th></tr>"
count=1
for x in raw:
    count+=1
    temp="<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>".format(x[0],x[1],x[2],x[3].strftime("%Y-%m-%d %H:%M:%S"),x[4])
    astr+=temp
astr+="</table>"
print(astr)
################################################
url = "http://sendcloud.sohu.com/webapi/mail.send_template.json"

# 不同于登录SendCloud站点的帐号，您需要登录后台创建发信子帐号，使用子帐号和密码才可以进行邮件的发送。
params = {"api_user": "justonlyyo_test_wvJpWL", \
          "api_key": "38DrPXtlwvTI6vc3", \
          "from": "admin@91dashi.cn", \
          "fromname": "注册信息", \
          "to": "15321355@qq.com", \
          "template_invoke_name":"send_reg_user_91",
          "subject": "注册信息", \
          "html": "hell", \
          "resp_email_id": "true"
          }

r = requests.post(url, files={}, data=params)
print(r.text)
