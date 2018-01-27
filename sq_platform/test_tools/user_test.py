# -*-coding:utf-8-*-
from api.data.item_module import CarLicense
import mongo_db
from bson.objectid import ObjectId


def add_vio_query_generator():
    """添加一个违章查询器"""
    """
    plate_number 车牌 必须
    engine_id  发动机号 必须
    vin_id  车架号   
    car_type 车型 大车小车
    user_id  用户id
    city    c城市
    """
    args = {"plate_number": "沪A12345", "engine_id": "Y123456",
            "vin_id": "041378", "city": "上海",
            "user_id": ObjectId("597eed50de713e34eb2fd6ae")}
    args = {"plate_number": "沪A12345", "engine_id": "Y123456",
            "vin_id": "041378", "city": "上海", "token": "94004e1cac3f4600b754316bb87d34dc"}


def add_car_license():
    """添加行驶证信息"""
    """
    通过添加违章查询器增加的行驶证记录，一般只会有2-4条信息
    plate_number 车牌 必须
    engine_id  发动机号 必须
    vin_id  车架号   
    car_type 车型 大车小车
    """
    args = {"plate_number": "沪A12345", "engine_id": "Y123456",
            "vin_id": "041378"}
    result = CarLicense.find_one_and_insert(**args)
    return result


if __name__ == "__main__":
    print(add_car_license())
