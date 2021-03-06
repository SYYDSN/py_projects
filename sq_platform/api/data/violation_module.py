# -*- coding:utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(sys.path[0])[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
import requests
import datetime
from log_module import get_logger
import json
from bson import regex
from api.data.item_module import User
from bson.objectid import ObjectId
from bson.dbref import DBRef
from error_module import pack_message
from error_module import RepeatError
from error_module import MongoDeleteError
from api.data.item_module import CarLicense
from api.data.item_module import Position
from api.data.item_module import ThroughCity
from amap_module import get_position_by_address
from extends.car_city import CarCity
from extends.vio_module import TrafficViolationHandler
import warnings
import Levenshtein


"""违章查询模块"""


logger = get_logger()
interval_seconds = 56400  # 一天的秒
cache = mongo_db.cache


def query(**kwargs):
    """
    查询违章，会查所有的违章记录，包含已处理的。此方法为示范。
    :param kwargs:{"plateNumber":"苏A97P90"(车牌号，必填),
                   "engineNo":"YS669D"(发动机号，视城市规则是否必填),
                   "vin":"662722"(车架号，视城市规则是否必填),
                   "carType":"02"(车辆类型01大车02小车,不必填,默认小车),
                   "city":"杭州市"(查询城市,不必填,默认查归属地)}
    :return: 返回示意
    {
        "success": true,
        "data": {
            "token": "8045402120367843",    //用户身份标识
            "totalFine": "200",                           //未处理违章总罚款
            "totalPoints": 6,                               //未处理违章总扣分
            "untreated": 3,                                 //未处理违章条数
            "violations": [{
                    "code": "1232-D1",                  //违章编码,唯一，非违章条例码
                    "time": "2016-06-06 12:32:38",         //违章时间
                    "fine": "200.00",                      //罚款金额
                    "address": "文二西路口",         //违章地址
                    "reason": "您在 xx 路违反了交通规则",       //违章处理原因
                    "point": 6,                                //违章扣分
                    "province": "浙江省",               //省份
                    "city": "杭州市",                       //城市
                    "serviceFee": "23.00",            //服务费
                    "canSelect": 1,                         //能否勾选办理：0不可勾选, 1可勾选。
                    "processStatus": 1,                  //违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
                    "paymentStatus": 1                  //违章缴费状态 不返回表示无法获取该信息，1-未缴费 2-已缴
            }]
        }
    }
    """
    args = {"plateNumber": "沪A0M084", "engineNo": "416098", "vin": "116280",
            "carType": "02", "city": "上海市"}
    args = {"plateNumber": "赣EG2681", "engineNo": "091697", "vin": "010012",
            "carType": "02", "city": "上海市"}
    args = kwargs
    json_str = json.dumps(args)  # 此接口的参数必须是json_str格式
    url = 'http://ddycapi.market.alicloudapi.com/violation/query'
    appcode = "e68af34cf135477caadcfc5b9816988f"
    headers = {"Authorization": "APPCODE {}".format(appcode)}
    resp = requests.post(url, data=json_str, headers=headers)
    if resp.status_code == 200:
        print(resp.json())
    else:
        print(resp.status_code)


#
#
# def query2(**kwargs):
#     """
#     查询车辆违章记录,此接口目前只能查询未处理违章,暂时搁置
#     :param kwargs:  鉴于查询接口的名字的生僻， 参数和对应的查询字段的转化如下说明
#     carorg  查询违章事件的所在地  必须  travel_zone
#     lsprefix   车牌前缀，比如 沪，豫等  必须  plate_prefix
#     lsnum      车牌号码，就是车牌除去前缀的部分  必须   plate_num
#     lstype     车型，大车01 ，小车02  视地区需要非必须项目      car_type
#     frameno    车架号，就是行驶证上的车辆识别代号的后6位 视地区需要非必须项目  frame_id
#     engineno   发动机号 必须项目  engine_id
#     :return:
#      JSON返回示例 :
#     {
#         "status": "0",
#         "msg": "",
#         "result": {
#             "lsprefix": "皖",
#             "lsnum": "B91801",
#             "carorg": "anhui",
#             "usercarid": "1483850",
#             "list": [
#                 {
#                     "time": "2015-06-23 18:24:00.0",
#                     "address": "赵非公路鼓浪路北约20米",
#                     "content": "违反规定停放、临时停车且驾驶人不在现场或驾驶人虽在现场拒绝立即驶离，妨碍其他车辆、行人通行的",
#                     "legalnum": "",
#                     "price": "0",
#                     "id": "3500713",
#                     "score": "0"
#                 },
#                 {
#                     "time": "2015-06-05 18:20:00.0",
#                     "address": "新松江路近人民北路东侧路段",
#                     "content": "违反规定停放、临时停车且驾驶人不在现场或驾驶人虽在现场拒绝立即驶离，妨碍其他车辆、行人通行的",
#                     "legalnum": "",
#                     "price": "0",
#                     "id": "3500714",
#                     "score": "0"
#                 },
#                 {
#                     "time": "2015-06-08 18:22:00.0",
#                     "address": "鼓浪路近291弄路段",
#                     "content": "违反规定停放、临时停车且驾驶人不在现场或驾驶人虽在现场拒绝立即驶离，妨碍其他车辆、行人通行的",
#                     "legalnum": "",
#                     "price": "0",
#                     "id": "3500715",
#                     "score": "0"
#                 }
#             ]
#         }
#     }
#
#     返回参数信息：
#     lsprefix ： 车牌前缀
#     lsnum  ： 车牌剩余部分
#     carorg  ： 管局名称
#     usercarid：车牌ID
#     time ： 时间
#     address ： 地点
#     content ： 违章内容
#     legalnum ： 违章代码
#     price：罚款金额
#     score ： 扣分
#     illegalid ： 违章ID
#     number ： 违章编号
#     agency ： 采集机关
#     process_status  注意，此接口返回值中全部是未处理的违章
#     """
#     """参数的映射关系"""
#     name_map = {"carorg": "travel_zone", "lsprefix": "plate_prefix", "lsnum": "plate_num",
#                 "lstype": "car_type", "frameno": "frame_id", "engineno": "engine_id"}
#     args = {k: '' if kwargs.get(v) is None else kwargs[v] for k, v in name_map.items()}
#     url = 'http://apis.baidu.com/netpopo/illegal/illegal'
#     """
#     参数示范
#     params = {"carorg": "shanghai", "lsprefix": "沪", "lsnum": "A0M084", "lstype": "",
#               "frameno": "116280", "engineno": "416098"}
#     """
#     headers = {"apikey": "5e9fe5825f7ac9b376d717655543da26"}
#     message = {"message": "success"}
#     try:
#         resp = requests.get(url, params=args, headers=headers)
#         if resp.status_code == 200:
#             resp = resp.json()
#             if resp['msg'] == "":
#                 """有未处理的违章记录"""
#                 name_map = {v: k for k, v in name_map.items()}
#                 """
#                 carorg 交管局名称
#                 count  违章次数
#                 total_price 总罚款金额
#                 total_score 总扣分
#
#                 illegalid 违章事件id
#                 usercarid 用户车牌id 在车管局下保持唯一
#                 address  事发地址
#                 content  违章内容
#                 time  事发时间
#                 price  本次罚款
#                 score  本次扣分
#                 """
#                 inner_map = {"count": "count", "totalprice": 'total_price', "totalscore": "total_score",
#                              "address": "address", "content": "content", "time": "time",
#                              "price": "price", "score": "score", "carorg": "city", "illegalid": "violation_id",
#                              "usercarid": "plate_id"}
#                 name_map.update(inner_map)
#
#                 pass
#             else:
#                 message['message'] = resp['msg']
#         else:
#             message = pack_message(message, 7001, url=url, headers=headers, query_dict=args,
#                                    status_code=resp.status_code)
#     except ConnectionError:
#         logger.exception("Error: ")
#         message = pack_message(message, 7000, url=url, headers=headers, query_dict=args)
#     finally:
#         return message


def query_position(*arg, **kwargs):
    """查询经纬度信息，此方法为类的内部方法调用"""
    city = kwargs['city']
    address = kwargs['address']
    object_id = mongo_db.get_obj_id(kwargs['object_id'])
    """先检查数据库是否有？"""
    in_db = Position.find_one(city=city, address=address)
    if in_db is None:
        """数据库没有对应的信息"""
        key = "query_geo_coordinate_{}_{}".format(city, address)  # 缓存标识
        cache.set(key, 1, timeout=5)
        position_data, real = get_position_by_address(city=city, address_str=address)
        cache.delete(key)
        args = {"address": address, "city": city, "real_value": real,
                "longitude": position_data[0], "latitude": position_data[1]}
        pos = Position(**args)
        filter_dict = {"city": city, "address": address}
        update = {k: v for k, v in pos.to_flat_dict().items() if k not in ("_id", "city", "address")}
        pos = pos.find_one_and_update(filter_dict=filter_dict, update=update)
        position_id = mongo_db.get_obj_id(pos['_id'])
    else:
        position_id = in_db.get_id()
    filter_dict = {"_id": object_id}
    update = {"$set": {"position_id": position_id}}
    ses = mongo_db.get_conn("violation_info")
    ses.find_one_and_update(filter=filter_dict, update=update)
    return str(position_id)


class ViolationRecode(mongo_db.BaseDoc):
    """
    违章记录
    以车牌号和违章时间,违章地址.作为唯一标识
    """
    _table_name = "violation_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_id'] = ObjectId  # 关联用户的id,
    type_dict['plate_number'] = str  # 违章时的车牌号
    type_dict["code"] = str  # 违章编码,唯一，非违章条例码
    type_dict["time"] = datetime.datetime  # 违章时间
    type_dict["update_time"] = datetime.datetime  # 记录最后一次从互联网查询的时间
    # type_dict["create_time"] = datetime.datetime  # 字段废弃,以update_time替代.2018-6-21
    type_dict["fine"] = float  # 罚款金额
    type_dict["address"] = str  # 违章地址
    type_dict["reason"] = str  # 违章处理原因
    type_dict["point"] = int  # 违章扣分
    type_dict["province"] = str  # 省份
    type_dict["city"] = str  # 城市
    type_dict["service_fee"] = float  # 服务费
    type_dict["violation_num"] = str  # 违章编码
    type_dict["can_select"] = int  # 能否勾选办理：0不可勾选, 1可勾选。
    type_dict["process_status"] = int  # 违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
    type_dict["payment_status"] = int  # 违章缴费状态 不返回表示无法获取该信息，1-未缴费 2-已缴
    type_dict['position_id'] = ObjectId  # 违章地址的经纬度信息的id，指向Position类
    type_dict['forgery'] = bool          # 是否是伪造的数据?如果添加的违章是虚拟的,需要加上这个字段并置为True,默认是False

    def __init__(self, **kwargs):
        if "update_time" not in kwargs:
            kwargs['update_time'] = datetime.datetime.now()
        if "forgery" not in kwargs:
            kwargs['forgery'] = False
        super(ViolationRecode, self).__init__(**kwargs)

    def check_position(self):
        """检查一条记录是否有违章记录的经纬度信息？
        如果没有，则查询经纬度信息，并将对应的经纬度信息的id填入self的
        position_id。
        """
        if hasattr(self, "position_id") and self.position_id is not None:
            return self
        else:
            """如果没有position_id这个属性的话，就去找到经纬度。"""
            city = self.city
            address = self.address
            object_id = self.get_id()
            args = {"city": city, "address": address, "object_id": str(object_id)}
            res = query_position(**args)
            if res is None:
                return self
            # if res.status != "SUCCESS":
            #     a_str = "数据库插入失败，celery插入结果{}".format(res.status)
            #     try:
            #         raise IOError(a_str)
            #     except IOError as e:
            #         print(e)
            #         logger.error(a_str, exc_info=True, stack_info=True)
            #     finally:
            #         return self
            else:
                return self

    def to_flat_dict(self):
        """覆盖父类的序列化方法,主要是为了取经纬度"""
        a_dict = super(ViolationRecode, self).to_flat_dict()
        key = 'position_id'
        if key in a_dict:
            pos = Position.find_by_id(a_dict.pop(key))
            a_dict['longitude'] = pos.longitude
            a_dict['latitude'] = pos.latitude
            a_dict['real_value'] = pos.real_value
        return a_dict

    def exists(self):
        """
        废弃方法 2018-5-23
        检查一条违章记录是否已存在？
        1. 存在且完全相同就不做更新。
        2. 存在不同就update
        3. 不存在就insert
        :return: DBRef对象。
        """
        ms = "此方法已被废弃,无需再在保存前检查重复,请直接调用self.save_plus方法," \
             "self.save_plus方法会自行决定是插入还是修改 2018-5-23"
        warnings.warn(ms)
        """先构建判断唯一的查询条件"""
        query_dict = {"code": self.get_attr("code"), "address": self.get_attr("address"),
                      "time": self.get_attr("time"), "plate_number": self.get_attr("plate_number")}
        query_obj = ViolationRecode.find_one(**query_dict)
        dbref = None
        if query_obj is None:
            dbref = self.insert_self_and_return_dbref()
        else:
            """如果查到对象了,那就比较差异"""
            flag = False
            for key in self.type_dict.keys():
                if key == "_id" or key == "update_time" or key == "position_id":
                    pass
                else:
                    new_key = query_obj.__dict__.get(key)
                    old_key = self.__dict__.get(key)
                    if new_key is None or old_key == new_key:
                        pass
                    else:
                        flag = True
                        self.set_attr("update_time", mongo_db.get_datetime(to_str=False))
                        self._id = query_obj.get_id()
                        query_obj = query_obj.check_position()  # 检查位置信息
                        position_id = query_obj.get_attr("query_obj")
                        if position_id is not None:
                            self.set_attr("position_id", query_obj.position_id)
                        break
            if flag:
                """有差异"""
                if not hasattr(self, "create_date"):
                    update_time = query_obj.__dict__.get("update_time")
                    if isinstance(update_time, datetime.datetime):
                        self.set_attr("create_time", update_time)
                dbref = self.save_self_and_return_dbref()
            else:
                if not hasattr(self, "create_date"):
                    self.set_attr("create_time", datetime.datetime.now())
                dbref = query_obj.get_dbref()
        return dbref

    def save_instance(self) -> dict:
        """
        重载父类的方法,用于在从互联网查询到违章记录后:
        1. 检查是否有重复记录?
        2. 检查是否需要更新? 更新哪些字段?
        :return: doc
        """
        f = {
            "user_id": self.get_attr("user_id"),
            "plate_number": self.get_attr("plate_number"),
            "time": self.get_attr("time")
        }
        ignore = ['_id']
        doc = self.get_dict(ignore=ignore)
        if "update_time" not in doc:
            doc['update_time'] = datetime.datetime.now()
        # doc['forgery'] = True  # 调试时开启,给虚拟数据一个标记
        u = {"$set": doc}
        res = ViolationRecode.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
        return res

    @classmethod
    def page(cls, user_id: str = None, city: str = None, plate_number: str = None, vio_status: str = None,
             fine: float = None, begin_date: datetime.datetime = None, end_date: datetime.datetime = None,
             index: int = 1, num: int = 20, can_json: bool = True, reverse: bool = True) -> dict:
        """
        分页查询违章记录
        :param user_id: 用户id或者id的list,id可以是str或者ObjectId类型,为空表示所有司机
        :param city:   城市
        :param plate_number:   车牌
        :param vio_status:  违章状态? 已/未处理
        :param fine:   罚金数目
        :param begin_date:   开始时间
        :param end_date:   截至时间
        :param index:  页码
        :param can_json:   是否进行can json转换
        :param num:   每页多少条记录
        :param reverse:   是否倒序排列?
        :return: 违章记录的列表和统计组成的dict
        """
        filter_dict = dict()
        if user_id is not None:
            if isinstance(user_id, list) and len(user_id) > 0:
                if isinstance(user_id[0], ObjectId):
                    """ViolationRecode.user_id的类型是ObjectId不是DBRef"""
                    filter_dict['user_id'] = {"$in": user_id}
                else:
                    filter_dict['user_id'] = {"$in": [ObjectId(x) for x in user_id]}
            else:
                filter_dict['user_id'] = mongo_db.get_obj_id(user_id)
        if city is not None:
            filter_dict['city'] = regex.Regex('.*{}.*'.format(city))  # 正则表达式,匹配city中包含city字符串的
        if plate_number is not None:
            filter_dict['plate_number'] = regex.Regex('.*{}.*'.format(plate_number))  # 正则表达式
        if isinstance(vio_status, str) and vio_status.isdigit():
            vio_status = int(vio_status)
        else:
            pass
        if isinstance(vio_status, int) and 0 < vio_status < 5:
            """
            违章状态分四种,分别是1-4的数组.
            1. 未处理
            2. 处理中
            3. 已处理
            4. 不支持
            """
            filter_dict['process_status'] = vio_status  # int类型
        if fine is not None:
            filter_dict['fine'] = float(fine)
        filter_dict['time'] = {"$lte": end_date, "$gte": begin_date}
        skip = (index - 1) * num
        sort_dict = {"time": -1 if reverse else 1}
        count = cls.count(filter_dict=filter_dict)
        res = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, skip=skip, limit=num, to_dict=True)
        if can_json:
            res = [mongo_db.to_flat_dict(x) for x in res]
        data = {"count": count, "data": res}
        return data

    @classmethod
    def all_vio(cls, user_id):
        user_id = mongo_db.get_obj_id(user_id)
        result = cls.find(user_id=user_id)
        return result

    @classmethod
    def instance(cls, **kwargs):
        """
        创建一个违章记录的实例,
        由于本方法会自动转换字段名称.然后再生成实例对象.所以
        推荐使用此方法创建实例,
        此方法目前适应聚合数据的直联查询接口  2018-5-23
        :param kwargs:
                    "code": "1232-D1",                  //违章编码,唯一，非违章条例码
                    "time": "2016-06-06 12:32:38",         //违章时间
                    "fine": "200.00",                      //罚款金额
                    "address": "文二西路口",                  //违章地址
                    "reason": "您在 xx 路违反了交通规则",       //违章处理原因
                    "point": 6,                                //违章扣分
                    "province": "浙江省",                     //省份
                    "city": "杭州市",                       //城市
                    "serviceFee": "23.00",                  //服务费
                    "violationNum": 10180,                  //违章编码
                    "canSelect": 1,                         //能否勾选办理：0不可勾选, 1可勾选。
                    "processStatus": 1,                  //违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
                    "paymentStatus": 1                  //违章缴费状态 不返回表示无法获取该信息，1-未缴费 2-已缴
        :return: ViolationRecode的实例
        """
        name_dict = {"serviceFee": "service_fee", "canSelect": "can_select",
                     "processStatus": "process_status", "paymentStatus": "payment_status",
                     'violationNum': "violation_num", "violationCity": "violation_city", "markFee": "mark_fee"}
        kwargs = {(name_dict[k] if k in name_dict else k): v for k, v in kwargs.items()}
        return cls(**kwargs)

    @classmethod
    def find_by_id(cls, o_id):
        """查找并返回一个对象，这个对象是o_id对应的类的实例"""
        o_id = mongo_db.get_obj_id(o_id)
        ses = mongo_db.get_conn(cls._table_name)
        result = ses.find_one({"_id": o_id})
        if result is None:
            return result
        else:
            return cls.instance(**result)

    @classmethod
    def repair_violation_num(cls) -> None:
        """
        修复违章记录中,没有违章代码的部分
        :return:
        """
        f = {
            "$or": [
                {"violation_num": {"$exists": False}},
                {"violation_num": ""}
            ]
        }
        vios = cls. find_plus(filter_dict=f, to_dict=True)
        for vio in vios:
            result = Penalty.match_code(vio)
            if result:
                f = {"_id": result['_id']}
                u = {"$set": {"violation_num": result['violation_num']}}
                r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                if r is None:
                    print(result)


class Penalty(mongo_db.BaseDoc):
    """
    对交通违规的处罚
    """
    _table_name = "penalty_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['code'] = str   # 违章代码 唯一
    type_dict['reason'] = str  # 原因
    type_dict['point'] = int  # 扣分
    type_dict['fine'] = float  # 罚金
    type_dict['extra'] = str   # 并罚

    @classmethod
    def import_data(cls) -> None:
        """
        从文件导入信息，初始化数据用。
        :return:
        """
        f_p = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resource", "最新车辆交通违章代码查询表.data")
        f = open(f_p, "r", encoding="utf-8")
        for line in f:
            l = line.split("\t")
            l = [x.rstrip() for x in l if x.rstrip() != ""]
            if len(l) == 4:
                l.append("")
            args = dict(zip(['code', 'reason', 'point', 'fine', "extra"], l))
            f = {"code": args.pop("code")}
            u = {"$set": args}
            r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
            if r is None:
                print(l)

    @classmethod
    def all_reason(cls) -> dict:
        """
        获取所有的违章代码和违章原因的字典.注意,有缓存2个小时
        :return:
        """
        key = "penalty_reason_cache"
        d = cache.get(key=key)
        if d is None:
            res = cls.find_plus(filter_dict={}, projection=['code', "reason"], to_dict=True)
            res = {x['code']: x['reason'] for x in res}
            cache.set(key, res, timeout=7200)
            d = res
        return d

    @classmethod
    def all_point(cls) -> dict:
        """
        获取所有的违章代码和扣分的字典.注意,有缓存2个小时
        :return:
        """
        key = "penalty_point_cache"
        d = cache.get(key=key)
        if d is None:
            res = cls.find_plus(filter_dict={}, projection=['code', "point"], to_dict=True)
            res = {x['code']: x['point'] for x in res}
            cache.set(key, res, timeout=7200)
            d = res
        return d

    @classmethod
    def match_code(cls, vio: (dict, ViolationRecode) = None, cover: bool = False) -> (None, dict, ViolationRecode):
        """
        给违章记录配置违章代码:
        1. 如果有违章代码就不匹配,除非强制重新匹配.
        2. 使用字符串近视度匹配,低于70%就认为匹配失败.
        :param vio: 违章记录, doc/dict/ViolationRecode的实例
        :param cover: 对于已有违章代码的对象,是否重新匹配?
        :return: 失败返回None
        """
        if isinstance(vio, dict):
            reason = vio.get("reason")
        elif isinstance(vio, ViolationRecode):
            reason = vio.get_attr("reason")
        else:
            ms = "错误的参数类型vio:{}".format(type(vio))
            raise TypeError(ms)
        d = cls.all_reason()
        result = {"code": "", "str": "", "per": 0}
        for code, word in d.items():
            per = Levenshtein.jaro_winkler(reason, word)
            if per > result['per']:
                result['str'] = word
                result['code'] = code
                result['per'] = per
        if result['per'] < 0.5:
            """匹配失败"""
            pass
        else:
            if isinstance(vio, dict):
                old = vio.get("violation_num")
                if old is None or old == "" or cover:
                    vio['violation_num'] = result['code']
                    return vio
                else:
                    pass
            else:
                if isinstance(vio, ViolationRecode):
                    old = vio.get_attr("violation_num")
                    if old is None or old == "" or cover:
                        vio.set_attr("violation_num", result['code'])
                        return vio
                    else:
                        pass


class ViolationQueryResult(mongo_db.BaseDoc):
    """违章查询结果类"""
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

    def read(self):
        """
        还原最近的违章记录
        :return: 可序列化的字典
        """

        violations = self.get_attr("violations", list())
        vio_list = list()
        if len(violations) == 0:
            pass
        else:
            for dbref in violations:
                vio = ViolationRecode.get_instance_from_dbref(dbref)
                if isinstance(vio, ViolationRecode):
                    vio = vio.check_position()
                    vio_list.append(vio.to_flat_dict())
                else:
                    pass
        self.set_attr("violations", vio_list)
        data = self.to_flat_dict()
        return data

    @classmethod
    def record(cls, user_id, generator_id, data_dict):
        """
        记录查询的结果。
        :param user_id: 用户id。
        :param generator_id: 查询器id。
        :param data_dict: 查询结果的字典。
        {'success': True,
        'data': {'amount': 9, 'totalFine': '0.00', 'totalPoints': 0, 'untreated': 0, 'violations':
        [
        {'violationNum': '10180', 'province': '上海市', 'violationCity': '', 'time': '2017-04-12 08:53:29', 'code': '49-466668', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '机动车不在机动车道内行驶的', 'address': '[嘉定]新源路泽普路东约10米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '10391', 'province': '上海市', 'violationCity': '', 'time': '2017-03-11 08:14:20', 'code': '49-466669', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '机动车违反临时停车规定且驾驶人不在现场的', 'address': '泽普路墨玉路东约99米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '13450', 'province': '上海市', 'violationCity': '', 'time': '2017-01-31 14:02:05', 'code': '49-466670', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3, 'reason': '违反禁止标线指示', 'address': '淀山湖大道进漕盈公路东约5米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '13450', 'province': '上海市', 'violationCity': '', 'time': '2016-12-19 16:21:22', 'code': '49-466671', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3, 'reason': '违反禁止标线指示', 'address': 'S5沪嘉高速北侧近中环与汶水路交汇处路段', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '10180', 'province': '上海市', 'violationCity': '', 'time': '2016-10-10 16:06:26', 'code': '49-466672', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '机动车不在机动车道内行驶的', 'address': '鹤旋路金运路北约5米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '10190', 'province': '上海市', 'violationCity': '', 'time': '2015-11-29 17:44:41', 'code': '49-466673', 'markFee': '0', 'fine': '100', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '违反规定使用专用车道的', 'address': '汶水路/高平路（东向西，公交专用车道）', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '13440', 'province': '上海市', 'violationCity': '', 'time': '2015-08-01 15:36:00', 'code': '49-466674', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3, 'reason': '机动车违反禁令标志指示的', 'address': '佳通支路真南路北约116米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '10391', 'province': '上海市', 'violationCity': '', 'time': '2014-10-16 15:22:00', 'code': '49-466675', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '机动车违反临时停车规定且驾驶人不在现场的', 'address': '墨玉路昌吉路南约168米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        {'violationNum': '10390', 'province': '上海市', 'violationCity': '', 'time': '2013-08-14 15:07:00', 'code': '49-466676', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3, 'reason': '在禁止停放和临时停放机动车的地点停车，驾驶人不在现场或虽在现场但拒绝立即驶离，妨碍其他车辆行人通行的', 'address': '长寿路昌化路西约100米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0}
        ]
        }}
        :return: ObjectId
        """
        user_id = mongo_db.get_obj_id(user_id)
        generator_id = mongo_db.get_obj_id(generator_id)
        kwargs = {"user_id": user_id, "generator_id": generator_id, "amount": 0, "total_fine": 0.0,
                  "untreated": 0, "create_date": datetime.datetime.now(), "violations": list()}
        if data_dict['message'] != "success":
            """没有查询成功,这时候不计数"""
            pass
        else:
            """查询成功，检查是否有数据"""
            data = data_dict['data']
            new_ids = list()  # 记录本次查询获取到的违章记录,用于确认哪些历史违章记录已被处理?
            if data['amount'] == 0:
                """没有查询到结果"""
                pass
            else:
                kwargs['amount'] = data['amount']
                try:
                    kwargs['total_fine'] = data['totalFine']
                except KeyError as e:
                    print(e)
                    kwargs['total_fine'] = data['total_fine']
                kwargs['untreated'] = data['untreated']
                data_vio_list = data['violations']
                vio_list = list()
                for vio in data_vio_list:
                    vio['user_id'] = user_id
                    vio.pop("_id", None)  # 这个_id可能是空字符,要去掉,让系统自行添加_id
                    obj = ViolationRecode.instance(**vio)
                    r = obj.save_instance()
                    if isinstance(r, dict):
                        save_id = r['_id']
                        """记录成功保存的违章记录的id,用于排除并更新那些已处理的违章记录"""
                        new_ids.append(save_id)
                        """保存违章记录的实例成功"""
                        dbref = DBRef(database=mongo_db.db_name, collection=ViolationRecode.get_table_name(),
                                      id=save_id)
                        vio_list.append(dbref)
                kwargs['violations'] = vio_list
            """更新已被处理的违章记录的信息"""
            f = {"_id": {"$nin": new_ids}, "user_id": user_id}
            u = {"$set": {"process_status": 3}}
            ViolationRecode.update_many_plus(filter_dict=f, update_dict=u)
            return cls.insert_one(**kwargs)  # 返回结果


class VioQueryGenerator(mongo_db.BaseDoc):
    """违章查询器"""
    _table_name = "violation_query_generator_info"

    """car_license和city组成唯一性index"""
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_id'] = DBRef  # 关联用户的id
    type_dict['car_license'] = DBRef  # 关联的行车证（上的有关信息）
    type_dict['city'] = str  # 查询的城市  聚合数据接口不需要这个字段
    type_dict['create_date'] = datetime.datetime  # 查询器的创建时间
    type_dict['prev_date'] = datetime.datetime  # 查询器的上一次使用时间(从网络)
    type_dict['prev_date_local'] = datetime.datetime  # 查询器的上一次使用时间(从本地数据库)
    """
    查询器的上一次的结果集的id(从网络),查询器每一次从网络查询违章记录后,
    都会更新此字段
    """
    type_dict['last_query_result_id'] = ObjectId
    type_dict['all_count'] = int  # 查询器的使用计数，包括本地查询
    type_dict['online_query_count'] = int  # 查询器的使用计数(从网络)
    type_dict['today_online_query_count'] = int  # 查询器的当日使用计数(从网络)
    type_dict['today_offline_query_count'] = int  # 查询器的当日使用计数

    def __init__(self, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        if "prev_date" not in kwargs:
            kwargs['prev_date'] = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        if "prev_date_local" not in kwargs:
            kwargs['prev_date_local'] = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        if "all_count" not in kwargs:
            kwargs['all_count'] = 0
        if "online_query_count" not in kwargs:
            kwargs['online_query_count'] = 0
        if "today_online_query_count" not in kwargs:
            kwargs['today_online_query_count'] = 0
        if "today_offline_query_count" not in kwargs:
            kwargs['today_offline_query_count'] = 0
        super(VioQueryGenerator, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        """工厂函数，此函数会创建CarLicense对象。
        所以初始化函数中需要部分的CarLicense类初始化参数.
        此方法会先检测相关的行车证信息是否存在。
        存在就返回旧的objid，不存在就插入一个新的行车证信息。
        然后检测当前用户是否已有相同的行车证信息？
        有的话就pass，没有的话就插入。
        然后再创建一个VioQueryGenerator的实例。
        token : 用户登录的token信息
        plate_number : 车牌
        engine_id: 发动机号
        vin_id: 车架号
        car_type: 车辆类型
        city： 查询城市。
        """
        user_id = kwargs.pop("user_id")
        user = User.find_by_id(user_id)
        if not isinstance(user, User):
            ms = "错误的用户id:{}".format(user_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            kwargs['user_id'] = user.get_dbref()
        plate_number = kwargs.pop("plate_number")
        engine_id = kwargs.pop("engine_id")
        vin_id = kwargs.pop("vin_id")
        car_type = kwargs.pop("car_type")
        city = kwargs.get("city")
        if city is None:
            raise KeyError("city 参数必须")
        else:
            """检查唯一性"""
            if VioQueryGenerator.is_only(user_id, plate_number):
                car_type = "小车" if str(car_type) == "02" else "大车"
                """插入行车证/车牌信息"""
                car_license = CarLicense.insert_and_return_dbref(plate_number=plate_number, car_type=car_type,
                                                                 vin_id=vin_id, engine_id=engine_id, user_id=user_id)

                kwargs["car_license"] = car_license
                kwargs["user_id"] = user_id
                keys = kwargs.keys()
                if "create_date" not in keys:
                    kwargs['create_date'] = datetime.datetime.now()
                if "prev_date" not in keys:
                    kwargs['prev_date'] = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
                if "all_count" not in keys:
                    kwargs['all_count'] = 0
                if "online_query_count" not in keys:
                    kwargs['online_query_count'] = 0
                if "today_online_query_count" not in keys:
                    kwargs['today_online_query_count'] = 0
                if "today_offline_query_count" not in keys:
                    kwargs['today_offline_query_count'] = 0
                obj = cls(**kwargs)
                return obj
            else:
                raise RepeatError(**kwargs)

    @classmethod
    def is_only(cls, user_id, plate_number):
        """
        检查是否有相同车牌的违章查询器, 没有返回True
        :param user_id:  用户dbref
        :param plate_number:  车牌
        :return: boolean
        """
        f = {"user_id": user_id, "plate_number": plate_number.upper()}
        result_query = cls.find_one_plus(filter_dict=f)
        flag = True
        if result_query is None:
            pass
        else:
            flag = False
        return flag

    def my_car_license(self) -> DBRef:
        """
        获取车牌信息
        :return: 车牌信息的DBRef对象
        """
        obj = self.car_license
        return obj

    def get_query_args(self):
        """获取查询参数"""
        ref = self.__dict__.get("car_license")
        if isinstance(ref, DBRef):
            object_id = ref.id
            license_obj = CarLicense.find_by_id(object_id)
            data = license_obj.get_vio_query_info()
            return data
        else:
            raise TypeError("{} 不是一个有效的DBRef对象".format(ref))

    @classmethod
    def get_car_licenses(cls, user_id: (str, ObjectId)) -> list:
        """
        查询用户名下所有的行驶证信息
        :param user_id: 用户id
        :return: 行驶证DBRef的list
        """
        user_id = mongo_db.get_obj_id(user_id)
        gens = cls.find(user_id=user_id)
        if gens is None:
            return list()
        else:
            res = [gen.car_license for gen in gens]
            return res

    @classmethod
    def get_input_history(cls, user_id: (str, ObjectId)) -> list:
        """
        根据用户id获取此用户所有的输入违章查询器和行车证信息的历史记录
        (由于城市是选择的，所以实际上只是行车证信息的输入历史)
        :param user_id: 用户id
        :return: 以每个行驶证为单位的的dict组成的list
        """
        user_id = mongo_db.get_obj_id(user_id)
        car_licenses = [CarLicense.find_by_id(x.get_attr('car_license').id) for x in cls.find(user_id=user_id)]
        results = list()
        keys = ['plate_number', 'owner_name', 'address', 'use_nature', 'car_model',
                'vin_id', 'engine_id', 'register_city', 'register_date', 'issued_date']
        car_licenses.sort(key=lambda obj: obj.get_attr("create_date"), reverse=True)
        license_list = []
        for car_license in car_licenses:
            plate_number = car_license.get_attr("plate_number")
            temp = dict()
            for key in keys:
                val = car_license.get_attr(key)
                if val is not None:
                    val = val.strip()
                    if val != "":
                        temp[key] = val
            if plate_number not in license_list:
                results.append(temp)
                license_list.append(plate_number)

        return results

    @classmethod
    def default_generator(cls, user_id) -> (None, dict):
        """
        由于业务逻辑的变更,此函数已被声明废止
        生成一组默认的违章查询器,
        生成条件是:
        1. 用户的行车证
        默认查询器在生成的时候会自动保存.
        :param user_id:
        :return:
        """
        ms = "由于业务逻辑的变更,此函数已被声明废止,并在将来被移除.{}".format(datetime.datetime.now())
        warnings.warn(ms)
        res = list()
        user_id = mongo_db.get_obj_id(user_id)
        """先取用户的行车证"""
        license_list = User.get_usable_license(user_id)
        if len(license_list) == 0:
            """用户没有行车证信息,忽视"""
            pass
        else:
            for car_license in license_list:
                dbref = DBRef(database="platform_db", collection=CarLicense.get_table_name(),
                      id=ObjectId(car_license['_id']))
                """检查是否所有的行车证都有对应的并且查询城市相同?"""
                plate_number = car_license.get("plate_number")
                city = CarCity.get_city(plate_number)
                if city is None:
                    """查询不到对应城市的"""
                    pass
                else:
                    f = {"user_id": user_id, "city": city}
                    r = cls.find_one_plus(filter_dict=f, instance=False)
                    if r is not None:
                        temp = {"_id": str(r['_id']), "plate_number": plate_number, "city": city}
                        res.append(temp)
                    else:
                        """新建一个查询器"""
                        # 违章查询器的初始化参数
                        now = datetime.datetime.now()
                        init = {
                            "_id": ObjectId(),
                            "user_id": user_id,  # 这个参数不是dbref，这是历史问题
                            "city": city,
                            "create_date": now,
                            "all_count": 0,
                            "car_license": dbref,
                            "online_query_count": 0,
                            "today_online_query_count": 0,
                            "today_offline_query_count": 0
                        }
                        generator = cls(**init)
                        r = generator.save_plus()
                        if r is None:
                            ms = "VioQueryGenerator对象保存失败,参数{}".format(init)
                            logger.exception(ms)
                            raise ValueError(ms)
                        else:
                            """保存成功,返回违章查询器的快捷方式"""
                            generator.set_attr("_id", r)
                            temp = {"_id": str(r), "plate_number": plate_number, "city": city}
                            res.append(temp)
        return res

    @classmethod
    def generator_list(cls, user_id: (str, ObjectId)):
        """
        查询用户名下所有的查询器,现阶段,利用用户车牌信息和去过的城市(ThroughCity类的实例)
        来自动组合生成违章查询器.
        :param user_id: 用户id
        :return:  字典的list
        """
        user_id = mongo_db.get_obj_id(user_id)
        """查询行车证"""
        license_list = User.get_usable_license(user_id, to_dict=True, can_json=False)  # [doc]
        """查询已有的违章查询器"""
        user_dbref = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=user_id)
        f = {"user_id": user_dbref}
        generator_list = cls.find_plus(filter_dict=f, to_dict=True)  # [doc]
        """
        将行车证列表整理成字典对象
        """
        license_dict = {x['_id']: x for x in license_list}
        res = list()  # 需要被返回的generator集合,包含已存在的和新创建的
        got_ids = list()  # 已经加入res的generator的_id,
        l_ids = [x['_id'] for x in license_list]  # 行车证对象的_id集合
        now = datetime.datetime.now()
        plate_map = dict()  # generator的_id和plate_number的映射关系
        for g in generator_list:
            l_id = g['car_license'].id
            g_id = g['_id']
            if l_id in l_ids:
                """
                查询器的车牌信息是合法的,
                因为以前存在多个查询器指向一个行车证信息的情况,而必须保证查询器和行车证信息是一一对应的
                所以必须要进行检查
                """
                if l_id not in got_ids:
                    """可以保留,检查是否有城市信息?那是是旧版的快捷方式特有的字段"""
                    city = g.get("city")
                    if city == "全国已开通城市":
                        """新版查询器"""
                        pass
                    else:
                        """旧版查询器"""
                        g["city"] = "全国已开通城市"
                        args = g.copy()
                        f = {"_id": args.pop("_id")}
                        u = {"$set": args}
                        cls.find_alone_and_update(filter_dict=f, update=u, upsert=False)
                    res.append(g)
                    got_ids.append(l_id)
                    plate_map[g_id] = license_dict[l_id].get("plate_number")
                else:
                    """已经有指向相同的行车证的查询器被保留了,再有指向相同行车证信息的查询器都需要被删除"""
                    f = {"_id": g_id}
                    cls.find_one_and_delete(filter_dict=f)
            else:
                """车牌信息不合法的查询器立即删除"""
                f = {"_id": g_id}
                cls.find_one_and_delete(filter_dict=f)
        """检查是否所有的行车证都有对应的查询器了?"""
        need_create = [x for x in license_list if x['_id'] not in got_ids]
        if len(need_create) > 0:
            for x in need_create:
                l_dbref = DBRef(database="platform_db", collection=CarLicense.get_table_name(), id=x['_id'])
                init = {
                    "plate_number": x.get("plate_number"),
                    "car_type": x.get("car_type"),
                    "vin_id": x.get("vin_id"),
                    "engine_id": x.get("engine_id"),
                    "city": "全国已开通城市" if x.get("city") is None else x['city'],  # 聚合数据不需要此字段
                    "user_id": user_dbref,
                    "car_license": l_dbref,
                    "create_date": now,
                    "all_count": 0,
                    "online_query_count": 0,
                    "today_online_query_count": 0,
                    "today_offline_query_count": 0
                }
                init = {k: v for k, v in init.items() if v is not None}
                g_id = cls.insert_one(**init)
                if g_id is None:
                    ms = "违章查询器插入失败,args={}".format(init)
                    logger.exception(ms)
                    print(ms)
                else:
                    init["_id"] = g_id
                    res.append(init)
                    plate_map[g_id] = license_dict[x["_id"]].get("plate_number")
        else:
            pass
        res = [{"_id": str(x['_id']), "plate_number": plate_map[x['_id']], "city": x['city']} for x in res]
        return res

    def update_count_online(self, last_query_result_id):
        """
        更新查询器在线查询的统计信息
        :param last_query_result_id: 查询结果集的id
        :return:
        """
        now = datetime.datetime.now()
        prev_date = self.get_attr("prev_date", datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
        now_str = now.strftime("%F")
        prev_date_str = prev_date.strftime("%F")
        """
        比较一下,看看是不是在同一天?同一天的话,today_online_query_count就加一.
        不是同一天的话,today_online_query_count=1
        """
        filter_dict = {"_id": self.get_id()}
        if prev_date_str == now_str:
            """同一天"""
            update_dict = {"$set": {"prev_date": now,
                                    "last_query_result_id": last_query_result_id},
                           "$inc": {"online_query_count": 1, "all_count": 1,
                                    "today_online_query_count": 1}}
        else:
            """不是同一天"""
            update_dict = {"$set": {"prev_date": now,
                                    "last_query_result_id": last_query_result_id,
                                    "today_online_query_count": 1
                                    },
                           "$inc": {"online_query_count": 1, "all_count": 1}
                           }
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)

    def update_count_offline(self):
        """更新查询器本地查询的统计信息"""
        now = datetime.datetime.now()
        prev_date_local = self.get_attr("prev_date_local", datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
        now_str = now.strftime("%F")
        prev_date_local_str = prev_date_local.strftime("%F")
        """
        比较一下,看看是不是在同一天?同一天的话,today_online_query_count就加一.
        不是同一天的话,today_online_query_count=1
        """
        filter_dict = {"_id": self.get_id()}
        if prev_date_local_str == now_str:
            """同一天"""
            update_dict = {
                "$inc": {"today_offline_query_count": 1, "all_count": 1}
            }
        else:
            update_dict = {
                "$set": {
                    "today_offline_query_count": 1,
                    "prev_date_local": now
                },
                "$inc": {"all_count": 1}
            }
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)

    @classmethod
    def insert_one(cls, **kwargs):
        """插入一个查询器对象，此方法覆盖了父类的方法,返回ObjectId"""
        plate_number = kwargs.pop("plate_number", None)
        engine_id = kwargs.pop("engine_id", None)
        vin_id = kwargs.pop("vin_id", None)
        car_type = kwargs.pop("car_type", None)
        result = None
        if plate_number is None or len(plate_number) < 7:
            logger.info("行车证信息plate_number参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif engine_id is None or len(engine_id) < 6:
            logger.info("行车证信息engine_id参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif car_type is None or len(car_type) < 2:
            logger.info("行车证信息car_type参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif vin_id is None or len(vin_id) < 6:
            logger.info("行车证信息vin_id参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        else:
            result = cls(**kwargs).save_plus()
        return result

    @classmethod
    def __query(cls, **kwargs):
        """
        从互联网查询违章，会查所有的违章记录，包含已处理的。
        :param kwargs:{"plateNumber":"苏A97P90"(车牌号，必填),
                       "engineNo":"YS669D"(发动机号，视城市规则是否必填),
                       "vin":"662722"(车架号，视城市规则是否必填),
                       "carType":"02"(车辆类型01大车02小车,不必填,默认小车),
                       "city":"杭州市"(查询城市,不必填,默认查归属地)}
        :return: 返回示意
        {
            "success": true,
            "data": {
                "token": "8045402120367843",    //用户身份标识
                "totalFine": "200",                           //未处理违章总罚款
                "totalPoints": 6,                               //未处理违章总扣分
                "untreated": 3,                                 //未处理违章条数
                "violations": [{
                        "code": "1232-D1",                  //违章编码,唯一，非违章条例码
                        "time": "2016-06-06 12:32:38",         //违章时间
                        "fine": "200.00",                      //罚款金额
                        "address": "文二西路口",         //违章地址
                        "reason": "您在 xx 路违反了交通规则",       //违章处理原因
                        "point": 6,                                //违章扣分
                        "province": "浙江省",               //省份
                        "city": "杭州市",                       //城市
                        "serviceFee": "23.00",            //服务费
                        "violationNum": 10180,                  //违章编码
                        "canSelect": 1,                         //能否勾选办理：0不可勾选, 1可勾选。
                        "processStatus": 1,                  //违章处理状态：1：未处理，2：处理中，3：已处理，4：不支持
                        "paymentStatus": 1                  //违章缴费状态 不返回表示无法获取该信息，1-未缴费 2-已缴
                }]
            }
        }
        """

        # args = {"plateNumber": "沪A0M084", "engineNo": "416098", "vin": "116280",
        #         "carType": "02", "city": "上海市"}
        # args = {"plateNumber": "赣EG2681", "engineNo": "091697", "vin": "010012",
        #         "carType": "02", "city": "上海市"}
        args = kwargs
        plateNumber = kwargs['plateNumber']
        ms = "raw查询违章参数:{}".format(args)
        logger.info(ms)
        json_str = json.dumps(args)  # 此接口的参数必须是json_str格式
        url = 'http://ddycapi.market.alicloudapi.com/violation/query'
        appcode = "e68af34cf135477caadcfc5b9816988f"
        headers = {"Authorization": "APPCODE {}".format(appcode)}
        ms = "查询违章参数:{}".format(json_str)
        logger.info(ms)
        resp = requests.post(url, data=json_str, headers=headers)
        if resp.status_code == 200:
            res = resp.json()
            data = dict()
            """转换数据为适合app端处理的格式，主要是key的名字转换"""
            transform_dict = {"totalFine": "total_fine", "totalPoints": "total_points",
                              "serviceFee": "service_fee", "canSelect": "can_select",
                              "processStatus": "process_status", "paymentStatus": "payment_status",
                              'violationNum': "violation_num", "violationCity": "violation_city",
                              "markFee": "mark_fee", "violations": "violations"}
            ms = "违章查询结果: {},查询参数{}".format(res, kwargs)
            logger.info(ms, exc_info=True, stack_info=True)
            print(res)
            if 'data' in res:
                for k, v in res['data'].items():
                    if k in transform_dict:
                        if k != "violations":
                            data[transform_dict[k]] = v
                        else:
                            vio_list = v
                            new_vio_list = list()
                            for vio in vio_list:
                                new_vio = dict()
                                new_vio['plateNumber'] = plateNumber
                                for k2, v2 in vio.items():
                                    if k2 in transform_dict:
                                        new_vio[transform_dict[k2]] = v2
                                    else:
                                        new_vio[k2] = v2
                                new_vio_list.append(new_vio)
                            data[k] = new_vio_list
                    else:
                        data[k] = v
                return {"success": True, "data": data}
            else:
                return res
        else:
            return {"success": False, 'message': '服务器未正确响应', 'errCode': resp.status_code}

    @classmethod
    def validate_query_args(cls, args_dict) -> bool:
        """
        检测一个违章查询参数是否合法.
        :param args_dict:
        :return:
        """

    @classmethod
    def query(cls, object_id, arg_dict: dict = None) -> dict:
        """
        查询违章，从api查询
        :param object_id: 查询器id
        :param arg_dict: 查询参数字典,调试的时候使用这个参数直接传值.平时不用
        :return: 查询结果的字典
        """
        message = {"message": "success"}
        if isinstance(arg_dict, dict):
            args = arg_dict
        else:
            object_id = mongo_db.get_obj_id(object_id)
            obj = cls.find_by_id(object_id)  # 查询器对象
            args = obj.get_query_args()
        result = TrafficViolationHandler.query_vio(**args)
        # result = cls.__query(**args)  # 节省资源先临时注销
        # result = {'success': True, 'data': {'amount': 9, 'totalFine': '0.00', 'totalPoints': 0, 'violations': [
        #     {'violationNum': '10180', 'province': '上海市', 'violationCity': '', 'time': '2017-04-12 08:53:29',
        #      'code': '49-466668', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '机动车不在机动车道内行驶的', 'address': '[嘉定]新源路泽普路东约10米', 'paymentStatus': 2, 'city': '上海市',
        #      'canSelect': 0},
        #     {'violationNum': '10391', 'province': '上海市', 'violationCity': '', 'time': '2017-03-11 08:14:20',
        #      'code': '49-466669', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '机动车违反临时停车规定且驾驶人不在现场的', 'address': '泽普路墨玉路东约99米', 'paymentStatus': 2, 'city': '上海市',
        #      'canSelect': 0},
        #     {'violationNum': '13450', 'province': '上海市', 'violationCity': '', 'time': '2017-01-31 14:02:05',
        #      'code': '49-466670', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '违反禁止标线指示', 'address': '淀山湖大道进漕盈公路东约5米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        #     {'violationNum': '13450', 'province': '上海市', 'violationCity': '', 'time': '2016-12-19 16:21:22',
        #      'code': '49-466671', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '违反禁止标线指示', 'address': 'S5沪嘉高速北侧近中环与汶水路交汇处路段', 'paymentStatus': 2, 'city': '上海市',
        #      'canSelect': 0},
        #     {'violationNum': '10180', 'province': '上海市', 'violationCity': '', 'time': '2016-10-10 16:06:26',
        #      'code': '49-466672', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '机动车不在机动车道内行驶的', 'address': '鹤旋路金运路北约5米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        #     {'violationNum': '10190', 'province': '上海市', 'violationCity': '', 'time': '2015-11-29 17:44:41',
        #      'code': '49-466673', 'markFee': '0', 'fine': '100', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '违反规定使用专用车道的', 'address': '汶水路/高平路（东向西，公交专用车道）', 'paymentStatus': 2, 'city': '上海市',
        #      'canSelect': 0},
        #     {'violationNum': '13440', 'province': '上海市', 'violationCity': '', 'time': '2015-08-01 15:36:00',
        #      'code': '49-466674', 'markFee': '0', 'fine': '200', 'point': 3, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '机动车违反禁令标志指示的', 'address': '佳通支路真南路北约116米', 'paymentStatus': 2, 'city': '上海市', 'canSelect': 0},
        #     {'violationNum': '10391', 'province': '上海市', 'violationCity': '', 'time': '2014-10-16 15:22:00',
        #      'code': '49-466675', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '机动车违反临时停车规定且驾驶人不在现场的', 'address': '墨玉路昌吉路南约168米', 'paymentStatus': 2, 'city': '上海市',
        #      'canSelect': 0},
        #     {'violationNum': '10390', 'province': '上海市', 'violationCity': '', 'time': '2013-08-14 15:07:00',
        #      'code': '49-466676', 'markFee': '0', 'fine': '200', 'point': 0, 'serviceFee': '0', 'processStatus': 3,
        #      'reason': '在禁止停放和临时停放机动车的地点停车，驾驶人不在现场或虽在现场但拒绝立即驶离，妨碍其他车辆行人通行的', 'address': '长寿路昌化路西约100米',
        #      'paymentStatus': 2,
        #      'city': '上海市', 'canSelect': 0}], 'untreated': 0}}
        if result['message'] == "success":
            """查询成功"""
            # data = result['data']
            """记录查询结果"""
            last_query_result_id = ViolationQueryResult.record(obj.user_id.id, object_id, result)
            """序列化"""
            result_obj = ViolationQueryResult.find_by_id(last_query_result_id)
            res = result_obj.read()
            message['data'] = res
            # message['data'] = data
            """更新查询器信息"""
            obj.update_count_online(last_query_result_id)
        else:
            ms = "在线违章查询结果:{}, args:{}".format(result, args)
            logger.info(ms)
            message['message'] = result['message']
            message['error_code'] = 0 if result.get('error_code') is None else result.get('error_code')
            message['args'] = {"generator_id": object_id}
        return message

    @classmethod
    def get_prev_query_result(cls, user_id, object_id):
        """
        获取上一次查询的结果,这个是正式用来查询的函数
        :param user_id: 用户id
        :param object_id: 查询器id
        :return: 可json化的字典/如果
        """
        message = {"message": "success"}
        user_id = mongo_db.get_obj_id(user_id)
        user_dbref = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=user_id)
        f = {"user_id": user_dbref}
        if isinstance(object_id, ObjectId):
            f['_id'] = object_id
        elif isinstance(object_id, str) and len(object_id) == 24:
            object_id = mongo_db.get_obj_id(object_id)
            f['_id'] = object_id
        else:
            pass
        generator = cls.find_one_plus(filter_dict=f, instance=True)
        if generator is None:
            l = cls.generator_list(user_id=user_id)
            if len(l) == 0:
                pass
            else:
                generator = cls(**l[0])
        else:
            pass
        if generator is None:
            data = {
                "amount": 0,
                "total_fine": 0,
                "total_points": 0,
                "untreated": 0,
                "plate_number": "",
                "violations": []
            }
            message['data'] = data
        else:
            object_id = object_id if object_id else generator.get_id()
            car_id = generator.get_attr("car_license").id
            """有对应的查询器"""
            now = datetime.datetime.now()
            try:
                prev_date = generator.get_attr("prev_date")  # 取上一次从互联网查询的时间,和现在的时间比较
                """
                如果prev_date是None,那就是没用过的的新查询器.直接就从互联网查了.
                interval_time = interval_seconds + 1 是为了创造大于interval_seconds的条件
                """
                if prev_date is None:
                    interval_time = interval_seconds + 1
                else:
                    interval_time = (now - prev_date).total_seconds()
                """检查查询的时间间隔"""
                # interval_time = 9999999999  # 调试时打开
                flag = False
                last_query_result_id = generator.get_attr("last_query_result_id")
                if last_query_result_id is None:
                    result_obj = None
                else:
                    """上一次查询记录"""
                    result_obj = ViolationQueryResult.find_by_id(last_query_result_id)
                """开始判断是否可以从互联网查询?"""
                if last_query_result_id is None:
                    flag = True
                elif result_obj is None:
                    """上一次查询记录被删除或者丢失了，那就从互联网查询一下"""
                    flag = True
                elif interval_time > interval_seconds:
                    """间隔大一天就从互联网读"""
                    flag = True
                    # if result_obj is None:
                    #
                    #     message = cls.query(object_id)
                    # else:
                    #     res = result_obj.read()
                    #     message['data'] = res
                    #     generator.update_count_offline()
                else:
                    """检查是否出发查询次数限制?现在的限制是一个查询器一天只能从网络查一次"""
                    today_online_query_count = generator.get_attr("today_online_query_count", 0)
                    flag = True if today_online_query_count < 1 else False
                # flag = True  # 调试时打开
                if flag:
                    """可以从互联网查询"""
                    message = cls.query(object_id)
                else:
                    """触发查询次数限制后从本地取"""
                    last_query_result_id = generator.last_query_result_id
                    result_obj = ViolationQueryResult.find_by_id(last_query_result_id)
                    res = result_obj.read()
                    message['data'] = res
                    generator.update_count_offline()
            except AttributeError as e:
                print(e)
                ms = "Error! case:{}, args:{}".format(e, str({"object_id": object_id}))
                logger.exception(ms, exc_info=True, stack_info=True)
                message = pack_message(message, 3008, object_id=object_id, car_id=car_id)
            except Exception as e:
                print(e)
                ms = "Error! reason:{},args:{}".format(e, str({"object_id": object_id}))
                logger.exception(ms, exc_info=True, stack_info=True)
                message = pack_message(message, 5000, object_id=object_id, car_id=car_id)
            finally:
                """
                返回的message.error_code的值:
                1. 如果是int,类型的.而且大于1000的,那就是包装过的.
                2. 如果是int类型的,小于1000的,那就是服务器返回的错误码
                3. 过是str类型的,那就是违章查询接口返回的错误码
                """
                error_code = message.get("error_code")
                if error_code is None or error_code == 0:
                    """正常的返回.没有错误"""
                    vio_data = message.get('data')
                    if isinstance(vio_data, dict):
                        """填充行车证相关信息"""
                        car = CarLicense.find_by_id(o_id=car_id, debug=True)
                        if isinstance(car, CarLicense):
                            car = car.get_dict()
                            data = message['data']
                            data['plate_number'] = car['plate_number'] if 'plate_number' in car else ""
                            data['car_model'] = car['car_model'] if 'car_model' in car else ""
                            data['car_id'] = str(car['_id'])
                            message['data'] = data
                    else:
                        message['args']['car_id'] = car_id
                        ms = "异常的违章查询结果:{}".format(str(message))
                        logger.exception(msg=ms)
                else:
                    ms = "查询违章接口发生错误error_code类型出错,error_code:{}".format(error_code)
                    print(ms)
                    city = generator.get_attr("city")
                    logger.exception(msg=ms, stack_info=True, exc_info=True)
                    error_code = int(error_code)
                    if isinstance(error_code, int) and error_code >= 1000:
                        """包装过的message"""
                        pass
                    elif isinstance(error_code, int) and error_code < 1000:
                        """
                        违章查询接口返回了错误的状态码
                        """
                        desc = "服务器返回了错误的状态码:{}".format(error_code)
                        ms = "{}, 查询器id:{}".format(desc, object_id)
                        logger.exception(ms)
                        message = pack_message(message, 7001, desc=desc, city=city, car_id=car_id)
                    else:
                        error_map = {
                            "1000": "系统异常",
                            "1001": "请求参数错误",
                            "1003": "违章查询请求参数错误",
                            "1012": "API接口调用过于频繁",
                            "1013": "查询失败	交管接口网络异常",
                            "1014": "查询中，请稍后再试",
                            "1015": "官方接口维护中",
                            "1016": "该接口不支持异地车牌查询",
                            "1020": "车辆信息错误",
                            "1021": "发动机号错误",
                            "1022": "车架号错误",
                            "1030": "车牌格式错误",
                            "1031": "该城市暂未开通",
                            "1032": "车架号或发动机号位数错误"}
                        if error_code in error_map:
                            desc = error_map[error_code]
                        else:
                            desc = "服务器返回了未识别的错误提示--error_code:{}".format(error_code)
                        message = pack_message(message, 7002, desc=desc, city=city, car_id=car_id)
        return message

    @classmethod
    def query_all(cls, user_id, to_flat_dict=True) -> dict:
        """
        一次获取所有查询器的结果
        :param user_id: 用户的id
        :param to_flat_dict: 是否转换成可json的字典
        :return: dict
        """
        user_id = mongo_db.get_obj_id(user_id)
        generator_list = cls.find(user_id=user_id)
        data = dict()
        for gen in generator_list:
            object_id = gen.get_id()
            result = cls.query(object_id, to_flat_dict)
            if to_flat_dict:
                object_id = str(object_id)
            data[object_id] = result
        return data

    @classmethod
    def delete_one(cls, object_id, user_id):
        """
        删除一个查询器generator
        :param object_id:  查询器id
        :param user_id: 用户id
        :return: message 字典
        """
        message = {"message": "success"}
        object_id = mongo_db.get_obj_id(object_id)
        generator = cls.find_by_id(object_id)
        user_id = mongo_db.get_obj_id(user_id)
        if user_id == generator.get_attr("user_id").id:
            """检查此查询器是否和用户身份吻合"""
            ses = mongo_db.get_conn(ViolationQueryResult.get_table_name())
            query = {"generator_id": object_id}
            count_1 = ses.count(query)
            res = ses.delete_many(filter=query)
            if res.deleted_count != count_1:
                """删除出错"""
                try:
                    raise MongoDeleteError("删除失败", [res.deleted_count, count_1], object_id=object_id, user_id=user_id)
                except MongoDeleteError as e:
                    print(e)
                    logger.error("删除失败", exc_info=True, stack_info=True)
                    message['message'] = "删除查询结果集异常，{}！={}".format(res.deleted_count, count_1)
            else:
                ses = mongo_db.get_conn(cls.get_table_name())
                query_2 = {"_id": object_id}
                count_2 = ses.count(filter=query_2)
                res = ses.delete_many(query_2)
                if res.deleted_count != count_2:
                    """删除出错"""
                    try:
                        raise MongoDeleteError("删除失败", [res.deleted_count, count_2], object_id=object_id,
                                               user_id=user_id)
                    except MongoDeleteError as e:
                        print(e)
                        logger.error("删除失败", exc_info=True, stack_info=True)
                        message['message'] = "删除查询器异常，{}！={}".format(res.deleted_count, count_2)
                else:
                    pass
        else:
            message = pack_message(message, 3011, user_id=user_id, object_id=object_id)
        return message

    @classmethod
    def repair_user_id(cls) -> None:
        """
        这是一个调试函数,用于把user_id的属性从旧的ObjectId转换为DBRef类型.
        :return:
        """
        f = {"user_id": {"$exists": True, "$type": 7}}
        res = cls.find_plus(filter_dict=f, to_dict=True)
        database = mongo_db.db_name
        collection = cls.get_table_name()
        for x in res:
            f = {"_id": x['_id']}
            ref = DBRef(database=database, collection=collection, id=x['user_id'])
            u = {"$set": {"user_id": ref, "repair": 1}}
            cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)


def add_plate_number():
    """把所有的违章记录都加上车牌号,这是一个调试专用函数"""
    rr = ViolationQueryResult.find()
    for r in rr:
        generator = VioQueryGenerator.find_by_id(r.get_attr('generator_id'))
        if generator is None:
            car = None
        else:
            car = CarLicense.find_by_id(generator.get_attr("car_license").id)
        if car is None:
            num = "沪A12345"
        else:
            num = car.get_attr("plate_number")
        vios = [x.id for x in r.get_attr("violations")]
        for v_id in vios:
            vio = ViolationRecode.find_by_id(v_id)
            vio.set_attr("plate_number", num)
            vio.save()


if __name__ == "__main__":
    import random
    u_id = ObjectId("59895177de713e304a67d30c")  # 上海市
    # g_id = ObjectId("5acac5214660d32418a93f3c")  # 信阳市
    g_id = ObjectId("5ac49aa74660d356cce9df9f")  # 违章查询器id
    q = {
        'vin': 'LGGX5D659GL327051', 'carType': '01', 'engineNo': 'L6AL3G00185', 'plateNumber': '赣CX3469', 'city': "宜春市"
    }
    """获取用户的违章查询器列表"""
    # print(VioQueryGenerator.generator_list(user_id=u_id))
    """利用违章查询器查询违章记录"""
    # vios = VioQueryGenerator.get_prev_query_result(user_id=u_id, object_id=ObjectId("5ae2ad74e39a7b41bd6d4100"))
    # print(vios)
    """测试直接调用查询接口的方法"""
    # print(VioQueryGenerator.query(g_id))
    # print(VioQueryGenerator.query(object_id=None, arg_dict=q))
    # r = ViolationQueryResult.find_by_id("5ae2b8c2e39a7b4cf7d7cc27")
    # print(r)
    """测试保存/更新违章记录"""
    # def random_args(num):
    #     res = {
    #         "can_select": 0,
    #         "code": "49-809554",
    #         "fine": 210.0,
    #         "position_id": ObjectId("5af547e4e39a7b5371943a4a"),
    #         "organ_name": "上海市公安局徐汇分局交通警察支队四大队",
    #         "user_id": ObjectId("5af547e4e39a7b5371943a4a"),
    #         "city": "上海市",
    #         "province": "上海市",
    #         "violation_city": "上海市",
    #         "plate_number": "沪A12345",
    #         "reason": "机动车违反规定停放(测试违章)",
    #         "point": 0,
    #         "violation_num": "1039A",
    #         "payment_status": "1",
    #         "address": "柳州路出宜山路北约{}米".format(random.randint(10, 20) * num),
    #         "update_time": mongo_db.get_datetime_from_str("2018-05-14T16:59:15.689Z"),
    #         "time": mongo_db.get_datetime_from_str("2018-05-{}T07:{}:00.000Z".format(10 + num,
    #                                                                                  random.randint(1, 59))),
    #         "process_status": 1,
    #         "forgery": True
    #     }
    #     return res
    # for i in range(3):
    #     vio = ViolationRecode(**random_args(i))
    #     vio.save_instance()
    """转换违章查询器的user_id属性为DBRef"""
    # VioQueryGenerator.repair_user_id()
    """转换所有的违章记录的处理状态为int类型"""
    # ff = {"process_status": {"$type": 2}}
    # rr = ViolationRecode.find_plus(filter_dict=ff, to_dict=True)
    # for r in rr:
    #     f = {"_id": r['_id']}
    #     u = {"$set": {"process_status": int(r['process_status'])}}
    #     ViolationRecode.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
    """导入处罚信息"""
    # Penalty.import_data()
    """匹配违章代码"""
    # vio = {"reason": "驾驶中型以上载客载货汽车、校车、危险物品运输车辆以外的其他机动车行驶超过规定时速20%以上未达到50%的"}
    # Penalty.match_code(vio)
    """修复违章记录中,没有违章代码的部分"""
    ViolationRecode.repair_violation_num()
    pass

