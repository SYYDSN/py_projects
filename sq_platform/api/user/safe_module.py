# -*- coding:utf8 -*-
import mongo_db
from bson.objectid import ObjectId
import datetime
from log_module import get_logger
from bson.dbref import DBRef
from error_module import pack_message


"""安全（评估）模块"""


logger = get_logger()


class SafeLevel(mongo_db.BaseDoc):
    """安全等级"""
    _table_name = "safe_level_info"
    type_dict = dict()

    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = ObjectId  # 用户id，指向user_info表
    type_dict["driver_fatigue"] = float   # 疲劳驾驶
    type_dict["driver_mileage"] = float  # 驾驶里程
    type_dict["driver_time"] = float  # 驾驶时长
    type_dict["emotion_status"] = float  # 情感状态
    type_dict["daily_habits"] = float  # 生活习惯/日常习惯
    type_dict["driver_behaviour"] = float  # 驾驶行为
    type_dict["safe_integral"] = float  # 安全积分
    type_dict["create_date"] = datetime.datetime  # 生成日期
    type_dict['engine_version'] = str  # 引擎版本号


class DriverRecode(mongo_db.BaseDoc):
    """行车记录类"""
    _table_name = "driver_recode_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = ObjectId  # 用户id，指向user_info表
    type_dict["begin_date"] = datetime.datetime  # 开始日期
    type_dict["end_date"] = datetime.datetime  # 结束日期
    type_dict["driver_mileage"] = float  # 本次行驶里程
    type_dict["driver_events"] = list  # 本次行驶中发生的事件，是DriverEvent对象的objectId组成的数组
    type_dict['engine_version'] = str  # 引擎版本号

    def __init__(self, **kwargs):
        if "driver_events" not in kwargs:
            kwargs['driver_events'] = list()
        super(DriverRecode, self).__init__(**kwargs)

    def add_event_id(self, event_id: ObjectId)->None:
        """
        添加一个行车事件的id
        :param event_id:
        :return:
        """
        if isinstance(event_id, ObjectId):
            if event_id not in self.driver_events:
                self.driver_events.append(event_id)
            else:
                try:
                    raise KeyError("重复的ObjectId")
                except KeyError as e:
                    print(e)
                    logger.error("Error: ", exc_info=True, stack_info=True)
        else:
            try:
                raise TypeError("类型错误")
            except TypeError as e:
                print(e)
                logger.error("Error: ", exc_info=True, stack_info=True)


class DriverEvent(mongo_db.BaseDoc):
    """行车事件,比如超速，急刹，急加速，打手机等，每个事件"""
    _table_name = "driver_event_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = ObjectId  # 用户id，指向user_info表
    type_dict["begin_date"] = datetime.datetime  # 事件开始时间
    type_dict["end_date"] = datetime.datetime  # 事件结束时间
    type_dict['event_type'] = str  # 时间类型，比如超速，急刹，急加速，打手机等
    type_dict['engine_version'] = str  # 引擎版本号


if __name__ == "__main__":
    safe = DriverRecode.find_by_id(ObjectId("598d7466de713e389daa193a"))

    print(safe.push_batch("driver_events", [123, 456, 4545]))