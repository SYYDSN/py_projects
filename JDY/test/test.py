import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from item_module import Customer
from item_module import ObjectId


def batch_reg():
    """批量注册"""
    for i in range(10):
        args = {
            "_id":ObjectId(),
            "search_keyword": "迅迭 测试",
            "user_name": "王满石",
            "group_count": 0,
            "page_url": "http://qhrj.sxzctec015.cn/20180719gjs/index.html?channel=360A-pc-hqrj-byds",
            "description": "页面标题:",
            "referrer": "https://www.so.com/s?ie=utf-8&src=hao_360so_suggest_b&shb=1&hsid=fc569f7380160a98&eci=407b847fad15303c&nlpv=suggest_3.2.2&q=%E5%8D%9A%E5%BC%88%E5%A4%A7%E5%B8%88%E5%AE%98%E7%BD%91%E4%B8%8B%E8%BD%BD",
            "group_by": "0",
            "phone": [
                "19972{}47964".format(i)
            ],
            "user_agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "time": "2018-12-12 0:0:0"
        }
        Customer.reg(**args)


if __name__ == "__main__":
    batch_reg()
    pass