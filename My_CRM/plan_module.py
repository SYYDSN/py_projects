# -*- coding:utf-8 -*-
import db_module
import datetime
from company_module import company_count


"""分配策略模块"""
table_name = "plan_info"
columns = db_module.get_columns(table_name, True)
cache = db_module.cache


def plan_count(owner_sn=0):
    """统计所有数量,owner_sn是计划所有者的sn
    返回int对象
    """
    session = db_module.sql_session()
    result = 0
    sql = "select count(1) from {} where owner_sn={}".format(table_name, owner_sn)
    try:
        proxy_result = session.execute(sql)
        result = proxy_result.fetchone()[0]
    finally:
        session.close()
    return result


def get_plan(owner_sn=0):
    """获取分配计划"""
    """先获取分配计划的sn"""
    sql = "select sn,update_date from {} where plan_status=1 and owner_sn={}".format(table_name, owner_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    plan_sn = 1  # 默认计划编号
    begin_plan = datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")  # 默认的计划开始时间
    result = dict()
    if raw is None:
        pass
    else:
        plan_sn = raw[0]
        begin_plan = raw[1]
    if plan_sn == 1:
        """默认分配计划
        默认分配计划是平均分配，先获取所有有效公司的sn
        """
        sql = "select sn from company_info where user_status=1"
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            pass
        else:
            sn_list = [x[0] for x in raw]
            result = {x: int(100/len(sn_list)) for x in sn_list}
    else:
        """不是默认计划，就要获取sn和分配比率"""
        sql = "select member_sn,per_num from plan_item_info where plan_sn={}".format(plan_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
    ses.close()
    return result, begin_plan


def get_plan_team(owner_sn=0):
    """获取分团队配计划"""
    ses = db_module.sql_session()
    sql = "select sn from employee_info where user_status=1 and team_sn={}".format(owner_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    begin_plan = datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")  # 默认的计划开始时间
    if len(raw) == 0:
        pass
    else:
        sn_list = [x[0] for x in raw]
        result = {x: int(100 / len(sn_list)) for x in sn_list}
    ses.close()
    return result, begin_plan


def __get_next(plan_dict, begin_plan):
    """根据分配计划字典和计划开始时间，计算下一个获取资源的客户的sn，
    plan_dict  分配计划，是分公司sn和分配比率的字典
    begin_plan  是计算分配比率的起始时间。
    以上两个参数可以直接由get_plan函数获取
    return 被分配的分公司的sn
    """
    ses = db_module.sql_session()
    d = dict()
    # begin_plan = begin_plan.strftime("%Y-%m-%d %H:%M:%S")
    for sn in plan_dict.keys():
        sql = "select count(1) from customer_info where company_sn={} and in_count=1 and create_date>'{}'".format(sn, begin_plan)
        proxy = ses.execute(sql)
        r = proxy.fetchone()[0]
        d[sn] = r
    ses.close()
    all_count = sum(list(d.values()))
    if all_count == 0:
        return list(plan_dict.keys())[0]
    else:
        result = list(plan_dict.keys())[0]
        for k, v in d.items():
            if (v / all_count) < (plan_dict[k] / 100):
                result = k
                break
        return result


def next_company_sn(owner=0):
    """获取下一个被分配公司的sn
    owner 计划拥有者的sn，对应company_info.sn，如果为0,则表示为总公司的策略。
    """
    result = get_plan(owner)
    if len(result) == 0:
        raise ValueError("没有公司参与分配")
    else:
        plan_dict, begin_plan = get_plan(owner)
        result = __get_next(plan_dict, begin_plan)
        return result


def page(index=1, length=30, term='', key_word=''):
    """分页查询，后台管理用，index是页码，length是每页多少条记录
    term是查询的条件 相当于 where case=value中的case
    key_word查询条件的值 相当于 where case=value中的value
    """
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            ses = db_module.sql_session()
            columns = db_module.get_columns(table_name)
            if term != "" and key_word != "" and term in columns:
                sql = "select " + ",".join(columns) + (" from {} where {}='{}' order by create_date desc "
                                                       "limit {},{}".format(table_name, term, key_word, (index - 1) * length, length))
            else:
                sql = "select " + ",".join(columns) + (" from {} order by create_date desc "
                                                   "limit {},{}".format(table_name, (index - 1) * length, length))
            try:
                proxy_result = ses.execute(sql)
                result = proxy_result.fetchall()
                if len(result) != 0:
                    result = [db_module.str_format(x) for x in result]
                    data = [dict(zip(columns, x)) for x in result]
                    data = db_module.str_format(data)
                    """根据策略sn查询成员数目"""
                    for x in data:
                        if x['sn'] == 1:  # 默认策略的情况
                            x["member_count"] = company_count(parent_sn=0)
                        else:
                            sql = "select count(1) from plan_item_info where plan_sn={}".format(x['sn'])
                            proxy = ses.execute(sql)
                            member_count = proxy.fetchone()[0]
                            x["member_count"] = member_count
                else:
                    data = []

                message['data'] = data
            except Exception as e:
                print(e)
                message['message'] = "查询错误"
            finally:
                ses.close()
        except TypeError:
            message['message'] = "参数错误"
        finally:
            pass
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message


def get_members(parent_sn):
    """根据parent_sn获取可用的团队成员"""
    result = dict()
    sql = "select sn,company_name from company_info where user_status=1 and parent_sn={}".format(parent_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        result = {x[0]: x[1] for x in raw}
    return result


def get_team_members(parent_sn):
    """根据parent_sn获取可用的团队成员"""
    result = dict()
    sql = "select sn,real_name from employee_info where user_status=1 and team_sn={}".format(parent_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        ses.close()
        return result
    else:
        result = {x[0]: x[1] for x in raw}
        sql = "select leader_sn,sn,team_name from team_info where company_sn=(select company_sn from team_info" \
              " where sn={})".format(parent_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        raw = {x[0]: [x[1], x[2]] for x in raw}
        ses.close()
        new_res = dict()
        for k, v in result.items():
            if k in raw:
                temp = raw[k]
                new_res[temp[0]] = temp[1]
            else:
                new_res[k] = v
    return new_res


def process(**kwargs):
    """对计划及其参与者的添加，修改，删除"""
    message = {"message": "success"}
    the_type = kwargs.pop("the_type")
    now = db_module.current_datetime()
    kwargs['create_date'] = now
    kwargs['update_date'] = "1970-01-01"
    try:
        member_list = kwargs.pop('member_list')
    except KeyError:
        member_list = list()
    ses = db_module.sql_session()
    if the_type == "add":
        """添加策略"""
        sql = db_module.structure_sql("add", table_name, **kwargs)
        proxy = ses.execute(sql)
        plan_sn = proxy.lastrowid
        for member in member_list:
            member['plan_sn'] = plan_sn
            member['create_date'] = now
            sub = db_module.structure_sql("add", "plan_item_info", **member)
            ses.execute(sub)
        ses.commit()
    elif the_type == "edit":
        plan_sn = kwargs.pop("sn")
        query = "where sn={}".format(plan_sn)
        sql = db_module.structure_sql("edit", table_name, query, **kwargs)
        ses.execute(sql)
        sql = "select sn,member_sn,per_num from plan_item_info where plan_sn={}".format(plan_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        # 添加容器，更新容器和删除容器。
        add_list, edit_list, delete_list = list(), list(), list()
        if len(raw) == 0:
            pass
        else:
            raw = [dict(zip(('sn', 'member_sn', "per_num"), x)) for x in raw]
            delete_list = [x for x in raw if x['sn'] not in [int(y['sn']) for y in member_list if y['sn'] != ""]]
            add_list = [x for x in member_list if x['sn'] == ""]
            edit_list = [x for x in member_list if x['sn'] in [str(y['sn']) for y in raw]]

            for x in delete_list:
                sql = "delete from plan_item_info where sn={}".format(x['sn'])
                ses.execute(sql)
            for x in edit_list:
                sql = "update plan_item_info set member_sn={},per_num={} where sn={}".format(x['member_sn'], x['per_num'], x['sn'])
                ses.execute(sql)
            for x in add_list:
                x.pop("sn")
                x['create_date'] = now
                x['plan_sn'] = plan_sn
                sql = db_module.structure_sql("add", "plan_item_info", **x)
                ses.execute(sql)
            ses.commit()
    elif the_type == "delete":
        plan_sn = kwargs.pop("sn")
        sql = "delete from {} where sn={}".format(table_name, plan_sn)
        ses.execute(sql)
        ses.commit()
    elif the_type in ("up", "down"):
        plan_status = 1 if the_type == "up" else 0
        plan_sn = kwargs.pop("sn")
        owner_sn = kwargs.pop("owner_sn")
        if plan_status:
            sql = "update {} set plan_status=0 where owner_sn={}".format(table_name, owner_sn)
            ses.execute(sql)
            sql = "update {} set plan_status=1,update_date='{}' where sn={}".format(table_name, now, plan_sn)
            ses.execute(sql)
        else:
            sql = "update {} set plan_status=0 where sn={}".format(table_name, plan_sn)
            ses.execute(sql)
        ses.commit()
    else:
        message['message'] = "不理解的操作"
    ses.close()
    return message


def get_plan_item(plan_sn):
    """根据分配计划的sn，获取参与分配的团队的信息，返回的是字典的数组"""
    sql = "select sn,member_sn,per_num from plan_item_info where plan_sn={}".format(plan_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        return list()
    else:
        return [dict(zip(("sn", "member_sn", "per_num"), x)) for x in raw]


if __name__ == "__main__":
    print(next_company_sn())