# -*- coding: utf-8 -*-

data = dict()


data['navs'] = [
        {"name": "产品信息", "path": "/manage/product", "class": "fa fa-exclamation-circle", "children": [
            {"name": "基本信息管理", "path": "/manage/product"}
        ]},
        {"name": "设备信息", "path": "/manage/device", "class": "fa fa-cogs", "children": [
            {"name": "设备信息一览", "path": "/manage/device_summary"},
            {"name": "生产线", "path": "/manage/device_line"},
            {"name": "嵌入式", "path": "/manage/device_embed"}
        ]},
        {"name": "条码信息", "path": "/manage/code_tools", "class": "fa fa-qrcode", "children": [
            {"name": "条码信息导入", "path": "/manage/code_import"},
            {"name": "提取打印条码", "path": "/manage/code_export"},
            {"name": "导出查询替换", "path": "/manage/code_pickle"},
        ]},
        {"name": "生产任务", "path": "/manage/task_summary", "class": "fa fa-server", "children": [
            # {"name": "生产任务概况", "path": "/manage/task_summary"},  # 暂时不用
            {"name": "生产任务列表", "path": "/manage/task_manage"},
            {"name": "条码回传记录", "path": "/manage/task_sync"}
        ]},
        {"name": "系统管理", "path": "/manage/user", "class": "fa fa-bar-chart", "children": [
            {"name": "权限组管理", "path": "/manage/role"},
            {"name": "用户管理", "path": "/manage/user"}
        ]}
    ]

"""自定义数据请按照上面的格式添加"""


if __name__ == "__main__":
    pass