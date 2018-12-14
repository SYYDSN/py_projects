#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import make_response
from flask import abort
from flask import send_file
from tools_module import *
import json
import requests
from hashlib import md5
from uuid import uuid4
from mail_module import send_mail
from tools_module import *
from module.trade_module import process_case
from module.teacher_module import *
import mongo_db
from io import BytesIO
from PIL import Image


BaseFile = mongo_db.BaseFile


"""注册蓝图"""
teacher_blueprint = Blueprint("teacher_blueprint", __name__, url_prefix="/teacher", template_folder="templates/")


"""分析师登录，喊单操作的视图函数"""


def version():
    """生成一个随机的版本号"""
    return uuid4().hex


def login() -> str:
    """teacher login page"""
    method = request.method.lower()
    if method == "get":
        page_title = "大师登录"
        return render_template("t_login.html", page_title=page_title,v=version())
    elif method == "post":
        phone = get_arg(request, "phone", '')
        pw = get_arg(request, "password", '')
        mes = {"message": "success"}
        if phone == "" or pw == "":
            mes['message'] = "必要参数不能为空"
        else:
            f = {"phone": phone}
            p = ['phone', 'name', 'password', "native"]
            t = Teacher.find_one(filter_dict=f, projection=p)
            if t is None:
                mes['message'] = "用户不存在"
            else:
                pw = md5(pw.encode(encoding='utf-8')).hexdigest().lower()
                if pw == t.get("password", "").lower():
                    if t.get("native"):
                        """登录成功"""
                        session['t_id'] = t["_id"]
                    else:
                        mes['message'] = "此账户无法登录"
                else:
                    mes['message'] = "密码错误"
        return json.dumps(mes)
    else:
        return abort(405)


def login_out():
    """注销"""
    session.pop("t_id", None)
    return json.dumps({"message": "success"})


def praise_func():
    """
    战绩图片页面,废止2018-10-10
    :return:
    """
    fid = get_arg(request, "fid", "")
    if fid == "":
        return abort(404)
    else:
        return render_template("praise_page.html", fid=fid)


def quotation_page():
    """报价页面"""
    page_title = "行情"
    return render_template("quotation.html", page_title=page_title, v=version())


def news_func():
    """
    新闻页面/系统信息
    :return:
    """
    page_title = "实时新闻"
    return render_template("news.html", page_title=page_title, v=version())


def log_func():
    """记录老师操作日志"""
    t_id = session.get("t_id", '')
    content = get_arg(request, "args", "")
    url = get_arg(request, "url", "")
    error = get_arg(request, "error", "")
    error_time = get_arg(request, "error_time", "")
    error_time_t = mongo_db.get_datetime_from_str(error_time)
    error_time = error_time_t if isinstance(error_time_t, datetime.datetime) else error_time
    TeacherLog.log(t_id=t_id, url=url, error_time=error_time, error=error, content=content)
    return json.dumps("ok")


def file_func(action: str = "", table_name: str = ""):
    """
    保存/获取文件,此函数仅允许老师上传图片.但允许所有人查看图片.
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    t_id = session.get("t_id", '')
    if isinstance(t_id, str) and len(t_id) == 24:
        teacher = Teacher.find_by_id(o_id=t_id, to_dict=True)
    else:
        teacher = None
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,对应mongo_db.BaseFile
    2. teacher_image                老师相关图片
    """
    tables = ['base_file', 'teacher_image', 'praise_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        if teacher is None:
            mes['message'] = '未登录'
        else:
            owner = teacher.get('_id')
            r = BaseFile.save_flask_file(req=request, collection=table_name, owner=owner)
            if isinstance(r, ObjectId):
                _id = str(r)
                mes['_id'] = _id
                if table_name == "teacher_image":
                    """这是老师更新图片"""
                    t_id = teacher['_id']
                    head_img = "/teacher/file/view/{}?fid={}".format(table_name, _id)
                    f = {"_id": t_id}
                    u = {"$set": {"head_img": head_img}}
                    r = Teacher.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                    if r is None:
                        mes['message'] = '更新老师头像信息失败'
                    else:
                        pass
                else:
                    """后继的处理方式陆续添加"""
                    pass
            else:
                mes['message'] = "保存失败"
    elif action == "view":
        """获取文件/图片"""
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
                img = Image.open(BytesIO(initial_bytes=r['data']))
                """这2个参数暂时用不上"""
                img_width = img.width
                img_height = img.height
                """重设图片大小"""
                size = get_arg(req=request, arg="size", default_value="")  # 参数size用于重设尺寸 size=width*height
                if size != "":
                    temp = size.split("*")
                    if len(temp) > 1 and temp[0].isdigit() and temp[1].isdigit():
                        width = int(temp[0])
                        height = int(temp[1])
                    else:
                        width = 80
                        height = 60
                    img = img.resize(size=(width, height))
                else:
                    pass
                """旋转图片,虽然理论上可以进行任何角度的旋转,但是出于效果,最好只进行90度的整数倍旋转"""
                rotate = get_arg(req=request, arg="rotate", default_value="0")  # 参数rotate用于旋转图片 rotate=90
                if isinstance(rotate, str) and rotate.isdigit():
                    rotate = int(rotate)
                    img = img.rotate(rotate)
                else:
                    pass
                data = BytesIO()
                if img.mode == "RGBA":
                    """
                    png图片是4通道.而JPEG是RGB三个通道，所以PNG转BMP时候程序不知道A通道怎么办,
                    会报 cannot write mode RGBA as JPEG  的错误.
                    解决方法是检查img的mode,进行针对性的处理.
                    文件的后缀名也要做针对性的修改
                    """
                    file_format = "png"
                    file_name = "{}.{}".format(file_name.split(".")[0], file_format)
                else:
                    if img.mode != "GBA":
                        """转换图像格式"""
                        img = img.convert("RGB")
                    else:
                        pass
                    file_format = file_name.split(".")[-1]
                if file_format.lower() == "jpg":
                    file_format = 'jpeg'
                img.save(fp=data, format=file_format)
                data = BytesIO(initial_bytes=data.getvalue())  # initial_bytes的值必须是二进制本身,不能是ByteIO对象.
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


def teacher_chart_func(the_type: str):
    """
    查看老师的各种图标数据, 允许任何人查看
    : params the_type: 图标类型
    :return:
    """
    t_id = get_arg(request, 't_id', "")
    if isinstance(t_id, str) and len(t_id) == 24:
        t_id = ObjectId(t_id)
    else:
        t_id = None
    mes = {"message": "success"}
    if the_type.lower() == 'bar':
        """柱装图数据"""
        data_list = Teacher.win_and_bar(t_id)
        if len(data_list) < 6:
            delta = 6 - len(data_list)
            for i in range(delta):
                data_list.append(dict())
        else:
            data_list = data_list[(len(data_list) - 6):]
        mes['data'] = data_list
    else:
        mes['message'] = "{} 类型未实现".format(the_type)
    return json.dumps(mes)


@check_teacher_session
def process_case_page2(teacher: dict = None):
    """老师操作相关页面"""
    method = request.method.lower()
    if method == "get":

        page_title = "交易管理"
        hold_list = Teacher.get_hold(t_id=teacher['_id'])  # 持仓信息
        """喊单历史"""
        f = dict()
        trade_list = Teacher.trade_history(t_id=teacher['_id'], filter_dict=f)
        return render_template("positions.html", page_title=page_title, teacher=teacher, hold_list=hold_list,
                               v=version(), trade_list=trade_list)
    elif method == "post":
        args = get_args(request)
        mes = {"message": "error"}
        the_type = args.pop("the_type", None)
        now = datetime.datetime.now()
        if the_type == "operate_trade":
            """分析师喊单"""
            t_id = teacher['_id']
            args['teacher_id'] = t_id
            args['teacher_name'] = teacher['name']
            args['version'] = "1.0"
            if teacher['native']:
                """真实老师"""
                args['change'] = "raw"
                args['native'] = True
            else:
                args['change'] = 'follow'
                args['native'] = False
            _id = args.get("_id", "")
            if isinstance(_id, str) and len(_id) == 24:
                """1 这是离场"""
                """1.1 处理离场时间"""
                ets = args.get('exit_time', '')
                et = mongo_db.get_datetime_from_str(ets)
                if isinstance(et, datetime.datetime):
                    args['exit_time'] = et
                else:
                    title = "{}离场时没有传递离场时间".format(now)
                    content = "老师id: {}, trade_id:{}, exit_time:{}".format(t_id, _id, ets)
                    logger.exception(msg=title + content)
                    send_mail(title=title, content=content)
                    args['exit_time'] = now
                """1.2 处理离场价格"""
                exit_price = None
                exit_price_s = args.pop("exit_price", None)
                try:
                    exit_price = float(exit_price_s)
                except Exception as e:
                    print(e)
                finally:
                    if isinstance(exit_price, float):
                        args['exit_price'] = float(exit_price)
                        ses = mongo_db.get_conn(table_name="trade")
                        f = {"_id": ObjectId(_id)}
                        obj = ses.find_one(filter=f)
                        if obj is None:
                            mes["message":] = "订单不存在"
                        else:
                            args['case_type'] = "exit"
                            obj.update(args)
                            args = obj
                            if process_case(doc_dict=args, raw=True):
                                """成功"""
                                mes['message'] = 'success'
                            else:
                                mes = {"message": "操作失败"}
                    else:
                        title = "{}离场时没有传递离场价格".format(now)
                        content = "老师id: {}, trade_id:{},exit_price:{} ".format(t_id, _id, exit_price_s)
                        logger.exception(msg=title + content)
                        send_mail(title=title, content=content)
                        mes = {"message": "缺少离场价格"}
            else:
                """2 这是进场"""
                """2.1 先处理进场时间"""
                enter_time_s = args.get("enter_time", '')
                enter_time = mongo_db.get_datetime_from_str(enter_time_s)
                if isinstance(enter_time, datetime.datetime):
                    args['enter_time'] = enter_time
                else:
                    title = "{}进场时没有传递进场时间".format(now)
                    content = "老师id: {}, trade_id:{}, enter_time:{}".format(t_id, _id, enter_time_s)
                    logger.exception(msg=title + content)
                    send_mail(title=title, content=content)
                    args['enter_time'] = now
                """2.2 处理进场价格"""
                enter_price = None
                enter_price_s = args.pop("enter_price", None)
                try:
                    enter_price = float(enter_price_s)
                except Exception as e:
                    print(e)
                finally:
                    if isinstance(enter_price, float):
                        args['enter_price'] = float(enter_price)
                        args['_id'] = ObjectId()
                        args['case_type'] = "enter"
                        args['each_profit'] = 0.0
                        args['lots'] = 1
                        args['native_direction'] = args['direction']
                        args['record_id'] = args['_id']
                        if process_case(doc_dict=args, raw=True):
                            """成功"""
                            mes['message'] = 'success'
                        else:
                            mes = {"message": "操作失败"}
                    else:
                        title = "{}进场时没有传递进场价格".format(now)
                        content = "老师id: {}, trade_id:{},enter_price:{} ".format(t_id, _id, enter_price_s)
                        logger.exception(msg=title + content)
                        send_mail(title=title, content=content)
                        mes = {"message": "缺少进场价格"}
        elif the_type == "trade_history":
            """历史喊单"""
            p = get_arg(request, "product", "")  # 是否对产品种类进行了筛选?
            if p == "":
                f = dict()
            else:
                f = {"product": p}
            first_exit_time = get_arg(request, "first_exit_time", "")  # 是否对产品离场时间进行过滤?
            if isinstance(first_exit_time, str) and len(first_exit_time) > 12:
                first_exit_time = mongo_db.get_datetime_from_str(first_exit_time)
                if isinstance(first_exit_time, datetime.datetime):
                    f['exit_time'] = {"$lt": first_exit_time}
            data = Teacher.trade_history(t_id=teacher['_id'], filter_dict=f, can_json=True)
            mes['data'] = data
            mes['message'] = 'success'
        elif the_type == "update_person":
            """老师编辑自己的资料"""
            f = {"_id": teacher['_id']}
            old_pw = args.pop("old_password", None)
            if old_pw is None:
                """修改除密码之外的资料"""
                u = {"$set": args}
                r = Teacher.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                if r is None:
                    mes['message'] = "更新个人资料失败"
                else:
                    mes['message'] = 'success'
            else:
                """这是修改密码,需要先验证原始密码是否正确?"""
                if old_pw == teacher['password']:
                    """旧密码正确"""
                    u = {"$set": args}
                    r = Teacher.find_one_and_update(filter_dict=f, update_dict=u, upsert=True)
                    if r is None:
                        mes['message'] = "修改密码失败"
                    else:
                        mes['message'] = 'success'
                        session.pop("t_id", None)  # 清除会话信息
                else:
                    mes['message'] = "旧密码不正确"
        else:
            mes = {"message": "未知的操作:{}".format(the_type)}
        return json.dumps(mes)

    else:
        return abort(405)


"""集中注册函数"""


"""日志接口"""
teacher_blueprint.add_url_rule(rule="/log", view_func=log_func, methods=['get', 'post'])
"""老师登录"""
teacher_blueprint.add_url_rule(rule="/login.html", view_func=login, methods=['get', 'post'])
"""战绩页面"""
teacher_blueprint.add_url_rule(rule="/praise.html", view_func=praise_func, methods=['get', 'post'])
"""老师图片的相关操作"""
teacher_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['get', 'post'])
"""查看老师的图表数据"""
teacher_blueprint.add_url_rule(rule="/chart/<the_type>", view_func=teacher_chart_func, methods=['get', 'post'])
"""老师注销"""
teacher_blueprint.add_url_rule(rule="/login_out", view_func=login_out, methods=['get', 'post'])
"""报价页面"""
teacher_blueprint.add_url_rule(rule="/quotation.html", view_func=quotation_page, methods=['get', 'post'])
"""新闻页面"""
teacher_blueprint.add_url_rule(rule="/news.html", view_func=news_func, methods=['get', 'post'])
"""交易管理"""
teacher_blueprint.add_url_rule(rule="/process_case.html", view_func=process_case_page2, methods=['get', 'post'])


