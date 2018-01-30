#!python
#-*- coding:utf-8 -*-
import requests
import json,os


def req():
    author = "8af044f186374563b30dfd5f3da2b5e3"
    headers = {
        "author":author,#token
        "debug":"1"#是否是测试
    }
    batch_info={"file4.zip":"ccccc","file5.zip":"dddddd","file6.zip":"eeeeeee"}
    batch_info = {"picc22332343434.zip": "06a9d348616dd320b9de9a55703dba6c"}

    print(batch_info)
    url1 = "http://192.168.116.15:8000/message/upload_success"
    url2 = "http://113.108.9.33:8000/message/upload_success"
    url3 = "http://113.108.9.33:8100/message/upload_success"
    url4 = "http://127.0.0.1:8000/message/upload_success"
    r = requests.post(url=url2, data=batch_info,headers=headers)
    print(r.json(),r.status_code)



if __name__ == "__main__":
    req()