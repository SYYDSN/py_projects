#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import requests
import datetime
import json
from log_module import get_logger
from module.spread_module import SpreadChannel


"""简道云对接模块,火狐版，没有问题"""


logger = get_logger()
current_dir = os.path.dirname(os.path.realpath(__file__))
ObjectId = mongo_db.ObjectId


class RegisterLog(mongo_db.BaseDoc):
    """
    向简道云的api写入注册信息的log
    """
    _table_name = "register_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['info'] = dict
    type_dict['time'] = datetime.datetime

    @classmethod
    def send_reg_info(cls, **kwargs) -> bool:
        """
        向简道云发送注册信息
        :param kwargs:
        :return:
        """
        data = dict()
        page_url = kwargs.get('page_url')
        spread_keywords = SpreadChannel.analysis_url(page_url)
        desc1 = ''   # 备注1
        try:
            desc1 = spread_keywords[0]
        except IndexError as e:
            logger.exception("to_jiandao_cloud error!")
        except Exception as e:
            logger.exception("to_jiandao_cloud error!")
            raise e
        finally:
            pass

        desc2 = ''  # 备注2
        try:
            desc2 = spread_keywords[1]
        except IndexError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        finally:
            pass

        desc3 = ''  # 备注3
        try:
            desc3 = spread_keywords[2]
        except IndexError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)
        finally:
            pass
        data['page_url'] = page_url
        data['desc1'] = desc1
        data['desc2'] = desc2
        data['desc3'] = desc3
        customer = kwargs.get('user_name')
        data['customer'] = customer
        phone = kwargs.get('phone')
        data['phone'] = phone
        content = kwargs.get('description')
        data['content'] = content
        search_keyword = kwargs.get('search_keyword')
        data['search_keyword1'] = search_keyword
        group_by = kwargs.get('group_by')
        data['group_by'] = group_by
        cls._send(**data)
        return True

    @classmethod
    def _send(cls, **kwargs) -> dict:
        """
        向简道云注册接口发送注册信息的内部方法
        :param kwargs:
        :return:
        """
        u = "https://www.jiandaoyun.com/api/v1/app/5a658ca3b2596932dab31f0c/entry/5a658cbc7b87e86216236cb2/data_create"
        headers = {
            'Authorization': 'Bearer gavQrjmjxekfyK4qeZAI0usSZmZq0oww',
            'Content-Type': 'application/json;charset=utf-8'
        }
        kw = {k: {"value": v} for k, v in kwargs.items()}
        # kw['creator'] = {'_id': '56956cdcf5377f7d03ff49bc', 'name': '上海迅迭网络科技有限公司', 'username': '测试人员'}
        d ={"data": kw}
        resp = requests.post(u, data=json.dumps(d), headers=headers, verify=False)
        print(resp.json())

    @classmethod
    def _query(cls):
        _id = "56956cdcf5377f7d03ff49bc"


if __name__ == "__main__":
    """测试往简道云写数据"""
    args = {
        "description": "搜索内容: 长江是有交易所↵预算: 0↵营销: 营销3↵水果: 梨子李子↵项目描述: 测试项目",
        "page_url": "http://localhost:63342/projects/index.html?_ijt=22a6gi3e6no6e4dkrnrqsp6q8o",
        "referrer": "",
        "search_keyword": "长江是有交易所",
        "sms_code": "6659",
        "user_name": "测试人员",
        "group_by": "2",
        "phone": 156183217645
    }
    RegisterLog.send_reg_info(**args)
    pass