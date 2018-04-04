# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
__project_dir = os.path.dirname(os.path.realpath(os.path.realpath(__file__)))
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
import json


"""城市和车牌前缀的对应关系"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class CarCity(mongo_db.BaseDoc):
    """城市和车牌前缀的对应表"""
    _table_name = "car_city_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['prefix'] = str  # 车牌前缀,唯一
    type_dict['city'] = str  # 城市名

    @classmethod
    def get_city(cls, plate_number: str) -> (str, None):
        """
        根据车牌获取归属地
        :param plate_number: 车牌
        :return:
        """
        if plate_number is None:
            return None
        else:
            plate_number = plate_number.lower()
            prefix = plate_number[0: 2]
            f = {"prefix": prefix}
            r = cls.find_one_plus(filter_dict=f, instance=False)
            if r is None:
                return None
            else:
                return r['city']

    @classmethod
    def import_data(cls):
        """导入数据,仅仅在初始化的时候使用"""
        d = os.path.dirname(os.path.realpath(os.path.realpath(__file__)))
        file_path = os.path.join(d, 'source', 'car_city.json')
        f = open(file_path, 'r', encoding="utf-8")
        c = f.read()
        data = json.loads(c)
        f.close()
        res = list()
        name_map = {
            '直系统': None, "青岛增补": "青岛市", "潍坊增补": "潍坊市",
            "崇明、长兴、横沙": "上海市", "天全县车辆管理所": "天全县",
            "格尔木车辆管理所": "格尔木市", "港澳进入内地车辆": None, "南昌,直系统": "南昌市",
            "重庆区（江南）": "重庆市", "重庆区（江北）": "重庆市", "云a-v": None,
            '晋j': "吕梁市"
        }
        new_map = {"闽k": "福州市", "粤z": "香港特别行政区"}
        for x in data:
            cs = x['city']
            for y in cs:
                prefix = y['code'].lower().strip()
                if prefix in new_map:
                    city = new_map[prefix]
                else:
                    city = y['name'].lower()
                    if not city.endswith("市") and not city.endswith("自治州州") \
                            and not city.endswith("区") and not city.endswith("县"):
                        if city in name_map:
                            city = name_map[city]
                        else:
                            city = city.strip() + "市"
                print(prefix, city)
                temp = {"prefix": prefix, "city": city}
                res.append(temp)
        cls.insert_many(res)


if __name__ == "__main__":
    CarCity.import_data()
    pass