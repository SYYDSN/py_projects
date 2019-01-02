#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests
from uuid import uuid4



"""极光的推送模块"""


AUTH = "MDIxMzFjYzA5OWU5NGYwNzQxN2QwOWE5OjZmNzA3ZmZlMzVmNzZjOTZjMmQ3YWQ3Mw=="
headers = {"Authorization": "Basic {}".format(AUTH)}


def push_mes(alert: str, title: str, url: str, cid: str = None, platform: (dict, None) = None, tags: (dict, None) = None) -> dict:
    """
    构建发送参数字典并推送消息
    :param alert:  内容摘要
    :param title:  消息标题
    :param url:  消息链接
    :param cid:  防止重复的消息的唯一性id
    :param platform:  {"platform": ["ios","android"]}/"all"
    :param tags:
                {"tag": ["深圳","北京", ...]}
                {"tag": ["all"]}
                {"registration_id": [registration_id1,registration_id2, ...]}
    :return:
    """
    mes = {"message": "success"}
    platform = "all" if platform is None else platform
    tags = "all" if tags is None else tags
    args = {
        "platform": platform,
        "audience": tags,
        "notification": {
            "android": {
                "alert": alert,
                "title": title,
                "builder_id": 1,
                "large_icon": "http://www.jiguang.cn/largeIcon.jpg",
                "extras": {
                    "HTTPURL": url,
                }
            },
            "ios": {
                "alert": alert,
                "sound": "default",
                "badge": "+1",
                "thread-id": "default",
                "extras": {
                    "HTTPURL": url,
                }
            }
        },
        "options": {
            "time_to_live": 60
        }
    }
    if isinstance(cid, str) and len(cid) >= 32:
        args['cid'] = cid
    else:
        pass
    u = "https://api.jpush.cn/v3/push"
    r = requests.post(url=u, json=args, headers=headers)
    print(r)
    return mes


if __name__ == "__main__":
    uid = uuid4().hex
    tags = {"registration_id": ["170976fa8ad9fd6f9ad"]}
    push_mes(alert="hello world", title="my title", url="http://www.middear.cn")
    pass
