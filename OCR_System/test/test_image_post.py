# -*-coding:utf8-*-
import os
import requests

url = "http://0.0.0.0:7999/2"
dir = "/home/walle/下载/redirect/项目需求/万达/上海医疗发票300dpi"
for i, file_name in enumerate(os.listdir(dir)):
    file_path = os.path.join(dir, file_name)
    headers = {"image_sn": i}
    files = {"file": open(file_path, "rb")}
    r = requests.post(url, files=files)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)