# -*-coding:utf-8-*-
import db_module
from uuid import uuid4
import os
import xlrd
from md5_module import get_md5
from pymongo import errors
from pymongo import DESCENDING
import xmltodict
from bson.objectid import ObjectId
from batch_module import batch_sn_list

"""对识别结果的存取"""
"""
ocr_image   以票据问单位保存的ocr识别的结果
supplier_image   以票据问单位保存的人工的识别的结果
supplier_case     以赔案问单位保存的人工识别的结果
checked_image   以票据问单位保存的校验后识别的结果
checked_case     以赔案问单位保存的校验后识别的结果
result_xml       万达的xml文件的直接保存结果
"""

cache = db_module.cache


def __get_key_dict_from_db(the_type):
    """从数据库查询key_str和key_name的对应关系，参数是票据类型"""
    ses = db_module.sql_session()
    sql = "select key_str,key_name from key_dict where the_type_sn=(select image_type_sn " \
          "from image_type_info where type_name='{}')".format(the_type)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if raw is None:
        return False
    else:
        result = {x[0]: x[1] for x in raw}
    ses.close()
    return result
# for k, v  in __get_key_dict_from_db("上海住院").items():
#     print(k, v)


def __get_key_dict(the_type):
    """获取某一类型的票据key_str和key_name的对应关系，参数是票据类型
        此方法的目的是给原文本的字典对象提供转换映射
    """
    key = "{}_keys".format(the_type)
    result = cache.get(key)
    if result is None:
        result = __get_key_dict_from_db(the_type)
        if result:
            cache.set(key, result, timeout=1)
        else:
            raise TypeError("错误的票据类型：{}".format(the_type))
    return result


def check_keys(the_type, key_str):
    """检查key_str是否合法，the_type是票据类型，key_str是待检查的key，返回布尔类型
        检查的对象是汉字的字段名
    """
    key_dict = __get_key_dict(the_type)
    if key_dict is None:
        return False
    else:
        if key_str in key_dict:
            return True
        else:
            return False


def get_key_name(the_type, key_str):
    """返回key_str对应的key_name，the_type是票据类型"""
    key_dict = __get_key_dict(the_type)
    if key_dict is None:
        return False
    else:
        if key_str in key_dict:
            return key_dict[key_str]
        else:
            return False


def get_all_key_name(obj_dict):
    """从一个复合dict获取所有的key_name,"""
    key_list = []
    if isinstance(obj_dict, dict):
        key_list.extend(list(obj_dict.keys()))
        values = list(obj_dict.values())
        for val in values:
            if isinstance(val, (dict, list)):
                key_list.extend(get_all_key_name(val))
    elif isinstance(obj_dict, list):
        for x in obj_dict:
            if isinstance(x, (dict, list)):
                key_list.extend(get_all_key_name(x))
    else:
        raise TypeError("错误的类型")
    return key_list


def check_key_name(obj_dict, the_type):
    """检查英文的字段名是否合法，作为插入千的检查，这是必备的额，一次检查一个对象，
        合法返回否则返回不合法的key_name组成的数组。
    """
    key = "key_name_list_{}".format(the_type)
    key_name_list = cache.get(key)
    if key_name_list is None:
        sql = "select key_name from key_dict,image_type_info where the_type_sn=image_type_sn " \
              "and type_name='{}'".format(the_type)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            raise TypeError("错误的票据类型:{}".format(the_type))
        else:
            key_name_list = [x[0] for x in raw]
            cache.set(key, key_name_list, timeout=60 * 60)
    else:
        pass
    """获取对象的所有key_name"""
    key_name_obj = get_all_key_name(obj_dict)
    error_key_names = [x for x in key_name_obj if x not in key_name_list]
    return error_key_names  # 返回错误的key_name


def mongo_save(cli, obj):
    """插入一个mongo对象，
    cli 为客户端
    obj 是待插入的的对象
    query_dict 是数据重复时，update的查询条件
    """
    oid = obj['_id']
    try:
        cli.insert_one(obj)
    except errors.DuplicateKeyError as e:
        print(e)
        cli.update({"_id": oid}, obj)
    finally:
        return oid


def save_ocr_result(result_dict, source_file_sn, engine_sn=0, result_status=''):
    """
    把ocr识别后的结果存入数据库，以票据为单位
    result_dict： 票据的识别结果
    source_file_sn：原始影像件sn,也是存储的_id
    engine_sn: ocr引擎编号
    result_status: 如果图片ocr出错，这里写错误原因，否则置空。
    :return: 返回插入的id或者更新已存在消息的提醒，
    """
    if not isinstance(result_dict, dict):
        raise TypeError("result_dict应当是字典对象")
    else:
        recode = {"source_file_sn": source_file_sn, "engine_sn": engine_sn,
                  "result_status": result_status, "receive_time": db_module.current_datetime()}
        oid = str(source_file_sn)
        result_dict["_id"] = oid
        recode['mongo_id'] = oid

        if result_status == "":
            """表示没有问题"""
            ses = db_module.sql_session()
            cli = db_module.get_mongodb("ocr_image")
            mongo_save(cli, result_dict)
            sql = db_module.structure_sql("add", "result_ocr", **recode)
            ses.execute(sql)
            ses.commit()
            ses.close()
        else:
            """写入错误信息"""
            ses = db_module.sql_session()
            sql = db_module.structure_sql("add", "result_ocr", **recode)
            ses.execute(sql)
            ses.commit()
            ses.close()


def save_xml(file_path, group_sn, suppliers_sn=0):
    """把万达的xml写入数据库
    file_path： xml路径，包含文件名
    group_sn:  万达对应的group_sn
    suppliers_sn： 供应商子账户，用于供应商内部区分不同用户，不用区分的话置0
    """
    if not os.path.exists(file_path):
        raise TypeError("{} 文件不存在".format(file_path))
    else:
        with open(file_path, encoding='utf8') as f:
            result_dict = xmltodict.parse(f.read())  # 读取xml信息
        recode = dict()  # 插入mysql的数据
        file_path, file_name = os.path.split(file_path)
        case_name = file_name.split(".xml")[0]
        case_sn = find_case_sn(group_sn, case_name)
        if case_sn is None:
            raise ValueError("没有查到对应的case_sn")
        recode["receive_time"] = db_module.current_datetime()
        recode['result_file_path'] = file_path
        recode['result_file_name'] = file_name
        recode['case_name'] = case_name
        recode['suppliers_sn'] = suppliers_sn
        recode['mongo_id'] = case_sn

        result_dict['_id'] = case_sn
        result_dict['date_time'] = db_module.current_datetime()
        client = db_module.get_mongodb("result_xml")

        mongo_save(client, result_dict)
        ses = db_module.sql_session()
        sql = db_module.structure_sql("add", "result_xml", **recode)
        ses.execute(sql)
        ses.commit()
        ses.close()


def update_result_file(source_file_sn, new_file_path, new_file_name=None):
    """
    转储xml文件后修改数据库中的存储位置的记录
    source_file_sn：原始影像件sn
    new_file_path: 转储后的文件路径，不包含文件名
    new_file_name: 如果转储后没有改变文件名，不需要传这个参数
    """
    if new_file_name:
        sql = "update result_ocr set result_file_path='{}',result_file_name='{}' where source_file_sn={}". \
            format(new_file_path, new_file_name, source_file_sn)
    else:
        sql = "update result_ocr set result_file_path='{}' where source_file_sn={}".format(new_file_path,
                                                                                           source_file_sn)
    ses = db_module.sql_session()
    ses.execute(sql)
    ses.commit()


def __read_excel(file_path, ticket_type='上海门急诊'):
    """读取excel文件的内容，返回字典,excel文件的文件名应该是图片名称。ticket_type是票据类型，"""
    if not os.path.exists(file_path):
        raise FileNotFoundError("文件{}不存在！".format(file_path))
    else:
        key_dict = __get_key_dict(ticket_type)
        file_name = os.path.split(file_path)[-1]
        file_type = file_name.lower().split(".")[-1]
        if file_type not in ("xls", "xlsx") or file_path.startswith("~"):
            raise TypeError("文件{}类型错误！".format(file_path))
        else:
            workbook = xlrd.open_workbook(file_path)
            sheet_01 = workbook.sheet_by_index(0)
            row_list = [[row[index] for index in range(8)] for row in sheet_01.get_rows()]

            row_list.pop(0)  # 弹出第一行
            """开始读取"""
            result = {"file_name": file_name}
            flag = None
            convert_key = ("service_id", "ticket_id", "event_date")
            for x in row_list:
                if len([i for i in x if i.value != ""]) > 0:
                    text_0 = x[0].value
                    if text_0 == "收费项目":
                        """为读取大项标识"""
                        flag = "p_class"
                        result['p_class'] = list()
                    elif text_0 == "合计(大写)" or text_0 == "合计":
                        key = key_dict[text_0]
                        val = x[1].value
                        result[key] = val
                        flag = None
                    elif text_0 == "项目明细":
                        """为插入明细做标识"""
                        flag = "p_detail"
                        result['p_detail'] = list()
                    else:
                        pass

                    if flag is None:
                        key = key_dict[text_0]
                        if key in convert_key:
                            try:
                                val = int(x[1].value)
                            except ValueError as e:
                                print(e)
                                print(x[1].value)
                                print(file_name)
                                val = x[1].value
                        else:
                            val = x[1].value
                        result[key] = val
                    elif flag == "p_class":
                        """插入大项"""
                        if text_0 != "收费项目" and text_0 != "项目":
                            key = x[0].value
                            val = x[1].value
                            temp = {'p_name': key, "p_val": val}
                            result['p_class'].append(temp)
                        else:
                            pass
                    elif flag == "p_detail":
                        if text_0 != "项目明细" and text_0 != "项目编码":
                            pd_code = x[0].value
                            pd_name = x[1].value
                            pd_spec = x[2].value
                            pd_level = x[3].value
                            pd_ratio = x[4].value
                            pd_num = x[5].value
                            pd_price = x[6].value
                            sum_price = x[7].value
                            temp = {"pd_code": pd_code, "pd_name": pd_name, "pd_spec": pd_spec, "pd_level": pd_level,
                                    "pd_ratio": pd_ratio, "pd_num": pd_num, "pd_price": pd_price,
                                    "sum_price": sum_price}
                            result['p_detail'].append(temp)
                        else:
                            pass
                    else:
                        print("不明row {}".format(x[0]))
                else:
                    # print("空列 {}".format(x))
                    pass

            # print(result)
            return result


def find_case_sn(group_sn, case_name):
    """根据用户sn和赔案名，返回case_sn对应的mongo_id"""
    key = "user_group_{}_case_mongo_id".format(group_sn)
    obj = None
    case_name = case_name.lower()
    result = cache.get(key)
    ses = db_module.sql_session()
    if result is None:
        sql = "SELECT case_name,case_sn from case_info where customer_sn={} order by case_sn desc limit 0, 2000".format(group_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            result = dict()
        else:
            result = {x[0].lower(): x[1] for x in raw}

    if case_name in result:
        obj = result[case_name]
    else:
        sql = "SELECT case_name,case_sn from case_info where customer_sn={} and case_name='{}'".format(group_sn,
                                                                                                        case_name)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        if raw is None:
            pass
        else:
            result.update({raw[0].lower(): raw[1]})
            obj = result[case_name]
    ses.close()
    cache.set(key, result, timeout=60 * 60)
    return obj


def get_case_sn(batch_sn, case_name):
    """根据批次sn和赔案号获取case_sn，返回case_sn或者None"""
    key = "batch_{}_case_sn".format(batch_sn)
    case_dict = cache.get(key)
    if case_dict is None:
        sql = "select case_name,case_sn from case_info where batch_sn={}".format(batch_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            raise ValueError("错误的batch_sn或者批次赔案为空")
        else:
            case_dict = {x[0]: x[1] for x in raw}
            cache.set(key, case_dict, timeout=60 * 60)
    if case_name in case_dict:
        return str(case_dict[case_name])
    else:
        raise ValueError("错误的case_name")


def get_image_sn(case_sn, image_name):
    """根据赔案sn和image_name，返回image_sn或者None"""
    key = "case_{}_image_sn".format(case_sn)
    image_dict = cache.get(key)
    if image_dict is None:
        sql = "select file_name,image_sn from image_info where case_sn={}".format(case_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            raise ValueError("错误的case_sn")
        else:
            image_dict = {x[0]: x[1] for x in raw}
            cache.set(key, image_dict, timeout=60 * 5)
    if image_name in image_dict:
        return str(image_dict[image_name])
    else:
        raise ValueError("错误的image_name")


def save_supplier_data(**kwargs):
    """保存供应商发来的处理结果，字典对象以赔案为单位
        """
    now = db_module.current_datetime()
    case_name = kwargs['case_name']
    batch_sn = kwargs['batch_sn']
    supplier_sn = kwargs['supplier_sn']
    case_sn = get_case_sn(batch_sn, case_name)
    kwargs['case_sn'] = case_sn
    kwargs['save_date'] = now
    # oid = uuid4().hex
    # kwargs['_id'] = oid
    image_list = kwargs['image_info']
    new_image_list = list()
    for x in image_list:
        x['_id'] = get_image_sn(case_sn, x['image_name'])  # image_sn做id
        x['case_sn'] = case_sn
        new_image_list.append(x)
    """开始插入发票的信息"""
    client = db_module.get_mongodb("supplier_image")
    oid_list = list()  # 存放插入成功的图片的image_sn
    for image in new_image_list:
        oid = image['_id']
        mongo_save(client, image)
        oid_list.append(oid)
    kwargs['image_info'] = oid_list
    recode = dict()  #
    recode["save_date"] = now
    recode['supplier_sn'] = supplier_sn
    recode['case_sn'] = case_sn
    recode['batch_sn'] = batch_sn
    recode['mongo_id'] = case_sn

    client = db_module.get_mongodb("supplier_case")
    kwargs["_id"] = kwargs['case_sn']
    mongo_save(client, kwargs)

    ses = db_module.sql_session()
    sql = db_module.structure_sql("add", "supplier_post_recode", **recode)
    ses.execute(sql)
    """更新image_info表"""
    for image_sn in oid_list:
        sql = "update image_info set is_return=1 where image_sn={}".format(image_sn)
        ses.execute(sql)
    ses.commit()
    ses.close()
    """发送更新信息给tornado服务器或者消息中间层"""

    return {"message": "success", "oid": recode['mongo_id']}


def query(**kwargs):
    """查询从mongo查询人工团队处理过的赔案信息"""
    message = {"message": "success"}
    the_type = kwargs.pop("the_type")

    if the_type == "by_case_name":
        """以赔案号来查询，这是客户最常用的查询方式。需要提供客户的sn，批次号，赔案号来查询。返回赔案的字典
        c_sn: 用户的代码，也就是user_group_info的group_sn,batch_info的customer_sn
        case_name: 赔案名
        """
        c_sn = kwargs.get("c_sn")
        case_name = kwargs['case_name']
        if c_sn and case_name:
            oid = find_case_sn(c_sn, case_name)
            client = db_module.get_mongodb("checked_case")
            result = client.find_one({"_id": oid})
            message['result'] = result
        else:
            message['message'] = '参数错误'
    elif the_type == "by_image_sn":
        """用image_sn查找图片识别结果"""
        image_sn = kwargs.get("image_sn")
        table_name = kwargs.get("table_name")
        client = db_module.get_mongodb(table_name)
        result = client.find_one({"_id": image_sn})
        message['result'] = result
    elif the_type == "custom_model":
        """自定义方式查询,这种自定义查询实际上是以票据为最小单位查询的"""
        table_name = kwargs.get("table_name")
        query_obj = kwargs.get("query_obj")  # 查询条件，字典格式
        skip = kwargs.get("skip")
        limit = kwargs.get("limit")
        client = db_module.get_mongodb(table_name)
        if skip is None or limit is None:
            result = client.find_one(query_obj)
        else:
            result = client.find(query_obj).skip(skip).limit(limit).sort("_id", DESCENDING)
            result = list(result)    # 取出结果的特殊方式
        message['result'] = result
    else:
        message['message'] = "不支持的操作"
    return message


def query_data(**kwargs):
    """让客户和供应商查询ocr和最终数据
    author_type: customer/supplier 客户还是供应商的查询
    author_sn： 客户/供应商的sn
    batch_sn: 批次号
    case_name： 赔案名
    image_name： 图片名
    info_set： ocr/checked/supplier 查ocr数据,人工团队还是最终数据？
    返回 {"message":"success","result": data_dict}
    """
    author_type = kwargs['author_type']
    author_sn = kwargs['author_sn']
    batch_sn = kwargs['batch_sn']
    case_name = kwargs['case_name']
    image_name = kwargs['image_name']
    info_set = kwargs['info_set']
    message = {"message": "success"}
    result = dict()

    if batch_sn in batch_sn_list(author_type, author_sn):
        case_sn = get_case_sn(batch_sn, case_name)
        image_sn = None if image_name == "" else get_image_sn(case_sn, image_name)
        if author_type == "customer":
            """用户查询"""
            if info_set == "ocr":
                """查ocr数据，只能以image_sn来查"""
                if image_sn is None:
                    message['message'] = "没有image_sn"
                else:
                    client = db_module.get_mongodb("ocr_image")
                    result = client.find_one({"_id": image_sn})
                    message['result'] = result
            else:
                """查最终结果,供应商不能查人工团队的结果，只能查ocr和最终结果"""
                if image_sn is None:
                    """按case_sn查"""
                    client = db_module.get_mongodb("checked_case")
                    result = client.find_one({"_id": case_sn})
                    image_sn_list = result["image_info"]
                    client = db_module.get_mongodb('checked_image')
                    image_info = [client.find_one({"_id": sn}) for sn in image_sn_list]
                    result['image_info'] = image_info
                    message['result'] = result
                else:
                    """按image_sn查"""
                    client = db_module.get_mongodb('checked_image')
                    result = client.find_one({"_id": image_sn})
                    message['result'] = result
        else:
            """供应商查询"""
            if info_set == "ocr":
                """查ocr数据，只能以image_sn来查"""
                if image_sn is None:
                    message['message'] = "没有image_sn"
                else:
                    client = db_module.get_mongodb("ocr_image")
                    result = client.find_one({"_id": image_sn})
                    message['result'] = result
            elif info_set == "supplier":
                """查人工团队的结果"""
                if image_sn is None:
                    """按case_sn查"""
                    client = db_module.get_mongodb("supplier_case")
                    result = client.find_one({"_id": case_sn})
                    image_sn_list = result["image_info"]
                    client = db_module.get_mongodb('supplier_image')
                    image_info = [client.find_one({"_id": sn}) for sn in image_sn_list]
                    result['image_info'] = image_info
                    message['result'] = result
                else:
                    """按image_sn查"""
                    client = db_module.get_mongodb('checked_image')
                    result = client.find_one({"_id": image_sn})
                    message['result'] = result
            else:
                """查最终结果"""
                if image_sn is None:
                    """按case_sn查"""
                    client = db_module.get_mongodb("checked_case")
                    result = client.find_one({"_id": case_sn})
                    image_sn_list = result["image_info"]
                    client = db_module.get_mongodb('checked_image')
                    image_info = [client.find_one({"_id": sn}) for sn in image_sn_list]
                    result['image_info'] = image_info
                    message['result'] = result
                else:
                    """按image_sn查"""
                    client = db_module.get_mongodb('checked_image')
                    result = client.find_one({"_id": image_sn})
                    message['result'] = result


    else:
        message['message'] = "错误的batch_sn"
    return message



if __name__ == "__main__":
    a = {"a": 111, "b": 2, 'case_name': 'PICC20170620016001', 'supplier_sn': 0, 'batch_sn': 10,
         "c": [{"c1": 31}, {"c2": 32}, {"c3": 33}],
         "image_info": [{"image_name": 'PICC2017062001600110015.jpg', "d2": 42,
              "ccc": 909}]}
    # print(len(__flat_dict(a)))
    # print(save_ocr_result(a, "232312", 0, ""))
    # print(save_checked_result(a, "232123", "a.jpg", "182.168.0.1/home/", 'vdf232'))
    # save_ocr_result(a, "23213", 0)
    # print(get_result(2323, 'tickets'))
    # print(pack_obj(get_result(2323)))
    for x in range(20):
        save_supplier_data(**a)
    # query(the_type="by_oid", oid=1212)

    # image_info = __read_excel("f://上海地区医疗发票全字段输入模板 (示范).xlsx", "上海门急诊")
    # image_info.pop('file_name')
    # image_info['image_name'] = '00000003AI20160324018.jpg'
    # image_info['image_name'] = '0000000000000000.jpg'
    # result = dict()
    # result['image_info'] = [image_info]
    # result['case_name'] = "case0001"
    # result['batch_sn'] = 1
    # result['supplier_sn'] = 0
    # result['case_sn'] = 12
    # # print(save_supplier_data(**result))
    # import requests,json
    # r = requests.post("http://127.0.0.1:8000/result/save", data={"mode":"debug","data":json.dumps(result)})
    # print(r.json())
    # print(get_all_key_name(a))
    # for x in range(10):
    #     print(query(the_type='by_oid', oid='5933353391576d0f48f61da1'))
