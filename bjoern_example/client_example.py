#  -*- coding: utf-8 -*-
import requests
from uuid import uuid4


"""client example"""


def example(url: str) -> None:
    token = uuid4().hex
    # headers = {"auth-token": token}  # success
    headers = {"auth_token": token}  # error
    r = requests.post(url=url, headers=headers)
    print(r.json())


if __name__ == "__main__":
    example("http://127.0.0.1:5000/token")
    example("http://127.0.0.1:6000/token")
    pass