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


def send_mail(to_mail, title, content):
    smtpserver = 'smtp.exmail.qq.com'
    imapserver = 'imap.exmail.qq.com'
    from_addr = 'justice.hong@e-ai.com.cn'
    password = '246642Ok'

    to_addr = to_mail

    mm = MySendMail(smtpserver)
    mm.send_mail(from_addr, password, to_addr, subject=title,  msg=content)
    mm.quit()


if __name__ == '__main__':
    send_mail("lijie.xu@e-ai.com.cn", "title","content")