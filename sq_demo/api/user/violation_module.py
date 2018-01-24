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
from api.data.item_module import User
from bson.objectid import ObjectId
from bson.dbref import DBRef
from error_module import pack_message
from error_module import RepeatError
from error_module import MongoDeleteError
from api.data.item_module import CarLicense
from api.data.item_module import Position
from celery_module import query_position


"""违章查询模块"""


logger = get_logger()
interval_seconds = 56400


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


class ViolationRecode(mongo_db.BaseDoc):
    """违章记录"""
    _table_name = "violation_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_id'] = ObjectId  # 关联用户的id
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

    def exist(self):
        """
        检查一条违章记录是否已存在？
        1. 存在且完全相同就不做更新。
        2. 存在不同就update
        3. 不存在就insert
        :return: DBRef对象。
        """
        """先构建判断唯一的查询条件"""
        query_dict = {"code": self.code, "address": self.address,
                      "time": self.time, "violation_num": str(self.violation_num)}
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
                        self.update_time = mongo_db.get_datetime(to_str=False)
                        self._id = query_obj.get_id()
                        query_obj = query_obj.check_position()  # 检查位置信息
                        self.position_id = query_obj.position_id
                        break
            if flag:
                """有差异"""
                dbref = self.save_self_and_return_dbref()
            else:
                dbref = query_obj.get_dbref()
        return dbref

    @classmethod
    def all_vio(cls, user_id):
        """查询某用户的全部的违章记录"""
        user_id = mongo_db.get_obj_id(user_id)
        result = cls.find(user_id=user_id)
        return result

    @classmethod
    def instance(cls, **kwargs):
        """
        创建一个违章记录的实例,应该用此方法创建实例
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

        violations = self.violations
        vio_list = list()
        if len(violations) == 0:
            pass
        else:
            for dbref in violations:
                vio = ViolationRecode.get_instance_from_dbref(dbref)
                vio = vio.check_position()
                vio_list.append(vio.to_flat_dict())
        self.violations = vio_list
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
        if not data_dict['success']:
            """data_dict['success']==False表示没有查询成功,这时候不计数"""
            pass
        else:
            """查询成功，检查是否有数据"""
            data = data_dict['data']
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
                    obj = ViolationRecode.instance(**vio)
                    dbref = obj.exist()
                    vio_list.append(dbref)
                kwargs['violations'] = vio_list
            return cls.insert_one(**kwargs)


class VioQueryGenerator(mongo_db.BaseDoc):
    """违章查询器"""
    _table_name = "violation_query_generator_info"

    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_id'] = ObjectId  # 关联用户的id
    type_dict['car_license'] = DBRef  # 关联的行车证（上的有关信息）
    type_dict['city'] = str  # 查询的城市
    type_dict['create_date'] = datetime.datetime  # 查询器的创建时间
    type_dict['prev_date'] = datetime.datetime  # 查询器的上一次使用时间(从网络)
    type_dict['last_query_result_id'] = ObjectId  # 查询器的上一次的结果集的id(从网络)
    type_dict['all_count'] = int  # 查询器的使用计数，包括本地查询
    type_dict['online_query_count'] = int  # 查询器的使用计数(从网络)
    type_dict['today_online_query_count'] = int  # 查询器的当日使用计数(从网络)
    type_dict['today_offline_query_count'] = int  # 查询器的当日使用计数

    @classmethod
    def create(cls, **kwargs):
        """工厂函数，此函数会创建CarLicense对象。仅仅用于添加一个包含此函数会创建CarLicense的
        DBRef对象的实例。
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
        user_id = mongo_db.get_obj_id(user_id)
        plate_number = kwargs.pop("plate_number")
        engine_id = kwargs.pop("engine_id")
        vin_id = kwargs.pop("vin_id")
        car_type = kwargs.pop("car_type")
        city = kwargs.get("city")
        if city is None:
            raise KeyError("city 参数必须")
        else:
            """检查唯一性"""
            if VioQueryGenerator.is_only(user_id, plate_number, city):
                car_type = "小车" if str(car_type) == "02" else "大车"
                """插入行车证/车牌信息"""
                car_license = CarLicense.insert_and_return_dbref(plate_number=plate_number, car_type=car_type,
                                                                 vin_id=vin_id, engine_id=engine_id, user_id=user_id)
                """"检查此car_license是否已在user的cars属性中？"""
                user = User.find_by_id(user_id)
                user.in_list("car_license", CarLicense.get_instance_from_dbref(car_license))
                kwargs["car_license"] = car_license
                kwargs["user_id"] = user_id
                kwargs['create_date'] = datetime.datetime.now()
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
    def is_only(cls, user_id, plate_number, city):
        """
        检查是否有相同车牌和城市的违章查询其
        :param user_id:  用户id
        :param plate_number:  车牌
        :param city: 城市
        :return: boolean
        """
        user_id = mongo_db.get_obj_id(user_id)
        result_query = cls.find(city=city, user_id=user_id)
        flag = True
        for x in result_query:
            _id = x.car_license.id
            if _id is None:
                pass
            else:
                temp = CarLicense.find_by_id(_id)
                if temp is not None and temp.plate_number.upper() == plate_number.upper():
                    flag = False
                    break
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
            data['city'] = "" if self.__dict__.get("city") is None else self.city
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
    def generator_list(cls, user_id):
        """
        查询用户名下所有的查询器
        :param user_id: 用户id
        :return:  字典的list
        """
        user_id = mongo_db.get_obj_id(user_id)
        data = list()
        generators = cls.find(user_id=user_id)
        for generator in generators:
            _id = generator.get_id()
            city = generator.city
            children_id = generator.car_license.id
            children = CarLicense.find_one(_id=children_id)
            if children is not None:
                plate_number = children.plate_number
                temp = {"_id": str(_id), "plate_number": plate_number, "city": city}
                data.append(temp)
            else:
                pass
        return data

    def update_count_online(self, last_query_result_id):
        """更新查询器在线查询的统计信息
        last_query_result_id 查询结果集的id
        """
        filter_dict = {"_id": self.get_id()}
        update_dict = {"$set": {"prev_date": datetime.datetime.now(),
                                "last_query_result_id": last_query_result_id},
                       "$inc": {"online_query_count": 1, "all_count": 1,
                                "today_online_query_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)

    def update_count_offline(self):
        """更新查询器本地查询的统计信息"""
        filter_dict = {"_id": self.get_id()}
        update_dict = {"$inc": {"today_offline_query_count": 1, "all_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)

    @classmethod
    def insert_one(cls, **kwargs):
        """插入一个查询器对象，此方法覆盖了父类的方法,返回ObjectId"""
        plate_number = kwargs.get("plate_number")
        engine_id = kwargs.get("engine_id")
        city = kwargs.get("city")
        user_id = kwargs.get("user_id")
        vin_id = "" if kwargs.get("vin_id") is None else kwargs.get("vin_id")
        car_type = "02" if kwargs.get("car_type") is None else kwargs.get("car_type")
        result = None
        if plate_number is None or len(plate_number) != 6:
            logger.info("参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif engine_id is None or len(engine_id) < 6:
            logger.info("参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif city is None or len(city) < 2:
            logger.info("参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        elif not isinstance(user_id, ObjectId):
            logger.info("参数错误:{}".format(str(kwargs)), exc_info=True, stack_info=True)
        else:
            arg = {"user_id": user_id, "plate_number": plate_number}
            obj_id = CarLicense.find_one_and_insert(**arg)
            if obj_id is None:
                pass
            else:
                dbref = CarLicense.create_dbref(obj_id)
                arg = {"user_id": user_id, "city": city, "car_license": dbref}
                result = cls(**arg).insert()
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
    def check_query_count(cls, user_id):
        """
        检查当日的查询次数。用于辅助判断是从数据库查询还是从互联网查询
        :param user_id: 用户的id
        :return: 布尔值,代表是否可以从互联网查询
        """
        user_id = mongo_db.get_obj_id(user_id)
        obj_list = cls.find(user_id=user_id)  # 客户名下所有的查询器
        max_limited = 1  # 未验证用户的每天的最大查询次数。
        count = 0  # 计数器
        now = datetime.datetime.now()
        if len(obj_list) > 0:
            for generator in obj_list:
                try:
                    prev_date = generator.prev_date
                    if isinstance(prev_date, datetime.datetime):
                        total_seconds = (now - prev_date).total_seconds()
                        if total_seconds < interval_seconds:
                            """如果相隔不到一天"""
                            count += 1
                        else:
                            pass
                except AttributeError:
                    pass
        else:
            pass
        flag = False
        if count < max_limited:
            flag = True
        else:
            pass
        return flag

    @classmethod
    def query(cls, object_id, to_flat_dict=True) -> dict:
        """
        查询违章，从api查询
        :param object_id: 查询器id
        :param to_flat_dict: 是否转换成可json的字典
        :return: 查询结果的字典
        """
        message = {"message": "success"}
        object_id = mongo_db.get_obj_id(object_id)
        ses = mongo_db.get_conn(cls._table_name)
        obj = cls.find_by_id(object_id)  # 查询器对象
        args = obj.get_query_args()
        result = cls.__query(**args)  # 节省资源先临时注销
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
        if result['success']:
            """查询成功"""
            # data = result['data']
            """记录查询结果"""
            last_query_result_id = ViolationQueryResult.record(obj.user_id, object_id, result)
            """序列化"""
            result_obj = ViolationQueryResult.find_by_id(last_query_result_id)
            res = result_obj.read()
            message['data'] = res
            # message['data'] = data
            """更新查询器信息"""
            obj.update_count_online(last_query_result_id)
        else:
            message['message'] = result['message']
            message['error_code'] = result['errCode']
            message['args'] = str({"generator_id": object_id})
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
        object_id = mongo_db.get_obj_id(object_id)
        generator = cls.find_by_id(object_id)
        user_id = mongo_db.get_obj_id(user_id)
        if user_id == generator.user_id:
            """检查此查询器是否和用户身份吻合"""
            now = datetime.datetime.now()
            try:
                prev_date = generator.prev_date
                interval_time = (now - prev_date).total_seconds()
                """检查查询的时间间隔"""
                if interval_time < interval_seconds:
                    """间隔小于一天就从数据库里读"""
                    last_query_result_id = generator.last_query_result_id
                    result_obj = ViolationQueryResult.find_by_id(last_query_result_id)
                    if result_obj is None:
                        """上一次查询记录被删除或者丢失了，那就从互联网查询一下"""
                        message = cls.query(object_id)
                    else:
                        res = result_obj.read()
                        message['data'] = res
                        generator.update_count_offline()
                else:
                    """大于一天优先从网络读"""
                    user_id = generator.user_id
                    flag = cls.check_query_count(user_id)
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
                logger.exception("Error! args:{}".format(str({"object_id": object_id})), exc_info=True, stack_info=True)
                raise ValueError("{}不合法".format(object_id))
                message = pack_message(message, 3008, object_id=object_id)
            finally:
                pass
        else:
            message = pack_message(message, 3011, user_id=str(user_id), generator_id=str(object_id))
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
        if user_id == generator.user_id:
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


if __name__ == "__main__":
    args = {"plateNumber": "赣EG2681", "engineNo": "091697", "vin": "010012",
            "carType": "02", "city": "上海市"}
    # args = {'carType': '02', 'vin': '118936', 'plateNumber': '苏ER52Y5', 'city': '上海市', 'engineNo': 'x74922'}
    args = {"plate_number": "赣EG2681", "engine_id": "091697", "vin_id": "010012",
            "car_type": "02", "city": "上海市"}
    args = {'city': '苏州市', 'vin': '118936', 'engineNo': 'x74922', 'plateNumber': '苏ER52Y5', 'carType': '02'}
    # query(**args)
    # user_id = {"user_id": ObjectId("59895177de713e304a67d30c")}
    # vio = VioQueryGenerator.find_by_id(ObjectId("598951e7de713e304a67d31f"))
    # obj = vio.my_car_license()
    history = VioQueryGenerator.get_input_history("59895177de713e304a67d30c")
    print(history)
    # query(**{"plate_number": "苏ER52Y5", "engine_id": "x74922", "vin_id": "118936",
    #         "car_type": "02", "city": "苏州市"})
    # res = VioQueryGenerator.get_prev_query_result(ObjectId("598d6ac2de713e32dfc74796"), ObjectId("59df38c3ad01be642b5d9074"))
    # print(res)
    pass

