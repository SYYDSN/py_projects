# -*- coding: utf-8 -*-
import requests
import json


def send_message(method: str = 'get', data: dict = None) -> None:
    url = "http://127.0.0.1:7011/test"
    data = {"hello": "world"} if data is None else data
    if method.lower() == "get":
        r = requests.post(url=url, json=data)
    else:
        r = requests.post(url=url, json=data)
        pass
    print(r.text)


if __name__ == "__main__":
    send_message()
    pass