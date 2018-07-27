# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
import requests
import pyquery


ObjectId = mongo_db.ObjectId


"""爬虫模块"""


class VegetableImage(mongo_db.BaseDoc):
    """
    蔬菜
    """
    _table_name = "vegetable_image"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str
    type_dict['file_type'] = str  # 文件类型
    type_dict['name'] = str  # 蔬菜的名字
    type_dict['desc'] = str  # 蔬菜的备注
    type_dict['url'] = str  # 蔬菜的链接
    type_dict['description'] = str
    type_dict['uploadDate'] = datetime.datetime
    type_dict['length'] = int
    type_dict['chunkSize'] = int
    type_dict['md5'] = str
    type_dict['data'] = bytes

    @classmethod
    def analysis_url(cls) -> list:
        """
        分析网站,取出所有蔬菜的链接,存入数据
        :return:
        """
        u = "https://www.meishichina.com/YuanLiao/category/shucailei/"
        r = requests.get(u)
        q = pyquery.PyQuery(r.content.decode())
        m = q.find(".mt20 > .clear")
        for x in m:
            ul = x.find("ul")
            ls = ul.findall("li")
            for a in ls:
                temp = dict()
                a = a.find("a")
                temp['name'] = a.text
                temp['url'] = "https:{}".format(a.attrib['href'])
                print(temp)
                obj = cls(**temp)
                obj.save_plus()




if __name__ == "__main__":
    VegetableImage.analysis_url()
    pass
