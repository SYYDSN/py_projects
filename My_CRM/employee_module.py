# -*-coding:utf-8-*-
import db_module
import hashlib
import datetime

""""员工模块"""

table_name = "employee_info"
columns = db_module.get_columns(table_name, True)


class Employee:
    def __init__(self, real_name, sex, company_sn, user_phone, user_password="123456", user_mail='', sn=None,
                 position_sn=None, born_date=None, team_sn=None, user_status=1):
        """
        员工类的构造方法。创建新员工请使用create方法。
        :param sn: sn
        :param real_name: 真实姓名
        :param sex: 性别
        :param position_sn: 职位的sn，对应position_info.sn 默认1
        :param company_sn: 所属公司的sn company_info.sn
        :param user_mail:  默认None
        :param user_phone: 必须，11位str
        :param user_password: 必须，1
        :param born_date: 默认None 出生日期
        :param team_sn:  团队sn，默认0，没有所属的团队。
        :param user_status:  用户状态，1为可用，0不可用。
        """
        self.sn = sn
        self.real_name = real_name
        self.sex = sex
        self.position_sn = position_sn
        self.company_sn = company_sn
        self.user_mail = user_mail
        self.user_phone = user_phone
        self.user_password = hashlib.md5(user_password.encode("utf8")).hexdigest()
        self.born_date = born_date
        self.team_sn = team_sn
        self.user_status = user_status

    def save(self):
        """写入数据库"""
        args = {k: v for k, v in self.__dict__.items() if v is not None}
        sql = db_module.structure_sql("add", table_name, **args)
        if "sn" in args.keys():  # 编辑的情况
            query = "where sn={}".format(args.pop('sn'))
            sql = db_module.structure_sql("edit", table_name, query, **args)
        ses = db_module.sql_session()
        ses.execute(sql)
        ses.commit()
        ses.close()

    @classmethod
    def create(cls, real_name, user_phone, company_sn, position_sn, sex=1, user_mail='', user_password="123456",
               born_date=None, team_sn=None):
        """创建用户"""
        obj = Employee(real_name=real_name, user_phone=user_phone, user_password=user_password, sex=sex,
                       user_mail=user_mail, born_date=born_date, company_sn=company_sn, position_sn=position_sn,
                       team_sn=team_sn)
        obj.save()
        return {"message": "success"}

    @classmethod
    def delete(cls, sn, company_sn):
        """
        删除用户
        :param sn: 用户sn
        :param company_sn: 公司sn
        :return: 删除结果的字典
        """
        sql = "delete from {} where sn={} and company_sn={}".format(table_name, sn, company_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        message = {"message": "success" if proxy.rowcount == 1 else "删除失败，没有此用户或没有删除的权限"}
        ses.commit()
        ses.close()
        return message

    @classmethod
    def count(cls, company_sn=0, team_sn=0):
        """统计员工人数"""
        where_str = ''
        if company_sn == 0:
            if team_sn == 0:
                pass
            else:
                where_str = "where team_sn={}".format(team_sn)
        else:
            if team_sn == 0:
                where_str = "where company_sn={}".format(company_sn)
            else:
                where_str = "where company_sn={} and team_sn={}".format(company_sn, team_sn)
        sql = "select count(1) from {} {}".format(table_name, where_str)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()[0]
        ses.close()
        return raw

    @classmethod
    def page(cls, company_sn=0, index=1, length=30):
        """分页查询，后台管理用，
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
        return result

    @classmethod
    def edit(cls, **kwargs):
        """
        编辑用户
        :param kwargs: 各种参数
        :return: 结果的字典
        """
        message = {"message": "success"}
        try:
            sn = kwargs.pop("sn")
            query = "where sn={}".format(sn)
            flag = True
            for x in kwargs.keys():
                if x not in columns:
                    flag = False
                    message['message'] = '错误的参数：{}'.format(x)
                    break
            if not flag:
                pass
            else:
                sql = db_module.structure_sql("edit", table_name, query, **kwargs)
                ses = db_module.sql_session()
                proxy = ses.execute(sql)
                message['message'] = "success" if proxy.rowcount == 1 else "编辑失败，没有此用户或没有删除的权限"
                ses.commit()
                ses.close()
        except KeyError:
            message['message'] = '缺少用户sn'
        except Exception as all_e:
            print(all_e)
            message['message'] = '数据库执行错位'
        finally:
            return message

    @classmethod
    def get_by_sn(cls, sn):
        """
        根据用户sn获取用户对象
        :return: Employee的实例
        """
        message = {"message": "success"}
        if sn is None:
            message['message'] = 'sn不能为空'
        else:
            query = "where sn={} and user_status=1".format(sn)
            sql = db_module.structure_sql("select", table_name, query)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            raw = proxy.fetchone()
            ses.close()
            if raw is None:
                return None
            else:
                args = dict(zip(columns, raw))
                obj = Employee(**args)
                return obj

    @classmethod
    def sn_name(cls, company_sn, manager=False):
        """返回sn和team_name的字典,manager表示是否要求是团队管理"""
        ses = db_module.sql_session()
        result = dict()
        sn_list = list()
        if manager:
            sql = "select sn from position_info where company_sn={} and has_team=1".format(company_sn)
            proxy = ses.execute(sql)
            raw = proxy.fetchall()
            if len(raw) == 0:
                pass
            else:
                sn_list = [x[0] for x in raw]

        sql = "select sn,real_name,position_sn from {} where company_sn={}".format(table_name, company_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
            if len(sn_list) == 0:
                pass
            else:
                result = {x[0]: x[1] for x in raw if x[2] in sn_list}

        return result

    @classmethod
    def sn_name_in_team(cls, team_sn):
        """返回sn和real_name的字典,"""
        ses = db_module.sql_session()
        result = dict()
        sql = "select sn,real_name from {} where team_sn={}".format(table_name, team_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
        return result

    @classmethod
    def sn_name_in_company(cls, company_sn):
        """返回sn和real_name的字典,"""
        ses = db_module.sql_session()
        result = dict()
        sql = "select sn,real_name from {} where company_sn={}".format(table_name, company_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
        return result

    def get_dict(self):
        return self.__dict__


def next_employee_sn():
    """分配客户给员工"""
    ses = db_module.sql_session()
    result = dict()
    sql = "select sn from company_info where user_status=1"
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if len(raw) == 0:
        pass
    else:
        sn_list = [x[0] for x in raw]
        result = {x: int(100 / len(sn_list)) for x in sn_list}


def check_login(user_name, user_password_md5):
    """检验登录"""
    user_name = user_name.strip()
    user_password_md5 = user_password_md5.strip()
    message = {"message": "success"}
    data = dict()
    if not db_module.validate_arg(user_name, "_"):
        message['message'] = "用户名非法"
    else:
        ses = db_module.sql_session()
        sql = "select user_password,sn,company_sn from employee_info where user_status=1 and user_phone='{}'".format(
            user_name)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        if raw is None:
            message['message'] = "用户名不存在"
        else:
            pwd = raw[0]
            if pwd != user_password_md5:
                message['message'] = "密码错误"
            else:
                data['employee_sn'] = raw[1]
                data['company_sn'] = raw[2]
                if message['message'] == 'success':
                    """检查团队"""
                    sql = "select sn from team_info where leader_sn={}".format(data['employee_sn'])
                    proxy = ses.execute(sql)
                    raw = proxy.fetchone()
                    if raw is None:
                        data['team_sn'] = -1
                    else:
                        data['team_sn'] = raw[0]
        ses.close()
    message['data'] = data
    return message


class Team:
    """团队类"""
    _table_name = "team_info"
    columns = db_module.get_columns(_table_name)

    def __init__(self, **kwargs):
        self.sn = kwargs.get("sn")
        self.team_name = kwargs["team_name"]
        self.leader_sn = kwargs["leader_sn"]
        self.company_sn = kwargs["company_sn"]

    def save(self):
        """保存"""
        args_dict = self.__dict__
        args = {k: v for k, v in args_dict.items() if v is not None}
        sql = db_module.structure_sql("add", self._table_name, **args)
        if "sn" in args.keys():  # 编辑的情况
            query = "where sn={}".format(args.pop('sn'))
            sql = db_module.structure_sql("edit", self._table_name, query, **args)
        ses = db_module.sql_session()
        ses.execute(sql)
        ses.commit()
        ses.close()

    @classmethod
    def children_sn_name(cls, employee_sn):
        """"
        求employee_sn的团队成员的sn和名字的对应关系的字典。
        1.如果此人没有自己的团队，返回本身的sn,name
        2.如果此人有自己的团队，返回他的团队成员的sn，name的dict
        3.如果此人的团队成员是其他团队的管理，那么返回团队的sn和name的dict
        4.如果此人的团队成员包含以上两种情况，则混合的返回以上两种情况组成的字典
        """
        sql = "select sn, real_name from {} where user_status=1 and " \
              "team_sn=(select sn from team_info where leader_sn={})".format(table_name, employee_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        if len(raw) == 0:
            sql = "select sn, real_name from employee_info where sn={}".format(employee_sn)
            proxy = ses.execute(sql)
            raw = proxy.fetchone()
            ses.close()
            return {raw[0]: raw[1]}
        else:
            result = dict()
            sn_name_dict = {x[0]: x[1] for x in raw}
            for k, v in sn_name_dict.items():
                sql = "select sn,team_name from team_info where leader_sn={}".format(k)
                proxy = ses.execute(sql)
                raw = proxy.fetchone()
                if raw is None:
                    result[k] = v
                else:
                    result[raw[0]] = raw[1]
            ses.close()
            return result

    @classmethod
    def delete_by_sn(cls, team_sn=None):
        """删除一个"""
        sql = "delete from {} where sn={}".format(cls._table_name, team_sn)
        ses = db_module.sql_session()
        ses.execute(sql)
        ses.commit()
        ses.close()

    @classmethod
    def count_by_condition(cls, **kwargs):
        """
        按照一定的条件统计，不做迭代统计
        :param kwargs: 统计条件的字典，比如 {sn:1}表示sn=1的条件
        :return: int
        """
        condition = " where {}".format(" and ".join(["{}='{}'".format(k, v) for k, v in kwargs.items()]))
        sql = "select count(1) from {}{}".format(cls._table_name, condition)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()[0]
        ses.close()
        return raw

    @classmethod
    def get_team_sn_by_leader_sn(cls, leader_sn):
        """
        根据领导的sn获取团队的sn
        :param leader_sn:
        :return:
        """
        sql = "select sn from team_info where leader_sn={}".format(leader_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        return raw[0]

    @classmethod
    def get_team_dict_by_leader_sn(cls, leader_sn):
        """
        根据领导的sn获取团队的sn和名字的字典
        :param leader_sn:
        :return:dict
        """
        sql = "select sn,team_name from team_info where leader_sn={}".format(leader_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        return {raw[0]: raw[1]}

    @classmethod
    def count_customer_by_employee_sn(cls, employee_sn, begin_date, all=False):
        """
        按照员工id统计客户数
        :param employee_sn:
        :param begin_date:  统计开始时间，这个一般是分配计划的开始时间
        :param all:  只统计按计划分配的还是统计所有的，默认只统计按计划分配的
        :return: int
        """
        all = "" if all else "and in_count_company=1"
        if isinstance(begin_date, datetime.datetime):
            begin_date = begin_date.strftime("%Y-%m-%d %H:%M:%S")
        sql = "select count(1) from customer_info where employee_sn={} {} and create_date>'{}'".format(
            employee_sn, all, begin_date)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()[0]
        ses.close()
        return raw

    @classmethod
    def count_customer_by_team_sn_simple(cls, team_sn):
        """
        根据team_sn统计客户数，不递归
        :param team_sn:
        :return:
        """
        ses = db_module.sql_session()
        sql = "select count(1) from customer_info where in_count_company=1 and team_sn={}".format(team_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        return raw[0]

    @classmethod
    def count_customer_by_team_sn(cls, team_sn, begin_date, all=False):
        """
        递归的统计一个团队的客户数目。
        :param team_sn: 团队sn
        :param begin_date:  统计开始时间，这个一般是分配计划的开始时间
        :param all:  只统计按计划分配的还是统计所有的，默认只统计按计划分配的
        :return: int
        """
        sql = "select employee_info.sn,position_info.has_team from " \
              "employee_info,position_info where employee_info.position_sn=position_info.sn and " \
              "employee_info.user_status=1 and employee_info.team_sn={}".format(team_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        result = 0
        if len(raw) == 0:
            return result
        else:
            team_sn_dict = {x[0]: x[1] for x in raw}
            for k, v in team_sn_dict.items():
                if v == 0:
                    result += cls.count_customer_by_team_sn_simple(team_sn=team_sn)
                    break
                else:
                    result += cls.count_customer_by_team_sn(cls.get_team_sn_by_leader_sn(k), begin_date, all)
            return result

    @classmethod
    def page(cls, condition_dict, order_by_col="sn", reverse=True, index=1, length=30):
        """分页查询，后台管理用，
        condition_dict  筛选条件 比如 {sn:1}表示sn=1的条件
        order_by_col  是拍序列的列名
        reverse   是否倒序
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

        skip = (index - 1) * length
        limit = length
        condition = " where {}".format(" and ".join(["{}='{}'".format(k, v) for k, v in condition_dict.items()]))
        order_by_str = "order by {} desc".format(order_by_col) if reverse else "order by {}".format(order_by_col)
        sql = "select {} from {} {} {} limit {},{}". \
            format(",".join(cls.columns), cls._table_name, condition, order_by_str, skip, limit)

        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = [dict(zip(cls.columns, x)) for x in raw]
        return result

    @classmethod
    def get_one_by_condition(cls, **kwargs):
        """
        根据条件获取对象
        kwargs  条件的字典，比如 {sn:1}表示sn=1的条件
        :return: 字典
        """
        condition = " where {}".format(" and ".join(["{}='{}'".format(k, v) for k, v in kwargs.items()]))
        sql = "select {} from {}{}".format(",".join(cls.columns), cls._table_name, condition)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is None:
            pass
        else:
            result = dict(zip(cls.columns, raw))
            return result

    @classmethod
    def find_root_team(cls, company_sn):
        """获取根团队sn"""
        sql = "select sn from team_info where company_sn={} and root_team=1".format(company_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is not None:
            return raw[0]

    @classmethod
    def get_sub_team_sn(cls, team_sn):
        """获取子团队sn"""
        sql = "select sn from team_info where leader_sn in (select sn from employee_info where team_sn={})".format(team_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) != 0:
            return [x[0] for x in raw]

    @classmethod
    def get_member_dict(cls, team_sn):
        """
        根据团队sn获取下面成员的
        :param team_sn:
        :return:dict
        """
        sql = "select employee_info.sn,position_info.has_team from " \
              "employee_info,position_info where employee_info.position_sn=position_info.sn and " \
              "employee_info.user_status=1 and employee_info.team_sn={}".format(team_sn)
        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            """说明没有子成员"""
            pass
        else:
            res = dict()
            if raw[0][1] == 1:
                for x in raw:
                    """说明这是团队"""
                    temp_dict = cls.get_team_dict_by_leader_sn(x[0])
                    res.update(temp_dict)
            else:
                res = Employee.sn_name_in_team(team_sn)
            return res

    @classmethod
    def get_plan_by_owner_sn(cls, owner_sn=0, curr=True):
        """
        根据拥有者id返回计划字典
        :param owner_sn:
        curr  是不是只返回当前使用的计划？
        :return: 字典的数组/字典
        """
        _table_name = "plan_info"
        plan_cols = db_module.get_columns(_table_name)
        if not curr:
            sql = "select {} from {} where owner_sn={}".format(",".join(plan_cols), _table_name, owner_sn)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            raw = proxy.fetchall()
            ses.close()
            res = [dict(zip(plan_cols, x)) for x in raw]
        else:
            sql = "select {} from {} where owner_sn={} and plan_status=1".format(",".join(plan_cols), _table_name, owner_sn)
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            raw = proxy.fetchone()
            ses.close()
            if raw is None:
                res = None
            else:
                res = dict(zip(plan_cols, raw))
        return res

    @classmethod
    def get_plan_detail(cls, plan_sn=None):
        ses = db_module.sql_session()
        """获取自己的分配计划详情"""
        sql = "select member_sn,per_num from plan_item_info where plan_sn={}".format(plan_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = {x[0]: x[1] for x in raw}
            return result

    @classmethod
    def allot_customer_by_team_sn(cls, team_sn):
        """分配客户，只分配到团队"""
        """先获取分配计划"""
        plan = cls.get_plan_by_owner_sn(team_sn)
        sub_team_sn = cls.get_sub_team_sn(team_sn)
        if sub_team_sn is None or len(sub_team_sn) == 0:
            """说明没有子团队"""
            return team_sn
        else:
            """没有计划的团队平均分配"""
            plan_dict = {sn: 100 / len(sub_team_sn) for sn in sub_team_sn}
            begin_plan = plan['update_date'].strftime("%Y-%m-%d %H:%M:%S")
            # today = datetime.date.today()
            # begin_plan = today.strftime("%Y-%m-%d %H:%M:%S")
            if plan is not None:
                """有计划的团队的分配"""
                begin_plan = plan['update_date'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(plan['update_date'], datetime.datetime) else plan['update_date']
                plan_dict = cls.get_plan_detail(plan['sn'])

            d = dict()
            # begin_plan = "2017-01-01"
            """计算各个团队已分配的客户人数"""
            for sn in plan_dict.keys():
                r = cls.count_customer_by_team_sn(sn, begin_plan)
                d[sn] = r

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

    @classmethod
    def allot_customer(cls, company_sn):
        """根据公司sn分配，返回的是team_sn"""
        root_team = cls.find_root_team(company_sn)
        if root_team is None:
            return company_sn
        else:
            team_sn = cls.allot_customer_by_team_sn(root_team)
            return team_sn


if __name__ == "__main__":
    Team.children_sn_team(12)
