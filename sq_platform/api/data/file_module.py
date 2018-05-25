# -*-coding:utf-8-*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
from log_module import get_logger
from log_module import recode
import datetime
import warnings
import os
import shutil
import zipfile
import requests
import re
import json
from api.data.item_module import User
from api.data.item_module import *
import threading
import warnings


"""文件处理模块，主要是zip文件的读取和格式化"""

cache = mongo_db.cache
work_key = "working_zipfile"
logger = get_logger()
zip_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), "static",
                            'data_file')
if not os.path.exists(zip_dir_path):
    os.makedirs(zip_dir_path)
print("zip_dir_path is {}".format(zip_dir_path))
move_file_lock = threading.Lock()  # 移动/删除文件的多线程锁
work_lock = threading.Lock()  # join_work/pop_work的锁


"""重启服务时，清除工作列表的缓存"""
cache.set(work_key, list())


def join_work(zip_path: str, key: str = "working_zipfile") -> bool:
    """
    记录一个文件正在进行解压和读取工作
    :param zip_path: zip文件路径
    :param key: cache用的key
    :return: bool 返回True表示可以执行任务，返回False表示此文件已经在工作中了，无需再进行解压和读取。
    """
    global work_lock
    lock = work_lock
    lock.acquire()
    values = cache.get(key)
    timeout = 60 * 5
    if values is None or len(values) == 0:
        values = [zip_path]
        cache.set(key, values, timeout=timeout)
        result = True
    else:
        if zip_path in values:
            result = False
        else:
            values.append(zip_path)
            cache.set(key, values, timeout=timeout)
            result = True
    lock.release()
    return result


def pop_work(zip_path: str, key: str = "working_zipfile") -> None:
    """
    取消一个文件正在进行解压和读取工作的标记
    :param zip_path: zip文件路径
    :param key: cache用的key
    :return: None
    """
    global work_lock
    lock = work_lock
    lock.acquire()
    values = cache.get(key)
    timeout = 60 * 5
    if values is None or len(values) == 0:
        pass
    else:
        if zip_path not in values:
            pass
        else:
            values.remove(zip_path)
            cache.set(key, values, timeout=timeout)
    lock.release()


def transform_date(file_path: str) -> datetime.datetime:
    """
    把文件名转换为时间格式，主要是用于对zip文件的排序
    :param file_path: 包含绝对路径的文件名
    :return: 时间
    """
    if not isinstance(file_path, str):
        raise TypeError("文件名必须是str类型，而不能是{}".format(type(file_path)))
    else:
        if os.path.exists(file_path):
            date_str = str(os.path.split(file_path)[1].split(".")[0])
            date_obj = None
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d-%H-%M-%S")
            except ValueError as e:
                # print(e)
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%Y_%m_%d_%H_%M_%S")
                except Exception as e1:
                    logger.exception("Error:")
                    raise e1
            return date_obj
        else:
            warnings.warn(message="文件 {0} 不存在或 {0} 不是有效的绝对路径".format(file_path))


def join_item(dict_item: dict, new_item: dict) -> dict:
    """
    往一个字典追加键值对，返回字典，用于列表推导时的操作
    :param dict_item: 原始dict
    :param new_item: 准备加进去的键值对
    :return: 最终结果
    """
    if isinstance(dict_item, dict) and isinstance(new_item, dict):
        if "ts" in dict_item:
            time_s = dict_item.pop('ts')
            dict_item['time'] = time_s
        if "sp" in dict_item:
            speed_s = dict_item.pop('sp')
            dict_item['speed'] = speed_s
        dict_item.update(new_item)
    return dict_item


def parse_content(content: str, user_id: str = None, app_version: str = None) -> list:
    """
    解析压缩文件的内容，返回传感器数据字典组成的数组
    :param content:  压缩文件内容
    :param user_id:  所属用户id，
    :param app_version:  app版本号，
    :return: list[dict]
    """
    pattern = r'\{.+?\}'  # 注意+号后面的？ 那是防止进入w贪婪模式的符号
    str_list = re.findall(pattern, content, re.M)
    extend_dict = {"user_id": user_id} if app_version is None else {"user_id": user_id, "app_version": app_version}
    dict_list = [join_item(json.loads(x), extend_dict) for x in str_list]
    return dict_list


def list_user_dir() -> list:
    """
    列出所有的用户的上传到目录的路径
    :return: 用户目录全路径的列表
    """
    path_list = [os.path.join(zip_dir_path, x) for x in os.listdir(zip_dir_path) if len(x) == 24]
    return path_list


def list_user_id() -> list:
    """
    列出所有的用户的ObjectId的字符串格式
    :return: 用户ObjectId的列表
    """
    id_list = [x for x in os.listdir(zip_dir_path) if len(x) == 24]
    return id_list


def list_zipfile(dir_path: str) -> list:
    """
    列出一个目录下所有zip文件的全路径,一般来说，一个zip文件至少有以下
    1.device_info.txt  设备信息。
    2.rec_acce.txt     加速度传感器
    3.rec_gps.txt      GPS传感器
    4.rec_grav.txt     重力传感器
    5.rec_gyro.txt     陀螺仪
    6.rec_rota.txt     角速度计
    7.rec_magn.txt     磁力计
    如果缺少某一种类型的传感器，对应的文件就会不存在。
    :param dir_path: ，目录
    :return: zip文件全路径的列表
    """
    pattern_01 = re.compile(r'^2\d{3}-[01]?\d-[0-3]?\d-[012]?\d-[0-6]?\d-[0-6]?\d\.zip$')  # 文件名匹配
    pattern_02 = re.compile(r'^2\d{3}_[01]?\d_[0-3]?\d_[012]?\d_[0-6]?\d_[0-6]?\d\.zip$')  # 文件名匹配
    path_list = [os.path.join(dir_path, x) for x in os.listdir(dir_path) if pattern_01.match(x) or pattern_02.match(x)]
    """给文件名按时间先后排序"""
    path_list.sort(key=lambda obj: transform_date(obj))
    return path_list


def read_zip(file_path: str) -> dict:
    """
    读取一个zip文件,返回内部的文件名和对象的数组组成的字典，
    :param file_path: zip文件绝对路径
    :return: {"file_01":[dict_01, dict_02..., dict_0n],
              "file_02":[dict_01, dict_02..., dict_0n],
              .....
              "file_0n":[dict_01, dict_02..., dict_0n]]
    """
    zf = None
    try:
        if os.path.exists(file_path):
            zf = zipfile.ZipFile(file_path)
        else:
            pass
            # raise FileNotFoundError("{} not found".format(file_path))
    except FileNotFoundError as e:
        print(e)
        recode("Error read_zip, file not found: filename={}".format(file_path))
        logger.exception("Error read_zip:")
    except Exception as e1:
        logger.exception("Error read_zip:")
        print(e1)
    finally:
        if zf is None:
            result_dict = dict()
        else:
            name_list = zf.namelist()  # 压缩文件内部的文件list
            result_dict = dict()  # 存放结果集的字典
            user_id = os.path.split(os.path.split(file_path)[0])[-1]
            user = User.find_by_id(user_id)
            user.set_attr("last_update", datetime.datetime.now())  # 更新上传时间
            user.save()
            if not isinstance(user, User):  # 这个文件夹的名字不合法
                """删除文件"""
                delete_file(file_path)
            else:
                user_id = user.get_dbref()  # 用户id
                app_version = None  # app版本信息
                phone_model = None  # 当前手机型号
                os_version = None  # 当前手机操作系统
                """检查是否有设备信息文件，如果有，就把设备信息文件中的app版本信息写入各种传感器/gps记录中"""
                device_file_name = 'device_info.txt'
                if device_file_name in name_list:
                    """如果设备信息文件在压缩文件中，那就先读取这个文件"""
                    name_list.remove(device_file_name)
                    print("inner file name is {}".format(device_file_name))
                    obj = zf.read(device_file_name)
                    file_content = obj.decode()
                    try:
                        dev_list = parse_content(file_content, user_id)
                        _version = None

                        """检查是否有app的版本信息？"""
                        for dev in dev_list:
                            app_version = dev.get('AppVersion')
                            phone_model = dev.get('model')
                            os_version = dev.get('os_version')
                            if app_version is not None and phone_model is not None and os_version is not None:
                                break
                        result_dict[device_file_name] = dev_list
                    except json.decoder.JSONDecodeError as e:
                        print(e)
                        msg = "文件{} {} json序列化失败".format(file_path, device_file_name)
                        print(msg)
                        logger.exception(msg)
                else:
                    """如果没有设备信息文件，n那就忽略，保持app版本号为None"""
                    pass
                """检查用户版本信息/ 手机设备是否一致？"""
                print(user)
                if app_version is not None:
                    user_app_version = user.get_attr("app_version")
                    if user_app_version != app_version:
                        """更新app版本信息"""
                        user.set_attr("app_version", app_version)
                if phone_model is not None:
                    user_phone_model = user.get_attr('phone_model')
                    if user_phone_model != phone_model:
                        user.set_attr("phone_model", phone_model)
                if os_version is not None:
                    user_os_version = user.get_attr('os_version')
                    if user_os_version != os_version:
                        user.set_attr("os_version", os_version)
                user.set_attr("last_update", datetime.datetime.now())  # 更新最后接收数据的时间
                user.save_plus()
                """向zip文件读取结果集中加入版本信息"""
                for name in name_list:
                    print("inner file name is {}".format(name))
                    obj = zf.read(name)
                    file_content = obj.decode()
                    try:
                        dict_list = parse_content(file_content, user_id, app_version)
                        result_dict[name] = dict_list
                    except json.decoder.JSONDecodeError as e:
                        print(e)
                        msg = "文件{} {} json序列化失败".format(file_path, name)
                        print(msg)
                        logger.exception(msg)
            zf.close()
        return result_dict


def files_to_mongodb_bak(args_dict: dict) -> None:
    """
    把一个zip文件的内容写入数据库
    此函数现在处于声明废止状态,现在仅仅用作为备份,将在一定时间后被删除, 2018-3-2 12:37
    :param args_dict: zip文件内部的文件的绝对路径和内容对象数组组成的字典
    :return: None
    """
    ms = "此函数现在处于声明废止状态,现在仅仅用作为备份,将在一定时间后被删除, 2018-3-2 12:37"
    warnings.warn(ms)
    for file_path, obj_list in args_dict.items():
        file_name = os.path.split(file_path)[-1]  # 获取文件名
        print(file_name)
        if file_name == "device_info.txt":
            """设备信息"""
            obj_dict = obj_list[0]
            user_id = obj_dict.pop("user_id")
            obj = PhoneDevice(**obj_dict)
            device_id = PhoneDevice.find_by_id(obj.save()).get_dbref()
            User.add_phone_device(user_id, device_id)
        elif file_name == "rec_gps.txt":
            """GPS传感器"""
            obj_list = [x for x in obj_list if not (x.get("time") == "0" or x.get('ts') == "0")]
            if len(obj_list) > 0:
                inserted_obj_list = GPS.insert_many(obj_list)  # 插入成功的GPS实例的doc的数组
                """生产track数据"""
                Track.batch_create_item_from_gps(inserted_obj_list)
            else:
                print("empty file: {}".format(file_path))
        else:
            """其他传感器"""
            sensor_type = file_name.split(".", 1)[0]
            """转换传感器类型的字典"""
            type_transform_dict = {"rec_acce": {"sensor_type": "accelerate", "description": "加速度传感器"},
                                   "rec_grav": {"sensor_type": "gravitation", "description": "重力传感器(GV-sensor)"},
                                   "rec_gyro": {"sensor_type": "gyroscope", "description": "陀螺仪传感器(Gyro-sensor)"},
                                   "rec_rota": {"sensor_type": "rotation vector", "description": "旋转矢量传感器(RV-sensor)"},
                                   "rec_magn": {"sensor_type": "magnetism", "description": "磁力传感器(M-sensor)"},
                                   "rec_bpm": {"sensor_type": "beat per minute", "description": "心率传感器"}}
            obj_list = [join_item(x, type_transform_dict.get(sensor_type)) for x in obj_list if
                        not (x.get("time") == "0" or x.get('ts') == "0")]
            if len(obj_list) > 0:
                Sensor.insert_many(obj_list)
            else:
                print("empty file: {}".format(file_path))


def files_to_mongodb(args_dict: dict) -> None:
    """
    把一个zip文件的内容写入数据库
    :param args_dict: zip文件内部的文件的绝对路径和内容对象数组组成的字典
    :return: None
    """
    for file_path, obj_list in args_dict.items():
        file_name = os.path.split(file_path)[-1]  # 获取文件名
        print(file_name)
        if file_name == "device_info.txt":
            """设备信息"""
            obj_dict = obj_list[0]
            user_id = obj_dict.pop("user_id")
            obj = PhoneDevice(**obj_dict)
            device_id = PhoneDevice.find_by_id(obj.save()).get_dbref()
            User.add_phone_device(user_id, device_id)
        elif file_name == "rec_gps.txt":
            """GPS传感器"""
            obj_list = [x for x in obj_list if not (x.get("time") == "0" or x.get('ts') == "0")]
            if len(obj_list) > 0:
                inserted_obj_list = GPS.insert_many(obj_list)  # 插入成功的GPS实例的doc的数组
                """生产track数据,并返回最后的位置点"""
                last_position = Track.batch_create_item_from_gps(inserted_obj_list)
            else:
                print("empty file: {}".format(file_path))
        else:
            """其他传感器"""
            sensor_type = file_name.split(".", 1)[0]
            """转换传感器类型的字典"""
            type_transform_dict = {"rec_acce": {"sensor_type": "accelerate", "description": "加速度传感器"},
                                   "rec_grav": {"sensor_type": "gravitation", "description": "重力传感器(GV-sensor)"},
                                   "rec_gyro": {"sensor_type": "gyroscope", "description": "陀螺仪传感器(Gyro-sensor)"},
                                   "rec_rota": {"sensor_type": "rotation vector", "description": "旋转矢量传感器(RV-sensor)"},
                                   "rec_magn": {"sensor_type": "magnetism", "description": "磁力传感器(M-sensor)"},
                                   "rec_bpm": {"sensor_type": "beat per minute", "description": "心率传感器"}}
            obj_list = [join_item(x, type_transform_dict.get(sensor_type)) for x in obj_list if
                        not (x.get("time") == "0" or x.get('ts') == "0")]
            if len(obj_list) > 0:
                Sensor.insert_many(obj_list)
            else:
                print("empty file: {}".format(file_path))


def move_file_to_backup(file_path: str, backup_path: str = None) -> None:
    """
    把一个文件移动到制定的目录
    :param file_path: 文件绝对路径
    :param backup_path: 指定的目录的绝对路径
    :return: None
    """
    user_id_str = os.path.split(os.path.split(file_path)[0])[-1]
    if backup_path is None:
        backup_path = os.path.join(zip_dir_path, user_id_str, "backup")
    else:
        if backup_path.endswith("/"):
            backup_path = backup_path.rstrip("/")
        elif backup_path.endswith(r"\\"):
            backup_path = backup_path.rstrip(r"\\")
        else:
            pass
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    file_name = os.path.split(file_path)[-1]
    dst_path = os.path.join(backup_path, file_name)
    global move_file_lock
    lock = move_file_lock
    lock.acquire()
    if os.path.exists(file_path):
        try:
            shutil.move(file_path, dst_path)
        except FileExistsError as e1:
            print(e1)
            logger.exception("move_file_to_backup Error:")
        except FileNotFoundError as e2:
            print(e2)
            logger.exception("move_file_to_backup Error:")
        except Exception as e3:
            print(e3)
            logger.exception("move_file_to_backup Error:")
        finally:
            pass
    else:
        pass
    # ms = "{}, {}".format(file_path, dst_path)
    # try:
    #     raise TypeError(ms)
    # except TypeError as e:
    #     logger.exception(ms)
    lock.release()


def delete_file(file_path: str) -> None:
    """
    删除一个文件
    :param file_path: 文件的绝对路径
    :return: None
    """
    try:
        os.remove(file_path)
    except FileNotFoundError as e2:
        print(e2)
        logger.exception("delete_file Error:")
    except Exception as e3:
        print(e3)
        logger.exception("delete_file Error:")
    finally:
        pass


def process_simple_zipfile(zipfile_path: str) -> (dict, None):
    """
    针对一个文件的操作。
    当app客户端上传完zip数据的时候调用此函数，把上传的数据写入数据库，并将zip文件进行删除/移动/改名,
    此函数建议由celery执行
    :param zipfile_path: app上传的zip文件的绝对路径
    :return:dict/None
    """
    if join_work(zipfile_path):  # 确认可以工作
        recode("process_simple_zipfile begin")
        read_result = read_zip(zipfile_path)
        recode("process_simple_zipfile end")
        files_to_mongodb(read_result)
        move_file_to_backup(zipfile_path)  # 测试阶段仅仅移动，正式的时候需要删除
        pop_work(zipfile_path)  # 移除此文件正在的标志
        return {zipfile_path: list(read_result.keys())}


def process_all_zipfile(user_id: (str, ObjectId, DBRef, MyDBRef)) -> dict:
    """
    一次性处理用户的所有zip文件,由于celery工作在多进程异步状态。这个命令并不经常使用。
    当app客户端上传完zip数据的时候可调用此函数，把上传的数据写入数据库，并将zip文件进行删除/移动/改名,
    此函数建议由celery执行
    :param user_id: 用户id
    :return:dict
    """
    if isinstance(user_id, ObjectId):
        user_id = str(user_id)
    elif isinstance(user_id, (DBRef, MyDBRef)):
        user_id = str(user_id.id)
    else:
        pass
    user_path = os.path.join(zip_dir_path, user_id)
    if os.path.exists(user_path):
        zip_file_list = list_zipfile(user_path)
        res = dict()
        recode("process_all_zipfile begin")
        for _zip_path in zip_file_list:
            if join_work(_zip_path):  # 判断是否有重复的工作？有的话就放弃
                read_result = read_zip(_zip_path)
                res[_zip_path] = list(read_result.keys())
                files_to_mongodb(read_result)
                move_file_to_backup(_zip_path)  # 测试阶段仅仅移动，正式的时候需要删除
                pop_work(_zip_path)  # 移除此文件正在的标志
        recode("process_all_zipfile end")
        return res
    else:
        msg = "{} 路径不存在".format(user_path)
        try:
            raise FileNotFoundError(msg)
        except FileNotFoundError as e:
            print(e)
            logger.exception(msg)
        finally:
            recode("function when_upload_success error, user_id={}, error={}".format(user_id, msg))


def when_upload_success(zip_path: str) -> None:
    """
    当app客户端上传完zip数据的时候调用此函数，把上传的数据写入数据库，并将zip文件进行删除/移动/改名,
    此函数建议由celery执行
    :param zip_path: 刚刚上传完毕的文件的绝对路径
    :return:None
    """
    """先执行当前文件的处理工作"""
    process_simple_zipfile(zip_path)
    """然后检查本目录是否是空的？"""
    file_list = list_zipfile(os.path.split(zip_path)[0])
    if len(file_list) == 0:
        pass
    else:
        """检查这些文件是否被人处理中？"""
        global work_key
        working_files = cache.get(work_key)
        [process_simple_zipfile(x) for x in file_list if x not in working_files]


def unzip_all_user_file() -> None:
    """
    解压所有用户的zip数据,非常规方法，仅做测试和调整用。
    :return:None
    """
    all_user = list_user_id()
    print(all_user)
    for user_id in all_user:
        user_path = os.path.join(zip_dir_path, user_id)
        for zip_path in list_zipfile(user_path):
            print(zip_path)
            when_upload_success(zip_path)


if __name__ == "__main__":
    # files_to_mongodb_bak({})
    process_all_zipfile(user_id=ObjectId("59895177de713e304a67d30c"))
    pass
