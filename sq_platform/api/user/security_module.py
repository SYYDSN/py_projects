# -*- coding:utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if project_dir not in sys.path:
    sys.path.append(project_dir)

import mongo_db
from uuid import uuid4
import numpy as np
from mongo_db import GeoJSON
from bson.objectid import ObjectId
import datetime
from log_module import get_logger
from bson.dbref import DBRef
from error_module import pack_message
from api.data.item_module import *
from manage.company_module import Dept, Employee
from extends.image_module import create_track_thumb_and_save_by_opencv
import random
import math
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError as ES_NotFoundError
import pickle


local_project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
"""缩略图的路径"""
thumb_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
thumb_dir = os.path.join(thumb_dir, 'static', 'thumb')
if not os.path.exists(thumb_dir):
    os.makedirs(thumb_dir)
path_dict = {
    "os.getcwd()": os.getcwd(),  # 程序运行目录
    "__file__": __file__,        # 脚本文件,目录,但不一定是绝对路径
    "os.path.realpath(__file__))": os.path.realpath(__file__),  # 保证是脚本的绝对路径
    "sys.path[0]": sys.path[0],     # 系统变量
    "sys.argv[0]": sys.argv[0]      # 同上,一个是目录一个是文件而已.
}
print(project_dir)
print(path_dict)



"""安全（评估）模块"""

logger = get_logger()
Binary = mongo_db.Binary


class SecurityLevel(mongo_db.BaseDoc):
    """安全等级"""
    _table_name = "security_level_info"
    type_dict = dict()

    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = DBRef  # 用户id，指向user_info表,指明此安全等级(评估)是属于哪个用户的?
    type_dict["total_mileage"] = float  # (起止时间内)总驾驶里程 单位公里
    type_dict["driving_hours_sum"] = float  # 总驾驶时长,单位小时
    type_dict["driving_hour_avg"] = float  # 平均驾驶时长,单位小时
    type_dict["speed_avg"] = float  # 平均驾驶速度,单位 公里/小时
    type_dict["emotion_status"] = int  # 情感状态,百分制
    type_dict["life_habits"] = int  # 生活习惯/日常习惯,百分制
    type_dict["driving_act"] = int  # 驾驶行为,百分制
    type_dict["fatigue_driving"] = int  # 疲劳驾驶,百分制
    type_dict["security_score"] = int  # 安全积分,百分制
    type_dict["security_rank"] = int  # (特定集体内的)安全等级排名,
    type_dict["begin_date"] = datetime.datetime  # 开始日期
    type_dict["end_date"] = datetime.datetime  # 结束日期
    type_dict["create_date"] = datetime.datetime  # 生成日期/查询日期
    type_dict['engine_version'] = str  # 引擎版本号
    type_dict["fictitious_values"] = list  # 此字段指明了对象中哪些数据是虚拟的?默认为空数组.

    def __init__(self, **kwargs):
        fictitious_values = list()
        factor = random.randint(5, 10)  # 因数
        score_pool = mongo_db.normal_distribution_range(0, 100, 1000, int)  # 公用的分值池
        if "speed_avg" not in kwargs:  # 平均驾驶速度,单位 公里/小时
            kwargs['speed_avg'] = random.choice(mongo_db.normal_distribution_range(30, 85, value_type=int))
            fictitious_values.append("speed_avg")

        if "driving_hour_avg" not in kwargs:  # 平均驾驶时长,单位小时
            kwargs['driving_hour_avg'] = random.choice(mongo_db.normal_distribution_range(7, 9))
            fictitious_values.append("driving_hour_avg")

        if "driving_hours_sum" not in kwargs:  # 总均驾驶时长,单位小时
            kwargs['driving_hours_sum'] = kwargs['driving_hour_avg'] * factor
            fictitious_values.append("driving_hours_sum")

        if "total_mileage" not in kwargs:  # 总驾驶里程 单位公里
            kwargs['total_mileage'] = kwargs['total_mileage'] * factor
            fictitious_values.append("total_mileage")

        if "emotion_status" not in kwargs:  # 情感状态,百分制
            kwargs['emotion_status'] = random.choice(score_pool)
            fictitious_values.append('emotion_status')

        if "life_habits" not in kwargs:  # 生活习惯/日常习惯,百分制
            kwargs['life_habits'] = random.choice(score_pool)
            fictitious_values.append('life_habits')

        if "driving_act" not in kwargs:  # 驾驶行为,百分制
            kwargs['driving_act'] = random.choice(score_pool)
            fictitious_values.append('driving_act')

        if "fatigue_driving" not in kwargs:  # 疲劳驾驶,百分制
            kwargs['fatigue_driving'] = random.choice(score_pool)
            fictitious_values.append('fatigue_driving')

        if "security_score" not in kwargs:  # 安全积分,百分制
            kwargs['security_score'] = random.choice(score_pool)
            fictitious_values.append('security_score')

        if "security_rank" not in kwargs:  # (特定集体内的)安全等级排名,
            kwargs['security_rank'] = random.randint(8, 30)
            fictitious_values.append('security_rank')

        if "create_date" not in kwargs:  # 生成日期/查询日期
            kwargs['create_date'] = datetime.datetime.now()

        super(SecurityLevel, self).__init__(**kwargs)

    @classmethod
    def get_security_rank_list(cls, user_id: str, dept_id: str = None, host_url: str = "") -> list:
        """
        获取当前用户所在公司和部门的安全等级的排名列表.
        :param user_id:用户id
        :param dept_id: 部门id,如果为空,则从self用户的直接管辖部门的id.
        :param host_url: 用来补全头像地址的host地址.
        :return:list(dict)
        字典说明:
        public int rank; 排名
        public int scr_synt; 驾驶综合分数
        public String driver_name; 司机姓名
        public String url_avatar； 司机头像地址
        """
        employee = Employee.find_by_id(user_id)
        if employee is None:
            ms = "错误的用户id:{}".format(user_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            company_id = employee.get_attr("company_id") if hasattr(employee, "company_id") else None
            if dept_id is None and hasattr(employee, "dept_path"):
                dept_id = employee.get_attr("dept_path")[-1]
            elif dept_id is None and not hasattr(employee, "dept_path"):
                dept_id = None
            else:
                dept = Dept.find_by_id(dept_id)
                if dept is None:
                    dept_id = None
                else:
                    dept_id = dept.get_dbref()
            # "$all"意思是dept_path包含dept_path后面的数组的全部内容即可
            query_dict = {"company_id": company_id, "dept_path": {"$all": [dept_id]}}
            employees = Employee.find(**query_dict)  # 同一公司,同一部门的所有员工.
            """创建虚拟数据"""
            length = len(employees)
            nums = list(np.arange(70, 96, 1))
            scores = [random.choice(nums) for i in range(length)]
            scores.sort(reverse=True)
            employees = [{
                "rank": str(i + 1),
                "driver_name": employee.get_attr("real_name") if employee.get_attr("real_name", None)
                else employee.get_attr("phone_num"),
                "url_avatar": host_url + employee.get_attr("head_img_url"),
                "scr_synt": str(scores[i])} for i, employee in enumerate(employees)]
            return employees

    @classmethod
    def get_security_indexes(cls, user_id: (ObjectId, str), count: int = 2) -> dict:
        """
        根据用户Id获取用户的(多个)安全指数,目前处于调试阶段.
        :param user_id:用户id
        :param count:返回几个报告? 默认是2个.
        :return:dict
        """
        score_pool = mongo_db.normal_distribution_range(50, 90, 1000, float)  # 公用的分值池
        indexes = [{
            "idx_1": random.choice(score_pool),  # 疲劳驾驶(指数),int类型,百分制.
            "idx_2": random.choice(score_pool),  # 驾驶行为(指数),int类型,百分制.
            "idx_3": random.choice(score_pool),  # 生活习惯(指数),int类型,百分制.
            "idx_4": random.choice(score_pool),  # 情绪状态(指数),int类型,百分制.
            "idx_5": random.choice(score_pool),  # 驾驶时长(指数),int类型,百分制.
            "idx_6": random.choice(score_pool)  # 驾驶里程(指数),int类型,百分制.
        } for i in range(count)]
        sum_time = random.randint(8, 10) * len(indexes)
        sum_mile = random.randint(600, 1100) * len(indexes)
        avg_speed = str(round((sum_mile / sum_time), 1))
        sum_time = str(round(sum_time, 1))
        sum_mile = str(round(sum_mile, 1))
        avg_cost = 0.0
        data = {
            "sum_time": sum_time,  # 全部时间, float类型.单位:分钟
            "sum_mile": sum_mile,  # 全部历程, float类型.单位:公里
            "avg_speed": avg_speed,  # 平均速度, float类型.单位:公里/小时
            "avg_cost": avg_cost,  # 平均时间, float类型.单位:分钟.目前此返回值的实际意义待定.
            "indexes": indexes  # 按去只能指数的集合
        }
        return data

    @classmethod
    def get_general(cls, user_id_list: list) -> (None, dict):
        """
        获取用户安全等级/指数/排行的总览信息,为管理平台服务.
        现在处于模拟阶段
        因为有排名,所以要整体返回.
        :param user_id_list: 用户id,ObjectId的数组.
        :return: dict/None 用户id(ObjectId类型)为key,安全总览为value的字典
        """
        length = len(user_id_list)
        # 分值池
        score_range = mongo_db.normal_distribution_range(55, 90, 1000)
        result = dict()
        values = list()
        for user_id in user_id_list:
            temp = {"user_id": user_id}
            if user_id == ObjectId("59cda7a4ad01be237680e280"):  # 程宗平 没有数据
                speed_avg = 0  # 平均速度
                temp['speed_avg'] = speed_avg
                driving_hours_sum = 0   # 总时长
                temp['driving_hours_sum'] = driving_hours_sum
                total_mileage = driving_hours_sum * speed_avg  # 总里程
                temp['total_mileage'] = total_mileage
                scr_synt = 0  # 安全指数
                temp['scr_synt'] = scr_synt
                fatigue_driving = 0  # 疲劳驾驶
                temp['fatigue_driving'] = fatigue_driving
                life_habits = 0  # 日常习惯
                temp['life_habits'] = life_habits
                emotion_status = 0  # 情感状态
                temp['emotion_status'] = emotion_status
                driving_act = 0  # 驾驶行为
                temp['driving_act'] = driving_act
            else:
                speed_avg = random.choice(score_range)  # 平均速度
                temp['speed_avg'] = speed_avg
                driving_hours_sum = random.randint(7, 20) * 8  # 总时长
                temp['driving_hours_sum'] = driving_hours_sum
                total_mileage = driving_hours_sum * speed_avg  # 总里程
                temp['total_mileage'] = total_mileage
                scr_synt = random.choice(score_range)  # 安全指数
                temp['scr_synt'] = scr_synt
                fatigue_driving = random.choice(score_range)  # 疲劳驾驶
                temp['fatigue_driving'] = fatigue_driving
                life_habits = random.choice(score_range)  # 日常习惯
                temp['life_habits'] = life_habits
                emotion_status = random.choice(score_range)  # 情感状态
                temp['emotion_status'] = emotion_status
                driving_act = random.choice(score_range)  # 驾驶行为
                temp['driving_act'] = driving_act
            values.append(temp)
        values.sort(key=lambda obj: obj['scr_synt'], reverse=True)
        for index, value in enumerate(values):
            key = value.pop("user_id")
            value['rank'] = index + 1
            result[key] = value
        return result


class DrivingEvent(mongo_db.BaseDoc):
    """行车事件,比如超速，急刹，急加速，打手机等，每个事件
       和安全模块的BadAction类相关
    """
    _table_name = "driving_event_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = DBRef  # 用户id，指向user_info表
    type_dict["loc"] = GeoJSON  # 事件发生坐标 [经度, 纬度]
    type_dict["begin_date"] = datetime.datetime  # 事件开始时间
    type_dict["end_date"] = datetime.datetime  # 事件结束时间
    type_dict['event_type'] = str  # 事件类型，比如超速，急刹，急加速，打手机等
    type_dict['engine_version'] = str  # 引擎版本号

    def __init__(self, **kwargs):
        if "user_id" not in kwargs:
            ms = "user_id不能为空"
            raise ValueError(ms)
        if "loc" not in kwargs:
            ms = "loc不能为空"
            raise ValueError(ms)
        if "event_type" not in kwargs:
            ms = "event_type"
            raise ValueError(ms)
        if "begin_date" not in kwargs:
            ms = "begin_date"
            raise ValueError(ms)
        super(DrivingEvent, self).__init__(**kwargs)


class SecurityReport(mongo_db.BaseDoc):
    """
    安全报告,此报告是从安全模块查询而来
    :param date_obj: date_obj 报告日期,现阶段的报告都是按天切分的.
    安全报告字典说明如下：
    begin_date': '2017-11-12',                  # 报告的开始日期,
    'end_date': '2017-11-12',                    # 报告的结束日期,
    'create_date': '2017-11-13 12:00:05.340',  # 报告的生成日期,
    'sum_mile': 7406.0,                          # 行驶里程, float类型.单位:公里.
    'sum_time': 688,                             # 行驶时间, float类型.单位:分钟.
    'scr_synt': 72,                              # 综合分数, float类型,百分制
    'idx_slep': 0,                               # 睡眠 0好 1坏
    'idx_mood': 0,                               # 情绪 0好 1坏
    'idx_heal': 0,                               # 健康 0好 1坏



    'cnt_make_call': 1,                          # 打电话次数
    'cnt_play_phon': 3,                          # 看手机
    'cnt_fati_driv': 1,                          # 疲劳驾驶次数
    'cnt_shar_turn': 1,                          # 急转弯次数. int类型.
    'cnt_rapi_acce': 0,                          # 急加速次数. int类型.
    'cnt_over_sped': 6,                          # 超速次数. int类型.
    'cnt_sudd_brak': 6,                          # 急刹车次数. int类型.
    :return:一个安全报告(dict字典)
    """
    _table_name = "security_report_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = DBRef  # 用户id，指向user_info表                user_id, begin_date和end_ate构成联合唯一主键
    type_dict['driving_event'] = list()  # 驾驶事件列表,指向DrivingEvent类, DBRef的list
    type_dict["sum_mile"] = float  # 总里程
    type_dict["scr_synt"] = int  # 综合分数, 对用户安全等级的综合评分。百分制
    type_dict["idx_slep"] = int  # 睡眠 0好 1坏
    type_dict["idx_heal"] = int  # 健康 0好 1坏
    type_dict["idx_mood"] = int  # 情绪 0好 1坏
    type_dict["sum_time"] = int  # 本次报告所涉及的驾驶时长的累计。单位分钟
    type_dict["cnt_make_call"] = int  # 打电话次数
    type_dict["cnt_play_phon"] = int  # 看手机
    type_dict["cnt_fati_driv"] = int  # 疲劳驾驶次数
    type_dict["cnt_rapi_acce"] = int  # 急加速统计，int，单位次。
    type_dict["cnt_shar_turn"] = int  # 急转弯统计，int，单位次，包含左转和右转。
    type_dict["cnt_sudd_brak"] = int  # 急刹车统计，int，单位次。
    type_dict["cnt_over_sped"] = int  # 超速统计，int，单位次。
    type_dict["begin_date"] = datetime.datetime  # 安全报告统计的开始日期  user_id, begin_date和end_ate构成联合唯一主键
    type_dict["end_date"] = datetime.datetime  # 安全报告统计的结束日期    user_id, begin_date和end_ate构成联合唯一主键
    type_dict["create_date"] = datetime.datetime  # 安全报告的生成日期/查询日期
    type_dict['url_polyline'] = str  # 相关轨迹缩略图 图片以文件形式保存在磁盘上，这里只是一个url
    type_dict['engine_version'] = str  # 引擎版本号
    type_dict["fictitious_values"] = list  # 此字段指明了对象中哪些数据是虚拟的?默认为空数组.

    def __init__(self, **kwargs):
        """由于安全报告需要生成，耗时，所以不因该在查询的时候才生成实例，而是由后台的异步任务队列批量的安全报告"""
        city_names = ["上海", "天津", "北京", "苏州", "无锡", "南京", "杭州", "宁波", "武汉", "长沙", "常州", "广州", "福州",
                      "厦门", "深圳", "成都", "重庆", "郑州", "合肥", "徐州", "济南", "青岛", "太原", "石家庄"]
        fictitious_values = list()
        factor = random.randint(5, 10)  # 因数
        score_pool = mongo_db.normal_distribution_range(50, 90, 1000, int)  # 公用的分值池

        if "user_id" not in kwargs:
            ms = "user_id不能为空"
            raise ValueError(ms)
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()

            fictitious_values.append("total_mileage")
        if "sum_mile" not in kwargs:  # 报告涉及周期的总里程,单位 公里
            kwargs['sum_mile'] = kwargs['total_mileage'] = random.choice(mongo_db.normal_distribution_range(100, 600, value_type=int))
            fictitious_values.append("sum_mile")
        if "scr_synt" not in kwargs:  # 综合分数
            kwargs['scr_synt'] = random.choice(score_pool)
            fictitious_values.append("scr_synt")
        if "idx_slep" not in kwargs:  # 睡眠
            kwargs['idx_slep'] = random.choice([0, 1])
            fictitious_values.append("idx_slep")
        if "idx_mood" not in kwargs:  # 情绪
            kwargs['idx_mood'] = random.choice([0, 1])
            fictitious_values.append("idx_mood")
        if "idx_heal" not in kwargs:  # 健康
            kwargs['idx_heal'] = random.choice([0, 1])
            fictitious_values.append("idx_heal")
        if "sum_time" not in kwargs:  # 本次报告所涉及的驾驶时长的累计。单位分钟
            kwargs['sum_time'] = random.randint(70, 90) * factor
            fictitious_values.append("sum_time")
        if "cnt_make_call" not in kwargs:  # 打电话次数
            kwargs['cnt_make_call'] = random.randint(0, factor * 2)
            fictitious_values.append("cnt_make_call")
        if "cnt_play_phon" not in kwargs:  # 看手机
            kwargs['cnt_play_phon'] = random.randint(0, factor * 2)
            fictitious_values.append("cnt_play_phon")
        if "cnt_fati_driv" not in kwargs:  # 疲劳驾驶次数
            kwargs['cnt_fati_driv'] = random.choice([0, 0, 0, 0, 1, 1, 2])
            fictitious_values.append("cnt_fati_driv")
        if "cnt_rapi_acce" not in kwargs:  # 急加速统计
            kwargs['cnt_rapi_acce'] = random.randint(0, factor * 2)
            fictitious_values.append("cnt_rapi_acce")
        if "cnt_shar_turn" not in kwargs:  # 急转弯统计
            kwargs['cnt_shar_turn'] = random.randint(0, factor * 2)
            fictitious_values.append("cnt_shar_turn")
        if "cnt_sudd_brak" not in kwargs:  # 急刹车统计
            kwargs['cnt_sudd_brak'] = random.randint(0, factor * 2)
            fictitious_values.append("cnt_sudd_brak")
        if "cnt_over_sped" not in kwargs:  # 超速统计
            kwargs['cnt_over_sped'] = 0  # 超速统计容易惹麻烦,不要显示.(顺丰有车载设备监控速度)
            fictitious_values.append("cnt_over_sped")

        super(SecurityReport, self).__init__(**kwargs)

    def to_app_format(self) -> dict:
        """
        专门为了迎合app端显示的方法,主要是把结果中的DBRef进行适合json化的转换.
        :return: 一个适合app端显示的字典
        """
        res = {k: v['$id'] if k == "user_id" else v for k, v in self.to_flat_dict().items()}
        return res

    @classmethod
    def create_report_track_thumb(cls, track_list: list, user_id: (str, ObjectId) = None,
                                  report_id: (str, ObjectId) = None) -> (str, None):
        """
        生成安全报告涉及的驾驶路线的回放轨迹的缩略图.
        :param track_list: 生成图像的数据，一般情况是Track实例的doc文档组成的数组
        :param user_id: 用户id
        :param report_id: 报告id
        :return: 图片url
        """
        """先拼接存储路径"""
        file_name = '{}.png'.format(str(report_id))
        dir_path = os.path.join(thumb_dir, 'track', str(user_id))
        # dir_path = os.path.join(thumb_dir, 'track', "demo")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, file_name)
        try:
            create_track_thumb_and_save_by_opencv(track_list, file_path)
            res = file_path.split(local_project_dir)[-1].lstrip("\\").lstrip("/")
            return res
        except Exception as e:
            logger.exception("保存文件失败:{}".format(e))
            print(e)

    @classmethod
    def get_report_detail(cls, report_id: (str, ObjectId) = None, user_id: (str, ObjectId) = None) -> dict:
        """
        根据报告id查询安全报告,这是一个临时的方法,并未对参数进行正确的处理.仅仅为了配合app的调试.非完成状态
        :param report_id: 安全报告id
        :param user_id: 用户id,此参数正式的时候将被废止
        :return: 一个经过to_app_format方法处理的实例对象的dict.
        """
        user_id = mongo_db.DBRef(id=ObjectId("59895177de713e304a67d30c"), collection="user_info", database="platform_db")
        instance = cls(user_id=user_id)
        res = instance.to_app_format()
        return res

    @classmethod
    def global_report(cls, user_id: (str, ObjectId)) -> (dict, None):
        """
        获取某人的整体安全报告,统计的周期涵盖用户的全部使用周期. 为管理平台服务.提供司机详情所需的部分资料
        本函数现阶段为模拟阶段. 非完成状态
        :param user_id: 用户id
        :return: dict
        """
        if user_id is None:
            ms = "{} Error, 用户i的不能为空".format(sys._getframe().f_code.co_name)
            logger.exception(ms)
            raise ValueError(ms)
        elif not isinstance(user_id, ObjectId):
            user_id = mongo_db.get_obj_id(user_id)
        else:
            pass
        user_id = mongo_db.DBRef(id=user_id, collection="user_info",
                                 database="platform_db")
        instance = cls(user_id=user_id)
        if not isinstance(instance, cls):
            ms = "{} Error, 创建cls实例失败,user_id:{}".format(sys._getframe().f_code.co_name, user_id)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            res = instance.to_flat_dict()
            return res

    @classmethod
    def get_list(cls, user_id: (str, ObjectId), begin_date: (datetime.datetime, datetime.date, str) = None,
                 end_date: (datetime.datetime, datetime.date, str) = None) -> list:
        """
        获取安全报告的列表,此接口将被废止而被get_report_history替代.现阶段仅仅模拟返回一个列表.2017-11-14
        :param user_id:用户id,
        :param begin_date:报告涉及的的开始日期. 2017-12-12格式的,
        :param end_date:报告涉及的的结束日期. 2017-12-12格式的,
        :return:安全报告的list[SecurityReport.instance,....]
        """
        raw_user_id = user_id
        if isinstance(user_id, str):
            user_id = mongo_db.get_obj_id(user_id)
        if not isinstance(user_id, ObjectId):
            try:
                ms = "{} 不是一个合法的user_id".format(raw_user_id)
                raise ValueError(ms)
            except ValueError as e:
                logger.exception("Error")
                raise e
            finally:
                pass
        else:
            user = User.find_by_id(user_id)
            if not isinstance(user, User):
                try:
                    ms = "user_id:{} 找不到对应的用户".format(raw_user_id)
                    raise ValueError(ms)
                except ValueError as e:
                    logger.exception("Error")
                    raise e
                finally:
                    pass
            else:
                user_id = user.get_dbref()
                now = datetime.datetime.now()
                default_count = random.randint(2, 5)  # 至少生成2个报告
                reports = [cls(create_date=(now - datetime.timedelta(days=i)), user_id=user_id).to_app_format() for i in range(default_count)]
                return reports

    @staticmethod
    def acce_and_grav(acce_list: list, grav_list: list)-> list:
        """
        暂时不知道如何实现
        输入加速度传感器和重力传感器的数据,混合到一起,方便观察.
        通过计算,得出时间轴上的加速度变化的数据.
        :param acce_list: 加速度数据, Sensor的实例的数组
        :param grav_list: 重力数据, Sensor的实例的数组
        :return: 混合后的加速度和重力数据, Sensor的实例的数组
        """
        prev_grav = None
        index_grav = 0
        for index, acce in enumerate(acce_list):
            if prev_grav is None:
                grav = None
                try:
                    grav = grav_list[index_grav]
                except IndexError:
                    pass
                finally:
                    if not isinstance(grav, Sensor):
                        pass
                    else:
                        a_time = acce.get_attr('time')
                        g_time = grav.get_attr('time')
                        delta = (g_time - a_time).total_seconds()
                        if delta == 0:
                            """加速度和重力采集的时间一致"""
                            acce.__dict__['gr_x'] = grav.get_attr("gr_x")
                            acce.__dict__['gr_y'] = grav.get_attr("gr_y")
                            acce.__dict__['gr_z'] = grav.get_attr("gr_z")
                            prev_grav = grav
                        elif delta < 0:
                            """重力取样较早,假设三轴的值的变化是线性的,为了计算更合理的值,需要查看下一个重力元素是否更接近加速度的取样时间点"""
                            prev_grav = grav
                            flag = True
                            index_grav = index
                            while flag:
                                next_grav = None
                                try:
                                    index_grav += 1
                                    next_grav = grav_list[index_grav]
                                except IndexError:
                                    break
                                finally:
                                    if not isinstance(next_grav, Sensor):
                                        ms = "grav_list的长度不足:{}".format(index_grav)
                                        print(ms)
                                        break
                                    else:
                                        temp_time = next_grav.get_attr("time")
                                        if temp_time == acce.get_attr("time"):
                                            """取样时间等于当前加速度传感器的取样时间,达到目的了"""
                                            acce.__dict__['gr_x'] = next_grav.get_attr("gr_x")
                                            acce.__dict__['gr_y'] = next_grav.get_attr("gr_y")
                                            acce.__dict__['gr_z'] = next_grav.get_attr("gr_z")
                                            prev_grav = next_grav
                                            break
                                        elif temp_time > acce.get_attr("time"):
                                            """取样时间大于当前加速度传感器的取样时间,达到目的了,计算开始"""
                                            """先计算线性常数"""
                                            next_grav_time = next_grav.get_attr("time")
                                            time_range = (next_grav_time - prev_grav.get_attr("time")).total_seconds()

                                            p_gr_x = prev_grav.get_attr("gr_x")
                                            p_gr_y = prev_grav.get_attr("gr_y")
                                            p_gr_z = prev_grav.get_attr("gr_z")

                                            k_x = (next_grav.get_attr("gr_x") - p_gr_x) / time_range
                                            k_y = (next_grav.get_attr("gr_y") - p_gr_y) / time_range
                                            k_z = (next_grav.get_attr("gr_z") - p_gr_z) / time_range

                                            variable_time = abs(delta)
                                            variable_x = variable_time * k_x
                                            variable_y = variable_time * k_y
                                            variable_z = variable_time * k_z

                                            acce.__dict__['gr_x'] = p_gr_x + variable_x
                                            acce.__dict__['gr_y'] = p_gr_y + variable_y
                                            acce.__dict__['gr_z'] = p_gr_z + variable_z
                                            """计算完成"""
                                            flag = False
                                        else:
                                            prev_grav = next_grav
                        else:
                            """如果地一个重力传感器就比加速传感器晚.那就直接pass"""
                            pass
            else:
                """如果不是第一个数据"""
                grav = None
                try:
                    grav = grav_list[index_grav]
                except IndexError:
                    pass
                finally:
                    if not isinstance(grav, Sensor):
                        pass
                    else:
                        a_time = acce.get_attr('time')
                        g_time = grav.get_attr('time')
                        delta = (g_time - a_time).total_seconds()
                        if delta == 0:
                            """加速度和重力采集的时间一致"""
                            acce.__dict__['gr_x'] = grav.get_attr("gr_x")
                            acce.__dict__['gr_y'] = grav.get_attr("gr_y")
                            acce.__dict__['gr_z'] = grav.get_attr("gr_z")
                            prev_grav = grav
                        elif delta < 0:
                            """重力取样较早,假设三轴的值的变化是线性的,为了计算更合理的值,需要查看下一个重力元素是否更接近加速度的取样时间点"""
                            prev_grav = grav
                            flag = True
                            index_grav = index
                            while flag:
                                next_grav = None
                                try:
                                    index_grav += 1
                                    next_grav = grav_list[index_grav]
                                except IndexError:
                                    break
                                finally:
                                    if not isinstance(next_grav, Sensor):
                                        ms = "grav_list的长度不足:{}".format(index_grav)
                                        print(ms)
                                        break
                                    else:
                                        temp_time = next_grav.get_attr("time")
                                        if temp_time == acce.get_attr("time"):
                                            """取样时间等于当前加速度传感器的取样时间,达到目的了"""
                                            acce.__dict__['gr_x'] = next_grav.get_attr("gr_x")
                                            acce.__dict__['gr_y'] = next_grav.get_attr("gr_y")
                                            acce.__dict__['gr_z'] = next_grav.get_attr("gr_z")
                                            prev_grav = next_grav
                                            break
                                        elif temp_time > acce.get_attr("time"):
                                            """取样时间大于当前加速度传感器的取样时间,达到目的了,计算开始"""
                                            """先计算线性常数"""
                                            next_grav_time = next_grav.get_attr("time")
                                            time_range = (next_grav_time - prev_grav.get_attr("time")).total_seconds()

                                            p_gr_x = prev_grav.get_attr("gr_x")
                                            p_gr_y = prev_grav.get_attr("gr_y")
                                            p_gr_z = prev_grav.get_attr("gr_z")

                                            k_x = (next_grav.get_attr("gr_x") - p_gr_x) / time_range
                                            k_y = (next_grav.get_attr("gr_y") - p_gr_y) / time_range
                                            k_z = (next_grav.get_attr("gr_z") - p_gr_z) / time_range

                                            variable_time = abs(delta)
                                            variable_x = variable_time * k_x
                                            variable_y = variable_time * k_y
                                            variable_z = variable_time * k_z

                                            acce.__dict__['gr_x'] = p_gr_x + variable_x
                                            acce.__dict__['gr_y'] = p_gr_y + variable_y
                                            acce.__dict__['gr_z'] = p_gr_z + variable_z
                                            """计算完成"""
                                            flag = False
                                        else:
                                            prev_grav = next_grav
                        else:
                            """如果地一个重力传感器就比加速传感器晚.那就直接pass"""
                            pass

    @classmethod
    def generate_report(cls, user_id: DBRef, begin_date: datetime.datetime, end_date: datetime.datetime,
                        report_id: ObjectId = None):
        """
        根据用户id和起止时间，生成安全报告
        这是一个底层函数,不应该用户直接调用.
        按天生成报告推荐.create_instance_by_day函数
        :param user_id: 用户id
        :param begin_date: 
        :param end_date: 
        :param report_id: 报告id，用于重建报告时使用。
        :return: 报告的实例
        """
        print((end_date - begin_date).days)
        """先取gps数据"""
        filter_dict = {
            "user_id": user_id,
            "time": {"$gte": begin_date, "$lte": end_date}
        }
        sort_dict = {"time": 1}
        gps_list = GPS.find_plus(filter_dict=filter_dict, sort_dict=sort_dict)
        gps_list_length = len(gps_list)
        if gps_list_length == 0:
            # print("没有gps数据")
            pass
        else:
            """处理gps数据"""
            print("gps数据长度： {}".format(len(gps_list)))
            simple_gps_list = mongo_db.reduce_list(gps_list)  # 精简数据
            """计算里程,时常和平均速度,返回 {"mileage":mileage, "total_time": total_time, "avg_speed":avg_speed}"""
            temp_dict = GPS.mile_time_speed(simple_gps_list)

            """
            依次取其他传感器数据.这里有个传感器相关类型的说明的副本.原始文件在
            file_module下面的file_to_mongodb函数的type_transform_dict变量.
            {"rec_acce": {"sensor_type": "accelerate", "description": "加速度传感器"},
            "rec_grav": {"sensor_type": "gravitation", "description": "重力传感器(GV-sensor)"},
            "rec_gyro": {"sensor_type": "gyroscope", "description": "陀螺仪传感器(Gyro-sensor)"},
            "rec_rota": {"sensor_type": "rotation vector", "description": "旋转矢量传感器(RV-sensor)"},
            "rec_magn": {"sensor_type": "magnetism", "description": "磁力传感器(M-sensor)"},
            "rec_bpm": {"sensor_type": "beat per minute", "description": "心率传感器"}}
                                   
            """
            """没有合理的算法,暂停处理传感器数据"""
            # """处理加速度传感器数据"""
            # filter_dict['sensor_type'] = 'accelerate'
            # file_name = "acce.pkl"
            # file_path = os.path.join(current_path, file_name)
            # if os.path.exists(file_path):
            #     f = open(file_path, "rb")
            #     acce_list = pickle.load(f)
            #     f.close()
            # else:
            #     acce_list = Sensor.find_plus(filter_dict=filter_dict)
            #     out_put = open(file_path, 'wb')
            #     pickle.dump(acce_list, out_put)
            #     out_put.close()
            # print(len(acce_list))
            # """处理重力传感器数据"""
            # filter_dict['sensor_type'] = 'gravitation'
            # file_name = "grav.pkl"
            # file_path = os.path.join(current_path, file_name)
            # if os.path.exists(file_path):
            #     f = open(file_path, "rb")
            #     grav_list = pickle.load(f)
            #     f.close()
            # else:
            #     grav_list = Sensor.find_plus(filter_dict=filter_dict)
            #     out_put = open(file_path, 'wb')
            #     pickle.dump(grav_list, out_put)
            #     out_put.close()
            # """用重力加速度数据来修正加速度数据"""
            # cls.acce_and_grav(acce_list, grav_list)

            """轨迹缩略图"""
            report_id = ObjectId(None) if report_id is None else report_id
            args = {
                "_id": report_id,  # 报告id,
                "user_id": user_id,
                "report_name": uuid4().hex[0: 12],  # 出车编号，为了迎合app的字段。
                "begin_date": begin_date,  # 报告开始时间
                "end_date": end_date,  # 报告的结束时间
                "report_time": end_date  # 报告时间
            }
            args.update(temp_dict)
            url_poly_line = cls.create_report_track_thumb(gps_list, user_id.id, report_id)
            args['url_polyline'] = url_poly_line
            instance = cls(**args)
            return instance

    @classmethod
    def virtual_data(cls, user_report_list,  setting_dict: dict = None) -> list:
        """
        根据用户id，对一个人的一段时间内的数据进行综合评估，虚拟出一些数据，比如，情绪指数，睡眠质量等。
        还可以根据人为指定的情绪指数和睡眠质量来生成报告
        :param user_report_list: 用户的安全报告的实例的数组
        :param setting_dict:  设定字典，是以日期的字符串为key，emotion_status（精神状态），
        life_habits（生活习惯/睡眠状态）做value的字典。比如：
        {"2017-12-12":{"emotion_status":43.2, "life_habits":76.1}}
        :return:
        """
        l = len(user_report_list)
        avg_speed = sum([x.get_attr('avg_speed') for x in user_report_list]) / l  # 单位 公里/小时
        avg_time = sum([x.get_attr('sum_time') for x in user_report_list]) / l  # 单位 分钟
        res = list()
        for report in user_report_list:
            cur_time = report.get_attr('sum_time')
            cur_speed = report.get_attr('avg_speed')
            life_habits = 90 if avg_time / cur_time > 1.8 else (50 if avg_time / cur_time < 0.5 else 75)
            emotion_status = 90 if cur_speed / avg_speed > 1.5 else (50 if cur_speed / avg_speed < 0.5 else 75)
            k_time = math.log(cur_time / avg_time) / math.log(1.3)
            k_speed = math.log(cur_speed / avg_speed) / math.log(1.3)
            k = k_time - k_speed  # 用驾驶时长和速度算出来的系数
            look_phone = round(0 if (random.randint(4, 6) + k) < 0 else (random.randint(4, 6) + k))  # 看手机
            breaks = abs(round(0 if (random.randint(4, 6) + k) < 0 else (random.randint(4, 6) + k)))  # 急刹车
            call_phone = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2])
            if k > 0:
                call_phone = abs(round(call_phone + math.log(k) / math.log(2)))
                accs = round(breaks + math.log(k) /math.log(2))
            elif k == 0:
                accs = breaks
            else:
                accs = abs(round(abs(breaks - math.log(abs(k)) / math.log(2))))
            look_phone = (call_phone + random.randint(0, 2)) if call_phone > look_phone else look_phone
            turns = random.randint(round(min([accs, breaks]) * 0.5), round(max([accs, breaks])))
            print(call_phone)
            report.add_attr('emotion_status', emotion_status)
            report.add_attr('life_habits', life_habits)
            report.add_attr('cnt_rapi_acce', accs if accs < 20 else accs - random.randint(5, 10))
            report.add_attr('cnt_shar_turn', turns if turns < 20 else turns - random.randint(5, 10))
            report.add_attr('cnt_sudd_brak', breaks if breaks < 20 else breaks - random.randint(5, 10))
            report.add_attr('look_phone', look_phone)
            report.add_attr('call_phone', call_phone)
            report.add_attr('scr_synt', (emotion_status + life_habits) / 2 + random.randint(1, 5))   # 综合分数
            report.save()
            res.append(report)

        return res

    @classmethod
    def create_instance_by_day(cls, user_id: (str, ObjectId), day: (str, datetime.date, datetime),
                               rebuild: bool = False):
        """
        按天生成安全报告优先使用此函数.
        根据日期和用户id,创建一个SecurityReport的实例并返回.如果存在相同的实例,那就返回以前的实例.
        :param user_id: 用户id
        :param day: 日期.
        :param rebuild: 找到相同安全报告的时候,是否重新生成?
        :return:SecurityReport的实例.
        """
        if user_id is None or day is None:
            ms = "user_id: {}, day: {} 不能为空".format(user_id, day)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            try:
                user_id = mongo_db.get_obj_id(user_id)
                day = mongo_db.get_datetime_from_str(day)
                if day is None:
                    day = datetime.datetime.today().strftime("%F")
                else:
                    day = day.strftime("%F")
                begin_date = mongo_db.get_datetime_from_str("{} 00:00:00".format(day))
                end_date = mongo_db.get_datetime_from_str("{} 23:59:59".format(day))
                user = User.find_by_id(user_id)
                if not isinstance(user, User):
                    ms = "无效的user_id: {}".format(user_id)
                    logger.exception(ms)
                    raise ValueError(ms)
                else:
                    user_dbref = user.get_dbref()
                filter_dict = {"user_id": user_dbref, "begin_date": begin_date, "end_date": end_date}
                instance = cls.find_one_plus(filter_dict=filter_dict, instance=True)
                if instance is None:
                    """没有这个对象,需要创建一下"""
                    instance = cls.generate_report(**filter_dict)
                elif rebuild:
                    """,或者rebuild为真值."""
                    filter_dict['report_id'] = instance.get_id()
                    instance = cls.generate_report(**filter_dict)
                else:
                    print("从数据库中查询到对应的安全报告： {}".format(filter_dict))
                    pass
                if instance is None:
                    pass
                else:
                    instance.save()
                return instance
            except ValueError:
                pass

    @classmethod
    def batch_create_instance_in_background(cls, prev_day: int = 1, rebuild: bool =False) -> None:
        """
        批量生产安全报告，这个方法一般是用来批量（重新）生成数据的。也可以给异步队列做定时任务
        比如每天凌晨00：30：00生成头一天的安全报告,(此方法不能生成当天的报告)
        也可以用来批量重建用户的安全报告。
        :param prev_day: 往前回溯几天生成报告？默认只生成前一天的。
        :param rebuild: 当报告已存在的情况下，是否重新生成报告？
        :return:
        """
        all_user_id = User.get_all_user_id()
        today = datetime.datetime.today()
        prev_day += 1
        days = list(range(1, prev_day))
        for i in days:
            delta = datetime.timedelta(days=i)
            current_date = today - delta
            print(current_date)
            [cls.create_instance_by_day(user_id, current_date, rebuild) for user_id in all_user_id]

    @classmethod
    def virtual_data_generator(cls, yesterday: bool = False, rebuild: bool = False, begin_str: str = None):
        """
        批量虚拟报告数据，11月15号之后的
        :param yesterday: 是否只生成昨天的报告?如果不是,就要看begin_str参数的设定.
        :param rebuild: 是否重建报告
        :param begin_str: 如果yesterday是True,那么此字段无效.否则此字段表示的就是查询报告的开始时间.
                          如果为None,则前推15天为开始时间.
        :return: 数据字典  用户id的ObjectId为key,报告为value
        """
        begin_str = "2017-11-15 0:0:0"
        yesterday_date_str = mongo_db.get_datetime(-1, True).split(" ")[0]  # 昨天日期的字符串格式
        end_time = mongo_db.get_datetime_from_str("{} 23:59:59".format(yesterday_date_str))
        if yesterday:
            begin_time = mongo_db.get_datetime_from_str("{} 0:0:0".format(yesterday_date_str))
        elif begin_str is None:
            begin_time = mongo_db.get_datetime_from_str("{} 0:0:0".format(mongo_db.get_datetime(-15, True).split(" ")[0]))
        else:
            begin_time = mongo_db.get_datetime_from_str(begin_str)
            if begin_time is None:
                begin_time = mongo_db.get_datetime_from_str(
                    "{} 0:0:0".format(mongo_db.get_datetime(-15, True).split(" ")[0]))
        filter_dict = {
            "report_time": {
                "$gte": begin_time,
                "$lte": end_time
            },
            "sum_mile": {"$gte": 100}
        }
        sort_dict = {"report_time": -1}
        reports = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict,)
        a_dict = {}
        for report in reports:
            user_id = report.get_attr("user_id").id
            if not rebuild:
                # 检查是否生成过虚拟数据
                scr_synt = report.get_attr("scr_synt")
                if scr_synt is None:
                    rebuild = True  # 需要重建虚拟数据
                else:
                    pass
            if user_id not in a_dict:
                a_dict[user_id] = [report]
            else:
                temp_list = a_dict[user_id]
                temp_list.append(report)
                a_dict[user_id] = temp_list
        if rebuild:
            data_dict = {}
            for user_id, report_list in a_dict.items():
                values = cls.virtual_data(report_list)
                data_dict[user_id] = values
        else:
            data_dict = a_dict
        return data_dict

    @classmethod
    def get_report_history(cls, user_id: (str, ObjectId), end_day: datetime.datetime = datetime.datetime.today(),
                           begin_day: datetime.datetime = None, can_json: bool = True) -> list:
        """
        根据用户id查询用户的安全报告的历史记录,返回用户的安全报告的列表,按时间倒序排列.
        :param user_id: 用户id,
        :param end_day:  结束时间, 默认是今天
        :param begin_day:  开始时间
        :param can_json:  返回的数据是否为json做好了准备?默认是.否则返回的是实例的list
        :return:
        """
        if begin_day is None:
            delta = datetime.timedelta(days=10)
            begin_day = end_day - delta
        """先取今天的安全报告,因为今天的安全报告需要计算"""
        report_today = cls.create_instance_by_day(user_id=user_id, day=end_day, rebuild=True)
        """其他时间的报告从数据库查询"""
        end_day = end_day - datetime.timedelta(days=1)
        end_day = end_day.strftime("%F")
        begin_day = begin_day.strftime("%F")
        begin_date = mongo_db.get_datetime_from_str("{} 00:00:00".format(begin_day))
        end_date = mongo_db.get_datetime_from_str("{} 23:59:59".format(end_day))
        filter_dict = {
            "user_id": User.find_by_id(user_id).get_dbref(),
            "report_time": {"$lte": end_date, "$gte": begin_date}
        }
        sort_dict = {"report_time": -1}
        result_list = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict)
        result_list.insert(0, report_today)
        if can_json:
            result_list = [x.to_flat_dict() for x in result_list]
        return result_list

    @classmethod
    def query_report(cls, prefix: str, user_id: str = None, date_str: str = None) -> list:
        """
        从ai模块查询安全报告
        精简查询方法http://localhost:9200/haogle/log/_search?pretty&filter_path=hits.hits
        :param prefix: 公司前缀,查询的url标识,默认是sf.
        :param user_id: 用户id,如果为None表示查询所有用户
        :param date_str:  日期,2017-12-12格式,查哪一天的报告?None表示查询最后一份报告
        :return: 数据字典的list。
        """
        if prefix is None:
            prefix = 'sf'
        if prefix.lower() == "sq":
            prefix = 'sf'   # 现阶段,苏秦的都使用sf的前缀

        es = Elasticsearch(['http://safego:safego.org@api.safego.org:9200'])
        # es = Elasticsearch(['http://safego:safego.org@api.safego.org:9200/sf/daily_report/'])

        l = 1000
        must_list = list()
        query = {
            "query": {
                "bool": {
                    "must": must_list
                }
            }
        }
        if isinstance(user_id, ObjectId):
            must_list.append({"match": {"id": str(user_id)}})
        elif isinstance(user_id, str) and len(user_id) == 24:  # 有用户id
            must_list.append({"match": {"id": user_id}})
        if date_str is not None:
            dates = date_str.split(" ")
            if len(dates) < 2:
                must_list.append({"match": {"report_datetime": dates[0]}})
            else:
                """时间区间查询"""
                query['query']['bool']['filter'] = {
                    "range": {
                        "report_datetime": {
                            "gte": dates[0],
                            "lte": dates[1]
                        }
                    }
                }
        else:
            """date_str为None是查询最后一个安全报告"""
            l = 100
            sort_dict = {
                "report_datetime": {
                    "order": "desc"
                }
            }
            query['sort'] = sort_dict
        res = []
        if len(must_list) == 0:
            pass
        else:  # 查询某天的报告
            query['query']['bool']['must'] = must_list

            # res = es.search(body=query, size=size, filter_path="hits.hits") # filter_path参数是过滤器,只留下此数据
            try:
                res = es.search(index=prefix, doc_type="daily_report", body=query, size=l)
                total = res['hits']['total']  # 总共有读少返回记录?
                ms = "elasticsearch query success! at {}, user_id:{},date:{}共计查询到{}条记录".format(
                    mongo_db.get_datetime(), user_id, date_str, total)
                print(ms)
                logger.info(ms)
                res = res['hits']['hits']
            except ES_NotFoundError as e:
                logger.exception("elasticsearch Error:")
                print(e)
                raise e
            except ConnectionError as e:
                logger.exception("elasticsearch Error:")
                print(e)
                raise e
            finally:
                pass
        return res


class HealthReport(mongo_db.BaseDoc):
    """
    健康报告类,是安全报告的一部分,也可以被独立引用,
    注重的是安全相关的信息,例如: 心跳,情绪,睡眠时间等等.
    限于技术问题,现阶段只记录心跳数据.简单的说,就是把心跳
    数据从传感器数据中提取出来单独保存.
    """
    _table_name = "health_report_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = DBRef  # 用户id，指向user_info表
    type_dict["heart_rate"] = dict  # 心率的值的字典,{"14:00","value":84,....} 每小时采样的心率值.
    type_dict["date"] = datetime.datetime  # 健康报告的时间  2017-12-12 00:00:00的datetime格式
    """
    user_id + date 联合唯一索引
    mongodb查询字典的长度的办法:find({$where:"Object.keys(this.heart_rate).length>1"})  注意这是个javascript方法,效率并不高.
    """

    @classmethod
    def exists(cls, user_id: DBRef, the_date: datetime.datetime):
        """
        根据用户id和日期,检查对应的健康报告是否存在.
        :param user_id: 用户id.不能为None
        :param the_date: 如果对应的实例已存在,是否需要重新生成?False会返回以前生成的实例.
        :return: doc或者None
        """
        filter_dict = {
            "user_id": user_id,
            "date": the_date
        }
        res = cls.find_one_plus(filter_dict=filter_dict, instance=False)
        return res

    @classmethod
    def get_instance(cls, user_id: (ObjectId, str), the_date: (datetime.datetime, str), rebuild: bool = False):
        """
        根据用户id和日期,从数据库查询对应的距离或者在记录不存在时从传感器集合获取数据生成一个记录,然后保存,返回实例.
        建议使用此方法替代__init__来创建实例,可以避免重复创建的问题.
        :param user_id: 用户id.不能为None
        :param the_date: datetime.datetime对象,或者类似2017-12-12 12:34:00/2017-12-12 这样的日期字符串,程序本身会自动去除时间
                         中的小时,分,秒的部分,只剩下年月日
        :param rebuild: 如果对应的实例已存在,是否需要重新生成?False会返回以前生成的实例.
        :return:实例
        """
        user = User.find_by_id(user_id)
        if not isinstance(user, User):
            raise ValueError("错误的用户id:{}".format(user_id))
        else:
            user_id = user.get_dbref()
            date = mongo_db.round_datetime(mongo_db.get_datetime_from_str(the_date))
            doc = cls.exists(user_id, date)
            if doc is None or rebuild:
                heart_rate_dict = cls.__get_heart_rate(user_id, date)
                instance = cls(**{"user_id": user_id, "date": date, "heart_rate": heart_rate_dict})
                save_result = None
                try:
                    save_result = instance.save()
                except Exception as e:
                    print(e)
                finally:
                    if isinstance(save_result, ObjectId):
                        return instance
                    elif save_result == 0:
                        raise ValueError("重复的实例")
                    else:
                        raise ValueError("保存实例失败,请检查日志")
            else:
                return cls(**doc)

    @classmethod
    def __get_heart_rate(cls, user_id: DBRef, the_date: datetime.datetime) -> dict:
        """
        按照指定条件从sensor_info查询心率数据,然后进行适当的处理后,返回一个字典的数组.此函数为类的内部调用方法,所以不做
        类型转换检测,也不建议除cls方法之外调用.
        :param user_id: user_id: 用户id.不能为None
        :param the_date: datetime.datetime对象,
        :return: {"00:00":84,"01:00":84.....}
        """
        date_str = the_date.strftime("%F")
        begin_date = datetime.datetime.strptime("{} 00:00:00.000".format(date_str), "%Y-%m-%d %H:%M:%S.%f")
        end_date = datetime.datetime.strptime("{} 23:59:59.999".format(date_str), "%Y-%m-%d %H:%M:%S.%f")
        filter_dict = {
            "user_id": user_id,
            "sensor_type": "beat per minute",
            "time": {"$lte": end_date, "$gte": begin_date},
            "bpm": {"$nin": [None, '']}
        }
        sort_dict = {"time": -1}
        projection = ["time", "bpm"]
        """data是字典的数组,不是instance的数组"""
        data = Sensor.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, projection=projection, to_dict=True)
        """按小时,求平均值"""
        res_dict = {}
        """先按小时分类聚集"""
        for record in data:
            key_str = record['time'].hour
            temp = res_dict.get(key_str)
            if temp is None:
                temp = [int(record['bpm']) if isinstance(record['bpm'], str) else record['bpm']]
            else:
                temp.append(int(record['bpm']) if isinstance(record['bpm'], str) else record['bpm'])
            res_dict[key_str] = temp
        """再求值"""
        res_dict = {"{}:00".format(str(k).zfill(2)): int(round(sum(v) / len(v))) for k, v in res_dict.items()}
        return res_dict


if __name__ == "__main__":
    u_id = ObjectId("59f19d8dad01be4d918cacb7")
    my_id = ObjectId("59895177de713e304a67d30c")
    date_str = "2017-11-16"
    # date_str = "2017-11-15"
    # SecurityReport.create_instance_by_day(u_id, date_str, True)
    #############################################################
    # SecurityReport.batch_create_instance_in_background(prev_day=15, rebuild=1)
    ###########################################################
    # SecurityReport.get_report_history(u_id, datetime.datetime.strptime("2017-11-15", "%Y-%m-%d"))
    # report = SecurityReport.create_instance_by_day(u_id, date_str, True)
    # SecurityReport.virtual_data_generator(rebuild=True)
    # '59cda57bad01be0912b352da 59cda886ad01be237680e28e 59cda964ad01be237680e29d'
    # print(SecurityReport.query_report("sf", "59cda964ad01be237680e29d", "2017-12-21"))
    # print(SecurityReport.query_report("sf", "59cda964ad01be237680e29d", "2018-01-02"))
    print(SecurityReport.query_report("sf", "59cda964ad01be237680e29d", "2018-01-03 2018-01-11"))
    # print(HealthReport.get_instance(ObjectId("59cda964ad01be237680e29d"), "2017-12-25").to_flat_dict())
    pass