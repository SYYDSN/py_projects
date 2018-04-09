#  -*- coding: utf-8 -*-
import requests


sign = '1cccca0e35ee476fb1d9b1097017e1a2'
app_id = '61413'
plateNumber = '赣CX3963'
engineNo = '1416C016063'
vin = 'LG6ZDCNH5GY203349'
preCarNum = '赣C'


def query_rule():
    url = 'http://route.showapi.com/1399-3'
    args = {
        'showapi_appid': app_id,
        "showapi_sign": sign,
        "province": "江西",
        "preCarNum": preCarNum
    }
    r = requests.post(url, data=args)
    if r.status_code == 200:
        print(r.json())
        """
        成功后返回
        {
            'showapi_res_code': 0, 'showapi_res_error': '', 
            'showapi_res_body': {
                'msg': '查询成功!', 'ret_code': '0', 'data': [
                                                            {
                                                                'carEngineLen': 6, 'province': '江西', 
                                                                'carCodeLen': 0, 'cityName': '宜春市', 
                                                                'preCarNum': '赣C'
                                                            }
                                                            ]
            }
        }
        """
    else:
        print(r.status_code)


def query_vio():
    url = 'http://route.showapi.com/1399-2'
    args = {
        'showapi_appid': app_id,
        "showapi_sign": sign,
        "carNumber":  plateNumber,
        "carCode": vin,
        "carEngineCode":engineNo
    }
    r = requests.post(url, data=args)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)


if __name__ == "__main__":
    query_vio()