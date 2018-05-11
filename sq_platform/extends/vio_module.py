# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
__project_dir = os.path.dirname(os.path.realpath(os.path.realpath(__file__)))
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
import json
import requests
from log_module import get_logger
import datetime
from mail_module import send_mail
from urllib.request import quote
import warnings


"""违章查询相关类和函数"""


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
interval_seconds = 56400  # 一天的秒
cache = mongo_db.cache
app_key = '7a82b61fbe44748d026802ba64b316db'


class ValidCity(mongo_db.BaseDoc):
    """
    有效的查询城市,由于并非所有的城市都可以进行违章查询.
    所以需要维护一个无效的查询城市的列表,避免过度的浪费查询资源.
    """
    _table_name = "valid_city_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['short_name'] = str         # 区域简称,车牌第一位,汉字.沪,京,赣等
    type_dict['first_letter'] = list             # 车牌第一个字母,可能有多个字符都属于同一个城市.比如沪A,沪C,统一小写
    type_dict['city_name'] = str   # 城市名称,
    type_dict['city_code'] = str   # 城市代码,查询违章的时候用来区域的唯一
    type_dict['province_name'] = str   # 省份名称,
    type_dict['province_code'] = str   # 省份
    type_dict['need_vin'] = bool  # 是否需要车架号?
    type_dict['vin_length'] = int  # 需要几位车架号? 0是全部
    type_dict['need_engine'] = bool  # 是否需要发动机号?
    type_dict['engine_length'] = int  # 需要几位发动机号? 0是全部
    type_dict['valid_date'] = datetime.datetime  # 验证日期
    type_dict['new_power'] = bool  # 是否新能源车?  车牌多一位 翠绿牌
    type_dict['can_use'] = bool  # 此城市是否能查询?
    """
    由于无效的查询城市也可能变成有效的,所以要设置老化期.过了老化期的就重新检查是否有效?
    """

    def __init__(self, **kwargs):
        if "invalid_date" not in kwargs:
            invalid_date = datetime.datetime.now()
            kwargs['invalid_date'] = invalid_date
        if "new_power" not in kwargs:
            kwargs['new_power'] = False
        if "can_use" not in kwargs:
            kwargs['can_use'] = True
        super(ValidCity, self).__init__(**kwargs)

    @classmethod
    def get_cities(cls) -> dict:
        """
        获取有效城市的dict {city_code1:city_name1, city_code2:city_name2,...}
        :return:
        """
        key = cls.get_table_name()
        cities = cache.get(key)
        if cities is None:
            """从数据库查询"""
            now = datetime.datetime.now()
            f = {"can_use": True}
            s = {"valid_date": 1}
            res = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
            if len(res) > 0:
                delta = now - res[0]['valid_date']
                if delta.total_seconds() > 3600:
                    """用了一天了,那就直接刷新"""
                    cls.refresh()
                    res = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
                else:
                    pass
                cities = {x['city_code']: x['city_name'] for x in res}
            else:
                cities = res
                cache.set(key, cities, timeout=60)
        else:
            pass
        return cities

    @classmethod
    def build_plate_city_map(cls) -> dict:
        """
        创建车牌前缀和归属地的映射,注意新能源车
        :return:
        """
        city_list = cls.find_plus(filter_dict=dict(), to_dict=True, can_json=False)
        key = "plate_number_and_city_code_map"
        res = dict()
        for x in city_list:
            first_letter = x['first_letter']
            if len(first_letter) == 0:
                pass
            else:
                short_name = x['short_name']
                city_code = x['city_code']
                city_name = x['city_name']
                need_engine = x['need_engine']
                engine_length = x['engine_length']
                need_vin = x['need_vin']
                vin_length = x['vin_length']
                new_power = x['new_power']
                flag = True if city_name.endswith("新能源") else False  # 是否是新能源车?
                if flag:
                    for y in first_letter:
                        k = short_name + y + "_new"
                else:
                    for y in first_letter:
                        k = short_name + y
                temp = dict()
                temp['city_code'] = city_code
                temp['city_name'] = city_name
                temp['need_engine'] = need_engine
                temp['engine_length'] = engine_length
                temp['need_vin'] = need_vin
                temp['vin_length'] = vin_length
                temp['new_power'] = new_power
                res[k] = temp
        if len(res) == 0:
            timeout = 60
        else:
            timeout = 86400  # 缓存一天
        cache.set(key=key, value=res, timeout=timeout)
        return res

    @classmethod
    def get_plate_city_map(cls) -> dict:
        """
        获取车牌前缀和归属地的映射
        :return:
        """
        key = "plate_number_and_city_code_map"
        res = cache.get(key)
        if res is None:
            res = cls.build_plate_city_map()
        else:
            pass
        return res

    @classmethod
    def augment_plate_city_map(cls, prefix: str, city_info: dict) -> None:
        """
        向车牌前缀和归属地的映射中增加一个读应关系.
        : param prefix:  车牌前两位 比如 沪A /  沪A_new  (新能源车)
        : param city_info:  信息字典,包含城市代码,用于违章查询
        :return:
        """
        key = "plate_number_and_city_code_map"
        the_map = cls.get_plate_city_map()
        the_map[prefix] = city_info
        timeout = 86400  # 缓存一天
        cache.set(key=key, value=the_map, timeout=timeout)

    @classmethod
    def validate_city_code(cls, city_code: str) -> bool:
        """
        验证一个城市是否可以查询?
        :param city_code: city_code
        :return:
        """
        cities = cls.get_cities()
        if city_code in cities:
            return True
        else:
            return False

    @classmethod
    def get_city_code_by_plate_number(cls, plate_number: str) -> dict:
        """
        根据车牌获取对应的城市码
        逻辑如下:
        1. 车牌长度确认是不是新能源车?
        2. 缓存中有就冲缓存取,返回,否则继续下一步.
        3. 从互联网查询.如果查询失败,抛出异常.查询成功,下一步.
        4. 更新数据库,更新缓存. 返回city_code
        :param plate_number: 车牌
        :return:  or dict()
        """
        s_map = [
            "京", "津", "沪", "渝", "蒙", "新", "藏", "宁", "桂", "澳", "港", "黑", "吉",
            "辽", "晋", "冀", "青", "鲁", "豫", "苏", "皖", "浙", "闽", "赣", "湘", "鄂",
            "粤", "琼", "甘", "陕", "贵", "云", "川"
        ]
        plate_number = plate_number.replace(" ", "")
        plate_number.strip()
        if plate_number[0] not in s_map:
            ms = "车牌'{}'前缀错误".format(plate_number)
            logger.exception(ms)
            raise ValueError(ms)
        if len(plate_number) < 7 or len(plate_number) > 8:
            ms = "车牌'{}'长度错误".format(plate_number)
            logger.exception(ms)
            raise ValueError(ms)
        prefix = plate_number[0: 2]
        if len(plate_number) > 7:
            """新能源车"""
            cache_key = prefix + "_new"
        else:
            cache_key = prefix
        the_map = cls.get_plate_city_map()
        result = the_map.get(cache_key)
        res = dict()
        if result is None:
            """
            没有对应的数据,需要从接口查询, 注意,有可能有不支持的城市或者查询失败.
            目前没有处理这种意外.
            """
            ms = "从聚合数据接口查询车牌前缀和城市代码的对应关系,有可能有不支持的城市或者查询失败的情况.目前没有处理这种意外."
            warnings.warn(ms)
            info = cls.query_city_by_plate_number(plate_number)
            """
            info's example:
                            temp['city_code'] = city_code
                            temp['city_name'] = city_name
                            temp['need_engine'] = need_engine
                            temp['engine_length'] = engine_length
                            temp['need_vin'] = need_vin
                            temp['vin_length'] = vin_length
                            temp['new_power'] = new_power
            """
            """这里应该有一个异常处理的逻辑和处理"""
            if isinstance(info, dict):
                res = info.copy()
                """保存进缓存"""
                cls.augment_plate_city_map(prefix=cache_key, city_info=info)
                """保存进数据库"""
                city_code = info.pop('city_code')
                f = {"city_code": city_code}
                u = {"$set": info}
                r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
            else:
                pass
        else:
            res = result
        return res

    @classmethod
    def query_city_by_plate_number(cls, plate_number: str) -> (dict, None):
        """
        根据车牌,从聚合数据查询归属地的信息.
        :param plate_number:
        :return:
        例子:
        {
            "reason":"查询成功",
            "result":{
                "city_name":"宜春",
                "city_code":"JX_YICHUN_J",
                "abbr":"赣C",
                "engine":"1",
                "engineno":"6",
                "classa":"1",
                "classno":"6",
                "province":"江西"
            },
            "error_code":0
        }
        """
        p = plate_number[0: 2]
        p = quote(p, encoding="utf-8")
        is_new = 0 if len(plate_number) == 7 else 1  # 是否能能源车?
        u = "http://v.juhe.cn/sweizhang/carPre?hphm={}&isNer={}&key={}".format(p, is_new, app_key)
        r = requests.get(url=u)
        status_code = r.status_code
        if status_code != 200:
            ms = "查询聚合数据的违章查询直连接口的车牌和城市的对应关系时出错,服务器返回了错误代码:{}".format(status_code)
            logger.exception(ms)
            print(ms)
            title = "{}聚合数据接口出错".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            send_mail(title=title, content=ms)
            raise ValueError(ms)
        else:
            r = r.json()
            if r['reason'] == "查询成功":
                temp = r['result']
                res = dict()
                res['city_code'] = temp['city_code']
                res['city_name'] = temp['city_name']
                res['need_vin'] = bool(int(temp['classa']))
                res['need_engine'] = bool(int(temp['engine']))
                res['vin_length'] = int(temp['classno'])
                res['engine_length'] = int(temp['engineno'])
                res['new_power'] = bool(is_new)
                return res
            else:
                ms = "询直连接口的车牌和城市的对应关系时返回了出错信息:{}".format(r)
                logger.exception(ms)
                raise ValueError(ms)

    @classmethod
    def read_data_from_file(cls) -> list:
        """
        从文件中读取数据,用于在离线情况下初始化的辅助函数.
        :return:
        """
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'source')
        file_path = os.path.join(dir_path, "can_query_cities.json")
        with open(file_path, mode="r", encoding="utf-8") as f:
            data = json.loads(f.read())
        data = data['result']
        return data

    @classmethod
    def batch_create(cls, raw: list) -> list:
        """
        根据从文件中读取/从互联网接口获取的原始数据的数组,批量生成doc(没有_id)
        :param raw:
        :return: dict的数组
        """
        res = list()
        now = datetime.datetime.now()
        for x in raw:
            province_name = x['province']
            province_code = x['province_code']
            for y in x['citys']:
                temp = dict()
                city_name = y.get("city_name")
                need_vin = y.get("class")
                need_vin = False if need_vin is None else (bool(int(need_vin)))
                need_engine = y.get("engine")
                need_engine = False if need_engine is None else (bool(int(need_engine)))
                temp["province_name"] = province_name
                temp["province_code"] = province_code
                temp['short_name'] = y.get("abbr")
                temp['first_letter'] = list()
                temp['city_name'] = city_name
                temp['city_code'] = y.get("city_code")
                temp['need_vin'] = need_vin
                temp['vin_length'] = int(y.get("classno"))
                temp['need_engine'] = need_engine
                temp['engine_length'] = int(y.get("engineno"))
                temp['valid_date'] = now
                temp['new_power'] = True if city_name.endswith("新能源") else False
                temp['can_use'] = True
                res.append(temp)
        return res

    @classmethod
    def refresh(cls):
        """
        从聚合数据提供的接口,刷新可用城市列表
        :return:
        """
        u = "http://v.juhe.cn/sweizhang/citys?province=&dtype=&key={}".format(app_key)
        r = requests.get(url=u)
        status_code = r.status_code
        if status_code != 200:
            ms = "查询聚合数据的违章查询直连接口的支持城市时出错,服务器返回了错误代码:{}".format(status_code)
            logger.exception(ms)
            print(ms)
            title = "{}聚合数据接口出错".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            send_mail(title=title, content=ms)
        else:
            raw = r.json()['result']
            instances = cls.batch_create(raw)
            old_list = cls.find_plus(filter_dict=dict(), to_dict=True, can_json=False)
            old_dict = {x['city_code']: x for x in old_list}
            old_keys = old_dict.keys()
            for instance in instances:
                city_code = instance['city_code']
                if city_code in old_keys:
                    """数据库已存在的城市记录,需要比对"""
                    temp = old_dict[city_code]
                    instance['_id'] = temp['_id']
                    instance['first_letter'] = temp['first_letter']
                    old_dict.pop(city_code, None)
                else:
                    pass
                obj = cls(**instance)
                obj.save_plus(upsert=True)
            ids = list(old_dict.keys())
            if len(ids) == 0:
                pass
            else:
                f = {"city_code": {"$in": ids}}
                u = {"$set": {"can_use": False}}
                cls.update_many_plus(filter_dict=f, update_dict=u, upsert=True)

    @classmethod
    def refresh_from_file(cls):
        """
        从json文件刷新可用城市列表
        :return:
        """
        instances = cls.batch_create(cls.read_data_from_file())
        f = dict()
        old_list = cls.find_plus(filter_dict=f, to_dict=True, can_json=False)
        old_dict = {x['city_code']: x for x in old_list}
        old_keys = old_dict.keys()
        for instance in instances:
            city_code = instance['city_code']
            if city_code in old_keys:
                """数据库已存在的城市记录,需要比对"""
                temp = old_dict[city_code]
                instance['_id'] = temp['_id']
                instance['first_letter'] = temp['first_letter']
                old_dict.pop(city_code, None)
            else:
                pass
            obj = cls(**instance)
            obj.save_plus(upsert=True)
        ids = list(old_dict.keys())
        if len(ids) == 0:
            pass
        else:
            f = {"city_code": {"$in": ids}}
            u = {"$set": {"can_use": False}}
            cls.update_many_plus(filter_dict=f, update_dict=u, upsert=False)


class TrafficViolationHandler:
    """
    违章查询处理器,这是一个非持久化类
    """
    def __init__(self, plate_number: str, vin: str, engine_id: str, car_type: str):
        """
        构造器
        :param plate_number:   车牌
        :param vin:         车架号,尽量长
        :param engine_id:   发动机号
        :param car_type:   车辆类型? 01:大型车,02:小型车, 51:新能源大型车 52:新能源小型车
        """
        self.error = ''
        r = ValidCity.get_city_code_by_plate_number(plate_number=plate_number)
        if len(r) == 0:
            ms = "{} 对应的地区不明".format(plate_number)
            logger.exception(ms)
            print(ms)
            self.error = ms
        else:
            new_power = r['new_power']
            """识别车辆类型. 默认是大型车"""
            if car_type is None:
                type_id = "01"
            elif isinstance(car_type, str):
                if car_type.find("大型") != -1:
                    if new_power:
                        type_id = "51"
                    else:
                        type_id = "01"
                else:
                    if new_power:
                        type_id = "52"
                    else:
                        type_id = "02"
            else:
                type_id = "01"
            city_code = r['city_code']
            city_name = r['city_name']
            self.car_type = type_id
            self.new_power = new_power
            self.city_code = city_code
            self.city_name = city_name
            self.plate_number = plate_number
            need_engine = r['need_engine']
            need_vin = r['need_vin']
            engine_length = r['engine_length']
            vin_length = r['vin_length']
            if not ValidCity.validate_city_code(city_code):
                ms = "{}对应的地区{}目前无法查询违章记录".format(plate_number, city_name)
                logger.exception(ms)
                print(ms)
                self.error = ms
            else:
                if need_engine:
                    """需要发动机号码"""
                    if engine_length == 0:
                        self.engine_id = engine_id
                    elif len(engine_id) >= engine_length:
                        self.engine_id = engine_id[-engine_length:]
                    else:
                        ms = "发动机号码需要后{}位".format(engine_length)
                        logger.exception(ms)
                        print(ms)
                        self.error = ms
                if need_vin:
                    """需要车架号码"""
                    if vin_length == 0:
                        self.vin = vin
                    elif len(vin) >= vin_length:
                        self.vin = vin[-vin_length:]
                    else:
                        ms = "车架号码需要后{}位".format(vin_length)
                        logger.exception(ms)
                        print(ms)
                        self.error = ms

    @classmethod
    def query_vio(cls,  plate_number: str, vin: str, engine_id: str, car_type: str = None) -> dict:
        """
        查询交通违章信息.
        :param plate_number:
        :param vin:
        :param engine_id:
        :param car_type: 车辆类型? 01:大型车,02:小型车, 51:新能源大型车 52:新能源小型车
        :return:
        """
        mes = {'message': 'success'}
        obj = cls(plate_number=plate_number, vin=vin, engine_id=engine_id, car_type=car_type)
        if obj.error != "":
            mes['message'] = obj.error
        else:
            r = cls.query_vio_from_api(obj.plate_number, obj.vin, obj.engine_id, obj.city_code, obj.car_type)
            mes = r
        return mes

    @staticmethod
    def query_vio_from_api(plate_number: str, vin: str, engine_id: str, city_code: str, car_type: str) -> dict:
        """
        从聚合数据的接口查询违章信息.
        :param plate_number:
        :param vin:
        :param engine_id:
        :param city_code:
        :param car_type: 车辆类型? 01:大型车,02:小型车, 51:新能源大型车 52:新能源小型车
        :return:{'message': '发动机号错误','data';{''violations}: [violation1,....], amount:2,....}
        """
        mes = {"message": "success"}
        u = "http://v.juhe.cn/sweizhang/query?dtype=&callback=&city={}&hphm={}&hpzl={}&engineno={}&classno={}&key={}".\
            format(city_code, quote(plate_number, encoding='utf-8'), car_type, engine_id, vin, app_key)
        r = requests.get(url=u)
        status_code = r.status_code
        if status_code != 200:
            ms = "查询聚合数据的违章查询直连接口的车牌和城市的对应关系时出错,服务器返回了错误代码:{}".format(status_code)
            logger.exception(ms)
            print(ms)
            title = "{}聚合数据接口出错".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            send_mail(title=title, content=ms)
            mes['message'] = ms
        else:
            r = r.json()
            """
            查询成功的示范
            r = {
                 'reason': '查询成功', 
                 'resultcode': '200', 
                 'error_code': 0, 
                 'result': {
                            'lists': [
                                       {
                                       'archiveno': '', 
                                       'date': '2018-03-17 15:12:00', 
                                       'act': '驾驶中型以上载货汽车在高速公路、城市快速路以外的道路上行驶超过规定时速10%未达20%的', 
                                       'wzcity': '广东深圳', 
                                       'handled': '0', 
                                       'money': '0', 
                                       'fen': '3', 
                                       'code': '13501', 
                                       'area': '省道22179公里500米'
                                       }, 
                                       {
                                       'archiveno': '',                              # 文书编号
                                       'date': '2017-11-25 15:42:00',                # 违章时间
                                       'act': '违反禁令标志指示',                       # 违章行为
                                       'wzcity': '',                                 # 违章行为发生的城市
                                       'handled': '0',                               # 是否处理,1处理 0未处理 空未知
                                       'money': '0',                                 # 违章罚款(仅供参考，不一定有值)
                                       'fen': '3',                                   #　违章扣分(仅供参考，不一定有值)
                                       'code': '1344', 　　　　　　　　　　　　　　　　　　# 违章代码(仅供参考，不一定有值)
                                       'area': '沪昆高速1073公里600米处东往西'           # 违章地点
                                       }
                                    ], 
                            'city': 'JX_YICHUN_J', 
                            'hphm': '赣CX3706', 
                            'province': 'JX', 
                            'hpzl': '01'
                            }
                }
            """
            if r['error_code'] != 0:
                mes['message'] = r['reason']
            else:
                result = r['result']
                """
                class ViolationQueryResult(mongo_db.BaseDoc):
                    _table_name = "violation_query_result_info"
                    type_dict = dict()
                    type_dict["_id"] = ObjectId  # id 唯一
                    type_dict['user_id'] = ObjectId  # 关联用户的id
                    type_dict['generator_id'] = ObjectId  # 关联查询器的id
                    type_dict['amount'] = int  # 截止到目前一共多少次违章？
                    type_dict['total_fine'] = float  # 未处理违章总罚款
                    type_dict['total_points'] = int  # 未处理违章总扣分
                    type_dict['untreated'] = int  # 未处理违章条数
                    type_dict['create_date'] = datetime.datetime  # 查询结果创建时间
                    type_dict['violations'] = list  # 违章记录，是DBRef的数组
                class ViolationRecode(mongo_db.BaseDoc):
                    _table_name = "violation_info"
                    type_dict = dict()
                    type_dict["_id"] = ObjectId  # id 唯一
                    type_dict['user_id'] = ObjectId  # 关联用户的id
                    type_dict['plate_number'] = str  # 违章时的车牌号
                    type_dict["code"] = str  # 违章编码,唯一，非违章条例码
                    type_dict["time"] = datetime.datetime  # 违章时间
                    type_dict["update_time"] = datetime.datetime  # 记录变更时间
                    type_dict["fine"] = float  # 罚款金额
                    type_dict["address"] = str  # 违章地址
                    type_dict["reason"] = str  # 违章处理原因
                    type_dict["point"] = int  # 违章扣分
                    type_dict["province"] = str  # 省份
                    type_dict["city"] = str  # 城市
                    type_dict["service_fee"] = float  # 服务费
                    type_dict["violation_num"] = str  # 违章编码
                    type_dict["can_select"] = int  # 能否勾选办理：0不可勾选, 1可勾选。
                    type_dict["process_status"] = str  # 违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
                    type_dict["payment_status"] = str  # 违章缴费状态 不返回表示无法获取该信息，1-未缴费 2-已缴
                    type_dict['position_id'] = ObjectId  # 违章地址的经纬度信息的id，指向Position类
                """
                vio_list = result.get('lists')
                if isinstance(vio_list, list):
                    data = dict()                  # 最后返回的数据
                    amount = 0                     # 违章总数
                    untreated = 0                  # 未处理违章条数
                    total_fine = 0.0               # 未处理违章总罚款
                    total_points = 0               # 未处理违章总扣分
                    violations = list()            # 违章记录容器
                    for vio in vio_list:
                        """
                        vio = {
                                'archiveno': '',                              # 文书编号
                                'date': '2017-11-25 15:42:00',                # 违章时间
                                'act': '违反禁令标志指示',                       # 违章行为
                                'wzcity': '',                                 # 违章行为发生的城市
                                'handled': '0',                               # 是否处理,1处理 0未处理 空未知
                                'money': '0',                                 # 违章罚款(仅供参考，不一定有值)
                                'fen': '3',                                   #　违章扣分(仅供参考，不一定有值)
                                'code': '1344', 　　　　　　　　　　　　　　　　　　# 违章代码(仅供参考，不一定有值)
                                'area': '沪昆高速1073公里600米处东往西'           # 违章地点
                              }
                        """
                        amount += 1
                        handled = vio['handled']
                        _id = vio.get('archiveno')  # 文书编号,页就是以前的违章唯一编号,不一定有
                        code = vio.get('code')
                        money = vio.get("money")
                        try:
                            money = float(money)
                        except Exception as e:
                            logger.exception(e)
                            money = None
                        fen = vio.get("fen")
                        try:
                            fen = int(fen)
                        except Exception as e:
                            logger.exception(e)
                            fen = None
                        """
                        聚合返回:是否处理,1处理 0未处理 空未知
                        接口要求,违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
                        """
                        payment_status = 1
                        if handled == "0":
                            """未处理"""
                            handled = 1
                            untreated += 1
                            if money is not None:
                                total_fine += money
                            if fen is not None:
                                total_points += fen
                        elif handled == "1":
                            handled = 0
                            payment_status = 2
                        else:
                            handled = 4
                        temp = {
                            "time": mongo_db.get_datetime_from_str(vio['date']),    # 违章时间
                            "city": '' if vio.get('wzcity') else vio['wzcity'],     # 违章城市
                            "plate_number": plate_number,                           # 车牌
                            "_id": _id,                                             # 文书编号,就是以前的违章唯一编号,不一定有
                            "code": code,                                           # 违章代码,不一定有
                            "fine": money,                                          # 罚款,不一定有
                            "point": fen,                                           # 扣分,不一定有
                            "reason": vio['act'],                                   # 违章原因
                            "address": vio['area'],                                 # 违章地址
                            "process_status": handled,                              # 违章状态,是否处理,int类型
                            "payment_status": payment_status                        # 支付状态,是否支付,int类型
                        }
                        temp = {k: v for k, v in temp.items()}
                        violations.append(temp)
                    data['amount'] = amount
                    data['untreated'] = untreated
                    data['total_fine'] = total_fine
                    data['total_points'] = total_points
                    data['violations'] = violations
                    mes['data'] = data
                else:
                    pass
        return mes


if __name__ == "__main__":
    """
    可被查询到违章记录的
    [
    {vin': 'LGAX5D652F8021160',  'engine_id': 'F2003733', 'plate_number': '赣CX0975'},
    {vin': 'LG6ZDCNHXFY200347',  'engine_id': '1415B004539', 'plate_number': '赣CX0431'}
    ]
    """
    q = {
        'vin': 'LFNFVXPXXG1F32315',  'engine_id': '52701239', 'plate_number': '赣CX3706'
    }
    TrafficViolationHandler.query_vio(**q)
    pass