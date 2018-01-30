# -*-coding:utf-8-*-
'''
Created on 2017年2月23日

@author: Administrator
'''

import smtplib
import imaplib
import time, string
from email.message import Message
import email.utils
import db_module
import base64

ttime = email.utils.formatdate(time.time(), True)


class MySendMail:
    def __init__(self, smtpserver, port=587, timeout=20):
        sm = smtplib.SMTP(smtpserver, port=port, timeout=timeout)
        # sm.set_debuglevel(1)
        sm.ehlo()
        sm.starttls()
        sm.ehlo()
        self.__sm = sm

    def __getSendContent(self, from_addr, to_addr, cc_addr=None, subject="邮件主题", msg="", **kargs):
        returnStr = ""
        if not kargs:
            message = Message()
            message['Subject'] = subject
            message['From'] = from_addr
            message['To'] = ",".join(to_addr)
            if cc_addr:
                message['Cc'] = ",".join(cc_addr)
            message.set_payload(msg)
            message.set_charset("utf-8")
            returnStr = message.as_string()
        return returnStr

    def send_mail(self, from_addr, password, to_addr, cc_addr=None, subject="邮件主题", msg="", **kargs):
        self.__sm.login(from_addr, password)
        to_addrList = []
        if type(to_addr) is not list:
            to_addr = [to_addr]
        to_addrList.extend(to_addr)
        if cc_addr != None and type(cc_addr) != list:
            cc_addr = [cc_addr]
        if cc_addr:
            to_addrList.extend(cc_addr)
        msg = self.__getSendContent(from_addr, to_addr, cc_addr=cc_addr, subject=subject, msg=msg, **kargs)
        # print msg
        self.__sm.sendmail(from_addr, to_addrList, msg)
        # print "发送成功"

    def quit(self):
        self.__sm.quit()


class MyRecvMail:
    def __init__(self, imapserver, user, password, port=993):
        im = imaplib.IMAP4_SSL(imapserver, port)
        im.login(user, password)
        self.__im = im
        self.__fileList = []
        for one in self.__im.list()[1]:
            fileName = one.split("\"")[-2]
            # print fileName
            # print base64.b64encode("我的文件夹")
            self.__fileList.append(fileName)

    def getEmail(self, floder="INBOX"):
        if floder not in self.__fileList:
            raise Exception("not this floder in mailbox")
        self.__im.select(floder)
        typ, data = self.__im.search(None, 'UNSEEN')  # Recent ALL
        # print typ,data
        for num in string.split(data[0]):
            # print num
            try:
                typ, data = self.__im.fetch(num, '(UID BODY.PEEK[])')  # HEADER.FIELDS(SUBJECT)
                msg = email.message_from_string(data[0][1])
                # print msg
                # time.sleep(10)
                # 获取主题
                subject = msg.get("Subject")
                try:
                    h = email.Header.Header(subject)
                    h = email.Header.decode_header(h)
                    subject = "".join([x[0] for x in h]).decode(h[-1][1])
                except Exception as e:
                    subject = subject.decode("gb2312")
                    # print typ,subject.encode("utf-8")
                    # 获取内容
                    # print extract_body(msg.get_payload(decode=True)),"\n\n"

            except Exception as e:
                print(e)


def __send_mail(to_mail, title, content):
    """发送通知邮件。
            title   邮件标题
            content   邮件正文
    """
    smtpserver = 'smtp.exmail.qq.com'
    imapserver = 'imap.exmail.qq.com'
    from_addr = 'justice.hong@e-ai.com.cn'
    password = '246642Ok'

    to_addr = to_mail

    mm = MySendMail(smtpserver)
    mm.send_mail(from_addr, password, to_addr, subject=title,  msg=content)
    mm.quit()


def __get_email_url(the_type, sn):
    """获取客户的通知邮件
    the_type 客户类型，customer代表客户，supplier代表供应商。
    sn group_sn
    return  通知邮件地址
    """
    table_name = "user_group_info"
    if the_type == "customer":
        pass
    elif the_type == "supplier":
        table_name = "supplier_group_info"
    else:
        raise TypeError("错误的类型：{}".format(the_type))
    sql = "select info_email from {} where group_sn={}".format(table_name, sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        raise ValueError("没有获取到通知邮件")
    else:
        result = raw[0]
        return result


def send_mail(the_type, the_sn, title, content):
    """向客户发送邮件
    the_type 客户类型customer代表客户，supplier代表供应商。
    the_sn   customer或者supplier的group_sn
    title     邮件标题
    content    邮件正文
    return None
    """
    message = {"message": "success"}
    try:
        mail_url = __get_email_url(the_type, the_sn)
        __send_mail(mail_url, title, content)
    except Exception:
        message['message'] = "没有找到对应的通知邮件地址"
    finally:
        return message


if __name__ == '__main__':
    __send_mail("lijie.xu@e-ai.com.cn", "title","content")