# -*-coding:utf-8-*-
import db_module

""""特殊链接模块"""

table_name = "special_url_info"
columns = db_module.get_columns(table_name, True)


def url_count():
    """统计所有链接个数"""
    sql = "select count(1) from {}".format(table_name)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()[0]
    ses.close()
    return raw


def separate_count(company_sn=0):
    """
    按照客户注册的sn，以专有链接为组统计注册人数。
    :param company_sn: 公司sn，0标识查询所有的专有链接的
    :return: 字典，以公司所属的专用链接的sn为key，注册人数为val的字典，其中，key=0表示是分配策略分配的用户
    """
    result = dict()
    sql = "select sn, url from special_url_info where company_sn={}".format(company_sn)
    if company_sn == 0:
        """查询所有的专有链接"""
        sql = "select sn, url from special_url_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if len(raw) == 0:
        pass
    else:
        sn_url = {x[0]: x[1] for x in raw}
        part_list = list()
        for k, v in sn_url.items():
            part = "(select {},count(1) from customer_info where page_url like '%{}%')".format(k, v)
            part_list.append(part)

        sql = " union ".join(part_list)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
    ses.close()
    return result


def get_channel_dict():
    """获取推广渠道信息"""
    result = dict()
    sql = "select sn,channel_name from extend_channel_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = {x[0]: x[1] for x in raw}
    return result


def get_pattern_dict():
    """获取推广方式信息"""
    result = dict()
    sql = "select sn,pattern_name from extend_pattern_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = {x[0]: x[1] for x in raw}
    return result


def get_platform_dict():
    """获取推广端口信息"""
    result = dict()
    sql = "select sn,platform_name from extend_platform_info"
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = {x[0]: x[1] for x in raw}
    return result


def add(**kwargs):
    """添加链接"""
    message = {"message": "success"}
    flag = True
    for x in kwargs.keys():
        if x not in columns:
            flag = False
            message['message'] = '错误的参数：{}'.format(x)
            break
    if not flag:
        return message
    else:
        sql = db_module.structure_sql('add', table_name, **kwargs)
        ses = db_module.sql_session()
        try:
            ses.execute(sql)
            ses.commit()
        except Exception as e:
            print(e)
            message['message'] = '添加链接失败'
        finally:
            ses.close()
            return message


def edit(**kwargs):
    """编辑"""
    message = {"message": "success"}
    flag = True
    for x in kwargs.keys():
        if x not in columns:
            flag = False
            message['message'] = '错误的参数：{}'.format(x)
            break
    if not flag:
        return message
    else:
        try:
            sn = kwargs.pop('sn')
            query = "where sn={}".format(sn)
            sql = db_module.structure_sql('edit', table_name, query, **kwargs)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            ses.commit()
            message['message'] = "success" if proxy.rowcount == 1 else "编辑失败，没有此链接或没有删除的权限"
            ses.close()
        except KeyError as e:
            print(e)
            message['message'] = '{}不能为空'.format(e.args[0])
        finally:
            return message


def delete(sn):
    """删除"""
    message = {"message": "success"}
    ses = db_module.sql_session()
    try:
        query = "where sn={}".format(sn)
        sql = db_module.structure_sql('delete', table_name, query)
        proxy = ses.execute(sql)
        ses.commit()
        message['message'] = "success" if proxy.rowcount == 1 else "删除失败，没有此链接或没有删除的权限"
    except KeyError as e:
        print(e)
        message['message'] = '{}不能为空'.format(e.args[0])
    finally:
        ses.close()
        return message


def page(index=1, length=30):
    """分页查询链接，后台管理用，
    index是页码，
    length是每页多少条记录
    return  数组
    """
    result = []
    try:
        index = int(index)
        length = int(length)
    except ValueError:
        index = 1
        length = 30
    sql = ""
    skip = (index - 1) * length
    limit = length

    sql = "select {} from {} order by sn desc limit {},{}". \
        format(",".join(columns), table_name, skip, limit)

    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = [dict(zip(columns, x)) for x in raw]

    return result
