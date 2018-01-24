# -*- encoding: utf-8 -*-
#ip安全工具包
__author__ = 'Administrator'
import my_sql
class ip_tools:
    def __init__(self):
        self.ip_list=[]
        self.black_ip_list=[]
    def check_guest_id_ip(self,guest_id,ip):#第一步检测匿名ip和访问ip是否匹配？ip必须和guest_action_recode表中的最后一次访问的ip一致，此举用来防止用机器注册但是没有模仿cookie中的guest_id的非法注册行为
        conn=my_sql.get_conn()
        cursor=conn.cursor()
        sql="select top 1 Guest_id,Ip from guest_action_recode where Event_type='open_page' and Guest_id={0} order by Event_Date desc".format(guest_id) #返回【匿名id,最后一次打开页面时的ip】
        cursor.execute(sql)
        raw=cursor.fetchone()
        if raw is None:
            return False
        else:
            return True if int(guest_id)==raw[0] and str(ip)==raw[1] else False

print(ip_tools().check_guest_id_ip(443,'127.0.0.1'))