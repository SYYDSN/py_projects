# -*-coding:utf-8-*-
import db_module

"""职务管理模块"""

table_name = "position_info"
columns = db_module.get_columns(table_name, True)


def position_count(company_sn):
    """统计"""
    sql = "select count(1) from {} where company_sn={}".format(table_name, company_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()[0]
    ses.close()
    return raw


def sn_name(company_sn):
    """返回sn和team_name的字典"""
    sql = "select sn,position_name from {} where company_sn={}".format(table_name, company_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        return dict()
    else:
        return {x[0]: x[1] for x in raw}


def add(**kwargs):
    """添加职务"""
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
            message['message'] = '添加职务失败'
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
            company_sn = kwargs.pop('company_sn')
            query = "where sn={} and company_sn={}".format(sn, company_sn)
            sql = db_module.structure_sql('edit', table_name, query, **kwargs)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            ses.commit()
            message['message'] = "success" if proxy.rowcount == 1 else "编辑失败，没有此职务或没有删除的权限"
            ses.close()
        except KeyError as e:
            print(e)
            message['message'] = '{}不能为空'.format(e.args[0])
        finally:
            return message


def delete(**kwargs):
    """删除"""
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
            company_sn = kwargs.pop('company_sn')
            query = "where sn={} and company_sn={}".format(sn, company_sn)
            sql = db_module.structure_sql('delete', table_name, query)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            ses.commit()
            message['message'] = "success" if proxy.rowcount == 1 else "删除失败，没有此职务或没有删除的权限"
            ses.close()
        except KeyError as e:
            print(e)
            message['message'] = '{}不能为空'.format(e.args[0])
        except Exception as e_all:
            print(e_all)
            message['message'] = '操作失败'
        finally:
            return message


def page(company_sn=0, index=1, length=30):
    """分页查询职位，后台管理用，
    company_sn
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

    if company_sn == 0:
        """所有分公司"""
        sql = "select {} from {} order by sn desc limit {},{}". \
            format(",".join(columns), table_name, skip, limit)
    else:
        sql = "select {} from {} where company_sn={} order by sn desc limit {},{}". \
            format(",".join(columns), table_name, company_sn, skip, limit)

    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = [dict(zip(columns, x)) for x in raw]
        result = sort_position(result, list())
    return result


def sort_position(position_list, result=list()):
    """对职位的数组进行排序"""
    if len(result) == 0:
        l1 = list()
        for x in position_list:
            if x['parent_sn'] == 0:
                result.append(x)
            else:
                l1.append(x)
        sort_position(l1, result)
    else:
        if len(set([x['parent_sn'] for x in result])) == 2:
            for i, n in enumerate(result):
                if i % 2 == 0 and n['parent_sn'] != 0:
                    n['color'] = '#E1FFFF'
                elif i % 2 == 1 and n['parent_sn'] != 0:
                    n['color'] = '#FFFACD'
                else:
                    pass

        if len(position_list) > 0:
            l1 = list()
            for x in position_list:
                find = False
                parent_sn = x['parent_sn']
                for index, y in enumerate(result):
                    if parent_sn == y['sn']:
                        try:
                            x['color'] = y['color']
                        except KeyError:
                            pass
                        result.insert(index + 1, x)
                        find = True
                        break
                    else:
                        pass
                if not find:
                    l1.append(x)
            sort_position(l1, result)
        else:
            pass
    return result


# a=[{'company_sn': 2, 'parent_sn': 2, 'position_name': '团队经理', 'sn': 3}, {'company_sn': 2, 'parent_sn': 0, 'position_name': '销售总监', 'sn': 2}]
# print(sort_position(a))
