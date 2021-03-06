#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime
from log_module import get_logger
import re


"""推广模块"""


logger = get_logger()


class SpreadKeyword(mongo_db.BaseDoc):
    """推广频道的关键词"""
    _table_name = "spread_keyword"
    type_dict = dict()             # 属性字典
    type_dict['_id'] = mongo_db.ObjectId     # id,唯一
    type_dict['english'] = str     # 英文词汇,唯一
    type_dict['chinese'] = str     # 中文词汇，唯一
    type_dict['create_date'] = datetime. datetime    # 创建时间

    def __init__(self, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(SpreadKeyword, self).__init__(**kwargs)

    @classmethod
    def rebuild_create_date(cls):
        """
        修复创建时间
        :return:
        """
        rs = cls.find_plus(filter_dict={}, to_dict=True)
        for r in rs:
            if "create_date" not in r:
                r['create_date'] = r['_id'].generation_time
                x = cls(**r)
                x.save_plus()

    @classmethod
    def get_word(cls, english: str) -> str:
        """
        根据英文词汇返回对应的推广关键词
        :param english: 英文词汇
        :return: 中文关键词
        """
        filter_dict = {"english": english.lower()}
        res = cls.find_one_plus(filter_dict=filter_dict, projection=['chinese'])
        return res


class SpreadChannel(mongo_db.BaseDoc):
    """宣传/推广渠道"""

    @classmethod
    def analysis_url(cls, the_str: str) -> list:
        """
        根据url片段来分析使用了哪些频道来推广?
        :param the_str: url
        :return: list/dict
        """
        words = list()
        if the_str is None:
            pass
        else:
            key_str = r'channel=\S+\b'
            pattern = re.compile(key_str)
            mat = pattern.search(the_str)
            if mat is None:
                pass
            else:
                group = mat.group()
                if "&" in group:
                    """说明后面还有其他参数"""
                    group = group.split("&")[0]
                else:
                    pass
                try:
                    group = group.split("=")[1].strip()
                    keys = group.split("-")
                    for key in keys:
                        res = SpreadKeyword.get_word(key)
                        res = '' if res is None else res['chinese']
                        words.append(res)
                except Exception as e:
                    ms = "Error:{}, url: {}".format(e, the_str)
                    logger.exception(ms)
                    raise e
                finally:
                    pass
        return words


class AllowOrigin(mongo_db.BaseDoc):
    """允许跨域注册的域名，域名要待http的"""
    _table_name = "allow_origin_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId  # id 唯一
    type_dict["origin"] = mongo_db.ObjectId  # 域名，理论上唯一
    type_dict['valid'] = bool   # 域名是否有效？

    @classmethod
    def list(cls, only_valid: bool = True) -> list:
        """
        获取允许跨域注册的域名的列表
        :param only_valid:  只包含有效域名？无效的域名也列出？
        :return: 域名列表
        """
        if only_valid:
            filter_dict = {"only_valid": True}
        else:
            filter_dict = {}

        result = cls.find_plus(filter_dict=filter_dict, projection=['origin'])
        return result

    @classmethod
    def allow(cls, origin: str, loosely: bool = True, only_valid: bool = True) -> bool:
        """
        验证一个域名是否允许访问？
        :param origin: 域名
        :param loosely: 宽松模式？如果是宽松模式的，空列表就是全部放行
        :param only_valid: 只包含有效域名？无效的域名也列出？
        :return:
        """
        origins = cls.list(only_valid=only_valid)
        if len(origins) == 0 and loosely:
            return True
        elif origin in origins:
            return True
        else:
            return False


if __name__ == "__main__":
    # SpreadChannel.analysis_url("http://www.91master.cn/zj-jg-zg/meg.html?channel=sg-pc-ziguan")
    # SpreadKeyword.rebuild_create_date()
    # SpreadChannel.analysis_url("http://touzi.jyschaxun.com/20160316wapMt4/index.html?channel=bd-yd-MT4-XUN003338&t=1522223265832")
    pass