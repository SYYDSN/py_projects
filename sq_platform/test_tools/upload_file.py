# -*- coding: utf-8 -*-
import requests


headers_remote = {"auth_token": "b1fd2295fa9c4843a0a1cc1ff20e9c88", "Content-Type": "multipart/form-data"}
headers_local_data = {"auth_token": "814c25d8e1df45e0ab91ef38980664db", "Content-Type": "multipart/form-data"}
headers_local_arg = {"auth_token": "39e7e6c7cc7d448190679bcd27b443fc"}


def upload_file():
    url_local = "http://127.0.0.1:5000/api/add_driving_data"
    url_remote = "http://safego.org:5000/api/add_driving_data"
    # url = "http://127.0.0.1:9000/cc"
    files = {"driving_data": open("/home/walle/work/projects/2017_10_11_18_47_01.zip", 'rb')}
    # r = requests.post(url, files=files, headers=headers)
    # r = s.post(url, files=files,  headers=headers)
    data = {"hello": "world"}
    r = requests.post(url_local, headers=headers_local_arg, files=files)
    print(r.status_code)
    print(r.json())


def input_history():
    url_local = "http://127.0.0.1:5000/api/get_vio_query_history"
    r = requests.post(url_local, headers=headers_local_arg)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)


def upload_image():
    img = "/home/walle/图片/2017-09-20 11-35-13屏幕截图.png"
    files = {"permit_image": open(img, 'rb')}
    url_local = "http://127.0.0.1:5000/api/upload_permit_image"
    r = requests.post(url_local, headers=headers_local_arg, files=files)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)


def test_input_history():
    url_local = "http://safego.org:5000/api/get_vio_query_history"
    r = requests.post(url_local, headers=headers_local_arg)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)


if __name__ == "__main__":
    test_input_history()
