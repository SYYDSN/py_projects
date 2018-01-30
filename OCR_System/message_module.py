# -*- coding:utf-8 -*-
import user_group_module
import requests
import db_module
import batch_module
import req_module
from request_module import get_customer_sn
from mail_module import send_mail

cache = db_module.cache
inner_author = "a38dfe37a4964e8890a86806d37a3f68"  # 内部通讯用author


"""消息处理中心"""


def __message(the_type, group_sn, ip, args_dict):
    message = {"message": "success"}


def check_author(author, the_type):
    """
    根据author检查用户的请求是否合法
    :param author:   请求的author
    :param the_type:   请求的类型
    :return:   布尔值
    """
    res = False
    author = author.strip(" ")
    author = author.strip("\n")
    print("begin|{}|end".format(author))
    if the_type == "upload_success":
        res = user_group_module.check_author(author)
    elif the_type in ["md5_error", "zip_error", "ocr_finish", "to_supplier_ftp"]:
        if author == inner_author:
            res = True
    return res


def message_listen(**kwargs):
    """消息响应"""
    message = {"message": "success"}
    the_type = kwargs.pop("the_type")
    author = kwargs.pop("author")

    if not check_author(author, the_type):
        message["message"] = "authorization error"
        return message
    else:
        if author == inner_author:
            """内部通讯的情况"""
            if the_type == "zip_error":
                """sftp服务器发来解压缩失败的消息"""
                request_sn = kwargs.get("request_sn")
                if request_sn is None:
                    pass
                else:
                    customer_sn = get_customer_sn(request_sn)
                    if customer_sn is None:
                        pass
                    else:
                        title = "批次压缩包解压失败"
                        content = "{} 批次压缩包解压失败，请重新上传此压缩包".format(kwargs("batch_name"))
                        send_mail("customer", customer_sn, title, content)  # 向用户发送通知邮件
            elif the_type == "to_supplier_ftp":
                """接收sftp发来的已拷贝给供应商的批次名 sftp-》运行平台，由于目前供应商采取轮询制，所以暂不处理"""
                pass
            elif the_type == "ocr_finish":
                """ocr服务器发来的ocr处理结束的命令,ocr-》运营平台"""
                image_sn = kwargs.get("image_sn")
                result = ocr_finish(image_sn)  # 当前image对应的批次下的所有image是否都已处理完毕？
                print("result:", end='')
                print(result)
                if result:  # 如果当前image所在的批次的所有图片批次都已经处理完了
                    url = "http://113.108.9.34:8001/message/transfer_zip"
                    """根据batch_sn获取supplier_sn，临时方案"""
                    customer_sn = batch_module.get_customer_sn(result)
                    if customer_sn is None:
                        print("批次 {} 没有找到对应的customer_sn".format(result))
                    else:
                        supplier_sn = 9 if customer_sn == 2 else 8
                        """通知sftp服务器拷贝此批次给供应商"""
                        res = requests.post(url, data={"batch_sn": result, "supplier_sn": supplier_sn})  # 临时方案
                        print(res.status_code)
                        print(res.json())
        else:
            """用户和供应商的通讯"""
            try:
                group_sn, ip, server_sn = user_group_module.get_server_ip(author)
            except ValueError:
                message['message'] = "author验证失败"
            if message['message'] != "success":
                pass
            else:
                if the_type == "upload_success":
                    """用户上传文件完毕发送的检查批次文件的请求"""
                    url = "http://113.108.9.34:8001/message/pretreatment"  # 临时方案
                    # url = "http://{0}:{1}/message/pretreatment".format('192.168.116.25', '8001')  # 内网调试用
                    if len(kwargs) == 0:
                        message['message'] = "没有发现批次信息"
                    else:
                        request_sn = batch_module.exist(kwargs, group_sn)  # 批次信息被写入
                        print("request_sn is {}".format(request_sn))
                        if request_sn == 0:
                            message['message'] = "重复的批次"
                        else:
                            data = {"request_sn": request_sn}
                            req_sn = req_module.begin(server_sn, url, data)
                            """向sftp服务器发送开始检查md5的命令"""
                            """临时测试"""
                            # url = "http://127.0.0.1:8001/message/pretreatment"
                            res = requests.post(url, data=data)
                            if res.status_code == 200:
                                message = res.json()  # 直接把结果返回给用户
                                batch_module.close_request_recode(request_sn)
                                req_module.end(req_sn, message)
                            else:
                                message['message'] = 'sftp服务器出现错误'
                else:
                    message['message'] = "未识别的请求"
    return message


def all_image_ocred(batch_sn):
    """根据批次号，判断此批次下所有的图片是否都ocr了？
    全部ocr过就返回0. 否则返回剩余未ocr的图片的数目
    """
    sql = "select count(1) from image_info where is_ocred=0 and batch_sn={}".format(batch_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    count = 0
    if raw is None:
        pass
    else:
        count = raw[0]
    return count


def ocr_finish(file_sn):
    """根据图片的sn检查此文件属的批次的全部文件是否已处理完毕
    处理完毕返回返回批次号，没有处理完毕返回False
    """
    ses = db_module.sql_session()
    sql = "select batch_sn from image_info where " \
          "image_sn={}".format(file_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    print(raw)
    ses.close()
    if raw is not None:
        batch_sn = raw[0]
        result = all_image_ocred(batch_sn)
        if result == 0:
            return batch_sn
        else:
            return False
    else:
        return False


def check_lost():
    """启动时检查是否有错误的回应"""
    tasks = req_module.check()
    for task in tasks:
        res = requests.post(task['command'], data=task['request_message'])
        if res.status_code == 200:
            resp = res.json()
            req_module.end(task['sn'], resp)


def send_message_customer(customer_sn, customer_url, message_content):
    """向客户发送消息
    customer_sn 是客户的sn，用于确认客户的服务器和端口号
    message_type 是消息类型，由于消息的发送和接收的url_path是一致的，所以这里实际上是url_path
    message
    """


case_info = {
    "base_info": "",
    "cash_count": 200,
    "cash_count": 200,
    "cash_count": 200,
    "cash_count": 200,
    "tickets": [{"ticket_sn": 2323, "zone": "上海", "count": 100},
                {"ticket_sn": 2324, "zone": "上海"}]
}
if __name__ == "__main__":
    # batch_info = {"picc22332343434.zip": "06a9d348616dd320b9de9a55703dba6c"}
    # author = "8af044f186374563b30dfd5f3da2b5e3"
    # the_type = "upload_success"
    # batch_info['the_type'] = the_type
    # batch_info['author'] = author
    # import requests
    #
    # data = {"request_sn": 18}
    # url = "http://113.108.9.34:8001/message/pretreatment"
    # r = requests.post(url, data=data)
    # print(r.json())
    # print(ocr_finish(12))
    pass