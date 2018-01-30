# -*- coding:utf-8 -*-
import requests
import json


"""供应商上传"""


headers = {"headers": "dc2b52ea0eee4ccab75cb4f3e047d0c1"}
data = {"case_name": "PICC20170630002",
        "batch_sn": 32,
        "image_info": [
            {"image_name": "00000298AI20160324018.jpg",
             "image_type": "门急诊",
             "zone": "上海",
             "h_name": "复旦大学附属儿科医院"}
        ]}

url = "http://113.108.9.33:8000/result/save"

r = requests.post(url, data={"data": json.dumps(data)}, headers=headers)
if r.status_code == 200:
    print(r.json())
else:
    print(r.status_code)