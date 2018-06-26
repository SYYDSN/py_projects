from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from model.document_tools import list_dir
from model.document_tools import get_project
from model.document_tools import get_md
from model.document_tools import markdown_to_html
import os
import json


app = Flask(__name__)
port = 7000
replace_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@app.route('/')
def index_view():
    page_title = "首页"
    ds = list_dir(replace_path=replace_path)  # 获取所有项目的文档集合
    return render_template("index.html", page_title=page_title, ds=ds)


@app.route('/project')
def project_view():
    project_path = request.args.get("p_path", "")
    if project_path == "":
        return redirect(url_for("index_view"))
    else:
        p_path = os.path.join(replace_path, project_path.strip("/"))
        project = get_project(project_path=p_path, replace_path=replace_path)  # 获取项目的文档集合
        page_title = project.get('name')
        children = project['children'] if project.get("children") else list()
        return render_template("project.html", page_title=page_title, children=children, project_path=project_path)


@app.route('/md', methods=['post', 'get'])
def md_view():
    """md文档视图"""
    if request.method.lower() == "get":
        md_path = request.args.get("m_path", "")
        # md_path = "/truck_driver/document/api.md"
        if md_path == "":
            return redirect(url_for("index_view"))
        else:
            page_title = md_path.split("/")[-1]
            m_path = os.path.join(replace_path, md_path.strip("/"))
            data = get_md(md_path=m_path)  # 获取文档
            html = markdown_to_html(data)
            return render_template("md.html", page_title=page_title, content=html, md_path=md_path)
    else:
        """请求文档数据,给接口准备的,非必须"""
        mes = {"message": "success"}
        md_path = request.form.get("m_path", "")
        if md_path != "":
            m_path = os.path.join(replace_path, md_path.strip("/"))
            data = get_md(md_path=m_path)  # 获取文档
        else:
            data = ""
        mes['data'] = data
        return json.dumps(mes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
