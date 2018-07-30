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
from io import BytesIO


ObjectId = mongo_db.ObjectId


"""爬虫模块"""


class VegetableImage(mongo_db.BaseFile):
    """蔬菜图片"""
    _table_name = "vegetable_image"


class Vegetable(mongo_db.BaseDoc):
    """
    蔬菜
    """
    _table_name = "vegetable"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str  # 蔬菜的名字
    type_dict['desc'] = str  # 蔬菜的备注
    type_dict['url'] = str  # 蔬菜的链接
    type_dict['description'] = str
    type_dict['data'] = ObjectId  # VegetableImage._id
    type_dict['time'] = datetime.datetime

    @classmethod
    def analysis_url(cls) -> None:
        """
        分析网站,取出所有蔬菜的链接,存入数据
        :return:
        """
        u = "https://www.meishichina.com/YuanLiao/category/shucailei/"
        r = requests.get(u)
        q = pyquery.PyQuery(r.content.decode())
        m = q.find(".mt20 > .clear")
        now = datetime.datetime.now()
        for x in m:
            ul = x.find("ul")
            ls = ul.findall("li")
            for a in ls:
                temp = dict()
                a = a.find("a")
                temp['name'] = a.text
                href = a.attrib['href']
                if href.startswith("http"):
                    temp['url'] = href
                else:
                    temp['url'] = "https:{}".format(a.attrib['href'])
                temp['time'] = now
                print(temp)
                obj = cls(**temp)
                obj.save_plus()

    @classmethod
    def find_image(cls, obj) -> None:
        """
        根据网址，找到一个蔬菜的图片和说明，存入数据库
        :param url:
        :return:
        """
        headers = {
            "accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"
        }
        data = obj.get("data")
        if isinstance(data, ObjectId) or data == "" or data == "not found":
            pass
        else:
            url = obj['url']
            if url.endswith("/"):
                u = "{}tiyan".format(url)
            else:
                u = "{}/tiyan".format(url)
            q = pyquery.PyQuery(requests.get(u, headers=headers).content.decode())
            desc = q.find(".mt10:eq(1)").text()
            blog = q.find(".blog_message")
            img = blog.find("img")
            src = img.attr("src")
            if src is None:
                f = {"_id": obj['_id']}
                u = {"$set": {"data": "", "desc": desc}}
                r = cls.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
            else:
                resp_img = None
                try:
                    resp_img = requests.get(src, headers=headers, timeout=10)
                except requests.exceptions.ConnectTimeout as e:
                    print(src)
                    print(e)
                finally:
                    if resp_img is None:
                        f = {"_id": obj['_id']}
                        u = {"$set": {"data": "not find", "desc": desc}}
                        r = cls.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
                    else:
                        file = BytesIO(initial_bytes=resp_img.content)
                        r = VegetableImage.save_cls(file_obj=file, name=obj['name'], description=desc)
                        f = {"_id": obj['_id']}
                        u = {"$set": {"data": r, "desc": desc}}
                        r = cls.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
                        print(r)

    @classmethod
    def call_back(cls, item: dict) -> dict:
        """
        分页查询的回调函数，详见mongo_db.BaseDoc.query_by_page对func参数的解释
        :param item:
        :return:
        """
        item['img_url'] = "/img/file/view/vegetable_image?fid={}".format(str(item['data']))
        return item





if __name__ == "__main__":
    # Vegetable.analysis_url()  # 获取所有的蔬菜的url
    f = dict()
    vegetables = Vegetable.find_plus(filter_dict=f, to_dict=True)
    for vegetable in vegetables:
        Vegetable.find_image(vegetable)
    pass
