#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import abort
import json
from tools_module import *
from bson.regex import Regex
from model.company_module import Company
from model.company_module import ResumeFavorite
from model.identity_validate import GlobalSignature
from model.driver_module import DriverResume
from flask import request
import os
import random
import base64
from mongo_db import db_name
from mongo_db import DBRef


"""注册蓝图"""
web_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/web", template_folder="templates/web")


"""用于站点部分的视图函数"""


def login_func():
    """登录函数"""
    method = request.method.lower()
    if method == "get":
        """登录页面"""
        return render_template("web/web_login.html")
    elif method == "post":
        mes = {"message": "success"}
        user_name = request.form.get("user_name", None)
        user_password = request.form.get("user_password", None)
        if user_name and user_password:
            r = Company.login(user_name=user_name, user_password=user_password, can_json=False)
            if r['message'] == "success":
                save = {"user_name": user_name, "user_password": user_password, "user_id": r['data']['_id']}
                save_platform_session(**save)
            else:
                mes = r
        else:
            mes['message'] = "用户名或密码必须"
        return json.dumps(mes)
    else:
        return abort(405)


def resume_favorite_func(key):
    """
    对公司的简历搜藏夹的操作.目前主要是以下2种操作:
    1. 把简历加入公司的收藏夹
    2. 把简历移出公司的收藏夹
    :return:
    """
    mes = {"message": "success"}
    company_id = get_platform_session_arg("user_id")
    if isinstance(company_id, ObjectId):
        if key == "add":
            """加入收藏夹"""
            resume_id = get_arg(request, "id", "")
            if isinstance(resume_id, str) and len(resume_id) == 24:
                resume = DriverResume.find_by_id(resume_id)
                if isinstance(resume, DriverResume):
                    resume_dbref = resume.get_dbref()
                    company_dbref = DBRef(database=db_name, collection=Company.get_table_name(), id=company_id)
                    obj = ResumeFavorite(resume_id=resume_dbref, company_id=company_dbref)
                    r = obj.save_plus()
                    if isinstance(r, ObjectId):
                        pass
                    else:
                        mes['message'] = "save fail"
                else:
                    mes['message'] = "无效的id:{}".format(resume_id)
            else:
                mes['message'] = "invalid id:{}".format(resume_id)
        elif key == "remove":
            """从收藏夹移除"""
            resume_id = get_arg(request, "id", "")
            if isinstance(resume_id, str) and len(resume_id) == 24:
                resume = DriverResume.find_by_id(resume_id)
                if isinstance(resume, DriverResume):
                    resume_dbref = resume.get_dbref()
                    company_dbref = DBRef(database=db_name, collection=Company.get_table_name(), id=company_id)
                    f = {"company_id": company_dbref, "resume_id": resume_dbref}
                    r = ResumeFavorite.find_one_and_delete(filter_dict=f)
                    if r is None:
                        mes['message'] = "移除失败"
                    else:
                        pass
                else:
                    mes['message'] = "无效的id:{}".format(resume_id)
            else:
                mes['message'] = "invalid id:{}".format(resume_id)
        else:
            mes['message'] = "无效的操作:{}".format(key)
    else:
        mes['message'] = "authenticity validate fail"
    return json.dumps(mes)


def driver_page_func():
    """
    分页显示页面信息
    :return:
    """
    company_id = get_platform_session_arg("user_id")
    if isinstance(company_id, ObjectId):
        args = dict()  # 传给DriverResume.query_by_page的参数字典
        url_path = request.path  # 当前web路径
        q = dict()  # 查询条件
        keywords = request.args.get("keywords", "")  # 搜索关键词
        keywords = keywords.strip()
        if keywords == "":
            pass
        else:
            keywords = [x.strip() for x in keywords.split(" ") if x.strip() != ""]
            if len(keywords) == 0:
                pass
            else:
                """填充搜索条件,匹配其他表的字段先忽视,因为那需要一个检索服务器,比如elasticsearch"""
                or_list = list()
                """匹配简历的字段"""
                fields = ["living_place", "address", "email"]  # 模糊匹配字段
                for word in keywords:
                    for field in fields:
                        t = {field: {"$regex": Regex("\S*{}\S*".format(word))}}
                        or_list.append(t)
                q['$or'] = or_list
        now = datetime.datetime.now()
        """从业年限"""
        i_exp = request.args.get("i_exp", "")
        if i_exp == "":
            pass
        else:
            try:
                i_exp = int(i_exp)
            except Exception as e:
                print(e)
        if isinstance(i_exp, int) and i_exp > 0:
            i_exp = now - datetime.timedelta(days=365 * i_exp)
            q['rtqc_first_date'] = {"$lte": i_exp}
        """工作经验"""
        work_exp = request.args.get("work_exp", "")
        if work_exp == "":
            pass
        else:
            try:
                work_exp = int(work_exp)
            except Exception as e:
                print(e)
        if isinstance(work_exp, int) and work_exp > 0:
            work_exp = now - datetime.timedelta(days=365 * work_exp)
            q['first_work_date'] = {"$lte": work_exp}
        """驾龄"""
        driving_exp = request.args.get("driving_exp", "")
        if driving_exp == "":
            pass
        else:
            try:
                driving_exp = int(driving_exp)
            except Exception as e:
                print(e)
        if isinstance(driving_exp, int) and driving_exp > 0:
            driving_exp = now + datetime.timedelta(days=365 * i_exp)
            q['dl_first_date'] = {"$lte": driving_exp}
        """发布时间"""
        update_date = request.args.get("update_date", "")
        times = ['today', 'three_day', 'week', 'month', 'three_month', 'half_year']
        if update_date in times:
            if update_date == "today":
                delta = datetime.timedelta(days=1)
            elif update_date == "three_day":
                delta = datetime.timedelta(days=3)
            elif update_date == "week":
                delta = datetime.timedelta(days=7)
            elif update_date == "month":
                """不精确,暂时这样"""
                delta = datetime.timedelta(days=30)
            elif update_date == "three_month":
                delta = datetime.timedelta(days=90)
            else:
                delta = datetime.timedelta(days=181)
            q['update_date'] = {"$gte": now - delta}
        """当前状态"""
        status = request.args.get("driver_status", "")
        if status == "":
            pass
        else:
            try:
                status = int(status)
            except Exception as e:
                print(e)
                status = 0
            finally:
                q['status'] = status
        """驾照级别"""
        dl_license_class = request.args.get("dl_class", "")
        if dl_license_class == "":
            pass
        else:
            q['dl_license_class'] = dl_license_class.upper()
        """期望待遇"""
        expected_salary = request.args.get("salary", "")
        if isinstance(expected_salary, str) and expected_salary.find(",") != -1:
            salary = [int(x) for x in expected_salary.split(",")]
            min_s = salary[0]
            max_s = salary[-1]
            q['expected_salary'] = {"$elemMatch": {"$gte": min_s, "$lte": max_s}}
        """教育程度"""
        education = None
        education_str = request.args.get("education", "1")
        try:
            education = int(education_str)
        except Exception as e:
            print(e)
        finally:
            if isinstance(education, int):
                q['education'] = {"$gte": education}
        args['filter_dict'] = q  # 添加搜索条件
        s = {"update_date": -1}  # 默认排序字典
        args['sort_dict'] = s   # 添加排序字典
        projection = [
            "_id", "education", "work_experience", "industry_experience",
            "driving_experience", "gender", "real_name", "age", "status",
            "dl_license_class", "dl_first_date", "rtqc_license_class",
            "rtqc_first_date", "want_job", "expected_salary", "birth_date",
            "last_company", "first_work_date", "update_date"
        ]
        args['projection'] = projection  # 添加投影数组
        """页码"""
        page_index = 1
        index = request.args.get("index", "1")  # 第几页
        try:
            page_index = int(index)
        except Exception as e:
            print(e)
        finally:
            args['page_index'] = page_index
        r = DriverResume.query_by_page(**args)
        resumes = r['data']
        favorite_map = Company.in_favorite(company_id=company_id, drivers=[x['_id'] for x in resumes], to_str=False)
        return render_template("web/drivers.html", url_path=url_path, resumes=resumes, total_record=r['total_record'],
                               total_page=r['total_page'], pages=r['pages'], page_index=page_index,
                               favorite_map=favorite_map)
    else:
        return redirect(url_for("web_blueprint.login_func"))


def company_resume_func():
    """
    公司客户操作司机简历的处理函数,目前的功能是:
    1. (公司客户)浏览司机简历.
    :return:
    """
    company_id = get_platform_session_arg("user_id")
    resume_id = get_arg(request, "id", "")
    if isinstance(resume_id, str) and len(resume_id) == 24:
        resume_id = ObjectId(resume_id)
    if isinstance(company_id, ObjectId) and isinstance(resume_id, ObjectId):
        """查看简历"""
        resume = DriverResume.find_by_id(o_id=resume_id, to_dict=True)
        head_image = resume.get("head_image")  # 头像
        if head_image is None:
            iu = os.path.join(__project_dir__, 'static', 'image', 'web', '{}.png'.format(random.randint(1, 3)))
            with open(iu, "rb") as f:
                head_image = f.read()
        head_image = base64.b64decode(head_image)
        return render_template("web/resume.html", head_image=head_image)
    else:
        return redirect(url_for("web_blueprint.login_func"))


"""集中注册函数"""


"""注册"""
web_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""对公司的简历收藏夹的操作"""
web_blueprint.add_url_rule(rule="/favorite/<key>", view_func=resume_favorite_func, methods=['get', 'post'])
"""分页查询司机信息"""
web_blueprint.add_url_rule(rule="/drivers", view_func=driver_page_func, methods=['get', 'post'])
"""公司客户查看司机简历"""
web_blueprint.add_url_rule(rule="/company/resume", view_func=company_resume_func, methods=['get'])
