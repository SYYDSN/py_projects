# -*-coding:utf8-*-
import requests
import json


"""消息通知接口客户端示范"""


# 你的通知接口的url，实际使用中，请把<你的sftp账户>部分替换成你的sftp账户名
url = "http://127.0.0.1:8000/message/<你的sftp账户>/"
# author用于身份验证，实际使用中，请把your_author_token>替换成你自己的token文件
author = "<your_author_token>"
# 开始组装请求头
headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:34.0) Gecko/20100101 Firefox/34.0",
                "author": author    # 带上author的值，用于确认请求的合法性
            }
"""
需要发送的文件，这些文件是本次上传完成的批次文件的文件名和对应的压缩包的md5组成的字典
{"file_name_1": "file_md5_1", "file_name_2": "file_md5_2".....}
其中：
file_name_n是指批次压缩包的文件名。
file_md5_n是指此批次压缩包对应的md5,请自行计算，此值用于确认文件的完整性和唯一性。

例如：
batch_info = {"20170520140502_01.zip": "04ae09ee1882522797f5c3247c0588c2"}

"""

batch_info = {"file_01_name": "file_01_md5", "file_02_name": "file_02_md5",
              "file_03_name": "file_03_md5"}

"""
开始发送消息，通知服务商可以开始作业
下面代码的意思是：
向url地址发送一个post请求。
发送的数据是batch_info，
发送的时候带上headers请求头用于校验身份。
"""
res = requests.post(url=url, data=batch_info, headers=headers)
if res.status_code == 200:   # 如果发送成功
    result = res.json(encoding="utf-8")   # 接收返回的信息，注意是json格式的，字符集为utf8
    if result['message'] == 'success':
        print(result['datetime'])  # 请求成功完成,取出作业开始时间
    else:
        print(result['message'])  # 打印错误信息
