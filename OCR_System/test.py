# -*-coding:utf8-*-
import json
import requests
data = {
    "author": 0,
    "batch_sn": 1,
    "data": json.dumps({"image_name": "393010201201602010050030003.jpg",
                    "image_type": "上海地区门急诊", "zone": "上海",
                        "case_name": "case0001",
                        "batch_sn": 1, "supplier_sn": 0,
                    "image_info":[{"image_name": "00000003AI20160324018.jpg"}]})}

url_1 = "http://113.108.9.33:8000/result/save"
headers={"author": 'fac24597548844afafc5b031663b7ffb'}

# res = requests.post(url=url_1, data=data, headers=headers)
# if res.status_code == 200:
#     print(res.json())

url_2 = "http://113.108.9.33:8000/result/query"
oid = 'e7684a6a158f4facbc788877c9e9afeb'
data = {"the_type": "by_oid", "oid": oid}
res = requests.post(url=url_2, data=data, headers=headers)
if res.status_code == 200:
    print(res.json())