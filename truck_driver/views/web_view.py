#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import send_file
from flask import make_response
from flask import abort
import json
from tools_module import *
from bson.regex import Regex
from model.company_module import Company
from model.company_module import ResumeFavorite
from model.company_module import Consign
from model.company_module import Resp
from model.identity_validate import GlobalSignature
from model.driver_module import DriverResume
from model.driver_module import WorkHistory
from model.driver_module import Honor
from model.driver_module import Education
from model.driver_module import Region
from flask import request
import os
import random
import base64
from io import BytesIO
from mongo_db import get_conn
from mongo_db import db_name
from mongo_db import DBRef
from mongo_db import BaseFile


"""注册蓝图"""
web_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/web", template_folder="templates/web")


"""用于公司客户站点部分的视图函数"""


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


def logout_func():
    """登出函数"""
    clear_platform_session()
    return redirect(url_for("web_blueprint.login_func"))


def resume_favorite_func(key):
    """
    对公司的简历搜藏夹的操作.目前主要是以下2种操作:
    1. 把简历加入公司的收藏夹
    2. 把简历移出公司的收藏夹
    :return:
    """
    mes = {"message": "success"}
    company_id = get_platform_session_arg("user_id")
    if company_id is None:
        return abort(403)
    else:
        company = Company.find_by_id(company_id)
        if isinstance(company, Company):
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
            elif key == "batch_remove":
                """从收藏夹批量移除"""
                ids = get_arg(request, "ids", "")
                if isinstance(ids, str) and len(ids) >= 24:
                    ids = ids.split(",")
                    fs = list()
                    for x in ids:
                        if len(x) == 24:
                            d_id = ObjectId(x)
                            dbref = DBRef(database=db_name, collection=DriverResume.get_table_name(), id=d_id)
                            fs.append(dbref)
                    f = {"company_id": company.get_dbref(), "resume_id": {"$in": fs}}
                    ResumeFavorite.delete_many(filter_dict=f)
                else:
                    mes['message'] = "invalid ids:{}".format(ids)
            else:
                mes['message'] = "无效的操作:{}".format(key)
        else:
            mes['message'] = "authenticity validate fail"
        return json.dumps(mes)


def driver_page_func():
    """
    分页显示司机简历页面信息
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


def random_resume() -> str:
    """
    根据企业用户的id和当前简历的id,随机从数据库中跳出指定数量的简历并返回.
    :return: json
    """
    company_id = get_platform_session_arg("user_id")
    resume_id = get_arg(request, "id", "")
    if isinstance(company_id, ObjectId) and isinstance(resume_id, str) and len(resume_id) == 24:
        resume_id = ObjectId(resume_id)
        num = get_arg(req=request, arg="num", default_value="2")
        try:
            num = int(num)
        except Exception as e:
            print(e)
            num = 2
        finally:
            pass
        mes = {"message": "success"}
        """可以取出指定数量的随机的用户"""
        key = "exclude_users_{}".format(str(company_id))
        exclude_users = cache.get(key)
        exclude_users = [resume_id] if exclude_users is None else exclude_users
        ef = {"_id": {"$nin": exclude_users}}
        ep = ['_id', 'head_image']
        es = DriverResume.find_plus(filter_dict=ef, projection=ep, limit=num, to_dict=True)  # 随机用户
        for x in es:
            t = dict()
            e_id = x['_id']
            exclude_users.append(e_id)
            x['_id'] = str(e_id)
            img_dbref = x['head_image']
            r_url = "/web/file/get/{}?fid={}".format(img_dbref.collection, img_dbref.id)
            x['head_image'] = r_url
        cache.set(key, exclude_users, timeout=1800)  # 已取过的随机用户缓存30分钟
        mes['data'] = es
        return json.dumps(mes)
    else:
        return abort(403)


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
        """查简历"""
        resume = DriverResume.find_by_id(resume_id, to_dict=True)
        if resume is None:
            return abort(404)
        else:
            """处理头像url"""
            head_image = resume.get("head_image")  # 头像
            if head_image is None:
                head_img_url = ""
            else:
                head_img_url = "/web/file/get/{}?fid={}".format(head_image.collection, head_image.id)
            """隐藏身份证后8位"""
            id_num = resume.get("id_num")
            if isinstance(id_num, str) and len(id_num) > 10:
                id_num = id_num[0: 10] + "********"
                resume['id_num'] = id_num
            """处理学历"""
            resume['education'] = "" if (resume['education'] - 1) < 1 or (resume['education'] - 1) > 4 else \
                ['小学', '中专', '大专', '本科'][resume['education'] - 1]
            """处理婚否"""
            married = {-1: "离异", 0: "未婚", 1: "已婚"}.get(resume['married'])
            resume['married'] = married if married else ""
            """处理状态"""
            status = {-1: "个体经营", 0: "离职", 1: "在职"}.get(resume.get('status'))
            resume['status'] = status if status else ""
            """查询工作经历"""
            work_history = resume.get("work_history")
            vehicle_type = ""  # 常驾车型
            if isinstance(work_history, list) and len(work_history) > 0:
                """有工作经历"""
                ids = [x.id for x in work_history]
                s = {"begin": -1}
                work_history = WorkHistory.find_plus(filter_dict={"_id": {"$in": ids}}, sort_dict=s, to_dict=True)
                for x in work_history:
                    y = x.get("vehicle_type")
                    x['begin'] = x['begin'].strftime("%F") if isinstance(x['begin'], datetime.datetime) else x['begin']
                    x['end'] = x['end'].strftime("%F") if isinstance(x['end'], datetime.datetime) else x['end']
                    if vehicle_type == "" and isinstance(y, str) and len(y) > 0:
                        vehicle_type = y  # 把第一个找到的车型当作常驾车型
                        resume['vehicle_type'] = vehicle_type
                        break
                    else:
                        pass
            else:
                work_history = list()
            """取教育经历"""
            education_history = resume.get("education_history")
            if isinstance(education_history, list) and len(education_history) > 0:
                ids = [x.id for x in education_history]
                s = {"begin": -1}
                education_history = Education.find_plus(filter_dict={"_id": {"$in": ids}}, sort_dict=s, to_dict=True)
                for x in education_history:
                    x['begin'] = x['begin'].strftime("%F") if isinstance(x['begin'], datetime.datetime) else x['begin']
                    x['end'] = x['end'].strftime("%F") if isinstance(x['end'], datetime.datetime) else x['end']
            else:
                education_history = list()
            """取荣誉证书"""
            honor_history = resume.get("honor")
            if isinstance(honor_history, list) and len(honor_history) > 0:
                ids = [x.id for x in honor_history]
                s = {"time": -1}
                honor_history = Honor.find_plus(filter_dict={"_id": {"$in": ids}}, sort_dict=s, to_dict=True)
                for x in honor_history:
                    x['time'] = x['time'].strftime("%F") if isinstance(x['time'], datetime.datetime) else x['time']
            else:
                honor_history = list()
            """收藏映射"""
            favorite_map = Company.in_favorite(company_id=company_id, drivers=[resume['_id']], to_str=False)

            return render_template("web/resume.html", resume=resume, head_img_url=head_img_url,
                                   work_history=work_history, vehicle_type=vehicle_type, honor_history=honor_history,
                                   education_history=education_history, favorite_map=favorite_map)
    else:
        return redirect(url_for("web_blueprint.login_func"))


def favorite_func() -> str:
    """公司客户收藏夹页面"""
    company_id = get_platform_session_arg("user_id")
    if company_id is None:
        return redirect(url_for("web_blueprint.login_func"))
    else:
        company = Company.find_by_id(company_id)
        url_path = request.path  # 当前web路径
        if isinstance(company, Company):
            page_index = 1  # 页码
            index = request.args.get("index", "1")  # 第几页
            try:
                page_index = int(index)
            except Exception as e:
                print(e)
            company_dbref = company.get_dbref()
            f = {"company_id": company_dbref}
            s = {"time": -1}
            p = ['_id', "resume_id"]
            r = ResumeFavorite.query_by_page(filter_dict=f, sort_dict=s, projection=p, page_index=page_index, page_size=10)
            ids = [x['resume_id'].id for x in r['data']]
            f = {"_id": {"$in": ids}}
            resumes = DriverResume.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
            for x in resumes:
                """转期望待遇的数组为字符串,以方便前端展示,此函数已集成在DriverResume类中"""
                expected_salary = x.get("expected_salary")
                if isinstance(expected_salary, list):
                    expected_salary = expected_salary[0:2]
                    if len(expected_salary) == 1:
                        expected_salary = "{}k".format(round(expected_salary[0] / 1000, 1))
                    else:
                        expected_salary = "{}k至{}k".format(round(expected_salary[0] / 1000, 1),
                                                           round(expected_salary[1] / 1000, 1))
                else:
                    expected_salary = "面议"
                x['expected_salary'] = expected_salary

            favorite_map = Company.in_favorite(company_id=company_id, drivers=ids, to_str=False)
            return render_template("web/favorite.html", resumes=resumes, total_record=r['total_record'],
                                   total_page=r['total_page'], pages=r['pages'], page_index=page_index,
                                   favorite_map=favorite_map, url_path=url_path)
        else:
            return redirect(url_for("web_blueprint.login_func"))


def add_consign_func() -> str:
    """公司客户填写委托招聘的页面"""
    company_id = get_platform_session_arg("user_id")
    mes = {"message": "success"}
    method = request.method.lower()
    if company_id is None:
        if method == "get":
            return redirect(url_for("web_blueprint.login_func"))
        else:
            mes['message'] = "authentication fail"
            return json.dumps(mes)
    else:
        company = Company.find_by_id(company_id)
        url_path = "/web/consign_list"  # 当前web路径,固定值,和我的委托共用url
        if isinstance(company, Company):
            if method == "get":
                """返回添加委托页面"""
                province_list = Region.get_province()  # 取省的列表
                """取sid,consign的id,如果这个id为空或者查找不到对应的对象,表示是新建委托"""
                consign = request.args.get("s_id", None)
                if isinstance(consign, str) and len(consign) == 24:
                    consign = Consign.find_by_id(o_id=consign, can_json=True)
                consign = dict() if consign is None else consign
                return render_template("web/consign.html", url_path=url_path, province_list=province_list,
                                       consign=consign)
            else:
                """添加/编辑委托的请求"""
                args = get_args(request)
                the_type = args.pop("type", None)
                now = datetime.datetime.now()
                if the_type == "add":
                    args.pop("_id", None)
                    args['create_date'] = now
                    args['update_date'] = now
                    args['company_id'] = company.get_dbref()
                    """对参数进行处理"""
                    industry_experience = args.pop('industry_experience', "")
                    if isinstance(industry_experience, int):
                        args['industry_experience'] = industry_experience
                    elif isinstance(industry_experience, str) and industry_experience.isdigit():
                        args['industry_experience'] = int(industry_experience)
                    else:
                        pass
                    welfare = args.pop("welfare", "")  # 福利待遇
                    welfare = [x.strip() for x in welfare.split(",")]
                    args['welfare'] = welfare
                    driving_experience = args.pop("driving_exp", None)  # 驾龄
                    if driving_experience is None:
                        pass
                    else:
                        if isinstance(driving_experience, int):
                            args['driving_experience'] = driving_experience
                        elif isinstance(driving_experience, str) and driving_experience.isdigit():
                            args['driving_experience'] = int(driving_experience)
                        else:
                            pass
                    work_experience = args.pop("work_exp", None)  # 工作年限
                    if work_experience is None:
                        pass
                    else:
                        if isinstance(work_experience, int):
                            args['work_experience'] = work_experience
                        elif isinstance(work_experience, str) and work_experience.isdigit():
                            args['work_experience'] = int(work_experience)
                        else:
                            pass
                    """创建并保存对象"""
                    consign = Consign.instance(**args)
                    object_id = None
                    try:
                        object_id = consign.save_plus()
                    except Exception as e:
                        print(e)
                        logger.exception(e)
                    finally:
                        if isinstance(object_id, ObjectId):
                            pass
                        else:
                            mes['message'] = "保存失败"
                elif the_type == "update":
                    """编辑委托"""
                    pass
                else:
                    mes['message'] = "不支持的操作"
                return json.dumps(mes)
        else:
            if method == "get":
                return redirect(url_for("web_blueprint.login_func"))
            else:
                mes['message'] = "authentication fail"
                return json.dumps(mes)


def consign_list_func() -> str:
    """公司客户委托列表的页面"""
    company_id = get_platform_session_arg("user_id")
    method = request.method.lower()
    if method == "get" and isinstance(company_id, ObjectId):
        company = Company.find_by_id(company_id)
        url_path = "/web/consign_list"  # 当前web路径,固定值,和我的委托共用url
        if isinstance(company, Company):
            """页码"""
            page_index = 1
            index = request.args.get("index", "1")  # 第几页
            try:
                page_index = int(index)
            except Exception as e:
                print(e)
            finally:
                pass
            f = {"company_id": company.get_dbref()}
            s = {"update_date": -1}
            page_size = 3
            res = Consign.query_by_page(filter_dict=f, sort_dict=s, page_index=page_index, page_size=page_size)
            consign_list = res['data']
            current_page = res['current_page']
            pages = res['pages']
            total_page = res['total_page']
            total_record = res['total_record']
            return render_template("web/consign_list.html", url_path=url_path, consign_list=consign_list, pages=pages,
                                   total_page=total_page, total_record=total_record,
                                   page_index=page_index)
        else:
            return redirect(url_for("web_blueprint.login_func"))
    else:
        return abort(405)


def resp_page_func():
    """
    分页显示委托招聘的反馈页面信息
    :return:
    """
    company_id = get_platform_session_arg("user_id")
    method = request.method.lower()
    if method == 'get':
        if isinstance(company_id, ObjectId):
            company = Company.find_by_id(company_id)
            if isinstance(company, Company):
                args = dict()
                url_path = request.path  # 当前web路径
                q = dict()  # 查询条件
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
                page_size = 10
                args['page_size'] = page_size
                f = {"company_id": company.get_dbref()}
                consign_id = get_arg(request, "cid", "")  # consign的id,
                if isinstance(consign_id, str) and len(consign_id) == 24:
                    consign = Consign.find_by_id(consign_id)
                    if isinstance(consign, Consign):
                        f['consign_id'] = consign.get_dbref()
                args['filter_dict'] = f
                s = {"time": -1}
                args['sort_dict'] = s
                resp_dict = Resp.query_by_page(**args)
                total_record = resp_dict['total_record']
                total_page = resp_dict['total_page']
                pages = resp_dict['pages']
                ids = [x['resume_id'].id for x in resp_dict['data']]
                if len(ids) == 0:
                    resumes = list()
                else:
                    f = {"_id": {"$in": ids}}
                    resumes = DriverResume.find_plus(filter_dict=f, to_dict=True)
                return render_template("web/consign_resp.html", url_path=url_path, resumes=resumes,
                                       total_record=total_record, total_page=total_page, pages=pages,
                                       page_index=page_index)
            else:
                return redirect(url_for("web_blueprint.login_func"))
        else:
            return redirect(url_for("web_blueprint.login_func"))
    else:
        mes = {"message": "success"}
        if isinstance(company_id, ObjectId):
            company = Company.find_by_id(company_id)
            if isinstance(company, Company):
                pass
            else:
                mes['message'] = "authentication fail"
        else:
            mes['message'] = "authentication fail"
        return json.dumps(mes)


def file_func(action, table_name):
    """
    保存/获取文件,
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    company_id = get_platform_session_arg("user_id")
    if isinstance(company_id, ObjectId):
        mes = {"message": "success"}
        """
        tables表名,分别存储不同的类的实例.
        1. base_info                  文件存储基础表,对应mongo_db.BaseFile
        2. head_image                 司机头像类,对应model.driver_module.HeadImage
        3. driving_license_image      驾照类,对应model.driver_module.DrivingLicenseImage
        4. rtqc_image                 运输从也许可证类,对应model.driver_module.RTQCImage
        """
        tables = ['base_file', 'head_image', 'driving_license_image', 'rtqc_image']
        table_name = table_name if table_name in tables else 'base_file'
        if action == "save":
            """保存文件"""
            r = BaseFile.save_flask_file(req=request, collection=table_name)
            if isinstance(r, ObjectId):
                mes['_id'] = str(r)
            else:
                mes['message'] = "保存失败"
        elif action == "get":
            """获取文件"""
            fid = get_arg(request, "fid", "")
            if isinstance(fid, str) and len(fid) == 24:
                fid = ObjectId(fid)
                f = {"_id": fid}
                r = BaseFile.find_one_cls(filter_dict=f, collection=table_name)
                if r is None:
                    return abort(404)
                else:
                    mime_type = "image/jpeg" if r.get('mime_type') is None else r['mime_type']
                    file_name = "1.jpeg" if r.get('file_name') is None else r['file_name']
                    """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
                    file_name = file_name.encode().decode('latin-1')
                    data = r['data']
                    data = BytesIO(initial_bytes=data)
                    resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                                   mimetype=mime_type))
                    return resp
            else:
                mes['message'] = '无效的id'
        else:
            mes['message'] = "不支持的操作"
        return json.dumps(mes)
    else:
        return redirect(url_for("web_blueprint.login_func"))


"""集中注册函数"""


"""注册"""
web_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""登出"""
web_blueprint.add_url_rule(rule="/logout", view_func=logout_func, methods=['get', 'post'])
"""对公司的简历收藏夹的操作"""
web_blueprint.add_url_rule(rule="/favorite/<key>", view_func=resume_favorite_func, methods=['get', 'post'])
"""分页查询司机信息"""
web_blueprint.add_url_rule(rule="/drivers", view_func=driver_page_func, methods=['get', 'post'])
"""公司客户查看司机简历"""
web_blueprint.add_url_rule(rule="/company/resume", view_func=company_resume_func, methods=['get'])
"""保存或者获取文件(mongodb存储)"""
web_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['post', 'get'])
"""随机查询简历"""
web_blueprint.add_url_rule(rule="/random/resume", view_func=random_resume, methods=['post', 'get'])
"""公司客户收藏夹页面"""
web_blueprint.add_url_rule(rule="/favorite", view_func=favorite_func, methods=['post', 'get'])
"""公司客户填写委托招聘的页面"""
web_blueprint.add_url_rule(rule="/add_consign", view_func=add_consign_func, methods=['post', 'get'])
"""公司客户委托招聘列表页面"""
web_blueprint.add_url_rule(rule="/consign_list", view_func=consign_list_func, methods=['get'])
"""分页显示委托招聘的反馈页面信息"""
web_blueprint.add_url_rule(rule="/consign_resp", view_func=resp_page_func, methods=['get', 'post'])