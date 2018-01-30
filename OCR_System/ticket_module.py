# -*- coding:utf8 -*-
import db_module
import sqlalchemy.exc
import datetime
import re
import json
import result_module

"""票据模块"""

table_name = "image_info"
columns = db_module.get_columns(table_name, True)  # 第一次启动时加载


def edit_ticket(**kwargs):
    """修改用户资料,参数必须是键值对的形式"""
    message = {"message": "success"}
    file_md5 = kwargs.pop("file_md5", None)
    if file_md5 is None or len(file_md5) != 32:
        message["message"] = "无效的票据ID"
    else:
        sql = db_module.structure_sql("edit", "result_data_sh", query_terms="where file_md5='{}'".format(file_md5),
                                      **kwargs)
        session = db_module.sql_session()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            print(e)
            message['message'] = '编辑票据信息失败'
        finally:
            session.close()
    return message


def name_and_str(the_type):
    """获取字段名和字段字符串的对应关系。the_type是字段类型的sn，返回字典"""
    key = "{}_name_and_str".format(the_type)
    cache = db_module.cache
    result = cache.get(key)
    if result is None:
        sql = "select key_name,key_str from key_dict where the_type_sn={}".format(the_type)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        result = {x[0]: x[1] for x in raw}
        cache.set(key, result, timeout=60 * 15)
    return result


def get_type_dict():
    """获取所有发票的类型名和sn的对应关系"""
    key = "tickets_type_dict"
    cache = db_module.cache
    result = cache.get(key)
    if result is None:
        sql = "select type_name,image_type_sn from image_type_info"
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        result = {x[0]: x[1] for x in raw}
        cache.set(key, result, timeout=60 * 15)
    return result


def ticket_count():
    """统计所有发票的数量
    返回int对象
    """
    session = db_module.sql_session()
    sql = "select count(1) from {}".format(table_name)
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchone()[0]
    finally:
        session.close()
        result = int(result)
        return result


def get_image_url(sn):
    """根据sn获取图片的remote_path"""
    sql = "select remote_path from image_info where image_sn={}".format(sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        return "#"
    else:
        result = raw[0]
        return result


def page(index=1, length=20, term='', key_word='', filter=dict()):
    """分页查询发票，后台管理用，index是页码，length是每页多少条记录
    term 查询的列
    key_word  查询的关键词的值
    filter  过滤条件
    """
    message = {"message": "success"}
    result = list()
    count = 0
    if not isinstance(index, int):
        try:
            index = int(index)
        except ValueError:
            index = 1
    if not isinstance(length, int):
        try:
            length = int(index)
        except ValueError:
            length = 20
    skip = (index - 1) * length
    limit = length
    term_list = list(filter.keys())
    """查询的表"""
    table_names = "image_info,case_info,batch_info,user_group_info where user_group_info.group_sn=" \
                          "case_info.customer_sn and image_info.case_sn=case_info.case_sn and image_info.batch_sn=" \
                          "batch_info.batch_sn {} order by case_sn desc limit {},{}"

    """用来组成字典的字段"""
    custom_columns = ['image_sn', "file_name", "case_sn", "case_name", "batch_sn", "batch_name",
                      "customer_sn", "company_alias", "remote_path", "is_return", "description",
                      "begin_datetime", "image_type_sn"]
    """用来串联sql语句的字段列表"""
    custom_columns_query = ['image_sn', "file_name", "image_info.case_sn", "case_info.case_name",
                           "image_info.batch_sn", "batch_info.batch_name", "case_info.customer_sn",
                           "user_group_info.company_alias", "remote_path", "is_return", "description",
                           "image_type_sn"]

    """可以用来查询的mysql表的image字段"""
    custom_columns_img = {"table_name": "image_info", "val": ['image_sn', "file_name", "case_sn", "batch_sn",
                                                              "remote_path", "is_return", "description",
                                                              "image_type_sn"]}
    """可以用来查询的mysql表的case字段"""
    custom_columns_case = {"table_name": "case_info", "val": ['case_name', 'customer_sn']}
    """可以用来查询的mysql表的batch字段"""
    custom_columns_batch = {"table_name": "batch_info",
                            "val": ["batch_name", "customer_sn", "supplier_sn", "begin_datetime"]}
    """可以用来查询的mysql表的user_group_info字段"""
    custom_columns_user_group = {"table_name": "user_group_info", "val": ["company_alias"]}

    """用来计数的语句"""
    table_names_count = "image_info,case_info,batch_info,user_group_info where user_group_info.group_sn=" \
                  "case_info.customer_sn and image_info.case_sn=case_info.case_sn and image_info.batch_sn=" \
                  "batch_info.batch_sn {}"
    sql_count = "select count(1) from {}".format(table_names_count)
    mysql_terms = dict()  # mysql 的查询条件
    mongo_terms = dict()  # mongo 的查询条件
    ses = db_module.sql_session()
    for term in term_list:
        """归类一下查询条件"""
        if term in custom_columns_img['val']:
            query_column_name = custom_columns_img['table_name'] + "." + term
            mysql_terms[query_column_name] = filter[term]
        elif term in custom_columns_case['val']:
            query_column_name = custom_columns_case['table_name'] + "." + term
            mysql_terms[query_column_name] = filter[term]
        elif term in custom_columns_batch['val']:
            query_column_name = custom_columns_batch['table_name'] + "." + term
            mysql_terms[query_column_name] = filter[term]
        elif term in custom_columns_user_group['val']:
            query_column_name = custom_columns_user_group['table_name'] + "." + term
            mysql_terms[query_column_name] = filter[term]
        else:
            mongo_terms[term] = filter[term]
    mysql_result = dict()
    mongo_result = dict()
    if len(mongo_terms) == 0:
        """没有mongo筛选条件的查询"""
        query_str = ''
        if len(mysql_terms) > 0:
            """mysql有筛选条件"""
            query_list = ["{}='{}'".format(k, v) for k, v in mysql_terms.items()]
            query_str = ' and {}'.format(' and '.join(query_list))
        sql = "select {} from {}".format(",".join(custom_columns_query), table_names.format(query_str, skip, limit))
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        proxy = ses.execute(sql_count.format(query_str))
        count = proxy.fetchone()[0]
        ses.close()
        if len(raw) == 0:
            pass
        else:
            """如果查询道mysql的结果了，从mongo中补全对应的结果"""
            mysql_result = [dict(zip(custom_columns, x)) for x in raw]
            oid_list = [x['image_sn'] for x in mysql_result]
            for oid in oid_list:
                mongo_result[oid] = result_module.query(the_type="by_image_sn", table_name="supplier_image",
                                                        image_sn=str(oid))['result']
            for x in mysql_result:
                item_data = mongo_result[x['image_sn']]
                if item_data is not None:
                    x.update(item_data)
            result = mysql_result
    else:
        """有mongo的筛选条件，就要取mongo和mysql的交集"""
        mongo_data = result_module.query(the_type="custom_model", table_name="supplier_image",query_obj=mongo_terms)['result']
        if mongo_data is None:
            ses.close()
            count = 0
        else:
            query_str = ''
            if len(mysql_terms) > 0:
                """mysql有筛选条件"""
                query_list = ["{}='{}'".format(k, v) for k, v in mysql_terms.items()]
                query_str = ' and {}'.format(' and '.join(query_list))
            sql = "select {} from {}".format(",".join(custom_columns_query), table_names.format(query_str, skip, limit))
            proxy = ses.execute(sql)
            raw = proxy.fetchall()
            ses.close()
            mysql_result = {x[0]: dict(zip(custom_columns, x)) for x in raw}
            for x in mongo_data:
                item_data = x
                mysql_d = mysql_result.get(int(item_data['_id']))
                if item_data is not None:
                    item_data.update(mysql_d)
                    result.append(item_data)

    message['data'] = result
    message['count'] = count
    return message


def page2(index=1, length=30, term='', key_word=''):
    """分页查询发票，后台管理用，index是页码，length是每页多少条记录"""
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            skip = (index - 1) * length
            limit = length
            """先查询mysql"""
            key = "image_sn" if term == "_id" else term
            custom_columns = ['image_sn', "file_name", "case_sn", "case_name", "batch_sn", "batch_name",
                              "customer_sn", "company_alias", "remote_path", "is_return", "description",
                              "begin_datetime", "image_type_sn"]
            custom_columns2 = ['image_sn', "file_name", "image_info.case_sn", "case_info.case_name",
                               "case_info.batch_sn", "batch_info.batch_name", "case_info.customer_sn",
                               "user_group_info.company_alias", "remote_path", "is_return", "description",
                               "begin_datetime", "image_type_sn"]
            ses = db_module.sql_session()
            if key in columns or key == "":
                """如果查询的关键字在mysql中或者非关键字查询"""
                if key != "" and key_word != "" and key in columns:
                    key = "image_info." + key
                    sql = "select " + ",".join(custom_columns2) + (" from {},case_info,batch_info,user_group_info "
                                                                   "where user_group_info.group_sn=case_info.customer_sn"
                                                                   " and image_info.case_sn=case_info.case_sn and "
                                                                   "image_info.batch_sn=batch_info.batch_sn and"
                                                                   " {}='{}' order by case_sn desc "
                                                                   "limit {},{}".format(table_name, key, key_word,
                                                                                        skip, limit))
                else:
                    sql = "select " + ",".join(custom_columns2) + (" from {},case_info,batch_info,user_group_info "
                                                                   "where user_group_info.group_sn=case_info.customer_sn"
                                                                   " and image_info.case_sn=case_info.case_sn and "
                                                                   "image_info.batch_sn=batch_info.batch_sn"
                                                                   " order by case_sn desc "
                                                                   "limit {},{}".format(table_name, skip, limit))

                proxy = ses.execute(sql)
                raw = proxy.fetchall()
                ses.close()
                result = dict()
                if len(raw) == 0:
                    message["data"] = result
                else:
                    result = {x[0]: dict(zip(custom_columns, x)) for x in raw}
                """再从mongo中补全信息"""
                print("line 251", end="")
                print(result)
                sn_list = list(result.keys())  # 取image的sn列表
                for x in sn_list:
                    query_obj = {"_id": str(x)}
                    image_info = result_module.query(the_type="custom_model", table_name="supplier_image",
                                                    query_obj=query_obj)
                    data = image_info['result']
                    if data is not None:
                        result[x].update(data)
                result = list(result.values())
                message['data'] = result
            else:
                """如果直接是使用识别结果的字段查询，那么就先查询mongodb"""
                """计算查询条件"""
                if term == "_id":
                    key_word = str(key_word)
                else:
                    try:
                        key_word = int(key_word)
                    except ValueError:
                        try:
                            key_word = float(key_word)
                        except ValueError:
                            pass
                        finally:
                            pass
                    finally:
                        pass
                if term == "":
                    query_obj = dict()
                else:
                    query_obj = {term: key_word}
                image_info = result_module.query(the_type="custom_model", table_name="supplier_image",
                                                 query_obj=query_obj, skip=skip, limit=limit)
                image_info = image_info['result']  # 数组格式
                sn_list = tuple([x["_id"] for x in image_info])
                sql = "select " + ",".join(custom_columns2) + (" from {},case_info,batch_info,user_group_info "
                                                               "where user_group_info.group_sn=case_info.customer_sn"
                                                               " and image_info.case_sn=case_info.case_sn and "
                                                               "image_info.batch_sn=batch_info.batch_sn and "
                                                               "image_info.image_sn in {} order by case_sn desc".
                                                               format(table_name, sn_list))
                ses = db_module.sql_session()
                proxy = ses.execute(sql)
                raw = proxy.fetchall()
                ses.close()
                if len(raw) == 0:
                    message['data'] = image_info
                else:
                    result = {x[0]: dict(zip(custom_columns, x)) for x in raw}
                    for x in image_info:
                        key = x["_id"]
                        if key in result:
                            x.update(result[key])
                    message['data'] = image_info
        except TypeError:
            message['message'] = "参数错误"
    else:
        message['message'] = "未知请求"
    return message


if __name__ == "__main__":
    print(page(filter={"case_name": 'PICC20170620012001'}))
