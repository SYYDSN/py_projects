PI = FX.API || {}, e.extend(FX.API, {
    sign: {
        get_email: "/auth/email/get",
        get_phone: "/auth/phone/get",
        unbind: "/auth/:value/unbind",
        password_forget: "/password/forget",
        password_reset: "/password/reset",
        register: "/register",
        signin: "/signin"
    },
    profile: {
        acquire_coupon: "/profile/acquire_coupon",
        apply: "/profile/affiliate/apply",
        apply_cash: "/profile/affiliate/apply_cash",
        get_income: "/profile/affiliate/get_income",
        list_apps: "/profile/affiliate/list_apps",
        list_asset: "/profile/affiliate/list_asset",
        list_joined_member: "/profile/affiliate/list_joined_member",
        list_paid_member: "/profile/affiliate/list_paid_member",
        user_verify: "/profile/affiliate/user_verify",
        user_verify_read: "/profile/affiliate/user_verify/read",
        user_verify_update: "/profile/affiliate/user_verify/update",
        create_api_key: "/profile/api_key/create",
        check_gift: "/profile/check_gift",
        corp_verify_check: "/profile/corp_verify/check",
        corp_verify_submit: "/profile/corp_verify/submit",
        coupons: "/profile/coupons",
        me: "/profile/me",
        check_unpaid: "/profile/order/check_unpaid",
        default_receipt: "/profile/order/default_receipt",
        order_list: "/profile/order/list",
        order_pricing: "/profile/order/pricing",
        order_receipt: "/profile/order/receipt",
        order_receipt_list: "/profile/order/receipt/list",
        order_submit: "/profile/order/submit",
        order_cancel: "/profile/order/:orderId/cancel",
        pay_proof_submit: "/profile/order/:orderId/pay_proof/submit",
        order_remove: "/profile/order/:orderId/remove",
        persona: "/profile/persona",
        persona_app_list: "profile/persona/app_list",
        start_trail: "/profile/start_trail",
        update: "/profile/update",
        vip_center: "/profile/vip_center",
        vip_item_usage: "/profile/vip_item_usage"
    },
    sa: {
        audit_apply: "/sa/affiliate/audit_apply",
        audit_cash: "/sa/affiliate/audit_cash",
        block_app: "/sa/affiliate/block_app",
        list: "/sa/affiliate/dingtalk_apply/list",
        update: "/sa/affiliate/dingtalk_apply/update",
        enable_user: "/sa/affiliate/enable_user",
        get_income: "/sa/affiliate/get_income",
        list_apply: "/sa/affiliate/list_apply",
        list_cash: "/sa/affiliate/list_cash",
        list_joined_member: "/sa/affiliate/list_joined_member",
        list_paid_member: "/sa/affiliate/list_paid_member",
        list_public_apps: "/sa/affiliate/list_public_apps",
        list_user: "/sa/affiliate/list_user",
        user_verify_list: "/sa/affiliate/user_verify/list",
        user_verify_update: "/sa/affiliate/user_verify/update",
        corp_verify_list: "/sa/corp_verify/list",
        corp_verify_update: "/sa/corp_verify/update",
        order_list: "/sa/order/list",
        order_update: "/sa/order/update",
        receipt_deny: "/sa/receipt/deny",
        receipt_list: "/sa/receipt/list",
        receipt_send: "/sa/receipt/send"
    },
    dingtalk: {
        secret_install: "/dingtalk/corp/secret/install",
        update: "/dingtalk/corp/ssosecret/update",
        suite_install: "/dingtalk/corp/suite/install",
        login: "/dingtalk/corp/:corpId/login"
    },
    corp_suite: {
        get_cron_sync: "/corp/suite/get_cron_sync",
        set_cron_sync: "/corp/suite/set_cron_sync",
        unbind: "/corp/suite/unbind",
        user_sync: "/corp/suite/user_sync",
        login_check: "/corp/:corpId/suite/login_check"
    },
    file: {
        delete: "/dashboard/app/:appId/filetask/:taskId/delete",
        file_url: "/dashboard/app/:appId/file_url",
        list: "/dashboard/app/:appId/form/:formId/filetask/list",
        mkzip: "/dashboard/app/:appId/form/:formId/filetask/mkzip",
        upload_token: "/dashboard/app/:appId/upload_token",
        get_token: "/upload/get_token"
    },
    app: {
        create: "/dashboard/app/create",
        apps: "/dashboard/apps",
        flow_start: "/dashboard/flow_start",
        flow_todo: "/dashboard/flow_todo",
        flow_todo_count: "/dashboard/flow_todo_count",
        get_config: "/dashboard/get_config",
        sort_app: "/dashboard/sort_app",
        switch_corp: "/dashboard/switch_corp",
        fork: "/dashboard/template/fork",
        install_public: "/dashboard/template/install_public",
        list: "/dashboard/template/list",
        user_corps: "/dashboard/user_corps",
        appId: "/dashboard/app/:appId",
        accept: "/dashboard/app/:appId/accept",
        copy: "/dashboard/app/:appId/copy",
        set_data_auth: "/dashboard/app/:appId/data_auth/set",
        get_entry_auth: "/dashboard/app/:appId/entry_auth/get",
        set_entry_auth: "/dashboard/app/:appId/entry_auth/set",
        get_fields: "/dashboard/app/:appId/fields/get",
        app_get_config: "/dashboard/app/:appId/get_config",
        get_ref: "/dashboard/app/:appId/get_ref",
        get_vip_pack: "/dashboard/app/:appId/get_vip_pack",
        list_aggregate: "/dashboard/app/:appId/list_aggregate",
        get_data_auth: "/dashboard/app/:appId/member/:memberId/data_auth/get",
        publish: "/dashboard/app/:appId/publish",
        publisher: "/dashboard/app/:appId/publisher",
        ref_app_forms: "/dashboard/app/:appId/ref_app_forms",
        ref_apps: "/dashboard/app/:appId/ref_apps",
        refuse: "/dashboard/app/:appId/refuse",
        remove: "/dashboard/app/:appId/remove",
        set_app_public: "/dashboard/app/:appId/set_app_public",
        set_ref: "/dashboard/app/:appId/set_ref",
        update: "/dashboard/app/:appId/update"
    },
    flow: {
        batch_transfer: "/dashboard/app/:appId/workflow/batch_transfer",
        batch_transfer_tasks: "/dashboard/app/:appId/workflow/batch_transfer_tasks",
        distinct: "/dashboard/app/:appId/workflow/distinct",
        get_node_fields: "/dashboard/app/:appId/workflow/get_node_fields",
        query_data: "/dashboard/app/:appId/workflow/query_data",
        query_menu: "/dashboard/app/:appId/workflow/query_menu",
        query_node: "/dashboard/app/:appId/workflow/query_node",
        stash_data_count: "/dashboard/app/:appId/workflow/stash_data_count",
        config_version: "/dashboard/app/:appId/form/:formId/workflow/config_version",
        create: "/dashboard/app/:appId/form/:formId/workflow/create",
        remove: "/dashboard/app/:appId/form/:formId/workflow/remove",
        update: "/dashboard/app/:appId/form/:formId/workflow/update",
        workflows: "/dashboard/app/:appId/form/:formId/workflows"
    },
    auth_group: {
        get_config: "/dashboard/app/:appId/form/:formId/auth_group/:groupId/get_config",
        list: "/dashboard/app/:appId/form/:formId/auth_group/list",
        list_name: "/dashboard/app/:appId/form/:formId/auth_group/list_name",
        pt_update: "/dashboard/app/:appId/form/:formId/auth_group/pt_update",
        remove: "/dashboard/app/:appId/form/:formId/auth_group/remove",
        update: "/dashboard/app/:appId/form/:formId/auth_group/update"
    },
    entry: {
        aggregate_table_edit: "/dashboard/app/:appId/aggregate_table/:entryId/edit",
        aggregate_table_remove: "/dashboard/app/:appId/aggregate_table/:entryId/remove",
        aggregate_table_update: "/dashboard/app/:appId/aggregate_table/:entryId/update",
        create: "/dashboard/app/:appId/entry/create",
        sort: "/dashboard/app/:appId/entry/sort",
        entryId: "/dashboard/app/:appId/entry/:entryId",
        copy: "/dashboard/app/:appId/entry/:entryId/copy",
        get_data_label: "/dashboard/app/:appId/entry/:entryId/get_data_label",
        get_qr_style: "/dashboard/app/:appId/entry/:entryId/get_qr_style",
        remove: "/dashboard/app/:appId/entry/:entryId/remove",
        set_data_label: "/dashboard/app/:appId/entry/:entryId/set_data_label",
        set_qr_style: "/dashboard/app/:appId/entry/:entryId/set_qr_style",
        update: "/dashboard/app/:appId/entry/:entryId/update",
        create_webhook: "/dashboard/app/:appId/entry/:entryId/webhook/create",
        list_webhook: "/dashboard/app/:appId/entry/:entryId/webhook/list",
        remove_webhook: "/dashboard/app/:appId/entry/:entryId/webhook/:webhookId/remove",
        update_webhook: "/dashboard/app/:appId/entry/:entryId/webhook/:webhookId/update",
        test_webhook: "/dashboard/app/:appId/entry/:entryId/webhook/test",
        edit: "/dashboard/app/:appId/form/:formId/edit",
        ext_param_add: "/dashboard/app/:appId/form/:formId/ext_param/add",
        ext_param_remove: "/dashboard/app/:appId/form/:formId/ext_param/remove",
        query_content: "/dashboard/app/:appId/form/:formId/query_content",
        notify_remove: "/dashboard/app/:appId/form/:formId/notify/:notifyId/remove",
        notify_update: "/dashboard/app/:appId/form/:formId/notify/:notifyId/update",
        notify_create: "/dashboard/app/:appId/form/:formId/notify/create",
        notify_list: "/dashboard/app/:appId/form/:formId/notify/list",
        pt_create: "/dashboard/app/:appId/form/:formId/pt/create",
        pt_list: "/dashboard/app/:appId/form/:formId/pt/list",
        pt_get: "/dashboard/app/:appId/form/:formId/pt/:printId/get",
        pt_get_apply_node: "/dashboard/app/:appId/form/:formId/pt/:printId/get_apply_node",
        pt_remove: "/dashboard/app/:appId/form/:formId/pt/:printId/remove",
        pt_set_apply_node: "/dashboard/app/:appId/form/:formId/pt/:printId/set_apply_node",
        pt_update: "/dashboard/app/:appId/form/:formId/pt/:printId/update",
        report_edit: "/dashboard/app/:appId/report/:reportId/edit",
        f: "/f/:formId/password",
        q: "/q/:formId/password",
        r: "/r/:reportId/password"
    },
    data: {
        allow_back_workflows: "/data/allow_back_workflows",
        batch_qr: "/data/batch_qr",
        batch_update: "/data/batch_update",
        batch_update_tasks: "/data/batch_update_tasks",
        chart_group: "/data/chart_group",
        combined_group: "/data/combined_group",
        excel_export: "/data/combined_group/excel_export",
        create: "/data/create",
        distinct: "/data/distinct",
        filter_link: "/data/filter_link",
        find: "/data/find",
        find_excel_export: "/data/find/excel_export",
        hard_remove: "/data/hard_remove",
        link: "/data/link",
        list: "/data/list",
        list_excel_export: "/data/list/excel_export",
        excel_template: "/data/list/excel_template",
        coop_comment_create: "/data/log/coop_comment/create",
        coop_comment_list: "/data/log/coop_comment/list",
        coop_log_list: "/data/log/coop_log/list",
        log_flow: "/data/log_flow",
        current_departments: "/data/member/current_departments",
        departments: "/data/member/departments",
        user_dept_role: "/data/member/dept_role_users",
        users: "/data/member/users",
        roles: "/data/member/roles",
        preview_chart_group: "/data/preview/chart_group",
        preview_combined_group: "/data/preview/combined_group",
        preview_list: "/data/preview/list",
        print: "/data/print",
        read: "/data/read",
        read_link: "/data/read_link",
        recover: "/data/recover",
        remove: "/data/remove",
        update: "/data/update",
        flow_candidates: "/data/flow_candidates",
        flow_change: "/data/flow_change",
        flow_creators: "/data/flow_creators",
        workflows: "/data/workflows"
    },
    formula: {aggregate: "/data/formula/aggregate", map: "/data/formula/map", recno: "/data/formula/recno"},
    manager: {create: "/manager/team/create", delete: "/manager/team/:corpId/delete"},
    excel: {
        create_entry: "/dashboard/app/:appId/excel/create_entry",
        get_sample: "/dashboard/app/:appId/excel/get_sample",
        import: "/dashboard/app/:appId/excel/import",
        check_data: "/dashboard/app/:appId/excel/check_data",
        match_head: "/dashboard/app/:appId/excel/match_head",
        upload: "/dashboard/app/:appId/excel/upload"
    },
    message: {list: "/manager/message/list", set_read: "/manager/message/set_read", unread: "/manager/message/unread"},
    corp: {
        contact_create: "/corp/contact/create",
        contact_list: "/corp/contact/list",
        contact_remove: "/corp/contact/remove",
        contact_update: "/corp/contact/:contactId/update",
        department_edit: "/corp/department/:departmentId/edit",
        department_list_member: "/corp/department/:departmentId/list_member",
        department_remove: "/corp/department/:departmentId/remove",
        department_create: "/corp/department/create",
        department_list: "/corp/department/list",
        get_manager: "/corp/department/manager/get",
        set_manager: "/corp/department/manager/set",
        list_dimission_member: "/corp/list_dimission_member",
        list_member_name: "/corp/list_member_name",
        group_remove: "/corp/manage/group/remove",
        group_update: "/corp/manage/group/update",
        group_list: "/corp/manage/group_list",
        get_config: "/corp/manage/group/:groupId/get_config",
        invite: "/corp/member/invite",
        invite_link_get: "/corp/member/invite_link/get",
        invite_link_set: "/corp/member/invite_link/set",
        invite_list: "/corp/member/invite_list",
        set_dept: "/corp/member/set_dept",
        member_list_department: "/corp/member/:memberId/list_department",
        role_list: "/corp/role/list",
        role_update: "/corp/role/update",
        role_list_member: "/corp/role/:roleId/list_member",
        role_remove: "/corp/role/:roleId/remove",
        set_member: "/corp/role/:roleId/set_member"
    },
    bbs: {
        topics: "/bbs/topics",
        create: "/bbs/topic/create",
        reply_remove: "/bbs/topic/reply/:replyId/remove",
        topicId: "/bbs/topic/:topicId",
        remove: "/bbs/topic/:topicId/remove",
        reply_create: "/bbs/topic/:topicId/reply/create",
        update: "/bbs/topic/:topicId/update"
    }
})
}
(jQuery), function (e) {
    window.FX = window.FX || {};
    var t = {};
    e.shortcut = function (i, a) {
        if (null != t[i]) throw"shortcut:[" + i + "] has been registered";
        t[i] = a, e.extend(a.prototype, {xtype: i})
    }, FX.createWidget = function (i) {
        if (i instanceof e) return new FX.Widget({renderEl: i});
        var a = i.type.toLowerCase(), s = t[a];
        if (!s) throw a + " does not exist";
        return new s(i)
    }, FX.extend = function (t, i, a) {
        "object" == typeof i && (a = i, i = t, t = function () {
            i.apply(this, arguments)
        });
        var s = function () {
        }, n = i.prototype;
        return s.prototype = n, t.prototype = new s, t.superclass = n, e.extend(t.prototype, a), t
    }, FX.STATIC = {
        _st: (new Date).getTime(),
        _ct: (new Date).getTime(),
        zIndex: 8e3,
        Language: "zh",
        num: 0,
        IDBase: new Date - 0,
        CSRF: e('meta[name="csrf-token"]').attr("content"),
        site: window.location.protocol + "//" + window.location.hostname
    }
}(jQuery), function (e) {
    var t = window._jdy_config || {};
    e.extend(FX, {
        CONFIG: {
            HOST: {
                SITE_HOST: t.site,
                SITE_SHORT_HOST: (t.site || "").replace("www.", ""),
                IMAGE_HOST: "https://images.jiandaoyun.com",
                OSS_IMAGE_HOST: "https://oss-image.jiandaoyun.com",
                HELP_DOC_HOST: "https://hc.jiandaoyun.com/doc",
                TRACK_HOST: "https://track.jiandaoyun.com",
                ASSETS_HOST: t.assets_site
            }, COOKIE_DOMAIN: t.cookie_domain
        },
        ValueWidgets: {
            text: 1,
            number: 1,
            textarea: 1,
            datetime: 1,
            checkboxgroup: 1,
            radiogroup: 1,
            combo: 1,
            combocheck: 1,
            address: 1,
            image: 1,
            upload: 1,
            subform: 1,
            user: 1,
            usergroup: 1,
            dept: 1,
            deptgroup: 1,
            location: 1,
            linkdata: 1
        },
        ValueTypeMap: {
            text: "string",
            textarea: "string",
            combo: "string",
            radiogroup: "string",
            user: "id",
            combocheck: "array",
            checkboxgroup: "array",
            usergroup: "idarray",
            number: "number",
            datetime: "datetime",
            address: "address",
            location: "address",
            dept: "did",
            deptgroup: "didarray",
            upload: "upload",
            image: "upload"
        },
        USER_ID: {CurrentUser: "100000000000000000000001"},
        DATA_PREFIX: {Aggregate: "2"},
        WidgetValueOption: {CUSTOM: 0, ASYNC: 1, RELY: 2, FORMULA: 3},
        Keys: {
            ENTER: 13,
            BACKSPACE: 8,
            COMMA: 188,
            DELETE: 46,
            DOWN: 40,
            END: 35,
            ESCAPE: 27,
            HOME: 36,
            LEFT: 37,
            PAGE_DOWN: 34,
            PAGE_UP: 33,
            PERIOD: 190,
            RIGHT: 39,
            SPACE: 32,
            TAB: 9,
            UP: 38
        },
        States: {NORMAL: 0, SUCCESS: 1, ERROR: 2, WARNING: 3},
        EntryAttributes: {creator: 1, createTime: 1, updateTime: 1, ext: 1},
        Time: {excelDayOffset: 25569, millisecondsOfDay: 864e5},
        TimeZone: {defaultOffset: 288e5},
        Events: {RELY: "x-rely"},
        InvisibleSubmitRules: {KEEP: 1, NULL: 2, ALWAYS: 3},
        LimitFields: {
            queryFilter: ["text", "radiogroup", "combo", "number", "datetime", "address", "user"],
            parameter: ["text", "radiogroup", "combo", "number", "datetime", "address", "user", "dept", "subform"],
            filter: ["text", "textarea", "radiogroup", "checkboxgroup", "combo", "combocheck", "number", "datetime", "address", "location", "user", "usergroup", "dept", "deptgroup", "subform", "flowstate", "flownode"],
            list: ["text", "textarea", "combo", "radiogroup", "checkboxgroup", "combocheck", "number", "datetime", "address", "location", "user", "usergroup", "dept", "deptgroup", "image", "upload", "subform", "linkdata"],
            listJoin: ["text", "combo", "radiogroup", "number", "user", "dept"],
            group: ["text", "radiogroup", "combo", "number", "datetime", "address", "string", "subform", "user", "dept", "id", "location", "linkdata"],
            subGroup: ["text", "combo", "number", "datetime", "linkdata"],
            groupJoin: ["text", "combo", "radiogroup", "number", "user", "datetime", "address", "location", "subform", "linkdata", "dept"],
            subGroupJoin: ["text", "combo", "number", "datetime", "linkdata"],
            validate: ["number", "text", "datetime", "radiogroup", "checkboxgroup", "combo", "combocheck", "user", "usergroup", "linkdata", "dept", "deptgroup", "subform"],
            rely: ["combo", "combocheck", "text", "datetime", "number", "subform", "radiogroup", "checkboxgroup", "user", "linkdata", "dept"],
            link: ["combo", "combocheck", "text", "datetime", "number", "radiogroup", "checkboxgroup", "user", "linkdata", "dept", "deptgroup"],
            brief: ["text", "textarea", "combo", "radiogroup", "combocheck", "checkboxgroup", "number", "datetime", "address", "location", "user", "usergroup", "dept", "deptgroup"],
            import: ["text", "textarea", "combo", "radiogroup", "combocheck", "checkboxgroup", "number", "datetime", "address", "subform", "user"],
            combodata: ["combo", "combocheck", "text", "datetime", "number", "radiogroup", "checkboxgroup"],
            linkData: ["text", "textarea", "combo", "radiogroup", "checkboxgroup", "combocheck", "number", "datetime", "address", "location", "user", "usergroup", "subform"],
            linkKey: ["text", "number", "datetime", "radiogroup", "combo"],
            subLinkData: ["text", "combo", "combocheck", "radiogroup", "checkboxgroup", "number", "datetime", "address", "location"],
            aggregate: ["text", "radiogroup", "combo", "string", "subform", "linkdata"],
            batchEdit: ["number", "text", "textarea", "datetime", "radiogroup", "checkboxgroup", "combo", "combocheck", "address", "user", "usergroup", "dept", "deptgroup"],
            fileExport: ["image", "upload"],
            fileExportName: ["text", "number", "radiogroup", "combo", "user"],
            itemLink: ["combo", "radiogroup"],
            printTemplate: ["text", "textarea", "combo", "radiogroup", "checkboxgroup", "combocheck", "number", "datetime", "address", "location", "user", "usergroup", "dept", "deptgroup", "subform", "linkdata", "flow"],
            excelExport: ["text", "textarea", "combo", "radiogroup", "checkboxgroup", "combocheck", "number", "datetime", "address", "location", "user", "usergroup", "dept", "deptgroup", "subform", "linkdata"],
            _sysExcelExport: ["flowState", "chargers"],
            noCache: ["location", "separator", "linkquery"],
            dataLabel: ["text", "number", "datetime", "radiogroup", "checkboxgroup", "combo", "combocheck", "address", "location", "user", "usergroup", "dept", "deptgroup"],
            sort: ["text", "textarea", "number", "radiogroup", "datetime", "combo", "linkdata"]
        },
        Operators: {group: ["+", "-", "*", "/", "."], aggregate: ["+", "-", "."]},
        CONST: {
            MAX_COUNT: 1e5,
            MAX_TODO_COUNT: 999,
            WIDGET_LIST: {
                text: {
                    name: "单行文本",
                    changeList: ["combo", "radiogroup"],
                    subChangeList: ["combo", "radiogroup"]
                },
                radiogroup: {name: "单选按钮组", changeList: ["combo", "text"], subChangeList: ["combo", "text"]},
                combo: {name: "下拉框", changeList: ["radiogroup", "text"], subChangeList: ["text", "radiogroup"]},
                checkboxgroup: {name: "复选框组", changeList: ["combocheck"], subChangeList: ["combocheck"]},
                combocheck: {name: "下拉复选框", changeList: ["checkboxgroup"], subChangeList: ["checkboxgroup"]},
                number: {name: "数字"},
                datetime: {name: "日期时间"},
                address: {name: "地址"},
                textarea: {name: "多行文本"},
                image: {name: "图片"},
                upload: {name: "附件"},
                subform: {name: "子表单"},
                separator: {name: "分割线"},
                user: {name: "成员单选"},
                usergroup: {name: "成员多选"},
                location: {name: "定位"},
                linkdata: {name: "关联数据"},
                linkquery: {name: "关联查询"},
                dept: {name: "部门单选"},
                deptgroup: {name: "部门多选"}
            },
            APP_CATE_NAME: {
                office: "行政办公",
                hr: "人力资源",
                crm: "客户关系",
                inventory: "进销存",
                store: "门店管理",
                production: "生产管理",
                universal_other: "其他",
                logistics: "物流快递",
                restaurant: "餐饮",
                it: "IT互联网",
                housing: "房产物业",
                education: "教育培训",
                medicine: "医疗卫生",
                government: "政府机关",
                vertical_other: "其他"
            },
            APP_CATE: {
                OFFICE: "office",
                HR: "hr",
                CRM: "crm",
                INVENTORY: "inventory",
                STORE: "store",
                PRODUCTION: "production",
                UNIVERSAL_OTHER: "universal_other",
                LOGISTICS: "logistics",
                RESTAURANT: "restaurant",
                IT: "it",
                HOUSING: "housing",
                EDUCATION: "education",
                MEDICINE: "medicine",
                GOVERNMENT: "government",
                VERTICAL_OTHER: "vertical_other"
            },
            FLOW_ACTION_NAME: {
                forward: "提交",
                save: "暂存",
                print: "提交并打印",
                back: "回退",
                transfer: "转交",
                close: "结束流程",
                revoke: "撤回"
            },
            QN_BUCKET: {PUBLIC_IMAGE: "media", PRIVATE_FILE: "file"},
            OSS_BUCKET: {PUBLIC_IMAGE: "oss_image"},
            WORKFLOW: {
                NODE_DELIMITER: "@",
                START_FLOW_ID: 0,
                END_FLOW_ID: -1,
                APPROVAL_ALL: 0,
                APPROVAL_ANY: 1,
                BACKRULE: {DISALLOW: 0, PARENT_NODE: 1, RANGE_NODE: 2},
                FLOWSTATE: {INPROCESS: 0, COMPLETE: 1},
                FLOWTYPE: {NORMAL: "flow", CC: "cc"},
                CREATOR_ID: "100000000000000000000000",
                DEPT_MANAGER_ID: "110000000000000000000000"
            },
            DEPT_ID: {CURRENT: "110000000000000000000001"},
            PARAMETER: {EMPTY: "fx_param_empty"},
            TEXT_TYPE_REGEXP: {
                mobile: "^((\\(\\d{2,3}\\))|(\\d{3}\\-))?1\\d{10}$",
                tel: "^(0[0-9]{2,3}\\-)?([2-9][0-9]{6,7})+(\\-[0-9]{1,4})?$",
                zip: "^\\d{6}$",
                email: "^([a-zA-Z0-9_\\.\\-])+\\@(([a-zA-Z0-9\\-])+\\.)+([a-zA-Z0-9]{2,4})+$",
                ID: "(^\\d{15}$)|(^\\d{18}$)|(^\\d{17}(\\d|X|x)$)"
            },
            VIP_ORDER: {
                PACK: {
                    free: {name: "免费版"},
                    lite: {name: "青春版", service: "basic", data: 2e5},
                    std: {name: "标准版", service: "silver", data: 75e4},
                    user: {name: "按用户数购买", service: "silver", data: 25e3},
                    pro: {name: "专业版", service: "silver", data: 2e6},
                    ent: {name: "企业版", service: "gold", data: 1e7},
                    logo: {name: "去LOGO版"},
                    oem: {name: "定制版"}
                },
                PACK_STATE: {TRAIL: 0, USING: 1, BUFFER: 2, EXPIRED: 3},
                SERVICE: {
                    basic: {name: "基本服务", desc: "赠送"},
                    silver: {name: "银牌服务", desc: "+2500元升级银牌服务（原价3000元）"},
                    gold: {name: "金牌服务", desc: "+6000元升级金牌服务（原价10000元）"}
                },
                DATA_UNIT: 1e4,
                DATA_ADD_UNIT: 1e5,
                FORM_DATA_UNIT: 1e4,
                USER_ADD_UNIT: 5,
                UPLOAD_ADD_UNIT: 1073741824
            },
            ORDER_STATE: {CANCELED: -1, UNPAID: 0, PAID: 1, RECEIPTING: 2, RECEIPTED: 3},
            FIELD: {DELIMITER: "@", ENTRY_DELIMITER: "#"},
            DEFAULT_AUTH_GROUP: 0,
            AUTH_GROUP: {SUBMIT: -1, VIEW_ALL: -2, MANAGE_OWN: -3, MANAGE_ALL: -4},
            AUTH_GROUP_CONTENT: [{groupId: -1, name: "直接提交数据", desc: "在此分组内的成员只可以填报数据，设置了页面共享的成员自动加入此分组"}, {
                groupId: -4,
                name: "管理全部数据",
                desc: "在此分组内的成员可以管理全部数据"
            }, {groupId: -2, name: "查看全部数据", desc: "在此分组内的成员可以查看所有数据"}, {
                groupId: -3,
                name: "管理本人数据",
                desc: "在此分组内的成员可以管理自己填报的数据"
            }],
            FLOW_AUTH_GROUP_CONTENT: [{
                groupId: -1,
                name: "发起流程",
                desc: "在此分组内的成员可以发起流程，设置了表单共享的成员自动加入此分组"
            }, {groupId: -2, name: "查看全部流程", desc: "在此分组内的成员可以查看全部流程"}, {
                groupId: -4,
                name: "管理全部流程",
                desc: "在此分组内的成员可以管理全部流程"
            }],
            APP_STATE: {private: 0, review: 1, onSale: 2},
            K12_APPROVE: {NOTPASS: -1, PASS: 1},
            VIP_MODULE: {
                USERS: "users",
                FORM_DATA: "form_data",
                DATA: "data",
                EXCEL_IMPORT: "excel_import",
                FILE_UPLOAD: "file_upload",
                AGGREGATE: "aggregate",
                PRINT: "print",
                DATA_BACKUP: "data_backup",
                FILE_ZIP: "file_zip",
                LOGO: "logo",
                USER_SYNC: "user_sync",
                APP_BRIDGE: "app_bridge",
                LEVEL: "level"
            },
            VIP_COOKIE: {
                TRAIL: {SUFFIX_KEY: "#tr_time", EXPIRES_DATE: new Date((new Date).getTime() + 1296e6)},
                SYS_DATA: {KEY: "exceed", EXPIRES_DATE: new Date((new Date).getTime() + 864e5), VALUE: !0},
                SERVICE_UPGRADE: {
                    SUFFIX_KEY: "#up_time",
                    EXPIRES_DATE: new Date((new Date).getTime() + 864e5),
                    VALUE: !0
                }
            },
            COOKIE: {
                PHONE: {KEY: "bind_phone", EXPIRES: new Date((new Date).getTime() + 864e5), VALUE: !0},
                UPDATE: {KEY: "update_note", EXPIRES: new Date((new Date).getTime() + 2592e6)},
                GUIDE: {
                    SUFFIX_KEY: "#guide",
                    EXPIRES_DATE: new Date((new Date).getTime() + 864e5),
                    TYPE: {APP_EDIT: 1}
                },
                HELP_ONLINE: {KEY: "help_online", EXPIRES: new Date((new Date).getTime() + 31536e6)},
                USER_GUIDE_BTN: {KEY: "user_guide_btn", EXPIRES: new Date((new Date).getTime() + 31536e6)},
                USER_GUIDE: {KEY: "user_guide", EXPIRES: new Date((new Date).getTime() + 31536e6), VALUE: !0},
                LAST_LOC: {SUFFIX_KEY: "#last_loc", EXPIRES: new Date((new Date).getTime() + 2592e6)},
                WPS_GUIDE: {KEY: "wps_guide", EXPIRES: new Date((new Date).getTime() + 31536e6)},
                DOT_GUIDE: {
                    KEY: "dot_guide",
                    EXPIRES: new Date((new Date).getTime() + 31536e6),
                    VALUE: {
                        FLOW_FILTER_PART: 32,
                        FLOW_FILTER_CREATE: 16,
                        FLOW_FILTER_TODO: 8,
                        DATA_FILTER: 4,
                        APP_SET: 2,
                        DASH_BOARD: 1
                    }
                },
                STEP_GUIDE: {
                    KEY: "step_guide",
                    EXPIRES: new Date((new Date).getTime() + 31536e6),
                    VALUE: {DASHBOARD: 6, MENU: 5, FORM_VISIT: 4, APP_VISIT: 3, FORM_EDIT: 2, APP_EDIT: 1, BEGIN: 0}
                },
                GIFT: {KEY: "gift-coupon", EXPIRES: new Date((new Date).getTime() + 6048e5)},
                ACTIVITY: {KEY: "activity", EXPIRES: new Date((new Date).getTime() + 31536e6), VALUE: "1"},
                PERSONA: {SUFFIX_KEY: "#user_portrait", EXPIRES: new Date((new Date).getTime() + 2592e5), VALUE: !0},
                RECOMMEND: {
                    SUFFIX_KEY: "#recommend_apps",
                    EXPIRES: new Date((new Date).getTime() + 31536e6),
                    VALUE: !0
                },
                INVITE_MEMBER: {
                    SUFFIX_KEY: "#invite_member",
                    EXPIRES: new Date((new Date).getTime() + 2592e6),
                    VALUE: !0
                }
            },
            WPS_TIP: {
                7102: "系统用量超出限制，系统已暂停使用，您可以删除部分数据来恢复系统。",
                7103: "系统用量超出限制，系统已暂停使用，您可以删除部分数据来恢复系统。",
                7104: "聚合表数量已达上限，请删除原先的聚合表后再进行新建。",
                7105: "您所安装的应用内聚合表数量超出WPS云表格限制，请重新选择应用安装。",
                7106: "您的聚合表数量已超出限制。",
                7107: "您本月的附件上传量已超出WPS云表格限制。",
                7108: "您系统内的总数据量已超出WPS云表格限制。",
                7109: "您系统内的单表数据量已超出WPS云表格限制。",
                7110: "您系统内的成员数量已超出WPS云表格限制。",
                7111: "成员数量超出限制，您可以删除部分成员，以邀请更多成员。"
            },
            TRACKER: {
                APP_CREATE: "app_create",
                APP_FORK: "app_fork",
                APP_EDIT: "app_edit",
                APP_CONFIG: "app_config",
                APP_REF: "app_ref",
                APP_VISIT: "app_visit",
                APP_RENAME: "app_rename",
                AUTH_GROUPS: "auth_groups",
                AGGREGATE_TABLE_CREATE: "aggregate_table_create",
                AGGREGATE_TABLE_EDIT: "aggregate_table_edit",
                FORM_CREATE: "form_create",
                FORM_EDIT: "form_edit",
                REPORT_CREATE: "report_create",
                REPORT_EDIT: "report_edit",
                REPORT_RENAME: "report_rename",
                REPORT_SHARE: "report_share",
                REPORT_REF: "report_ref",
                ORDER_LIST: "order_list",
                VIP_CENTER: "vip_center",
                WORKFLOW: "workflow",
                MENU_PACK: "menu_pack",
                VIP_CENTER_PACK: "vip_center_pack",
                MEMBER_LIST: "member_list",
                MEMBER_ADD: "member_add",
                HELP_DOC: "help_doc",
                HELP_VIDEO: "help_video",
                HELP_CUSTOM: "help_custom",
                TEMP_SEARCH: "temp_search",
                APP_VIEW: "app_view",
                PRINT_CREATE: "print_create",
                FORM_SHARE: "form_share",
                FORM_RENAME: "form_rename",
                FLOW_FORM_CREATE: "flow_form_create",
                AUTH_GROUP_CREATE: "auth_group_create",
                APP_INSTALL: "app_install",
                FORM_SETTING: "form_setting",
                FORM_REF: "form_ref",
                TRAIL_DASHBOARD: "trail_dashboard",
                TRAIL_VIP_CENTER: "trail_vip_center",
                FORM_FIELD_ADD: "form_field_add",
                FORM_FIELD_RENAME: "form_field_rename",
                FORM_CREATE_FROM_EXCEL: "form_create_from_excel",
                FLOW_FORM_CREATE_FORM_EXCEL: "flow_form_create_from_excel",
                DASHBOARD_FLOW_LAUNCH: "dashboard_flow_launch",
                DATA_SOURCE_PICK: "data_source_pick",
                ENTRY_SHARE_TO_MEMBER: "entry_share_to_member",
                USER_PORTRAIT_COLLECT: "user_portrait_collect",
                USER_PORTRAIT_FINISH: "user_portrait_finish",
                FILE_PREVIEW: "file_preview"
            },
            KEY_CODE: {LEFT: 37, RIGHT: 39},
            ALLIANCE_APPLY_STATE: {
                APPROVED: "approved",
                WAITING: "waiting",
                DENIED: "denied",
                NOT_APPLIED: "not_applied",
                BANNED: "banned"
            },
            CONTACT_DEF_GROUP: "1",
            DEPARTMENT_ROOT: 1,
            MANAGE_GROUP: {SYS: {ID: -1, NAME: "系统管理组"}},
            LOCAL_STORAGE: {APP_INSTALL_GUIDE: "app_install_guide"},
            WEBHOOK: {
                API_TRIGGER: {CREATE: "data_create", UPDATE: "data_update", REMOVE: "data_remove"},
                SERVER_TYPE: {FR: "fr", CUSTOM: "custom"}
            },
            PRINT_DPI: 96,
            UPLOAD_FILE_COUNT: {SINGLE: 1, MULTI: 10},
            SEP_LINE_STYLE: {NONE: "none", DASHED: "dashed", THIN: "thin", THICK: "thick"},
            FILTER_METHOD: {
                EQ: "eq",
                NE: "ne",
                ALL: "all",
                IN: "in",
                NIN: "nin",
                LK: "like",
                ULK: "unlike",
                EP: "empty",
                NEP: "not_empty",
                GT: "gt",
                GTE: "gte",
                LT: "lt",
                LTE: "lte",
                RG: "range"
            },
            FILTER_RELATION: {AND: "and", OR: "or"},
            DATA_LIMIT_TIP: {LINK: "该账号的本月数据流量已用完，无法提交新数据，请联系链接发布者升级套餐", ACCOUNT: "该账号的本月数据流量已用完，无法提交新数据，请联系账号创建者升级套餐"}
        },
        MEI_QIA: {
            VIP: "https://static.meiqia.com/dist/standalone.html?_=t&eid=89905&groupid=ccd49a5cfe1ac9576135a9f0bd0a9414&fallback=1",
            FREE: "https://static.meiqia.com/dist/standalone.html?_=t&eid=89905&groupid=24eb490c50ca74c3e276a6cdb8ac4787&fallback=1"
        }
    })
}(jQuery), $.extend(FX, {
    PROPERTIES: {
        zh: {
            Sunday: "星期日",
            Monday: "星期一",
            Tuesday: "星期二",
            Wednesday: "星期三",
            Thursday: "星期四",
            Friday: "星期五",
            Saturday: "星期六",
            "Short-Sun": "日",
            "Short-Mon": "一",
            "Short-Tue": "二",
            "Short-Wed": "三",
            "Short-Thu": "四",
            "Short-Fri": "五",
            "Short-Sat": "六",
            January: "一月",
            February: "二月",
            March: "三月",
            April: "四月",
            May: "五月",
            June: "六月",
            July: "七月",
            August: "八月",
            September: "九月",
            October: "十月",
            November: "十一月",
            December: "十二月",
            "Short-Jan": "一",
            "Short-Feb": "二",
            "Short-Mar": "三",
            "Short-Apr": "四",
            "Short-May": "五",
            "Short-Jun": "六",
            "Short-Jul": "七",
            "Short-Aug": "八",
            "Short-Sep": "九",
            "Short-Oct": "十",
            "Short-Nov": "十一",
            "Short-Dec": "十二"
        },
        en: {
            Sunday: "Sunday",
            Monday: "Monday",
            Tuesday: "Tuesday",
            Wednesday: "Wednesday",
            Thursday: "Thursday",
            Friday: "Friday",
            Saturday: "Saturday",
            "Short-Sun": "Sun",
            "Short-Mon": "Mon",
            "Short-Tue": "Tue",
            "Short-Wed": "Wed",
            "Short-Thu": "Thu",
            "Short-Fri": "Fri",
            "Short-Sat": "Sat",
            January: "January",
            February: "February",
            March: "March",
            April: "April",
            May: "May",
            June: "June",
            July: "July",
            August: "August",
            September: "September",
            October: "October",
            November: "November",
            December: "December",
            "Short-Jan": "Jan",
            "Short-Feb": "Feb",
            "Short-Mar": "Mar",
            "Short-Apr": "Apr",
            "Short-May": "May",
            "Short-Jun": "Jun",
            "Short-Jul": "Jul",
            "Short-Aug": "Aug",
            "Short-Sep": "Sep",
            "Short-Oct": "Oct",
            "Short-Nov": "Nov",
            "Short-Dec": "Dec"
        },
        ja: {}
    }, i18nText: function (e) {
        return FX.PROPERTIES[FX.STATIC.Language][e]
    }
}), function (e) {
    FX.Utils = FX.Utils || {}, e.extend(FX.Utils, {
        isString: function (e) {
            return "string" == typeof e
        }, isNumber: function (t) {
            return e.isNumeric(t)
        }, isFunction: function (t) {
            return e.isFunction(t)
        }, isDate: function (e) {
            return e instanceof Date
        }, isArray: function (t) {
            return e.isArray(t)
        }, isEmpty: function (e) {
            return "" === e || FX.Utils.isNull(e)
        }, isBlank: function (e) {
            return FX.Utils.isNull(e) || "" === e.trim()
        }, isNull: function (e) {
            return null == e
        }, isObjectEmpty: function (e) {
            if (null == e) return !0;
            if (e.length > 0) return !1;
            if (0 === e.length) return !0;
            for (var t in e) if (hasOwnProperty.call(e, t)) return !1;
            return isNaN(e)
        }, isValueWidget: function (e) {
            return !!FX.ValueWidgets[e]
        }, pick: function (e, t) {
            var i = {};
            return FX.Utils.forEach(t, function (t, a) {
                a in e && (i[a] = e[a])
            }), i
        }, applyFunc: function (e, t, i, a) {
            return FX.Utils.isFunction(t) ? t.apply(e, i || []) : a
        }, forEach: function (e, t) {
            if (Array.isArray(e) || e instanceof jQuery) for (var i = 0, a = e.length; i < a && !1 !== t.apply(e[i], [i, e[i]]); i++) ; else if (e && "object" == typeof e) for (var s in e) if (e.hasOwnProperty(s) && !1 === t.apply(e[s], [s, e[s]])) break
        }, flatten: function (e, t, i) {
            if (i || (i = []), e) for (var a = 0, s = e.length; a < s; a++) {
                var n = e[a];
                Array.isArray(n) ? FX.Utils.flatten(n, t, i) : t && !t(n) || i.push(n)
            }
            return i
        }, applyCss: function (e, t) {
            FX.Utils.isEmpty(t) || (FX.Utils.isString(t) ? e.addClass(t) : e.css(t))
        }, getServerDate: function (e) {
            if (e && e.getResponseHeader) {
                var t = e.getResponseHeader("date");
                t && (FX.STATIC._st = new Date(t).getTime(), FX.STATIC._ct = (new Date).getTime())
            }
        }, getApi: function (e) {
            if (!FX.Utils.isString(e)) return "";
            var t = arguments;
            if (t.length <= 1) return e;
            var i = /\/:[a-z]+/gi, a = 1;
            return e.replace(i, function () {
                return "/" + t[a++]
            })
        }, ajax: function (t, i, a, s) {
            return e.ajax({
                type: "POST",
                beforeSend: function (e) {
                    e.setRequestHeader("X-CSRF-Token", FX.STATIC.CSRF), e.setRequestHeader("X-JDY-Ver", FX.STATIC._ver)
                },
                url: t.url,
                async: !1 !== t.async,
                data: JSON.stringify(t.data),
                contentType: "application/json;charset=UTF-8",
                timeout: t.timeout
            }).done(function (e, t, a) {
                FX.Utils.getServerDate(a), i && i(e, t), s && s(e, t)
            }).fail(function (e, t, i) {
                switch (e.status) {
                    case 400:
                        if (!1 === FX.Utils.applyFunc(this, a, [e, t], !1)) {
                            var n = e.responseJSON || {};
                            n.msg ? FX.Msg.toast({type: "warning", msg: n.msg}) : FX.Msg.toast({
                                type: "error",
                                msg: "错误的请求"
                            })
                        }
                        break;
                    case 401:
                        FX.Msg.toast({type: "warning", msg: "用户未登录"});
                        break;
                    case 402:
                        FX.Msg.toast({type: "warning", msg: "当前会话已过期"});
                        break;
                    case 403:
                        FX.Msg.toast({type: "warning", msg: "没有数据请求权限"});
                        break;
                    case 404:
                        FX.Msg.toast({type: "warning", msg: "找不到数据资源"});
                        break;
                    case 0:
                        break;
                    default:
                        FX.Msg.toast({type: "warning", msg: "与服务器通信失败"}), console && console.log("通信失败")
                }
                s && s(e, t)
            })
        }, ajaxUpload: function (t, i, a, s) {
            e.ajax({
                type: "POST",
                url: t.url,
                data: t.data,
                cache: !1,
                contentType: !1,
                processData: !1,
                beforeSend: function (e) {
                    e.setRequestHeader("X-CSRF-Token", FX.STATIC.CSRF)
                },
                xhr: function () {
                    var i = e.ajaxSettings.xhr();
                    return i.upload && t.onUpload && i.upload.addEventListener("progress", function (e) {
                        e.lengthComputable ? t.onUpload(e.loaded, e.total) : t.onUpload(3, 10)
                    }, !1), i
                }
            }).done(function () {
                i && i.apply(this, arguments), s && s.apply(this, arguments)
            }).fail(function () {
                a && a.apply(this, arguments), s && s.apply(this, arguments)
            })
        }, dataAjax: function (e, t, i, a) {
            e.data = e.data || {};
            var s = e.data;
            return FX.Utils.isEmpty(FX.STATIC.APPID) || (s.appId = FX.STATIC.APPID), FX.Utils.isEmpty(FX.STATIC.ENTRYID) || (s.entryId = FX.STATIC.ENTRYID), FX.Utils.isEmpty(FX.STATIC.DATAID) || (s.dataId = FX.STATIC.DATAID), FX.STATIC.BACKUP && (s.isBackup = !0), FX.Utils.isEmpty(FX.STATIC.FTOKEN) ? FX.Utils.isEmpty(FX.STATIC.QTOKEN) ? FX.Utils.isEmpty(FX.STATIC.RTOKEN) ? FX.Utils.isEmpty(FX.STATIC.ATOKEN) ? FX.Utils.isEmpty(FX.STATIC.DTOKEN) || (s.fx_access_token = FX.STATIC.DTOKEN, s.fx_access_type = "form_data") : (s.fx_access_token = FX.STATIC.ATOKEN, s.fx_access_type = "app_public") : (s.fx_access_token = FX.STATIC.RTOKEN, s.fx_access_type = "report_public") : (s.fx_access_token = FX.STATIC.QTOKEN, s.fx_access_type = "form_query") : (s.fx_access_token = FX.STATIC.FTOKEN, s.fx_access_type = "form_public"), FX.Utils.ajax(e, function (e, i) {
                t(e, i)
            }, i, a)
        }, getUrlParameter: function (e) {
            for (var t = window.location.search.substring(1).split("&"), i = 0; i < t.length; i++) {
                var a = t[i].split("=");
                if (a[0] == e) return a[1]
            }
            return null
        }, escapeRegexp: function (e) {
            if ("string" != typeof e) return "";
            var t = /[|\\{}()[\]^$+*?.]/g;
            return e.replace(t, "\\$&")
        }, validateEmail: function (e) {
            return new RegExp(FX.CONST.TEXT_TYPE_REGEXP.email).test(e)
        }, validateMobile: function (e) {
            return new RegExp(FX.CONST.TEXT_TYPE_REGEXP.mobile).test(e)
        }, redirectTo: function (e) {
            window.location.href = e
        }, isCanvasSupported: function () {
            var e = document.createElement("canvas");
            return !(!e.getContext || !e.getContext("2d"))
        }, isFormDataSupported: function () {
            return void 0 !== window.FormData
        }, getFileDownloadURL: function (e, t, i) {
            switch (e.bucket) {
                case FX.CONST.QN_BUCKET.PUBLIC_IMAGE:
                    var a = "?attname=" + encodeURIComponent(e.name), s = e.thumb;
                    return s && (a += "&imageView2/" + s.mode + "/w/" + s.width + "/h/" + s.height), t(FX.CONFIG.HOST.IMAGE_HOST + "/" + e.qnKey + a);
                case FX.CONST.OSS_BUCKET.PUBLIC_IMAGE:
                    return t(FX.CONFIG.HOST.OSS_IMAGE_HOST + "/" + e.ossKey);
                case FX.CONST.QN_BUCKET.PRIVATE_FILE:
                default:
                    if (!FX.STATIC.APPID) return i();
                    FX.Utils.dataAjax({
                        url: FX.Utils.getApi(FX.API.file.file_url, FX.STATIC.APPID),
                        data: e
                    }, function (e) {
                        t(e.url)
                    }, function (e) {
                        !1 === FX.Utils.applyFunc(this, i, [e], !1) && FX.Msg.toast({type: "warning", msg: "文件获取失败"})
                    })
            }
        }, evalFormula: function (e) {
            var t = [];
            FX.STATIC.FormulaEnv || (FX.Utils.forEach(Object.keys(FX.Formula), function (e, i) {
                t.push("var " + i + "=FX.Formula." + i)
            }), FX.STATIC.FormulaEnv = t.join(";") + ";");
            var i;
            try {
                i = new Function(FX.STATIC.FormulaEnv + "return " + e)()
            } catch (e) {
                i = null
            }
            return i
        }, createEntryAttributeField: function (t, i, a) {
            if (a && a.indexOf(t) > -1) return null;
            var s = {id: i.entryId};
            switch (t) {
                case"label":
                    e.extend(s, {name: "label", type: "text", text: "标题"});
                    break;
                case"ext":
                    e.extend(s, {name: "ext", type: "text", text: "扩展字段", items: i.extParams});
                    break;
                case"createTime":
                    e.extend(s, {name: "createTime", type: "datetime", format: "yyyy-MM-dd HH:mm:ss", text: "提交时间"});
                    break;
                case"updateTime":
                    e.extend(s, {name: "updateTime", type: "datetime", format: "yyyy-MM-dd HH:mm:ss", text: "更新时间"});
                    break;
                case"creator":
                    e.extend(s, {name: "creator", type: "user", text: "提交人"});
                    break;
                case"flowState":
                    e.extend(s, {name: "flowState", type: "flowState", text: "流程状态"});
                    break;
                case"chargers":
                    e.extend(s, {name: "chargers", type: "chargers", text: "当前节点/负责人"});
                    break;
                case"deleter":
                    e.extend(s, {name: "deleter", type: "user", text: "删除人"});
                    break;
                case"deleteTime":
                    e.extend(s, {name: "deleteTime", type: "datetime", format: "yyyy-MM-dd HH:mm:ss", text: "删除时间"});
                    break;
                default:
                    return null
            }
            return s
        }, createWidgetName: function () {
            return "_widget_" + FX.STATIC.IDBase++
        }, formatFileSize: function (e) {
            return FX.Utils.isNumber(e) ? e >= 1e9 ? (e / 1e9).toFixed(2) + " GB" : e >= 1e6 ? (e / 1e6).toFixed(2) + " MB" : (e / 1e3).toFixed(2) + " KB" : "未知"
        }, formatData: function (e, t) {
            if (!e) return t;
            var i = e.cellFmt && e.cellFmt.data || e.format;
            switch (e.type) {
                case"datetime":
                    (i = i || "yyyy-MM-dd") && t && (t = FX.Utils.date2Str(new Date(t), i));
                    break;
                case"address":
                    i = i || "pcda", t = FX.Utils.address2Str(t, "", i);
                    break;
                case"location":
                    i = i || "pcda";
                    var a = "";
                    e.lnglatVisible && t && t.lnglatXY && (a = "经度：" + FX.Utils.fixDecimalPrecision(t.lnglatXY[0], 6) + "，纬度：" + FX.Utils.fixDecimalPrecision(t.lnglatXY[1], 6)), t = {
                        address: FX.Utils.address2Str(t, "", i),
                        lngLat: a
                    };
                    break;
                case"number":
                case"formula":
                    i = i || "", t = FX.Utils.num2Str(t, i);
                    break;
                case"text":
                    t = t || "", "creator" !== e.name || FX.Utils.isString(t) || (t = t ? t.name : "");
                    break;
                default:
                    t = FX.Utils.isNull(t) ? "" : t
            }
            return t
        }, chunkArray: function (e, t) {
            var i = [];
            if (!t || !e.length) return i;
            for (var a = 0, s = e.length; a < s; a += t) {
                var n = e.slice(a, a + t);
                i.push(n)
            }
            return i
        }, UUID: function (e) {
            return e ? (e ^ 16 * Math.random() >> e / 4).toString(16) : ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, this.UUID)
        }, GCD: function (e, t) {
            return t ? this.GCD(t, e % t) : e
        }, LCM: function (e, t) {
            return e * t / this.GCD(e, t)
        }, str2num: function (e) {
            if (FX.Utils.isEmpty(e)) return null;
            var t = parseFloat(e);
            return isNaN(t) ? null : t
        }, fixDecimalPrecision: function (e, t) {
            var i = "";
            if (t || (t = 8), !this.isEmpty(e)) {
                var a = parseFloat(e);
                if (!isNaN(a)) {
                    var s = (a + "").split(".")[1];
                    i = s && s.length > t ? parseFloat(a.toFixed(t)) : a, t > 6 && Math.abs(i) < 1 && /e-/.test(i + "") && (i = parseFloat(a.toFixed(6)))
                }
            }
            return i
        }, getSelectionText: function () {
            return window.getSelection ? window.getSelection().toString() : document.selection && document.selection.createRange ? document.selection.createRange().text : ""
        }, getCorpType: function (e) {
            return e ? (e = e.toLowerCase(), /^ding/.test(e) ? "dingtalk" : /^w/.test(e) ? "wechat" : "internal") : null
        }, isCorpSuiteAdmin: function (e) {
            var t = FX.Utils.getCorpType(e);
            return t && ("dingtalk" === t || "wechat" === t)
        }, parseDate: function (e) {
            return isNaN(e) ? null : new Date(e)
        }, getWeekStartDate: function (e) {
            var t = e.getDay();
            return 0 === t && (t = 7), new Date(e.getFullYear(), e.getMonth(), e.getDate() - (t - 1))
        }, getWeekEndDate: function (e) {
            var t = e.getDay();
            return 0 === t && (t = 7), new Date(e.getFullYear(), e.getMonth(), e.getDate() + (7 - t))
        }, getMonthStartDate: function (e) {
            return new Date(e.getFullYear(), e.getMonth(), 1)
        }, getMonthEndDate: function (e) {
            return new Date(e.getFullYear(), e.getMonth() + 1, 0)
        }, setPageTitle: function (e) {
            FX.Utils.isEmpty(e) || (document.title = e)
        }, createMask: function (t, i) {
            var a = e('<div class="x-window-mask"/>'), s = i || {};
            if (s.isModal && a.addClass("modal"), s.isLight ? a.addClass("light") : s.isDark && a.addClass("dark"), s.hasLoader) {
                var n = !s.isDark;
                this.createLoadIcon(a, n)
            }
            return t && a.css({"z-index": FX.STATIC.zIndex++}).appendTo(t), a
        }, createLoadIcon: function (t, i) {
            var a = e('<div class="x-loader-icon"/>').appendTo(t);
            return i && a.addClass("colorful"), e("<div/>").appendTo(a), a
        }, createQrcodeBtn: function (t, i) {
            i = i || "icon-qrcode";
            var a = e("<a/>").attr("title", "二维码").append(e("<i/>").addClass(i)).on("click", function () {
                var i = e('<div class="qrcode-dropdown"/>');
                e("<img/>").attr("src", "/qrcode?u=" + encodeURIComponent(t)).appendTo(i), e("<div/>").text("扫描二维码，分享给好友").appendTo(i), FX.Msg.bubble({
                    anchor: a,
                    text4Ok: null,
                    minWidth: 150,
                    text4Cancel: null,
                    contentHTML: i,
                    edge: 200
                })
            });
            return a
        }, doPrint: function (t, i) {
            e("body").children("div").addClass("x-ui-notprint");
            var a = e("#x-printer").removeClass().empty();
            0 === a.length && (a = e('<div id="x-printer"/>').appendTo("body")), t && a.append(t), i = FX.Utils.isNull(i) ? 0 : i, setTimeout(function () {
                window.print()
            }, i)
        }, cancelPrint: function () {
            e("body").children(".x-ui-notprint").removeClass("x-ui-notprint"), e("#x-printer").remove()
        }, parseMm2Pt: function (e) {
            return parseFloat((e / 25.4 * FX.CONST.PRINT_DPI).toFixed(6))
        }, parsePt2Mm: function (e) {
            return parseFloat((e / FX.CONST.PRINT_DPI * 25.4).toFixed(6))
        }, copyToClipboard: function (e, t) {
            if (e && e.length) {
                var i = document.createElement("textarea");
                i.style.background = "transparent", i.style.color = "transparent", i.value = e, document.body.appendChild(i), i.select();
                var a;
                try {
                    a = document.execCommand("copy")
                } catch (e) {
                    a = !1
                }
                document.body.removeChild(i), a && FX.Utils.applyFunc(this, t, [], !1)
            }
        }, getFlowOption: function (e, t) {
            var i = {btn: {}}, a = i.btn;
            switch (e.hasPrint && (a.print = {text: "打印"}), t) {
                case"stash":
                case"todo":
                    e.isEditable && e.currentFlowId !== FX.CONST.WORKFLOW.END_FLOW_ID && (a.forward = {text: FX.Utils.getFlowActionText("forward", e)}, e.allowSave && (a.save = {text: FX.Utils.getFlowActionText("save", e)}), e.allowBack && (a.back = {text: FX.Utils.getFlowActionText("back", e)}), e.allowClose && (a.close = {text: FX.Utils.getFlowActionText("close", e)}), e.hasPrint && (a.print = {text: FX.Utils.getFlowActionText("print", e)}), e.allowTransfer && (a.transfer = {text: FX.Utils.getFlowActionText("transfer", e)}), i.comment = e.comment, i.isEditable = !0);
                    break;
                case"create":
                    e.allowRevoke && (a.revoke = {text: FX.Utils.getFlowActionText("revoke")})
            }
            i.flowState = e.data.flowState, i.version = e.data.flowVer, i.hasLogView = e.hasLogView, i.chargers = e.data.chargers, i.transactors = e.data.transactors, i.dataId = e.data._id, i.ccUsers = e.data.ccUsers, i.flowStack = e.data.flowStack;
            var s = [];
            return FX.Utils.isArray(e.flowNodes) && e.flowNodes.length > 0 && (s = e.flowNodes.filter(function (e) {
                return "todo" === t ? "charger" === e.type : "part" === t ? "transactor" === e.type : void 0
            })), i.flowId = e.currentFlowId, i.printId = e.printId, i.flowNodes = s, i.backNodes = e.backNodes, i
        }, getFlowActionText: function (e, t) {
            t = t || {};
            var i = "", a = FX.CONST.FLOW_ACTION_NAME[e];
            switch (e) {
                case"forward":
                    i = t.submit_text || a;
                    break;
                case"save":
                    i = t.save_text || a;
                    break;
                case"print":
                    i = t.print_text || a;
                    break;
                case"back":
                    i = t.back_text || a;
                    break;
                case"transfer":
                    i = t.transfer_text || a;
                    break;
                case"close":
                    i = t.close_text || a;
                    break;
                default:
                    i = a
            }
            return i
        }, getCurrentCorp: function () {
            return FX.STATIC.currentCorpId || FX.STATIC.corpId
        }, isCorpCreator: function () {
            var e = FX.Utils.getCurrentCorp(), t = FX.STATIC.user ? FX.STATIC.user.corpId : "";
            return !(!e || !t) && e === t
        }, getTeamManageText: function () {
            return "通讯录"
        }, getColorNumber: function (e) {
            return FX.Utils.isEmpty(e) ? 1 : parseInt(e.toString().substring(0, 8), 16) % 6 + 1
        }, getShowFieldItems: function (e, t, i) {
            var a = [], s = {};
            return FX.Utils.forEach(e, function (e, t) {
                "subform" === t.type ? FX.Utils.forEach(t.items, function (e, i) {
                    s[[t.name, i.name].join(".")] = !0
                }) : s[t.name] = !0
            }), FX.Utils.forEach(t, function (e, t) {
                if (!(i && i.indexOf(t.type) < 0)) {
                    var n = {text: t.text, value: t.name};
                    n.selected = s[n.value], "subform" === t.type ? FX.Utils.forEach(t.items, function (e, n) {
                        if (!(i && i.indexOf(n.type) < 0)) {
                            var o = {value: [t.name, n.name].join("."), text: [t.text, n.text].join(".")};
                            o.selected = s[o.value], a.push(o)
                        }
                    }) : a.push(n)
                }
            }), a
        }, getFieldAttr: function (t, i) {
            if (!FX.Utils.isValueWidget(t.widget.type)) return null;
            if (i && i.indexOf(t.widget.type) < 0) return null;
            var a = {id: t.formId, text: t.label, name: t.widget.widgetName, type: t.widget.type};
            switch (t.widget.type) {
                case"subform":
                    var s = [];
                    FX.Utils.forEach(t.widget.items, function (a, n) {
                        e.extend(n, {formId: t.formId});
                        var o = FX.Utils.getFieldAttr(n, i);
                        o && (e.extend(o, {subform: t.widget.widgetName}), s.push(o))
                    }), e.extend(a, {items: s});
                    break;
                case"linkdata":
                    e.extend(a, {
                        linkForm: t.widget.linkForm,
                        linkFields: t.widget.linkFields,
                        linkType: t.widget.linkType,
                        linkKey: t.widget.linkKey,
                        refAppId: t.widget.refAppId
                    });
                    break;
                case"combo":
                case"combocheck":
                case"radiogroup":
                case"checkboxgroup":
                    e.extend(a, {async: t.widget.async, items: t.widget.items});
                    break;
                case"datetime":
                    e.extend(a, {format: t.widget.format});
                    break;
                case"address":
                    e.extend(a, {needDetail: t.widget.needDetail});
                    break;
                case"location":
                    e.extend(a, {lnglatVisible: t.widget.lnglatVisible})
            }
            return a
        }, leftPad: function (e, t, i) {
            var a = String(e);
            for (i || (i = " "); a.length < t;) a = i + a;
            return a.toString()
        }, startWith: function (e, t) {
            var i = e.length;
            return !(null == t || "" == t || 0 === i || t.length > i) && e.substr(0, t.length) == t
        }, getFieldInfoByFormula: function (e) {
            var t = {}, i = (e + "").match(/(\$[0-9a-zA-Z\._]+)(#[0-9a-f]+)?(@[0-9a-f]+)?/),
                a = ["", "field", "entryId", "appId"];
            return FX.Utils.forEach(i, function (e, i) {
                0 !== e && i && (t[a[e]] = i.substr(1))
            }), t
        }, getFieldInfoById: function (e) {
            var t = {}, i = (e = "#" + e).match(/(#[0-9a-f]+)(@[0-9a-f]+)?/), a = ["", "entryId", "appId"];
            return FX.Utils.forEach(i, function (e, i) {
                0 !== e && i && (t[a[e]] = i.substr(1))
            }), t
        }, fieldAuthValue2Json: function (e) {
            return {
                visible: !!(1 & e),
                enable: !!(2 & e),
                brief: !!(4 & e),
                subform_create: !!(16 & e),
                subform_edit: !!(32 & e),
                subform_delete: !!(64 & e)
            }
        }, fieldAuthJson2Value: function (e) {
            return (+e.visible << 0) + (+e.enable << 1) + (+e.brief << 2) + (+e.subform_create << 4) + (+e.subform_edit << 5) + (+e.subform_delete << 6)
        }, isFieldAuthVisible: function (e) {
            return 1 & e
        }, getSubformRowIdx: function (t) {
            return e(t.element).closest(".subform-row").data("row-idx")
        }, getSubformWidgetWidth: function (e) {
            var t = 150;
            switch (e.type) {
                case"datetime":
                    t = 180;
                    break;
                case"combo":
                case"combocheck":
                case"checkboxgroup":
                case"user":
                case"usergroup":
                case"dept":
                case"deptgroup":
                    t = 200;
                    break;
                case"address":
                case"textarea":
                    t = 250
            }
            return t
        }, setLayoutSize: function (t, i, a) {
            switch (i) {
                case"normal":
                    e.extend(t, FX.Utils.getNormalLayoutSize(a));
                    break;
                case"grid-2":
                    e.extend(t, FX.Utils.getGrid2LayoutSize(a));
                    break;
                case"full-line":
                    e.extend(t, FX.Utils.getFullLineLayoutSize(a))
            }
            "linkquery" !== t.type && "linkdata" !== t.type || e.extend(t, {layout: i})
        }, getNormalLayoutSize: function (e) {
            switch (e) {
                case"location":
                    return {width: 330, btnWidth: 330};
                case"image":
                case"upload":
                    return {width: 330, thumbWidth: 65, thumbHeight: 65};
                case"subform":
                    return {tipWidth: 330};
                case"linkdata":
                case"linkquery":
                    return {width: 330, btnWidth: 330};
                case"text":
                case"number":
                case"datetime":
                case"combo":
                case"combocheck":
                case"user":
                case"dept":
                    return {width: 330};
                case"textarea":
                case"checkboxgroup":
                case"usergroup":
                case"deptgroup":
                    return {width: 720};
                case"radiogroup":
                    return {width: 720, otherInputWidth: 274};
                case"address":
                    return {width: 720, width4province: 310, width4city: 200, width4district: 200};
                default:
                    return {}
            }
        }, getGrid2LayoutSize: function (e) {
            switch (e) {
                case"location":
                    return {width: 330, btnWidth: 330};
                case"image":
                case"upload":
                    return {width: 330, thumbWidth: 65, thumbHeight: 65};
                case"subform":
                    return {tipWidth: 330};
                case"linkdata":
                case"linkquery":
                    return {width: 330, btnWidth: 330};
                case"text":
                case"number":
                case"datetime":
                case"combo":
                case"combocheck":
                case"user":
                case"dept":
                    return {width: 330};
                case"textarea":
                case"checkboxgroup":
                case"usergroup":
                case"deptgroup":
                    return {width: 330};
                case"radiogroup":
                    return {width: 330, otherInputWidth: 274};
                case"address":
                    return {width: 330, width4province: 160, width4city: 80, width4district: 80};
                default:
                    return {}
            }
        }, getFullLineLayoutSize: function (e) {
            switch (e) {
                case"location":
                    return {width: 720, btnWidth: 330};
                case"image":
                case"upload":
                    return {width: 720, thumbWidth: 65, thumbHeight: 65};
                case"subform":
                    return {tipWidth: 330};
                case"linkdata":
                case"linkquery":
                    return {width: 720, btnWidth: 720};
                case"text":
                case"number":
                case"datetime":
                case"combo":
                case"combocheck":
                case"user":
                case"dept":
                    return {width: 720};
                case"textarea":
                case"checkboxgroup":
                case"usergroup":
                case"deptgroup":
                    return {width: 720};
                case"radiogroup":
                    return {width: 720, otherInputWidth: 664};
                case"address":
                    return {width: 720, width4province: 310, width4city: 200, width4district: 200};
                default:
                    return {}
            }
        }, getVipTrail: function () {
            FX.STATIC.user.phone || "wechat" === FX.Utils.getCorpType(FX.Utils.getCurrentCorp()) ? this.ajax({url: FX.Utils.getApi(FX.API.profile.start_trail)}, function (e) {
                FX.Msg.alert({
                    type: "success",
                    title: "领取成功",
                    msg: "您已领取简道云高级功能30天试用期。",
                    text4Ok: "开始使用",
                    text4Cancel: "",
                    onOk: function () {
                        var e = FX.Cookie.get(FX.STATIC.user.username + FX.CONST.VIP_COOKIE.TRAIL.SUFFIX_KEY);
                        e && 1 === (e = e.split(",")).length && (e.push(+new Date), FX.Cookie.set(FX.STATIC.user.username + FX.CONST.VIP_COOKIE.TRAIL.SUFFIX_KEY, e.join(","), {expires: FX.CONST.VIP_COOKIE.TRAIL.EXPIRES_DATE})), window.location.reload()
                    }
                })
            }) : (new FX.VipTrailDialog).show()
        }, isWpsWebView: function () {
            return /wpscloudform/.test(navigator.userAgent)
        }, callWPSAPI: function (e) {
            var t = "jsAsynCall(" + JSON.stringify(e) + ")";
            window.cefQuery && window.cefQuery({request: t})
        }, onWPSPageUnload: function (e, t) {
            e ? FX.Msg.alert({
                type: "warning", msg: "当前页面未保存，是否确定离开？", text4Ok: "离开", text4Cancel: "取消", onOk: function () {
                    FX.Utils.applyFunc(this, t, [], !1)
                }
            }) : FX.Utils.applyFunc(this, t, [], !1)
        }, fileDownload: function (e, t) {
            if (FX.Utils.isWpsWebView()) {
                var i = {method: "downloadUrl", url: e, filename: t}, a = t && t.split(".").pop();
                i.filter = "(*." + (a || "*") + ")", FX.Utils.callWPSAPI(i)
            } else FX.Utils.redirectTo(e)
        }, isSupportPdf: function () {
            return void 0 !== navigator.mimeTypes["application/pdf"]
        }, isExternalLink: function () {
            return FX.STATIC.FTOKEN || FX.STATIC.RTOKEN || FX.STATIC.ATOKEN || FX.STATIC.DTOKEN
        }, isMembersEmpty: function (e) {
            return !!FX.Utils.isObjectEmpty(e) || !e.creator && !e.deptManager && !e.hasCurrentUser && !e.hasCurrentDept && FX.Utils.isObjectEmpty(e.widgets) && FX.Utils.isObjectEmpty(e.departs) && FX.Utils.isObjectEmpty(e.users) && FX.Utils.isObjectEmpty(e.deptWidgets) && FX.Utils.isObjectEmpty(e.deptMgrWidgets) && FX.Utils.isObjectEmpty(e.contacts) && FX.Utils.isObjectEmpty(e.roles)
        }, dt: function (t, i) {
            if (t) {
                var a = ["e=" + t, "t=" + (new Date).getTime()];
                FX.Utils.isEmpty(i) || a.push("ext=" + i), FX.STATIC.user && FX.STATIC.user.username && a.push("u=" + FX.STATIC.user.username), e.ajax({
                    type: "GET",
                    url: FX.CONFIG.HOST.TRACK_HOST + "/log?" + a.join("&")
                })
            }
        }, createSvgEl: function (t, i) {
            return e(document.createElementNS("http://www.w3.org/2000/svg", t)).attr(i || {})
        }, getTargetUrl: function (e, t) {
            var i = "/dashboard";
            switch (e) {
                case"aggregateList":
                    i += "#/app/" + t.appId + "/set/app-aggregate";
                    break;
                case"printList":
                    i += "/app/" + t.appId + "/form/" + t.entryId + "/edit?action=print#/set";
                    break;
                case"formData":
                    i += "/app/" + t.appId + "/form/" + t.entryId + "/edit#/data"
            }
            return i
        }, formatOrderProduct: function (e) {
            var t = "";
            switch (e.type) {
                case"level":
                    t = FX.CONST.VIP_ORDER.PACK[e.value].name;
                    break;
                case"service":
                    t = FX.CONST.VIP_ORDER.SERVICE[e.value].name;
                    break;
                case"user":
                    t = "按用户数购买 * " + e.value + "人";
                    break;
                case"data_addon":
                    t = "总数据量增购包10万条 * " + e.value / FX.CONST.VIP_ORDER.DATA_ADD_UNIT;
                    break;
                case"form_data_addon":
                    t = "单表数据上限增购包 * " + e.value / FX.CONST.VIP_ORDER.FORM_DATA_UNIT + "万条";
                    break;
                case"data_api_addon":
                    t = "数据推送";
                    break;
                case"upload_addon":
                    t = "附件上传增购包 * " + e.value / FX.CONST.VIP_ORDER.UPLOAD_ADD_UNIT + "GB";
                    break;
                case"aggregate_addon":
                    t = "聚合表增购包 * " + e.value + "个/应用";
                    break;
                case"managers_addon":
                    t = "子管理员 * " + e.value + "人"
            }
            return t
        }, addClsToSystemField: function (t, i) {
            return FX.Utils.forEach(t, function (t, a) {
                var s = a.value;
                /^_widget_/.test(s) || e.extend(a, {cls: i})
            }), t
        }, parseMembers2Ids: function (e) {
            var t = {};
            return FX.Utils.forEach(e, function (e, i) {
                switch (e) {
                    case"users":
                    case"departs":
                    case"roles":
                    case"contacts":
                        t[e] = i.map(function (e) {
                            return e._id
                        });
                        break;
                    default:
                        t[e] = i
                }
            }), t
        }, format2ThumbDate: function (e) {
            if (FX.Utils.isNull(e)) return null;
            var t, i = new Date(e), a = new Date, s = a.getTime() - i.getTime(), n = +a.setHours(0, 0, 0, 0),
                o = +a.setHours(23, 59, 59, 999);
            return 0 <= s && s < 36e5 ? (t = parseInt(s / 6e4, 10)) ? t + "分钟前" : "刚刚" : n < +i && +i <= o ? "今天" + FX.Utils.leftPad(i.getHours() + "", 2, "0") + ":" + FX.Utils.leftPad(i.getMinutes() + "", 2, "0") : FX.Utils.date2Str(i, "yyyy-MM-dd HH:mm:dd")
        }, formatUserThumb: function (e) {
            if (!FX.Utils.isEmpty(e)) return {color: e.charCodeAt(0) % 6, name: e.substr(0, 1).toUpperCase()}
        }, getCouponTip: function (e) {
            var t = [];
            if (e.discount < 1) {
                var i = [];
                FX.Utils.forEach(e.levels, function (e, t) {
                    FX.CONST.VIP_ORDER.PACK[t] && i.push(FX.CONST.VIP_ORDER.PACK[t].name)
                }), t.push("折扣仅对" + i.join("或") + "「套餐」生效")
            }
            return t.join("，")
        }, acquireCoupon: function (e) {
            FX.Utils.ajax({url: FX.Utils.getApi(FX.API.profile.acquire_coupon), data: {couponTags: e}}, function () {
                FX.Utils.redirectTo("/profile?shouldShowCoupon=true#/vip")
            }, function (e) {
                var t = e.responseJSON || {};
                1045 === t.code ? new FX.PhoneBindDialog({
                    title: "领取优惠券",
                    bindTip: "绑定手机号码，即可领取优惠券",
                    text4Ok: "立即领取",
                    text4Cancel: "暂不领取",
                    onSuccess: function () {
                        FX.Utils.acquireCoupon()
                    }
                }).show() : FX.Msg.toast({type: "warning", msg: t.msg})
            })
        }, isPdfExt: function (e) {
            return /^pdf$/i.test(e)
        }, isOfficeExt: function (e) {
            return /^(doc|docx|ppt|pptx|xls|xlsx)$/i.test(e)
        }, isImageExt: function (e) {
            return /^(png|jpg|jpeg|gif)$/i.test(e)
        }, getArrayFromRange: function (e, t) {
            var i = [];
            switch (t) {
                case"number":
                    i.push(FX.Utils.isNull(e.min) ? null : e.min), i.push(FX.Utils.isNull(e.max) ? null : e.max);
                    break;
                case"address":
                    i.push(e.province || null), i.push(e.city || null), i.push(e.district || null);
                    break;
                case"datetime":
                    i.push(e.min ? FX.Utils.date2Str(new Date(e.min), "yyyy-MM-dd") : null), i.push(e.max ? FX.Utils.date2Str(new Date(e.max), "yyyy-MM-dd") : null)
            }
            return i
        }, createFileThumb: function (t, i) {
            i = i || "normal";
            var a = ["ppt", "pptx", "doc", "docx", "xls", "xlsx", "zip", "rar", "csv", "txt", "pdf"].indexOf(t) > -1 ? t : "other";
            return e('<div class="fui_file_thumb ' + a + " size-" + i + '"/>')
        }, getFileOnlineUrl: function (e, t) {
            return FX.Utils.isPdfExt(e) ? "https://assets.jiandaoyun.com/shared/pdfjs/1.10/web/viewer.html?file=" + encodeURIComponent(t) : FX.Utils.isOfficeExt(e) ? "https://view.officeapps.live.com/op/view.aspx?src=" + encodeURIComponent(t) : void 0
        }, getRandomCode: function (e, t) {
            for (var i = t || "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", a = ""; e > 0;) a += i[Math.floor(Math.random() * i.length)], e--;
            return a
        }
    })
}(jQuery), jQuery.extend(FX.Utils, {
    needDotGuide: function (e) {
        FX.STATIC.user && FX.STATIC.user.regTime;
        return !1
    }, getTimeById: function (e) {
        var t = e.toString().substr(0, 8);
        return new Date(1e3 * parseInt(t, 16))
    }, isRegtimeBeforePersona: function () {
        return new Date(FX.STATIC.user.regTime) < new Date(2017, 11, 4).getTime()
    }, handleInviteGuide: function (e, t, i) {
        FX.Utils.needInviteGuide() ? FX.Utils.ajax({
            url: FX.Utils.getApi(FX.API.corp.department_list_member, FX.CONST.DEPARTMENT_ROOT),
            data: {corpId: FX.Utils.getCurrentCorp(), limit: 1}
        }, function (a) {
            a.count > 1 ? (FX.Cookie.set(FX.STATIC.user._id + FX.CONST.COOKIE.INVITE_MEMBER.SUFFIX_KEY, FX.CONST.COOKIE.INVITE_MEMBER.VALUE, {
                expires: FX.CONST.COOKIE.INVITE_MEMBER.EXPIRES,
                path: "/"
            }), t && t()) : (e && FX.UI.inviteGuide(e), i && i())
        }) : t && t()
    }, needInviteGuide: function () {
        return "internal" === FX.STATIC.user.corpType && FX.Utils.getCurrentCorp() === FX.STATIC.user.corpId && !FX.Cookie.get(FX.STATIC.user._id + FX.CONST.COOKIE.INVITE_MEMBER.SUFFIX_KEY)
    }
}), function (e) {
    e.extend(FX.Utils, {
        getLinkFilter: function (t, i) {
            var a = {type: t.type};
            switch (e.extend(a, FX.Utils.dealFilterFieldName(t)), t.type) {
                case"datetime":
                    a.method = FX.CONST.FILTER_METHOD.RG, a.value = i;
                    break;
                case"address":
                case"location":
                    a.type = "address", a.method = FX.CONST.FILTER_METHOD.ALL, a.value = i;
                    break;
                case"user":
                case"id":
                    a.type = "user", a.method = FX.CONST.FILTER_METHOD.IN, a.value = e.makeArray(i);
                    break;
                case"dept":
                case"did":
                    a.type = "dept", a.method = FX.CONST.FILTER_METHOD.IN, a.value = e.makeArray(i);
                    break;
                default:
                    a.type = "text", a.method = FX.CONST.FILTER_METHOD.IN, a.value = e.makeArray(i)
            }
            return a
        }, getReportLinkFilter: function (t, i) {
            var a = {type: t.type, method: FX.CONST.FILTER_METHOD.IN};
            switch (e.extend(a, FX.Utils.dealFilterFieldName(t)), t.type) {
                case"user":
                case"id":
                    a.type = "user", a.value = e.makeArray(i.value);
                    break;
                case"dept":
                case"did":
                    a.type = "dept", a.value = e.makeArray(i.value);
                    break;
                default:
                    "creator" === t.name ? (a.type = "user", a.value = e.makeArray(i.value)) : a = FX.Utils.getLinkFilter(t, i)
            }
            return a
        }, dealFilterFieldName: function (e) {
            var t = {};
            if (/\./.test(e.name)) {
                var i = e.name.split(".");
                t.subform = i[0], t.subField = i[1]
            } else t.field = e.name;
            return t
        }, dealFilterInfoByField: function (t) {
            var i = FX.Utils.getFieldInfoById(t.id), a = FX.Utils.dealFilterFieldName(t);
            return e.extend({}, i, a)
        }, dealFormFilterCond: function (e) {
            if (e && e.cond) {
                var t = [];
                FX.Utils.forEach(e.cond, function (e, i) {
                    i.entryId = void 0, t.push(i)
                }), e.cond = t
            }
            return e
        }, pretreatFormFilterCond: function (e) {
            var t = [];
            return e && (FX.Utils.forEach(e, function (e, t) {
                t.entryId = void 0
            }), t = e), t
        }, getDateRange: function (e, t, i) {
            var a = "yyyy-MM-dd", s = new Date, n = [];
            if (i) {
                s.setFullYear(e, t - 1, i);
                var o = FX.Utils.date2Str(s, a);
                n = [o, o]
            } else t ? (s.setFullYear(e, t - 1, 1), n.push(FX.Utils.date2Str(s, a)), s.setFullYear(e, t, 1), s.setHours(0, 0, 0, 0), n.push(FX.Utils.date2Str(new Date(s.getTime() - 1), a))) : (s.setFullYear(e, 0, 1), n.push(FX.Utils.date2Str(s, a)), s.setFullYear(e + 1, 0, 1), s.setHours(0, 0, 0, 0), n.push(FX.Utils.date2Str(new Date(s.getTime() - 1), a)));
            return n
        }
    })
}(jQuery), function (e) {
    FX.Utils = FX.Utils || {}, e.extend(FX.Utils, {
        address2Str: function (e, t, i) {
            if (i && e) {
                t = "";
                var a = !0;
                /p/.test(i) && e.province && (t += e.province, e.province === e.city && (a = !1)), /c/.test(i) && e.city && a && (t += e.city), /d/.test(i) && e.district && (t += e.district), /a/.test(i) && e.detail && (t += e.detail)
            }
            return t
        }, num2Str: function (e, t) {
            if (FX.Utils.isEmpty(e)) return "";
            var i = e + "";
            if (FX.Utils.isEmpty(t)) return i;
            var a = /\[Num0\]/;
            if (a.test(t)) return t.replace(a, i);
            if ((a = /\[Num1\]/).test(t)) return t.replace(a, FX.Utils._num2CN(i, !1));
            if ((a = /\[Num2\]/).test(t)) return t.replace(a, FX.Utils._num2CN(i, !0));
            a = /[#0]+,?[#0]*\.?[#0]*%?/;
            var s = t.match(a);
            if (s && s.length > 0) {
                var n = s[0];
                return i = FX.Utils._numberFormat(e, n), t.replace(a, i)
            }
            return t
        }, _numberFormat: function (e, t) {
            var i = "", a = e + "";
            if (/%$/.test(t)) {
                i = "%", e *= 100, t = t.replace("%", "");
                var s = a.indexOf(".");
                if (s > -1) {
                    var n = a.length - 3 - s;
                    n = n < 0 ? 0 : n > 8 ? 8 : n, e = parseFloat(e.toFixed(n))
                }
                a = e + ""
            }
            var o = t.split("."), l = o[0], r = o[1];
            if ("" !== r) {
                for (var c = r ? r.length : 0, d = (a = parseFloat(e).toFixed(c)).split(""), u = c; u > 0 && "#" === r.charAt(u - 1); u--) {
                    var h = d.pop();
                    if ("0" !== h) {
                        d.push(h);
                        break
                    }
                }
                var p = d.pop();
                "." === p && (p = ""), a = d.join("") + p
            }
            var f = a.split("."), m = f[0];
            if (/,/.test(l)) f[0] = m.replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, "$1,"); else {
                var g = l.match(/[0]+[0#]*$/);
                g && g.length > 0 && (f[0] = FX.Utils.leftPad(m, g[0].length, "0"))
            }
            return f.join(".") + i
        }, _num2CN: function (e, t) {
            var i = "〇一二三四五六七八九", a = "个十百千万亿";
            t && (i = "零壹贰叁肆伍陆柒捌玖", a = "个拾佰仟万亿");
            var s = Math.floor(Math.abs(e)), n = Math.abs(e).toString(), o = n.replace(/\..*$/, ""), l = n.split("."),
                r = i, c = a, d = r[0], u = new RegExp(r[0] + "*$"), h = new RegExp(r[0] + "+", "g"), p = "", f = "";
            if (p = e < 0 ? "-."[0] : "", l.length >= 2) {
                var m = l[1];
                if (m) {
                    f = "-."[1];
                    for (var g = 0; g < m.length; g++) f += r[+m[g]]
                }
            }
            if (1 == o.length) return p + r[s] + f;
            if (o.length <= 5) {
                for (var v = "", F = 0, s = o.length; s--;) {
                    var b = +o[F];
                    v += this._num2CN(o[F], t) + (b && s ? c[s] : ""), F++
                }
                return v = v.replace(h, d), v = v.replace(u, ""), p + v + f
            }
            for (var _ = o.length / 4 >> 0, y = o.length % 4, v = ""; 0 == y || !c[3 + _];) y += 4, _--;
            if (+o.substr(0, y)) {
                v = this._num2CN(o.substr(0, y), t) + c[3 + _];
                var w = o.substr(y);
                "0" === w[0] && (v += r[0]), v += this._num2CN(w, t)
            } else v = this._num2CN(o.substr(0, y), t) + this._num2CN(o.substr(y), t);
            return v = v.replace(h, d), v = v.replace(u, ""), p + v + f
        }, date2Str: function (e, t) {
            if (!e) return "";
            var i = t.length, a = "";
            if (i > 0) {
                for (var s = t.charAt(0), n = 0, o = s, l = 1; l < i; l++) {
                    var r = t.charAt(l);
                    s !== r ? (a += FX.Utils._compileDateFormat({
                        char: s,
                        str: o,
                        len: l - n
                    }, e), n = l, o = s = r) : o += r
                }
                a += FX.Utils._compileDateFormat({char: s, str: o, len: i - n}, e)
            }
            return a
        }, _compileDateFormat: function (e, t) {
            var i = e.str, a = e.len;
            switch (e.char) {
                case"E":
                    i = a > 2 ? Date._DN[t.getDay()] : a > 1 ? Date._SDN[t.getDay()] : t.getDay() + "";
                    break;
                case"y":
                    i = a <= 3 ? (t.getFullYear() + "").slice(2, 4) : t.getFullYear();
                    break;
                case"M":
                    i = a > 2 ? Date._MN[t.getMonth()] : a < 2 ? t.getMonth() + 1 : FX.Utils.leftPad(t.getMonth() + 1 + "", 2, "0");
                    break;
                case"d":
                    i = a > 1 ? FX.Utils.leftPad(t.getDate() + "", 2, "0") : t.getDate();
                    break;
                case"h":
                    var s = t.getHours() % 12;
                    0 === s && (s = 12), i = a > 1 ? FX.Utils.leftPad(s + "", 2, "0") : s;
                    break;
                case"H":
                    i = a > 1 ? FX.Utils.leftPad(t.getHours() + "", 2, "0") : t.getHours();
                    break;
                case"m":
                    i = a > 1 ? FX.Utils.leftPad(t.getMinutes() + "", 2, "0") : t.getMinutes();
                    break;
                case"s":
                    i = a > 1 ? FX.Utils.leftPad(t.getSeconds() + "", 2, "0") : t.getSeconds();
                    break;
                case"a":
                    i = t.getHours() < 12 ? "am" : "pm";
                    break;
                default:
                    i = e.str
            }
            return i
        }
    })
}(jQuery), function ($) {
    FX.Formula = {
        AND: function () {
            for (var e = FX.Utils.flatten(arguments), t = 0, i = e.length; t < i; t++) if (!e[t]) return !1;
            return !0
        }, OR: function () {
            for (var e = FX.Utils.flatten(arguments), t = 0, i = e.length; t < i; t++) if (e[t]) return !0;
            return !1
        }, FALSE: function () {
            return !1
        }, TRUE: function () {
            return !0
        }, IF: function (e, t, i) {
            return e ? t : i
        }, NOT: function (e) {
            return !e
        }, XOR: function () {
            for (var e = 0, t = FX.Utils.flatten(arguments), i = 0, a = t.length; i < a; i++) t[i] && e++;
            return !!(1 & Math.floor(Math.abs(e)))
        }, CONCATENATE: function () {
            for (var e = FX.Utils.flatten(arguments), t = 0; (t = e.indexOf(!0)) > -1;) e[t] = "TRUE";
            for (var i = 0; (i = e.indexOf(!1)) > -1;) e[i] = "FALSE";
            return e.join("")
        }, EXACT: function (e, t) {
            return e === t
        }, LEFT: function (e, t) {
            return t = FX.Utils.isEmpty(t) ? 1 : t, e ? e.substring(0, t) : ""
        }, LEN: function (e) {
            return FX.Utils.isString(e) ? e ? e.length : 0 : e && e.length ? e.length : 0
        }, LOWER: function (e) {
            return FX.Utils.isString(e) ? e ? e.toLowerCase() : e : ""
        }, REPLACE: function (e, t, i, a) {
            return FX.Utils.isNumber(t) && FX.Utils.isNumber(i) ? (e = e || "", a = a || "", e.substr(0, t - 1) + a + e.substr(t - 1 + i)) : e
        }, REPT: function (e, t) {
            return t = t || 0, new Array(t + 1).join(e)
        }, RIGHT: function (e, t) {
            return t = void 0 === t ? 1 : t, e ? e.substring(e.length - t) : ""
        }, SEARCH: function (e, t, i) {
            return FX.Utils.isString(e) && FX.Utils.isString(t) ? (i = FX.Utils.isNull(i) ? 0 : i, t.toLowerCase().indexOf(e.toLowerCase(), i - 1) + 1) : 0
        }, SPLIT: function (e, t) {
            return FX.Utils.isString(e) ? e.split(t) : []
        }, TRIM: function (e) {
            return FX.Utils.isString(e) ? e.replace(/ +/g, " ").trim() : ""
        }, UPPER: function (e) {
            return FX.Utils.isString(e) ? e.toUpperCase() : ""
        }, MID: function (e, t, i) {
            return e = e || "", FX.Utils.isNumber(t) && FX.Utils.isNumber(i) ? e.substr(t - 1, i) : e
        }, AVERAGE: function () {
            for (var e = FX.Utils.flatten(arguments, function (e) {
                return FX.Utils.isNumber(e)
            }), t = e.length, i = 0, a = 0, s = 0; s < t; s++) i += e[s], a += 1;
            return i / a
        }, COUNT: function () {
            return FX.Utils.flatten(arguments).length
        }, COUNTIF: function () {
            var len = arguments.length, criteria = arguments[len - 1];
            /[<>=!]/.test(criteria) || (criteria = '=="' + criteria + '"');
            for (var args = FX.Utils.flatten(Array.prototype.slice.call(arguments, 0, len - 1)), matches = 0, i = 0; i < args.length; i++) "string" != typeof args[i] ? eval(args[i] + criteria) && matches++ : eval('"' + args[i] + '"' + criteria) && matches++;
            return matches
        }, LARGE: function (e, t) {
            return (e = FX.Utils.flatten(e, function (e) {
                return FX.Utils.isNumber(e)
            })).sort(function (e, t) {
                return t - e
            })[t - 1]
        }, MAX: function () {
            var e = FX.Utils.flatten(arguments, function (e) {
                return FX.Utils.isNumber(e)
            });
            return 0 === e.length ? 0 : Math.max.apply(Math, e)
        }, MIN: function () {
            var e = FX.Utils.flatten(arguments, function (e) {
                return FX.Utils.isNumber(e)
            });
            return 0 === e.length ? 0 : Math.min.apply(Math, e)
        }, SMALL: function (e, t) {
            return (e = FX.Utils.flatten(e, function (e) {
                return FX.Utils.isNumber(e)
            })).sort(function (e, t) {
                return e - t
            })[t - 1]
        }, ABS: function (e) {
            return FX.Utils.isNumber(e) ? Math.abs(e) : 0
        }, ROUND: function (e, t) {
            return Math.round(e * Math.pow(10, t)) / Math.pow(10, t)
        }, CEILING: function (e, t) {
            if (0 === t) return 0;
            var i = t < 0 ? -1 : 0, a = (t = Math.abs(t)) - Math.floor(t), s = 0;
            return a > 0 && (s = -Math.floor(Math.log(a) / Math.log(10))), e >= 0 ? FX.Formula.ROUND(Math.ceil(e / t) * t, s) : 0 === i ? -FX.Formula.ROUND(Math.floor(Math.abs(e) / t) * t, s) : -FX.Formula.ROUND(Math.ceil(Math.abs(e) / t) * t, s)
        }, FLOOR: function (e, t) {
            if (0 === t) return 0;
            if (!(e > 0 && t > 0 || e < 0 && t < 0)) return 0;
            var i = (t = Math.abs(t)) - Math.floor(t), a = 0;
            return i > 0 && (a = -Math.floor(Math.log(i) / Math.log(10))), e >= 0 ? FX.Formula.ROUND(Math.floor(e / t) * t, a) : -FX.Formula.ROUND(Math.floor(Math.abs(e) / t) * t, a)
        }, INT: function (e) {
            return FX.Utils.isNumber(e) ? Math.floor(e) : 0
        }, LOG: function (e, t) {
            return t = void 0 === t ? 10 : t, FX.Utils.isNumber(t) ? Math.log(e) / Math.log(t) : 0
        }, MOD: function (e, t) {
            if (0 === t) return 0;
            var i = Math.abs(e % t);
            return t > 0 ? i : -i
        }, POWER: function (e, t) {
            var i = Math.pow(e, t);
            return isNaN(i) ? 0 : i
        }, PRODUCT: function () {
            for (var e = FX.Utils.flatten(arguments, function (e) {
                return FX.Utils.isNumber(e)
            }), t = 1, i = 0; i < e.length; i++) t *= e[i];
            return t
        }, SQRT: function (e) {
            return e < 0 ? 0 : Math.sqrt(e)
        }, SUM: function () {
            for (var e = 0, t = FX.Utils.flatten(arguments, function (e) {
                return FX.Utils.isNumber(e)
            }), i = 0, a = t.length; i < a; ++i) e += t[i];
            return e
        }, SUMPRODUCT: function () {
            for (var e = 0, t = [], i = -1, a = 0; a < arguments.length; a++) arguments[a] instanceof Array && (i = i < 0 ? arguments[a].length : Math.min(arguments[a].length, i), t.push(arguments[a]));
            for (var s, n, o, l = 0; l < i; l++) {
                for (s = 1, n = 0; n < t.length; n++) o = parseFloat(t[n][l]), isNaN(o) && (o = 0), s *= o;
                e += s
            }
            return e
        }, FIXED: function (e, t) {
            return t = void 0 === t ? 0 : t, FX.Utils.isNumber(t) && t >= 0 ? Number(e).toFixed(t) : ""
        }, DATE: function () {
            return 6 === arguments.length ? new Date(parseInt(arguments[0], 10), parseInt(arguments[1], 10) - 1, parseInt(arguments[2], 10), parseInt(arguments[3], 10), parseInt(arguments[4], 10), parseInt(arguments[5], 10)) : 3 === arguments.length ? new Date(parseInt(arguments[0], 10), parseInt(arguments[1], 10) - 1, parseInt(arguments[2], 10)) : new Date(arguments[0])
        }, TIME: function (e, t, i) {
            return (3600 * e + 60 * t + i) / 86400
        }, TIMESTAMP: function (e) {
            return FX.Utils.isDate(e) ? e.getTime() : 0
        }, TODAY: function () {
            return new Date
        }, NOW: function () {
            return new Date
        }, SYSTIME: function () {
            var e = FX.STATIC._st, t = (new Date).getTime() - FX.STATIC._ct;
            return t > 0 && t < 36e5 && (e += t), new Date(e)
        }, IP: function () {
            return FX.STATIC.ip || ""
        }, DAY: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getDate()
        }, MONTH: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getMonth() + 1
        }, YEAR: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getFullYear()
        }, HOUR: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getHours()
        }, MINUTE: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getMinutes()
        }, SECOND: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return e.getSeconds()
        }, DAYS: function (e, t) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) {
                var t = FX.Utils.parseDate(t);
                if (!FX.Utils.isNull(t)) return (new Date(e.getFullYear(), e.getMonth(), e.getDate()) - new Date(t.getFullYear(), t.getMonth(), t.getDate())) / 864e5
            }
        }, DAYS360: function (e, t, i) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) {
                var t = FX.Utils.parseDate(t);
                if (!FX.Utils.isNull(t)) {
                    var a, s, n = t.getMonth(), o = e.getMonth();
                    if (i) a = 31 === t.getDate() ? 30 : t.getDate(), s = 31 === e.getDate() ? 30 : e.getDate(); else {
                        var l = new Date(t.getFullYear(), n + 1, 0).getDate(),
                            r = new Date(e.getFullYear(), o + 1, 0).getDate();
                        a = t.getDate() === l ? 30 : t.getDate(), e.getDate() === r ? a < 30 ? (o++, s = 1) : s = 30 : s = e.getDate()
                    }
                    return 360 * (e.getFullYear() - t.getFullYear()) + 30 * (o - n) + (s - a)
                }
            }
        }, DATEDELTA: function (e, t) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) return FX.Utils.isNumber(t) || (t = 0), new Date(e.getTime() + 864e5 * t)
        }, ISOWEEKNUM: function (e) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) {
                e.setHours(0, 0, 0), e.setDate(e.getDate() + 4 - (e.getDay() || 7));
                var t = new Date(e.getFullYear(), 0, 1);
                return Math.ceil(((e - t) / 864e5 + 1) / 7)
            }
        }, WEEKNUM: function (e, t) {
            var e = FX.Utils.parseDate(e);
            if (!FX.Utils.isNull(e)) {
                var i = 2 === t ? 1 : 0, a = new Date(e.getFullYear(), 0, 1), s = (i + 7 - a.getDay()) % 7,
                    n = s > 0 ? 1 : 0, o = a.getTime() + 24 * s * 60 * 60 * 1e3;
                return Math.floor((e.getTime() - o) / 864e5 / 7 + 1) + n
            }
        }, TEXT: function (e, t) {
            return FX.Utils.isNull(e) ? "" : FX.Utils.isDate(e) && !FX.Utils.isEmpty(t) ? FX.Utils.date2Str(e, t) : FX.Utils.num2Str(e, t)
        }, VALUE: function (e) {
            return FX.Utils.isEmpty(e) ? 0 : isNaN(e) ? 0 : parseFloat(e)
        }, UUID: function () {
            return FX.Utils.UUID()
        }, RECNO: function () {
            return FX.Utils.isNull(FX.STATIC.EntryRecNo) ? FX.STATIC.APPID && FX.STATIC.ENTRYID ? (FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.formula.recno),
                async: !1,
                data: {appId: FX.STATIC.APPID, formId: FX.STATIC.ENTRYID, hasIncLock: FX.STATIC.RecnoLock}
            }, function (e) {
                FX.STATIC.EntryRecNo = e.incId
            }), FX.STATIC.EntryRecNo) : "" : FX.STATIC.EntryRecNo
        }, ISEMPTY: function (e) {
            return FX.Utils.isObjectEmpty(e)
        }, MAPX: function (e, t, i, a) {
            var s = null;
            if (FX.Utils.isEmpty(e) || FX.Utils.isObjectEmpty(t)) return s;
            e = e.toLowerCase();
            var n = FX.Utils.getFieldInfoByFormula(i), o = FX.Utils.getFieldInfoByFormula(a);
            if (/^sum|avg|max|min|count|first|last$/.test(e) && n.entryId && n.entryId === o.entryId) {
                var l = FX.Utils.isDate(t), r = l ? t.getTime() : t;
                FX.Utils.dataAjax({
                    url: FX.Utils.getApi(FX.API.formula.aggregate),
                    async: !1,
                    data: {
                        op: e,
                        formId: n.entryId,
                        lookup_value: r,
                        lookup_field: n.field,
                        result_field: o.field,
                        date_type: l,
                        refAppId: n.appId
                    }
                }, function (e) {
                    e.result && e.result[0] && (s = e.result[0].result)
                })
            }
            return s
        }, MAP: function (e, t, i) {
            var a = [];
            if (FX.Utils.isObjectEmpty(e)) return a;
            var s = FX.Utils.getFieldInfoByFormula(t), n = FX.Utils.getFieldInfoByFormula(i);
            return s.entryId && s.entryId === n.entryId && FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.formula.map),
                async: !1,
                data: {
                    formId: s.entryId,
                    lookup_value: e,
                    lookup_field: s.field,
                    result_field: n.field,
                    refAppId: s.appId
                }
            }, function (e) {
                FX.Utils.forEach(e.result, function (e, t) {
                    a.push(t[n.field])
                })
            }, function () {
            }), a
        }, GETUSERNAME: function () {
            return FX.STATIC.user ? FX.STATIC.user.nickname : ""
        }
    }
}(jQuery), FX.OB = function (e) {
    this.options = $.extend(this._defaultConfig(), e), this._beforeInit(), this._init(), this._afterInit()
}, $.extend(FX.OB.prototype, {
    _defaultConfig: function () {
        return {onBeforeInit: null, onAfterInit: null}
    }, _init: function () {
    }, _beforeInit: function () {
        FX.Utils.applyFunc(this, this.options.onBeforeInit, [], !1)
    }, _afterInit: function () {
        FX.Utils.applyFunc(this, this.options.onAfterInit, [], !1)
    }
}), FX.Widget = FX.extend(FX.OB, {
    _defaultConfig: function () {
        return $.extend(FX.Widget.superclass._defaultConfig.apply(this, arguments), {
            widgetName: "",
            baseCls: "",
            customCls: null,
            enable: !0,
            visible: !0,
            invalidateType: "blank"
        })
    }, _init: function () {
        FX.Widget.superclass._init.apply(this, arguments), this._initRoot(), this._initNameEffects()
    }, _afterInit: function () {
        this._initElementSize(), this._initVisualEffects(), this._initDefaultValue(), FX.Widget.superclass._afterInit.apply(this, arguments)
    }, _initRoot: function () {
        var e = this.options;
        this.xtype && (e.type = this.xtype), null != e.renderEl ? this.element = $(e.renderEl) : this.element = this._defaultRoot(), e.baseCls && this.element.addClass(e.baseCls), e.customCls && this.element.addClass(e.customCls)
    }, _initNameEffects: function () {
        var e = this.options;
        e.widgetName || (e.widgetName = "_widget_" + FX.STATIC.IDBase++), this.element.attr({widgetName: e.widgetName})
    }, _initElementSize: function () {
        this.doResize()
    }, _initVisualEffects: function () {
        this.setEnable(this.options.enable), this.setVisible(this.options.visible)
    }, _initDefaultValue: function () {
        var e = this.options;
        null != e.value ? this.setValue(e.value) : null != e.text && this.setText(e.text)
    }, _defaultRoot: function () {
        return $("<div/>")
    }, getWidgetByName: function (e) {
        return this.options.resultWidgets ? this.options.resultWidgets[e] : null
    }, getWidgetName: function () {
        return this.options.widgetName
    }, getWidgetType: function () {
        return this.options.type
    }, getText: function () {
        return this.options.text
    }, setText: function (e) {
        this.options.text = e
    }, getValue: function () {
        return this.options.value
    }, setValue: function (e) {
        this.options.value = e
    }, isEnabled: function () {
        return this.options.enable
    }, setEnable: function (e) {
        this.options.enable = !!e, !0 === this.options.enable ? this.element.removeClass("x-ui-disable") : this.element.addClass("x-ui-disable")
    }, isVisible: function () {
        return this.options.visible
    }, setVisible: function (e) {
        this.options.visible = !!e, !0 === this.options.visible ? this.element.removeClass("x-ui-hidden") : this.element.addClass("x-ui-hidden")
    }, reset: function () {
        this.setValue(null)
    }, doResize: function (e) {
        var t = this.options;
        e && (t.width = e.width, t.height = e.height), FX.Utils.isEmpty(t.width) || this.element.css({width: t.width}), FX.Utils.isEmpty(t.height) || this.element.css({height: t.height})
    }, destroy: function () {
        this.element.remove()
    }, rebuild: function () {
        this.options.renderEl = this.element, this.element.empty(), this._beforeInit(), this._init(), this._afterInit()
    }, checkValidate: function () {
        return !0
    }, fireEvent: function (e, t) {
        this.element.trigger(e, t)
    }, getOptions: function (e) {
        var t = this.options;
        return {
            type: t.type,
            widgetName: t.widgetName,
            height: t.height,
            width: t.width,
            text: t.text,
            value: t.value,
            enable: t.enable,
            visible: t.visible,
            allowBlank: t.allowBlank,
            rely: t.rely
        }
    }, getInvalidateType: function () {
        return this.options.invalidateType
    }, setInvalidateType: function (e) {
        this.options.invalidateType = e
    }, getNullValue: function () {
        return null
    }, getLinkValue: function () {
        return this.getValue()
    }, getLinkType: function () {
        return this.getWidgetType()
    }, getCacheValue: function () {
        return this.getValue()
    }, setCacheValue: function (e) {
        this.setValue(e)
    }, bindWidgetEvent: function (e, t) {
        this.options[e] = t
    }, unbindWidgetEvent: function (e) {
        this.options[e] = null
    }
}), function (e) {
    FX.RelyProcessor = function (e) {
        this.options = {
            defaultVersion: 0,
            version: 0,
            versionMap: {},
            stateMap: {},
            asyncMap: {},
            defaults: [],
            relyMap: {},
            linkMap: {},
            defaultMap: {}
        }, this._init(e)
    }, e.extend(FX.RelyProcessor.prototype, {
        RELY_END: -1, _init: function (e) {
            this.options.relyMap = this._getRelyWidgetsMap(e), this.options.linkMap = this._getLinkMap(this.options.relyMap)
        }, _getLinkMap: function (e) {
            var t = this, i = {};
            return FX.Utils.forEach(e, function (e, a) {
                FX.Utils.forEach(a, function (a, s) {
                    t._add2LinkMap(i, s, e)
                })
            }), i
        }, _add2LinkMap: function (e, t, i) {
            if (e[t] || (e[t] = []), e[t].push(i), /\./.test(t) && !/\./.test(i)) {
                var a = t.split(".")[0];
                this._add2LinkMap(e, a, i)
            }
            return e
        }, _getRelyWidgetsMap: function (e) {
            var t = this, i = {};
            return FX.Utils.forEach(e, function (e, a) {
                var s = a.widget;
                if (s && "linkdata" !== s.type) {
                    if ("subform" === s.type) {
                        var n = t._getRelyWidgetsMap(s.items);
                        FX.Utils.forEach(n, function (e, t) {
                            var a = [s.widgetName, e].join(".");
                            i[a] = t
                        })
                    }
                    var o = s.rely;
                    o && o.widgets && (i[s.widgetName] = o.widgets)
                }
            }), i
        }, _isSubformWidget: function (e) {
            return /\./.test(e)
        }, _getVersion: function (e, t) {
            var i = this.options, a = i.versionMap[e] || i.defaultVersion;
            return t > -1 && this._isSubformWidget(e) && (a = Math.max(a, i.versionMap[e + t] || i.defaultVersion)), a
        }, _getState: function (e, t) {
            var i = this.options, a = i.stateMap[e] || i.defaultVersion;
            return t > -1 && this._isSubformWidget(e) && (a = Math.max(a, i.stateMap[e + t] || i.defaultVersion)), a
        }, _getAsync: function (e, t) {
            var i = this.options;
            return t > -1 && this._isSubformWidget(e) ? i.asyncMap[e] && i.asyncMap[e][t] : i.asyncMap[e]
        }, getRelyVersion: function (e, t, i, a, s) {
            var n = this;
            return s = s || {}, this._isSubformWidget(t) || (i = -1), FX.Utils.forEach(e[t], function (t, o) {
                s[o] || s[o + i] || (i > -1 && n._isSubformWidget(o) ? s[o + i] = a : s[o] = a, n.getRelyVersion(e, o, i, a, s))
            }), s
        }, checkAsyncState: function () {
            var e = this, t = this.options, i = !0;
            return FX.Utils.forEach(t.asyncMap, function (a) {
                var s = t.asyncMap[a];
                if (e._isSubformWidget(a) ? FX.Utils.forEach(s, function (e, t) {
                        if (!1 === t) return i = !1, !1
                    }) : i = !1 !== s, !i) return !1
            }), i
        }, setStateMap: function (e, t, i) {
            var a = this.options;
            i > -1 ? a.stateMap[e + i] = t : a.stateMap[e] = t
        }, setAsyncMap: function (e, t, i) {
            var a = this.options;
            i > -1 ? (a.asyncMap[e] = a.asyncMap[e] || {}, a.asyncMap[e][i] = t) : a.asyncMap[e] = t
        }, addDefaultRely: function (e) {
            FX.Utils.isObjectEmpty(e.options.value) || this.options.defaults.push(e)
        }, getDefaultRely: function () {
            return this.options.defaults
        }, _checkRely: function (e, t, i, a) {
            var s = this, n = this.options, o = !0;
            return FX.Utils.forEach(n.relyMap[i], function (n, l) {
                if (s._isSubformWidget(l) && !s._isSubformWidget(i)) {
                    var r = null, c = 0;
                    do {
                        if ((r = e.getWidgetByName(l, c)) && t === s._getVersion(l, c) && s._getAsync(l, c) !== t) {
                            o = !1;
                            break
                        }
                        c++
                    } while (r)
                } else !1 === s._getAsync(l, a) ? o = !1 : t === s._getVersion(l, a) && (o = s._getAsync(l, a) === t);
                if (!o) return !1
            }), o && (this._getState(i, a) === t ? o = !1 : this.setStateMap(i, t, a)), o
        }, fireRely: function (t, i, a) {
            var s = this.options, n = this, o = -1, l = t.options.widgetName;
            t.options.subform && (l = [t.options.subform, l].join("."), o = FX.Utils.getSubformRowIdx(t)), i || (s.version++, i === s.defaultVersion && (s.defaultMap[s.version] = !0), i = s.version, e.extend(s.versionMap, this.getRelyVersion(s.linkMap, l, o, i)), this.setStateMap(l, i, o)), this.setAsyncMap(l, i, o);
            var r = t.getLinkValue();
            FX.Utils.forEach(s.linkMap[l], function (e, t) {
                if (!(i < n._getState(t, o)) || s.defaultMap[i]) {
                    var l;
                    if (n._isSubformWidget(t) && o < 0) {
                        var c = 0;
                        do {
                            if (!n._checkRely(a, i, t, c)) return;
                            (l = a.getWidgetByName(t, c)) && (n.setAsyncMap(t, !1, c), a.dealRely(t, l, i, r)), c++
                        } while (l)
                    } else {
                        if (!n._checkRely(a, i, t, o)) return;
                        if (!(l = a.getWidgetByName(t, o))) return;
                        n.setAsyncMap(t, !1, o), a.dealRely(t, l, i, r)
                    }
                }
            })
        }, checkAsyncVersion: function (e, t) {
            var i = this.options, a = -1, s = e.options.widgetName;
            return e.options.subform && (s = [e.options.subform, s].join("."), a = FX.Utils.getSubformRowIdx(e)), this._getState(s, a) <= t || i.defaultVersion[t]
        }
    })
}(jQuery), function () {
    FX.Store = FX.Store || {}, $.extend(FX.Store, {
        expireTime: 864e5, set: function (e, t) {
        }, get: function (e, t) {
        }, has: function (e) {
            return void 0 !== this.get(e)
        }, remove: function (e) {
        }, clear: function () {
        }, transact: function (e, t, i) {
            null == i && (i = t, t = null), null == t && (t = {});
            var a = this.get(e, t);
            i(a), this.set(e, a)
        }, getAll: function () {
            var e = {};
            return this.forEach(function (t, i) {
                e[t] = i
            }), e
        }, forEach: function () {
        }, serialize: function (e) {
            return JSON.stringify(e)
        }, deserialize: function (e) {
            if ("string" == typeof e) try {
                return JSON.parse(e)
            } catch (t) {
                return e || void 0
            }
        }, getKey: function (e, t) {
            var i = "";
            switch (e) {
                case"paramFields":
                case"showFields":
                case"metaFields":
                    i = [e, t.appId, t.entryId, t.groupId].join("");
                    break;
                case"authGroup":
                    i = [e, t.appId, t.entryId].join("");
                    break;
                case"formData":
                    i = FX.STATIC.user && !FX.STATIC.FTOKEN ? [e, t.appId, t.entryId, FX.STATIC.user._id].join("") : [e, t.appId, t.entryId].join("")
            }
            return i
        }
    });
    var e = "undefined" != typeof window ? window : global, t = "localStorage";
    (function () {
        try {
            return t in e && e[t]
        } catch (e) {
            return !1
        }
    })() && $.extend(FX.Store, {
        storage: e[t], set: function (e, t, i) {
            if (void 0 === t) return this.remove(e);
            i && (t = {data: t, expire: +new Date + this.expireTime * i});
            try {
                this.storage.setItem(e, this.serialize(t))
            } catch (e) {
                return void this.clear(!0)
            }
            return t
        }, get: function (e, t) {
            var i = this.deserialize(this.storage.getItem(e));
            return i && i.expire && (i = i.data), void 0 === i ? t : i
        }, remove: function (e) {
            this.storage.removeItem(e)
        }, clear: function (e) {
            var t = this;
            if (e) {
                var i = +new Date;
                this.forEach(function (e, a) {
                    a.expire && i > a.expire && t.remove(e)
                })
            } else this.storage.clear()
        }, forEach: function (e) {
            for (var t = 0; t < this.storage.length; t++) {
                var i = this.storage.key(t);
                e(i, this.deserialize(this.storage.getItem(i)))
            }
        }
    })
}(), function (e) {
    FX.UI = {
        showPopover: function (t) {
            var i = e('<div class="x-ui-popover"/>').appendTo("body"), a = e.extend({
                anchor: null,
                position: "topLeft",
                content: null,
                maxWidth: null,
                animation: !0,
                type: "info"
            }, t);
            a.maxWidth && i.css({"max-width": a.maxWidth}), a.type && i.addClass(a.type), a.animation && i.addClass("animation"), a.content && a.content.appendTo(i);
            var s = a.anchor, n = s.offset(), o = {"z-Index": FX.STATIC.zIndex++}, l = n.top - e("body").offset().top;
            switch (a.position) {
                case"topLeft":
                    i.addClass("top"), o.left = Math.max(n.left + s.width() / 2 - i.width() / 2 - 5, 4), o.bottom = document.body.clientHeight - l + 8;
                    break;
                case"topRight":
                    i.addClass("top"), o.right = Math.max(document.body.clientWidth - n.left - s.width() / 2 - i.width() / 2 - 5, 4), o.bottom = document.body.clientHeight - l + 8;
                    break;
                case"bottomLeft":
                    i.addClass("bottom"), o.left = Math.max(n.left + s.width() / 2 - i.width() / 2 - 5, 4), o.top = l + s.height() + 8
            }
            i.css(o), i.addClass("fadein")
        }, closePopover: function () {
            var t = e(".x-ui-popover");
            t.length > 0 && (t.remove(), t = null)
        }, shareUrl: function (t) {
            var i = e.extend({url: "", title: "", subTitle: "", hasQrcode: !0}, t),
                a = e('<div class="share-link-content"/>').append(e('<div class="url-wrapper"/>')).append(e('<a class="btn-icon" target="_blank">').attr("href", i.url).attr("title", "打开链接").append(e('<i class="icon-share-open"/>')));
            if (i.hasQrcode) {
                var s = FX.Utils.createQrcodeBtn(i.url).addClass("btn-icon");
                a.append(s)
            }
            new FX.TextEditor({
                renderEl: e(".url-wrapper", a),
                width: 388,
                enable: !1,
                height: 30,
                value: i.url
            }), new FX.Dialog({
                title: i.title,
                subTitle: i.subTitle,
                customCls: "share-link-dialog",
                width: 520,
                height: 146,
                contentWidget: {rowSize: [90], colSize: [520], items: [[a]]}
            }).show()
        }, inviteGuide: function (e) {
            var t = new FX.Dialog({
                width: 487,
                height: 188,
                title: "",
                style4Header: "white",
                customCls: "invite-guide-dialog",
                autoClose: !1,
                contentWidget: {
                    type: "inviteguidepane", msgType: e, onClose: function () {
                        t.close()
                    }
                }
            });
            t.show()
        }
    }
}(jQuery), function (e) {
    FX.Vip = {
        _getPack: function () {
            if (!FX.STATIC.VIP_PACK) {
                if (!FX.STATIC.APPID) return {};
                FX.Utils.dataAjax({
                    url: FX.Utils.getApi(FX.API.app.get_vip_pack, FX.STATIC.APPID),
                    async: !1
                }, function (t) {
                    FX.STATIC.VIP_PACK = e.extend({}, t.vipPack)
                }, function () {
                    FX.STATIC.VIP_PACK = {}
                })
            }
            return FX.STATIC.VIP_PACK
        }, clear: function () {
            FX.STATIC.VIP_PACK = null
        }, showUpgradeTip: function (e, t, i) {
            if (i = i || !1, !FX.Utils.isObjectEmpty(e)) if (FX.Utils.isWpsWebView()) this._showWpsTip(e.code, e.message || t); else if (!(i && FX.STATIC.user && FX.Cookie.get(FX.STATIC.user.username + FX.CONST.VIP_COOKIE.SERVICE_UPGRADE.SUFFIX_KEY))) {
                var a, s, n, o = null, l = null;
                if (/^71[0-9]{2}/.test(e.code)) {
                    if (a = "立即升级", s = "暂不升级", o = function () {
                            return FX.Utils.redirectTo("/profile#/vip"), !1
                        }, FX.Utils.isArray(e.bufferItems)) {
                        var r = e.bufferItems.slice(0);
                        r.length > 1 ? (l = function () {
                            FX.Utils.redirectTo("/profile#/vip")
                        }, s = "查看详情") : 1 === r.length && (s = "查看详情", l = function () {
                            switch (r[0]) {
                                case"form_data":
                                case"print":
                                case"aggregate":
                                    new FX.VipUsageDialog({usageType: r[0]}).show()
                            }
                        })
                    }
                } else /^72[0-9]{2}/.test(e.code) && (a = "我知道了", s = "");
                n = e.expireDays && e.expireDays < 8 ? (e.message || e.msg) + e.expireDays + "天后系统将会受限。" : e.message || e.msg, i && FX.STATIC.user && FX.Cookie.set(FX.STATIC.user.username + FX.CONST.VIP_COOKIE.SERVICE_UPGRADE.SUFFIX_KEY, FX.CONST.VIP_COOKIE.SERVICE_UPGRADE.VALUE, {expires: FX.CONST.VIP_COOKIE.SERVICE_UPGRADE.EXPIRES_DATE}), FX.Utils.isCorpCreator() ? FX.Msg.alert({
                    msg: n,
                    text4Ok: a,
                    text4Cancel: s,
                    onOk: o,
                    onCancel: l
                }) : (n = {
                    7101: "您使用的[当前套餐]不包含此项功能，请联系企业创建者升级套餐。",
                    7104: "聚合表数量已达上限，请联系企业创建者升级套餐后再使用该功能。",
                    7105: "你所安装的应用中聚合表数量超出当前套餐限制。请联系企业创建者升级套餐后再安装应用。",
                    7111: "成员数量超出限制。请联系创建者升级套餐以同步/邀请更多成员。",
                    7112: "您使用的[当前套餐]不包含自定义打印功能，请联系企业创建者升级套餐。",
                    7113: "自定义打印模版数量已达上限，请联系企业创建者升级套餐后再新建。",
                    7114: "您所安装的应用中自定义打印模版数量超出当前套餐限制。请联系企业创建者升级套餐后再安装应用。"
                }[e.code] || n, FX.Msg.toast({type: "warning", msg: n}))
            }
        }, _showWpsTip: function (e, t) {
            t = FX.CONST.WPS_TIP[e] || t, FX.Msg.toast({type: "error", msg: t})
        }, getExcelMFS: function () {
            return this._getPack()[FX.CONST.VIP_MODULE.EXCEL_IMPORT] || 2097152
        }, getUploadMFS: function () {
            return 20971520
        }, hasAppBridge: function () {
            return this._getPack()[FX.CONST.VIP_MODULE.APP_BRIDGE] > 0
        }, hasDataBackup: function () {
            return this._getPack()[FX.CONST.VIP_MODULE.DATA_BACKUP] > 0
        }, hasFileExport: function () {
            return this._getPack()[FX.CONST.VIP_MODULE.FILE_ZIP] > 0
        }, getPTSize: function () {
            return this._getPack()[FX.CONST.VIP_MODULE.PRINT]
        }, getVipLimit: function () {
            var e = this._getPack();
            return e && e.vipLimit || {}
        }, isDataCreateLimit: function () {
            return this.getVipLimit().data_create
        }, showDataLimitTip: function (t) {
            this.isDataCreateLimit() && new FX.Tip(e.extend({msg: FX.CONST.DATA_LIMIT_TIP.LINK, height: 45}, t))
        }
    }
}(jQuery), function (e) {
    FX.Cookie = FX.Cookie || {}, e.extend(FX.Cookie, {
        _encode: function (e) {
            return this.raw ? e : encodeURIComponent(e)
        }, _decode: function (e) {
            return this.raw ? e : decodeURIComponent(e)
        }, _stringifyCookieValue: function (e) {
            return this._encode(this.json ? JSON.stringify(e) : String(e))
        }, _parseCookieValue: function (e) {
            0 === e.indexOf('"') && (e = e.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, "\\"));
            try {
                return e = decodeURIComponent(e.replace(/\+/g, " ")), this.json ? JSON.parse(e) : e
            } catch (e) {
            }
        }, _read: function (t, i) {
            var a = this.raw ? t : this._parseCookieValue(t);
            return e.isFunction(i) ? i(a) : a
        }, set: function (t, i, a) {
            if (arguments.length > 1 && !e.isFunction(i)) {
                if ("number" == typeof(a = e.extend({
                        expires: new Date((new Date).getTime() + 1728e6),
                        domain: FX.CONFIG.COOKIE_DOMAIN
                    }, a)).expires) {
                    var s = a.expires, n = a.expires = new Date;
                    n.setMilliseconds(n.getMilliseconds() + 864e5 * s)
                }
                return document.cookie = [this._encode(t), "=", this._stringifyCookieValue(i), a.expires ? "; expires=" + a.expires.toUTCString() : "", a.path ? "; path=" + a.path : "", a.domain ? "; domain=" + a.domain : "", a.secure ? "; secure" : ""].join("")
            }
        }, get: function (e, t) {
            for (var i = e ? void 0 : {}, a = document.cookie ? document.cookie.split("; ") : [], s = 0, n = a.length; s < n; s++) {
                var o = a[s].split("="), l = this._decode(o.shift()), r = o.join("=");
                if (e === l) {
                    i = this._read(r, t);
                    break
                }
                e || void 0 === (r = this._read(r)) || (i[l] = r)
            }
            return i
        }, remove: function (t, i) {
            return this.set(t, "", e.extend({}, i, {expires: -1})), !this.set(t)
        }
    })
}(jQuery), function (e) {
    FX.Hotkeys = {
        specialKeys: {
            8: "backspace",
            9: "tab",
            13: "return",
            16: "shift",
            17: "ctrl",
            18: "alt",
            19: "pause",
            20: "capslock",
            27: "esc",
            32: "space",
            33: "pageup",
            34: "pagedown",
            35: "end",
            36: "home",
            37: "left",
            38: "up",
            39: "right",
            40: "down",
            45: "insert",
            46: "del",
            96: "0",
            97: "1",
            98: "2",
            99: "3",
            100: "4",
            101: "5",
            102: "6",
            103: "7",
            104: "8",
            105: "9",
            106: "*",
            107: "+",
            109: "-",
            110: ".",
            111: "/",
            112: "f1",
            113: "f2",
            114: "f3",
            115: "f4",
            116: "f5",
            117: "f6",
            118: "f7",
            119: "f8",
            120: "f9",
            121: "f10",
            122: "f11",
            123: "f12",
            144: "numlock",
            145: "scroll",
            188: ",",
            190: ".",
            191: "/",
            224: "meta"
        },
        shiftNums: {
            "`": "~",
            1: "!",
            2: "@",
            3: "#",
            4: "$",
            5: "%",
            6: "^",
            7: "&",
            8: "*",
            9: "(",
            0: ")",
            "-": "_",
            "=": "+",
            ";": ": ",
            "'": '"',
            ",": "<",
            ".": ">",
            "/": "?",
            "\\": "|"
        },
        keyHandler: function (t) {
            var i = t.handler, a = (t.namespace || "").toLowerCase().split(" ");
            (1 !== (a = e.map(a, function (e) {
                return e.split(".")
            })).length || "" !== a[0] && "autocomplete" !== a[0].substring(0, 12) && "accordion" !== a[0].substring(0, 9) && "tabs" !== a[0].substring(0, 4) && "menu" !== a[0].substring(0, 4)) && (t.handler = function (t) {
                if (this === t.target || !/textarea|select/i.test(t.target.nodeName) && "text" !== t.target.type && "true" != e(t.target).prop("contenteditable")) {
                    var s = "keypress" !== t.type && FX.Hotkeys.specialKeys[t.which],
                        n = String.fromCharCode(t.which).toLowerCase(), o = "", l = {};
                    t.altKey && "alt" !== s && (o += "alt_"), t.ctrlKey && "ctrl" !== s && (o += "ctrl_"), t.metaKey && !t.ctrlKey && "meta" !== s && (o += "meta_"), t.shiftKey && "shift" !== s && (o += "shift_"), s ? l[o + s] = !0 : (l[o + n] = !0, l[o + FX.Hotkeys.shiftNums[n]] = !0, "shift_" === o && (l[FX.Hotkeys.shiftNums[n]] = !0));
                    for (var r = 0, c = a.length; r < c; r++) if (l[a[r]]) return i.apply(this, arguments)
                }
            })
        }
    }, FX.Utils.forEach(["keydown", "keyup", "keypress"], function (t, i) {
        e.event.special[i] = {add: FX.Hotkeys.keyHandler}
    })
}(jQuery), $.extend(Array.prototype, {
    remove: function (e) {
        var t = this.indexOf(e);
        return -1 != t && this.splice(t, 1), this
    }, unique: function () {
        for (var e = {}, t = this.length, i = [], a = 0; a < t; a++) {
            var s = this[a];
            e.hasOwnProperty(s) || (e[s] = 1, i.push(s))
        }
        return i
    }
}), $.extend(Date.prototype, {
    getMonthDays: function (e) {
        var t = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], i = this.getFullYear();
        return void 0 === e && (e = this.getMonth()), 0 != i % 4 || 0 == i % 100 && 0 != i % 400 || 1 !== e ? t[e] : 29
    }
}), Date._DN = [FX.i18nText("Sunday"), FX.i18nText("Monday"), FX.i18nText("Tuesday"), FX.i18nText("Wednesday"), FX.i18nText("Thursday"), FX.i18nText("Friday"), FX.i18nText("Saturday")], Date._SDN = [FX.i18nText("Short-Sun"), FX.i18nText("Short-Mon"), FX.i18nText("Short-Tue"), FX.i18nText("Short-Wed"), FX.i18nText("Short-Thu"), FX.i18nText("Short-Fri"), FX.i18nText("Short-Sat")], Date._MN = [FX.i18nText("January"), FX.i18nText("February"), FX.i18nText("March"), FX.i18nText("April"), FX.i18nText("May"), FX.i18nText("June"), FX.i18nText("July"), FX.i18nText("August"), FX.i18nText("September"), FX.i18nText("October"), FX.i18nText("November"), FX.i18nText("December")], Date._SMN = [FX.i18nText("Short-Jan"), FX.i18nText("Short-Feb"), FX.i18nText("Short-Mar"), FX.i18nText("Short-Apr"), FX.i18nText("Short-May"), FX.i18nText("Short-Jun"), FX.i18nText("Short-Jul"), FX.i18nText("Short-Aug"), FX.i18nText("Short-Sep"), FX.i18nText("Short-Oct"), FX.i18nText("Short-Nov"), FX.i18nText("Short-Dec")], $.extend($.Event.prototype, {
    stopEvent: function () {
        this.stopPropagation(), this.preventDefault()
    }
}), function (e) {
    FX.Container = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Container.superclass._defaultConfig.apply(), {
                baseCls: "fui_container",
                resultWidgets: {}
            })
        }, _addWidget: function (t) {
            var i = this.options, a = FX.createWidget(t);
            i.resultWidgets[a.options.widgetName] = a;
            var s = a.options.resultWidgets;
            return s && e.extend(i.resultWidgets, s), a
        }
    })
}(jQuery), function (e) {
    FX.List = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.List.superclass._defaultConfig.apply(), {
                baseCls: "x-list",
                items: [],
                value: null,
                onItemCreate: null,
                onItemSelect: null
            })
        }, _init: function () {
            FX.List.superclass._init.apply(this, arguments), this._createList(), this._bindEvent()
        }, _createList: function () {
            var t = this, i = this.options;
            this.$list = e('<div class="x-list-pane"/>').appendTo(this.element), FX.Utils.forEach(i.items, function (e, i) {
                t.$list.append(t._createItem(i))
            })
        }, _createItem: function (t) {
            var i = this.options;
            FX.Utils.applyFunc(this, i.onItemCreate, [t], !1);
            var a = "x-list-item";
            return t.selected && (a += " select"), e('<div class="' + a + '"></div>').text(t.text).attr({title: t.text}).data({item: t})
        }, _bindEvent: function () {
            var t = this, i = this.options;
            this.$list.on("click", ".x-list-item", function (a) {
                var s = e(a.currentTarget).data("item");
                FX.Utils.applyFunc(t, i.onItemSelect, [s], !1)
            })
        }, reload: function (e) {
            this.$list.empty(), FX.Utils.forEach(e, function (e, t) {
                self.$list.append(self._createItem(t))
            })
        }
    }), e.shortcut("list", FX.List)
}(jQuery), function (e) {
    FX.TextEditor = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.TextEditor.superclass._defaultConfig.apply(), {
                baseCls: "fui_text",
                inputCls: "x-input",
                width: 240,
                height: 30,
                allowBlank: !0,
                noRepeat: !1,
                onValidateSuccess: null,
                onValidateFail: null,
                onAfterValidate: null,
                onBeforeEdit: null,
                onAfterEdit: null,
                onStopEdit: null
            })
        }, _init: function () {
            FX.TextEditor.superclass._init.apply(this, arguments);
            var e = this.options, t = this;
            this.editComp = this._createEditComp(), this.editComp.addClass(e.inputCls).appendTo(this.element), e.waterMark && this.editComp.attr("placeholder", e.waterMark), this.editComp.focus(function (i) {
                t.$err && t.$err.hide(), t.isEnabled() && t._isScanEditable() && (t.editComp.addClass(e.inputCls + "-focus"), FX.Utils.applyFunc(t, e.onBeforeEdit, [i], !1))
            }).blur(function (i) {
                if (t.isEnabled() && t._isScanEditable()) {
                    t.editComp.removeClass(e.inputCls + "-focus");
                    var a = t.checkValidate();
                    a && (t.cacheValue = t.getValue(), FX.Utils.applyFunc(t, e.onStopEdit, [a, i], !1))
                }
            }).keyup(function (i) {
                t.isEnabled() && t._isScanEditable() && FX.Utils.applyFunc(t, e.onAfterEdit, [i], !1)
            })
        }, _createEditComp: function () {
            return e("<input type='text'/>")
        }, checkValidate: function () {
            var e = this.options, t = this.editComp.val().trim(), i = !0;
            if (FX.Utils.isEmpty(t)) i = e.allowBlank; else if (!FX.Utils.isEmpty(e.regex)) {
                try {
                    i = new RegExp(e.regex).test(t)
                } catch (e) {
                    i = !1
                }
                i || this.setInvalidateType("regex")
            }
            return i ? !1 === FX.Utils.applyFunc(this, e.onValidateSuccess, [t], !1) && this.setState(FX.States.NORMAL) : !1 === FX.Utils.applyFunc(this, e.onValidateFail, [t], !1) && this.setState(FX.States.ERROR), FX.Utils.applyFunc(this, e.onAfterValidate, [t, i], !1), i
        }, showErrorMsg: function (t) {
            FX.Utils.isEmpty(t) || (this.$err || (this.$err = e('<span class="invalid-info"/>').appendTo(this.element)), this.$err.text(t).show())
        }, select: function () {
            this.editComp && (this.editComp.select(), this.editComp.focus())
        }, _isScanEditable: function () {
            var e = this.options;
            return !e.scan || e.scan.editable
        }, setEnable: function (e) {
            FX.TextEditor.superclass.setEnable.apply(this, [e]), e && this._isScanEditable() ? this.editComp.removeAttr("readOnly") : this.editComp.attr("readOnly", "readOnly")
        }, setText: function (e) {
            this.setValue(e)
        }, setValue: function (e) {
            this.editComp.val(e), this.cacheValue = e
        }, getText: function () {
            return this.getValue()
        }, getValue: function () {
            return this.editComp.val().trim()
        }, getCacheValue: function () {
            return this.cacheValue
        }, rebuild: function () {
            FX.TextEditor.superclass.rebuild.apply(this, arguments), this.cacheValue = ""
        }, reset: function () {
            this.setValue("")
        }, setState: function (e) {
            var t = this.options, i = t.inputCls + "-error " + t.inputCls + "-success " + t.inputCls + "-warning";
            switch (t.state = e, e) {
                case FX.States.SUCCESS:
                    this.editComp.removeClass(i).addClass(t.inputCls + "-success");
                    break;
                case FX.States.ERROR:
                    this.editComp.removeClass(i).addClass(t.inputCls + "-error");
                    break;
                case FX.States.WARNING:
                    this.editComp.removeClass(i).addClass(t.inputCls + "-warning");
                    break;
                default:
                    this.editComp.removeClass(i)
            }
        }, getState: function () {
            return this.options.state ? 0 : this.options.state
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.TextEditor.superclass.getOptions.apply(this, arguments), {
                regex: t.regex,
                noRepeat: t.noRepeat,
                scan: t.scan
            })
        }, getNullValue: function () {
            return ""
        }
    }), e.shortcut("text", FX.TextEditor)
}(jQuery), function (e) {
    FX.TextArea = FX.extend(FX.TextEditor, {
        _defaultConfig: function () {
            return e.extend(FX.TextArea.superclass._defaultConfig.apply(), {
                baseCls: "fui_textarea",
                inputCls: "x-textarea",
                width: 420,
                height: 140
            })
        }, _createEditComp: function () {
            return e("<textarea/>")
        }
    }), e.shortcut("textarea", FX.TextArea)
}(jQuery), function (e) {
    FX.Number = FX.extend(FX.TextEditor, {
        _defaultConfig: function () {
            return e.extend(FX.Number.superclass._defaultConfig.apply(), {allowDecimals: !1, allowNegative: !0})
        }, _init: function () {
            FX.Number.superclass._init.apply(this, arguments);
            var e = this.options, t = "[\\d]{0,}";
            e.allowDecimals && (t = "[\\d]{0,}[\\.]?[\\d]{0,}"), e.allowNegative && (t = "[-]?" + t), e.regex = "^" + t + "$"
        }, _createEditComp: function () {
            return e("<input/>")
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Number.superclass.getOptions.apply(this, arguments), {
                allowDecimals: t.allowDecimals,
                allowNegative: t.allowNegative
            })
        }, setValue: function (e) {
            e = FX.Utils.fixDecimalPrecision(e), this.editComp.val(e), this.cacheValue = e
        }, getValue: function () {
            var e = this.editComp.val();
            return FX.Utils.str2num(e)
        }, getCacheValue: function () {
            var e = this.cacheValue;
            return FX.Utils.str2num(e)
        }, getNullValue: function () {
            return null
        }, getText: function () {
            return this.editComp.val()
        }
    }), e.shortcut("number", FX.Number)
}(jQuery), function (e) {
    FX.Password = FX.extend(FX.TextEditor, {
        _createEditComp: function () {
            return e('<input type="password"/>')
        }
    }), e.shortcut("password", FX.Password)
}(jQuery), function (e) {
    FX.Trigger = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Trigger.superclass._defaultConfig.apply(), {
                baseCls: "fui_trigger",
                width: 240,
                height: 30,
                btnWidth: 30,
                waterMark: null,
                onElementCreate: null,
                triggerIcon: "",
                edge: {width: 240, height: 200}
            })
        }, _init: function () {
            FX.Trigger.superclass._init.apply(this, arguments);
            var e = this.options;
            !1 === FX.Utils.applyFunc(this, e.onElementCreate, [], !1) && (this.editComp = this._createEditComp(), e.waterMark && this.editComp.attr("placeholder", e.waterMark), this.triggerBtn = this._createTriggerBtn()), this._bindEvts()
        }, _createEditComp: function () {
            return e('<input class="fui_trigger-input" onfocus="this.blur();"/>').attr("readOnly", "readOnly").attr("UNSELECTABLE", "on").appendTo(this.element)
        }, _createTriggerBtn: function () {
            return e('<i class="fui_trigger-btn"/>').addClass(this.options.triggerIcon).appendTo(this.element)
        }, _bindEvts: function () {
            var e = this;
            this.element.unbind("click.trigger"), this.element.bind("click.trigger", function (t) {
                e._onTriggerClick()
            })
        }, _onTriggerClick: function (e) {
        }, _getTriggerView: function () {
            var t = e(".x-dropdown-wrapper");
            return 0 === t.length && (t = e('<div class="x-dropdown-wrapper"/>').appendTo("body")), t
        }, _calTriggerViewPos: function () {
            var t = {"z-Index": FX.STATIC.zIndex++}, i = this.element.offset(), a = this.options.edge,
                s = document.body.clientWidth - i.left, n = i.top - e("body").offset().top;
            return s < a.width ? (t.right = s - this.element.outerWidth(), t.left = "auto") : (t.right = "auto", t.left = i.left), document.body.clientHeight + document.body.scrollTop - n - this.element.outerHeight() < a.height ? (t.top = "auto", t.bottom = document.body.clientHeight - n) : (t.top = n + this.element.outerHeight(), t.bottom = "auto"), t
        }, setValue: function (e) {
            this.setText(e)
        }, setText: function (e) {
            this.editComp.val(e)
        }, getValue: function () {
            return this.getText()
        }, getText: function () {
            return this.editComp.val()
        }, doResize: function (e) {
            FX.Trigger.superclass.doResize.apply(this, arguments);
            var t = this.options.height;
            this.element.css({"line-height": t - 2 + "px"})
        }
    })
}(jQuery), function (e) {
    FX.DateTime = FX.extend(FX.Trigger, {
        _defaultConfig: function () {
            return e.extend(FX.DateTime.superclass._defaultConfig.apply(), {
                baseCls: "fui_datetime",
                triggerIcon: "icon-widget-datetime",
                startDate: null,
                endDate: null,
                allowBlank: !0,
                format: "yyyy-MM-dd",
                onAfterEdit: null,
                defaultPickDate: null,
                edge: {width: 240, height: 315}
            })
        }, _init: function () {
            FX.DateTime.superclass._init.apply(this, arguments);
            var e = this.options;
            this.viewMode = this._initViewMode(), this.std = this._initStartDate(e.startDate, this.viewMode), this.edd = this._initEndDate(e.endDate, this.viewMode)
        }, _onTriggerClick: function () {
            if (this.isEnabled()) {
                var t = this;
                this._showDatePicker(), e(document).bind("mousedown.datepicker", function (i) {
                    var a = i.target;
                    0 === e(a).closest(t.datepicker.element).length && t._hideDatePicker()
                })
            }
        }, _initViewMode: function () {
            var e = this.options, t = 1;
            return e.format.match(/[YyMDd]/) ? e.format.match(/[Dd]/) ? e.format.match(/[Hhms]/) && (t = 3) : t = 0 : t = e.format.match(/s/) ? 2 : 4, t
        }, _initStartDate: function (e, t) {
            if (!e) return null;
            var i = new Date(e);
            switch (t) {
                case 0:
                    return new Date(i.getFullYear(), i.getMonth(), 1, 0, 0, 0);
                case 1:
                    return new Date(i.getFullYear(), i.getMonth(), i.getDate(), 0, 0, 0);
                case 2:
                    var a = new Date;
                    return a.setHours(0), a.setMinutes(0), a.setSeconds(0), a;
                case 3:
                    return new Date(i.getFullYear(), i.getMonth(), i.getDate(), 0, 0, 0);
                default:
                    return i
            }
        }, _initEndDate: function (e, t) {
            if (!e) return null;
            var i = new Date(e);
            switch (t) {
                case 0:
                    return new Date(i.getFullYear(), i.getMonth(), i.getMonthDays(), 23, 59, 59);
                case 1:
                    return new Date(i.getFullYear(), i.getMonth(), i.getDate(), 23, 59, 59);
                case 2:
                    var a = new Date;
                    return a.setHours(23), a.setMinutes(59), a.setSeconds(59), a;
                case 3:
                    return new Date(i.getFullYear(), i.getMonth(), i.getDate(), 23, 59, 59);
                default:
                    return i
            }
        }, _showDatePicker: function () {
            var e = this, t = this.options;
            if (!this.datepicker) {
                var i = null;
                i = this.value ? new Date(this.value) : t.defaultPickDate ? new Date(t.defaultPickDate) : new Date;
                var a = {
                    viewMode: this.viewMode,
                    startDate: this.std,
                    endDate: this.edd,
                    customCls: "x-dropdown",
                    date: i,
                    onDateUpdate: function () {
                        var i = this.getValue();
                        i ? e.setValue(i.getTime()) : e.setValue(null), FX.Utils.applyFunc(e, t.onAfterEdit, arguments, !1)
                    },
                    onClear: function () {
                        e._hideDatePicker()
                    },
                    onOk: function () {
                        e._hideDatePicker()
                    },
                    onClose: function () {
                        e._hideDatePicker()
                    },
                    onToday: function () {
                        e._hideDatePicker()
                    }
                };
                this.datepicker = new FX.DatePicker(a)
            }
            this.datepicker.element.appendTo("body").css(this._calTriggerViewPos()).show()
        }, _hideDatePicker: function () {
            this.datepicker && (e(document).unbind("mousedown.datepicker"), this.datepicker.element.detach(), FX.Utils.applyFunc(this, this.options.onStopEdit, [], !1))
        }, checkValidate: function () {
            var e = this.options;
            return !(!e.allowBlank && FX.Utils.isEmpty(this.getValue())) && (!(e.startDate && this.value < e.startDate) && !(e.endDate && this.value > e.endDate))
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.DateTime.superclass.getOptions.apply(this, arguments), {format: t.format})
        }, rebuild: function () {
            FX.DateTime.superclass.rebuild.apply(this, arguments), this.datepicker && (this.datepicker.element.remove(), this.datepicker = null)
        }, setValue: function (e) {
            var t = this.options;
            if (FX.Utils.isNull(e)) return this.value = null, void this.setText(null);
            var i = null;
            i = "today" === e ? new Date : new Date(e), 0 !== this.viewMode && 1 !== this.viewMode || i.setHours(0, 0, 0), i.setMilliseconds(0);
            var a = i.getTime();
            if (isNaN(a)) return this.value = null, void this.setText(null);
            this.value = a, this.setText(FX.Utils.date2Str(new Date(this.value), t.format))
        }, setText: function (e) {
            this.editComp.val(e)
        }, getValue: function () {
            return this.value
        }, getText: function () {
            return this.editComp.val()
        }
    }), e.shortcut("datetime", FX.DateTime)
}(jQuery), function (e) {
    FX.DatePicker = FX.extend(FX.Widget, {
        CONSTS: {
            VIEWMODE: {YM: 0, YMD: 1, HMS: 2, YMDHMS: 3, HM: 4},
            MINYEAR: 1900,
            MAXYEAR: 2999,
            NAV: {
                prevm: 2,
                nextm: 3,
                title: 4,
                clear: 5,
                today: 6,
                dok: 7,
                prevy: 8,
                nexty: 9,
                cancel: 10,
                mok: 11,
                plus: 12,
                minus: 13,
                current: 15,
                day: 100,
                month: 200,
                year: 300
            }
        },
        _TT: {CALENDAR: "日历", CLEAR: "清空", TODAY: "今天", OK: "确定", CURRENT: "当前", TIME: "时间"},
        _defaultConfig: function () {
            return e.extend(FX.DatePicker.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_datepicker",
                viewMode: 1,
                endDate: null,
                startDate: null,
                date: null,
                onDateUpdate: null,
                onClear: null,
                onOk: null,
                onClose: null,
                onToday: null
            })
        },
        _init: function () {
            FX.DatePicker.superclass._init.apply(this, arguments), this.cache = {
                showYear: null,
                showMonth: null
            }, this._initTables(), this._bindEvts()
        },
        _initTables: function () {
            var t = this.options;
            switch (this.$datetable = this._createDatePicker(), this._loadDateData(this.$datetable, new Date(this.options.date)), this.$monthtable = this._createMonthPicker(), this.$timetable = this._createTimePicker(), t.viewMode) {
                case this.CONSTS.VIEWMODE.YM:
                    this._loadMonthData(this.$monthtable, new Date(this.options.date)), this.$monthtable.appendTo(this.element).show();
                    break;
                case this.CONSTS.VIEWMODE.HMS:
                    this._loadTimeData(this.$timetable, this.options.date), this._addTimeOptPane(this.$timetable), this.$timetable.appendTo(this.element).show();
                    break;
                case this.CONSTS.VIEWMODE.HM:
                    this.$timetable.remove(), this.$timetable = this._createTimePicker({s: !1}), this._loadTimeData(this.$timetable, this.options.date), this.$timetable.appendTo(this.element).show();
                    break;
                case this.CONSTS.VIEWMODE.YMD:
                    this.$datetable.appendTo(this.element).show(), this.$monthtable.hide().appendTo(this.element);
                    break;
                default:
                    this.$datetable.appendTo(this.element).show(), this.$monthtable.hide().appendTo(this.element);
                    var i = e("<tr/>").prependTo(this.$datetable.find("tfoot"));
                    this._loadTimeData(this.$timetable, this.options.date), this.$timetable.show().appendTo(e('<td colspan="7"/>').appendTo(i))
            }
        },
        _createTimePicker: function (t) {
            t = t || {};
            var i = e('<table cellspacing = "0" cellpadding = "0" class="tt"/>'), a = e("<tbody>").appendTo(i),
                s = this, n = this.options, o = this.CONSTS.NAV,
                l = e("<td/>").append(e('<i class="icon-angleup"/>')).data("nav", o.plus),
                r = e("<td/>").append(e('<i class="icon-angledown"/>')).data("nav", o.minus),
                c = e("<tr/>").append(e('<td rowspan="2"/>').text(this._TT.TIME));
            return !1 !== t.h && (i.$h = e("<input/>").data("time", "h").keyup(function () {
                var e = this.value, t = parseInt(e, 10);
                t < 24 && t >= 0 && (n.date.setHours(t), FX.Utils.applyFunc(s, n.onDateUpdate, arguments))
            }).focus(function () {
                i.focus = e(this)
            }), i.focus = i.$h, c.append(e('<td rowspan="2"/>').append(i.$h))), !1 !== t.m && (i.$m = e("<input/>").data("time", "m").keyup(function () {
                var e = this.value, t = parseInt(e, 10);
                t < 60 && t >= 0 && (n.date.setMinutes(t), FX.Utils.applyFunc(s, n.onDateUpdate, arguments))
            }).focus(function () {
                i.focus = e(this)
            }), i.focus = i.$m, c.append(e('<td class="common" rowspan="2"/>').text(":")).append(e('<td rowspan="2"/>').append(i.$m))), !1 !== t.s && (i.$s = e("<input/>").data("time", "s").keyup(function () {
                var e = this.value, t = parseInt(e, 10);
                t < 60 && t >= 0 && (n.date.setSeconds(t), FX.Utils.applyFunc(s, n.onDateUpdate, arguments))
            }).focus(function () {
                i.focus = e(this)
            }), i.focus = i.$s, c.append(e('<td class="common" rowspan="2"/>').text(":")).append(e('<td rowspan="2"/>').append(i.$s))), c.append(l).appendTo(a), e("<tr/>").append(r).appendTo(a), i
        },
        _addTimeOptPane: function (t) {
            var i = this.CONSTS.NAV, a = e("<tfoot/>"), s = e("<tr/>").appendTo(a);
            this._createCell(s, this._TT.CLEAR, 2, i.clear, "clear"), this._createCell(s, this._TT.CURRENT, 3, i.current, "current"), this._createCell(s, this._TT.OK, 2, i.dok, "ok"), a.appendTo(t)
        },
        _createDatePicker: function () {
            var t = e('<table cellspacing = "2px" cellpadding = "0" class="dt"/>'), i = this.CONSTS.NAV,
                a = e("<thead/>").appendTo(t);
            l = e('<tr class = "mainhead"/>'), t.$prevm = this._createCell(l, '<i class="icon-angleleft"/>', 1, i.prevm, "prevm"), t.$title = e('<td class="title" colspan="5"/>').data("nav", i.title).appendTo(l), t.$nextm = this._createCell(l, '<i class="icon-angleright"/>', 1, i.nextm, "nextm"), l.appendTo(a), l = e("<tr/>");
            for (s = 7; s > 0; --s) e("<td/>").appendTo(l);
            for (var s = 0; s < 7; ++s) {
                var n = l.children().eq(s);
                n.addClass("day name").text(Date._SDN[s]), -1 != [0, 6].indexOf(s) && n.addClass("weekend")
            }
            l.appendTo(a);
            var o = e('<tbody onselectstart="return false"/>').appendTo(t);
            for (s = 6; s > 0; s--) for (var l = e("<tr/>").appendTo(o), r = 0; r < 7; r++) e("<td/>").appendTo(l);
            var c = e("<tfoot/>").appendTo(t);
            this._createCell(e("<tr/>").appendTo(c), "", 7, null, "split");
            l = e("<tr/>");
            return this._createCell(l, this._TT.CLEAR, 2, i.clear, "clear"), this._createCell(l, this._TT.TODAY, 3, i.today, "today"), this._createCell(l, this._TT.OK, 2, i.dok, "ok"), l.appendTo(c), t
        },
        _createMonthPicker: function () {
            for (var t = e('<table cellspacing = "2px" cellpadding = "0" class="mt"/>'), i = this.CONSTS.NAV, a = e("<tbody/>").appendTo(t), s = e("<tr/>").appendTo(a), n = 0; n < 2; n++) e('<td class="month"/>').appendTo(s);
            this._createCell(s, '<i class="icon-angleleft"/>', 1, i.prevy, " prevy"), this._createCell(s, '<i class="icon-angleright"/>', 1, i.nexty, " nexty");
            for (var o = 0; o < 5; o++) s = e("<tr/>").appendTo(a), e('<td class="month"/><td class="month"/><td class="year"/><td class="year"/>').appendTo(s);
            var l = e("<tfoot/>").appendTo(t);
            return s = e("<tr/>").appendTo(l), this._createCell(s, this._TT.OK, 4, i.mok, "ok"), t
        },
        _toPrevMonth: function () {
            var e = this.options.startDate, t = this.options.date, i = this.cache.showMonth, a = this.cache.showYear;
            e ? a > e.getFullYear() ? i > 0 ? this._setMonth(i - 1) : (t.setFullYear(a - 1), this._setMonth(11)) : a == e.getFullYear() && i > e.getMonth() && i > 0 && (this._setMonth(i - 1), t < e && (t = new Date(e))) : i > 0 ? this._setMonth(i - 1) : (t.setFullYear(a - 1), this._setMonth(11))
        },
        _toNextMonth: function () {
            var e = this.options.endDate, t = this.options.date, i = this.cache.showMonth, a = this.cache.showYear;
            e ? a < e.getFullYear() ? i < 11 ? this._setMonth(i + 1) : (t.setFullYear(a + 1), this._setMonth(0)) : a == e.getFullYear() && i < e.getMonth() && (this._setMonth(i + 1), t > e && (t = new Date(e))) : i < 11 ? this._setMonth(i + 1) : (t.setFullYear(a + 1), this._setMonth(0))
        },
        _toPrevDecade: function () {
            var e, t, i = this.options.startDate, a = this.options.date, s = a.getFullYear() - 10, n = a.getMonth();
            i && s == (t = i.getFullYear()) && (e = i.getMonth()), (!t || t < this.CONSTS.MINYEAR) && (t = this.CONSTS.MINYEAR), s < t ? (a.setFullYear(t), n < e && a.setMonth(e)) : a.setFullYear(s)
        },
        _toNextDecade: function () {
            var e, t, i = this.options.endDate, a = this.options.date, s = a.getFullYear() + 10, n = a.getMonth();
            i && s == (t = i.getFullYear()) && (e = i.getMonth()), (!t || t > this.CONSTS.MAXYEAR) && (t = this.CONSTS.MAXYEAR), s > t ? (a.setFullYear(t), n < e && a.setMonth(e)) : a.setFullYear(s)
        },
        _setMonth: function (e) {
            var t = this.options.date, i = t.getDate(), a = this.options.endDate, s = this.options.startDate,
                n = t.getMonthDays(e);
            i > n && t.setDate(n), t.setMonth(e), a && t > a && t.setDate(a.getDate()), s && t < s && t.setDate(s.getDate())
        },
        _loadDateData: function (e, t) {
            if (t) {
                var i = t.getFullYear(), a = t.getMonth(), s = t.getDate(), n = new Date, o = n.getFullYear(),
                    l = n.getMonth(), r = n.getDate();
                this.cache.showYear = i, this.cache.showMonth = a;
                var c = this.options.startDate, d = this.options.endDate;
                e.$title.text(Date._MN[a] + ", " + i);
                var u = new Date(t);
                u.setDate(u.getMonthDays() + 1), d && u > d || u.getFullYear() > this.CONSTS.MAXYEAR ? e.$nextm.addClass("disabled").removeClass("hover").data("disabled", !0) : e.$nextm.removeClass("disabled").data("disabled", !1);
                var h = new Date(t);
                h.setDate(0), c && h < c || h.getFullYear() < this.CONSTS.MINYEAR ? e.$prevm.addClass("disabled").removeClass("hover").data("disabled", !0) : e.$prevm.removeClass("disabled").data("disabled", !1), t.setDate(1);
                var p = t.getDay() % 7;
                t.setDate(0 - p), t.setDate(t.getDate() + 1);
                for (var f = e.find("tbody").children().eq(0), m = 0; m < 6 && f.length; m++) {
                    for (var g, v = f.children(), F = 0; F < 7; ++F, t.setDate(g + 1)) {
                        var b = v.eq(F);
                        if (b.removeClass().data("nav", this.CONSTS.NAV.day), !b.length) break;
                        g = t.getDate(), b.text(g);
                        var _ = t.getMonth() == a;
                        if (_) {
                            var y = !1;
                            if (null != c && c > t || null != d && d < t ? (b.addClass("day disabled"), y = !0) : b.addClass("day"), b.data("disabled", y), !y) {
                                _ && g == s && (this.cache.selectedDate && this.cache.selectedDate.removeClass("selected"), b.addClass("selected"), this.cache.selectedDate = b, this.cache.showDay = g), t.getFullYear() == o && t.getMonth() == l && g == r && b.addClass("today");
                                var w = t.getDay();
                                -1 != [0, 6].indexOf(w) && b.addClass("weekend")
                            }
                        } else b.addClass("oday").data("disabled", !0)
                    }
                    f = f.next()
                }
            }
        },
        _loadMonthData: function (t, i) {
            if (i) {
                var a = i.getFullYear(), s = i.getMonth(), n = e(t).data("midYear");
                n ? a > n + 5 ? n += 10 : a < n - 4 && (n -= 10) : n = a, e(t).data("midYear", n);
                var o, l, r, c, d = [n - 4, n - 3, n - 2, n - 1, n, n + 1, n + 2, n + 3, n + 4, n + 5],
                    u = e("td.year", t), h = e("td.month", t), p = this.options, f = p.endDate, m = p.startDate;
                f && f && a == (o = f.getFullYear()) && (l = f.getMonth()), (!o || o > this.CONSTS.MAXYEAR) && (o = this.CONSTS.MAXYEAR), m && m && a == (r = m.getFullYear()) && (c = m.getMonth()), (!r || r < this.CONSTS.MINYEAR) && (r = this.CONSTS.MINYEAR);
                for (var g = 0; g < 12; g++) {
                    var v = h.eq(g).text(Date._MN[g]).data("nav", this.CONSTS.NAV.month).data("month", g);
                    if (g == s && (this.cache.selectedMonth && this.cache.selectedMonth.removeClass("selected"), v.addClass("selected"), this.cache.selectedMonth = v), !FX.Utils.isEmpty(c) && g < c || !FX.Utils.isEmpty(l) && g > l ? v.addClass("disabled").data("disabled", !0) : v.removeClass("disabled").data("disabled", !1), g < 10) {
                        var F = u.eq(g).text(d[g]).data("nav", this.CONSTS.NAV.year);
                        d[g] == a && (this.cache.selectedYear && this.cache.selectedYear.removeClass("selected"), F.addClass("selected"), this.cache.selectedYear = F), !FX.Utils.isEmpty(r) && d[g] < r || !FX.Utils.isEmpty(o) && d[g] > o ? F.addClass("disabled").data("disabled", !0) : F.removeClass("disabled").data("disabled", !1)
                    }
                }
                var b = e("td.prevy", t).removeClass("disabled").data("disabled", !1);
                d[0] <= r && b.addClass("disabled").data("disabled", !0).removeClass("hover");
                var _ = e("td.nexty", t).removeClass("disabled").data("disabled", !1);
                d[9] >= o && _.addClass("disabled").data("disabled", !0).removeClass("hover")
            }
        },
        _loadTimeData: function (e, t) {
            if (t) {
                var i = t.getHours() + "", a = t.getMinutes() + "", s = t.getSeconds() + "";
                e.$h && e.$h.val(FX.Utils.leftPad(i, 2, "0")), e.$m && e.$m.val(FX.Utils.leftPad(a, 2, "0")), e.$s && e.$s.val(FX.Utils.leftPad(s, 2, "0"))
            }
        },
        _doTimeInc: function (e, t) {
            var i = t.data("time"), a = this.options;
            if ("h" === i) {
                s = (a.date.getHours() + 1) % 24;
                a.date.setHours(s), e.$h.val(FX.Utils.leftPad(s + "", 2, "0"))
            } else if ("m" === i) {
                s = (a.date.getMinutes() + 1) % 60;
                a.date.setMinutes(s), e.$m.val(FX.Utils.leftPad(s + "", 2, "0"))
            } else {
                var s = (a.date.getSeconds() + 1) % 60;
                a.date.setSeconds(s), e.$s.val(FX.Utils.leftPad(s + "", 2, "0"))
            }
            t.select(), FX.Utils.applyFunc(this, a.onDateUpdate, arguments, !1)
        },
        _doTimeDec: function (e, t) {
            var i = t.data("time"), a = this.options;
            if ("h" === i) {
                s = (a.date.getHours() + 23) % 24;
                a.date.setHours(s), e.$h.val(FX.Utils.leftPad(s + "", 2, "0"))
            } else if ("m" === i) {
                s = (a.date.getMinutes() + 59) % 60;
                a.date.setMinutes(s), e.$m.val(FX.Utils.leftPad(s + "", 2, "0"))
            } else {
                var s = (a.date.getSeconds() + 59) % 60;
                a.date.setSeconds(s), e.$s.val(FX.Utils.leftPad(s + "", 2, "0"))
            }
            t.select(), FX.Utils.applyFunc(this, a.onDateUpdate, arguments, !1)
        },
        _bindEvts: function () {
            var t = this, i = this.options, a = this.CONSTS.NAV, s = this.$monthtable, n = this.$datetable,
                o = this.$timetable, l = function (l) {
                    var r = l.target, c = e(r).closest("td"), d = l.type, u = c.data("nav");
                    if (!c.data("disabled") && 0 !== c.length && u) if (t.options.date || (t.options.date = new Date), "mouseover" === d) c.addClass("hover"); else if ("mouseup" === d) switch (c.removeClass("hover"), u) {
                        case a.prevm:
                            t._toPrevMonth(), t._loadDateData(n, new Date(t.options.date)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.nextm:
                            t._toNextMonth(), t._loadDateData(n, new Date(t.options.date)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.title:
                            t._loadMonthData(s, new Date(t.cache.showYear, t.cache.showMonth)), s.css({
                                position: "absolute",
                                top: 0,
                                "z-index": FX.STATIC.zIndex++
                            }).show("fast");
                            break;
                        case a.clear:
                            t.options.date = null, t.cache.selectedDate && t.cache.selectedDate.removeClass("selected"), FX.Utils.applyFunc(t, i.onDateUpdate, arguments), FX.Utils.applyFunc(t, i.onClear, arguments);
                            break;
                        case a.current:
                            t.options.date = new Date, FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.today:
                            var h = new Date;
                            if (t.options.startDate && h < t.options.startDate || t.options.endDate && h > t.options.endDate) return;
                            t.options.date = h, t.cache.selectedDate && t.cache.selectedDate.removeClass("selected"), t.cache.selectedDate = t.$datetable.find("td.today").addClass("selected"), FX.Utils.applyFunc(t, i.onDateUpdate, arguments), FX.Utils.applyFunc(t, i.onToday, arguments);
                            break;
                        case a.dok:
                            FX.Utils.applyFunc(t, i.onDateUpdate, arguments), FX.Utils.applyFunc(t, i.onOk, arguments);
                            break;
                        case a.prevy:
                            t._toPrevDecade(), t._loadMonthData(s, new Date(t.options.date)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.nexty:
                            t._toNextDecade(), t._loadMonthData(s, new Date(t.options.date)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.mok:
                            t._loadDateData(n, new Date(t.options.date)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments), s.hide("fast");
                            break;
                        case a.cancel:
                            t._loadDateData(n, new Date(t.options.date)), s.hide("fast");
                            break;
                        case a.year:
                            t.cache.selectedYear && t.cache.selectedYear.removeClass("selected"), t.cache.selectedYear = c, (p = t.options.date).setFullYear(c.text()), t._loadMonthData(s, new Date(p)), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.month:
                            t.cache.selectedMonth && t.cache.selectedMonth.removeClass("selected"), t.cache.selectedMonth = c.addClass("selected"), t.options.date.setMonth(c.data("month")), FX.Utils.applyFunc(t, i.onDateUpdate, arguments);
                            break;
                        case a.day:
                            t.cache.selectedDate && t.cache.selectedDate.removeClass("selected"), t.cache.selectedDate = c.addClass("selected");
                            var p = t.options.date;
                            p.setFullYear(t.cache.showYear), p.setMonth(t.cache.showMonth), p.setDate(c.text()), FX.Utils.applyFunc(t, i.onDateUpdate, arguments), o.parent().length || FX.Utils.applyFunc(t, i.onClose, arguments);
                            break;
                        case a.plus:
                            t._doTimeInc(o, o.focus);
                            break;
                        case a.minus:
                            t._doTimeDec(o, o.focus)
                    } else "mouseout" === d && c.removeClass("hover")
                };
            this.element.unbind(), this.element.bind("mousedown", l).bind("mouseover", l).bind("mouseup", l).bind("mouseout", l)
        },
        _createCell: function (t, i, a, s, n) {
            var o = e("<td class/>").attr("colSpan", a).html(i).appendTo(t);
            return s && o.data("nav", s), n = n ? "btn " + n : "btn", o.addClass(n), o
        },
        getValue: function () {
            var e = this.options, t = this.CONSTS.VIEWMODE, i = this.options.date;
            return i && (i.setMilliseconds(0), e.viewMode !== t.YMD && e.viewMode !== t.YM || i.setHours(0, 0, 0)), i
        },
        setValue: function (e) {
            this.options.date = e
        },
        getText: function () {
            return this.getValue()
        },
        setText: function (e) {
            this.setValue(e)
        }
    }), e.shortcut("datepicker", FX.DatePicker)
}(jQuery), function (e) {
    FX.ComboBox = FX.extend(FX.Trigger, {
        _defaultConfig: function () {
            return e.extend(FX.ComboBox.superclass._defaultConfig.apply(), {
                baseCls: "fui_combo",
                triggerIcon: "icon-caret-down",
                triggerList: "combo-list",
                textField: "text",
                valueField: "value",
                allowBlank: !0,
                async: null,
                asyncResultKey: "items",
                items: [{value: "选项1", text: "选项1"}, {value: "选项2", text: "选项2"}, {value: "选项3", text: "选项3"}],
                searchable: !0,
                onDataFilter: null,
                onItemCreate: null,
                onAfterItemSelect: null,
                onAfterTriggerHide: null,
                limitData: 300,
                emptyTip: null,
                minWidth4Trigger: 160
            })
        }, _init: function () {
            FX.ComboBox.superclass._init.apply(this, arguments), this._initStoreValue(), this.options.async && !this._hasDefaultValue() || this._createTriggerView()
        }, _initStoreValue: function () {
            this.text = null, this.value = null
        }, _hasDefaultValue: function () {
            return !FX.Utils.isEmpty(this.options.value)
        }, _onTriggerClick: function (t) {
            if (this.isEnabled()) {
                this._showTriggerView();
                var i = this;
                e(document).bind("mousedown.trigger", function (t) {
                    var a = t.target;
                    0 === e(a).closest(i.triggerView).length && i._hideTriggerView()
                })
            }
        }, _hideTriggerView: function () {
            var t = this.options;
            if (this.triggerView) {
                if (e(document).unbind("mousedown.trigger"), this.triggerView.detach(), FX.Utils.applyFunc(this, t.onAfterTriggerHide, [], !1), !this.changed) return;
                FX.Utils.applyFunc(this, t.onStopEdit, [], !1)
            }
        }, _showTriggerView: function () {
            var e = this.options;
            null == this.triggerView && this._createTriggerView(), this.triggerView.appendTo("body").css(this._calTriggerViewPos()).show(), this.$listView.css({
                maxWidth: Math.max(240, this.element.width()),
                minWidth: e.minWidth4Trigger
            }), this.changed = !1
        }, _createTriggerView: function () {
            if (this.triggerView = e('<div class="x-dropdown"/>'), this.valueMap = {}, this.options.searchable) {
                var t = this, i = e('<div class="fui_combo-search"/>').appendTo(this.triggerView);
                e("<input/>").bind("input propertychange", function (e) {
                    if (t.searchValue !== this.value) {
                        t.searchinterval && clearTimeout(t.searchinterval), t.searchValue = this.value, t.$listView.empty();
                        var i = t._createLoadingIcon("搜索中...");
                        t.searchinterval = setTimeout(function () {
                            i.remove(), t.startIndex = 0, t._onBeforeItemsLoaded(), t._createItemList(t.searchValue)
                        }, 500)
                    }
                }).appendTo(i), i.append(e('<i class="icon-search search-icon"/>'))
            }
            this.$listView = e('<div class="x-dropdown-list"/>').addClass(this.options.triggerList).appendTo(this.triggerView), this._onLoadItems(), this._bindViewEvts()
        }, _hideItems: function (t) {
            var i = this.$listView.children(".x-dropdown-item");
            FX.Utils.forEach(i, function (i, a) {
                var s = e(a);
                s.text().indexOf(t) < 0 && s.addClass("hide")
            })
        }, _onLoadItems: function (e) {
            var t = this.options, i = this;
            if (t.async && t.async.url) if (this.items) i._onBeforeItemsLoaded(), FX.Utils.forEach(this.items, function (t, a) {
                i._onItemCreate(a, t, e)
            }); else {
                var a = this._createLoadingIcon("加载中...");
                FX.Utils.applyFunc(this, t.onBeforeAsync, [], !1), FX.Utils.dataAjax({
                    url: t.async.url,
                    data: t.async.data
                }, function (s, n) {
                    a.remove(), i._onBeforeItemsLoaded(), i.items = FX.Utils.applyFunc(i, t.onAsyncSuccess, [s], !1), !1 === i.items ? (i.items = [], i.startIndex = 0, FX.Utils.forEach(s[t.asyncResultKey], function (e, a) {
                        var s = {};
                        FX.Utils.isEmpty(a) || (s[t.textField] = a[t.textField] || a, s[t.valueField] = a[t.valueField] || a, i.items.push(s))
                    }), i.items = i._sortItems(i.items), i._createItemList(e)) : FX.Utils.forEach(i.items, function (t, a) {
                        i._onItemCreate(a, t, e)
                    }), i._onAfterItemsLoaded()
                }, function () {
                    a.remove()
                })
            } else if (t.items) {
                if (i._onBeforeItemsLoaded(), FX.Utils.isArray(t.items)) FX.Utils.forEach(t.items, function (t, a) {
                    i._onItemCreate(a, t, e)
                }); else {
                    var s = 0;
                    for (var n in t.items) {
                        var o = {};
                        o[t.valueField] = n, o[t.textField] = t.items[n], i._onItemCreate(o, s, e), s++
                    }
                }
                i._onAfterItemsLoaded()
            }
        }, _sortItems: function (e) {
            var t = this.options;
            return e.sort(function (e, i) {
                var a = e[t.valueField] || e[t.textField] || e, s = i[t.valueField] || i[t.textField] || i;
                return +(a > s) || +(a === s) - 1
            })
        }, _createItemList: function (e) {
            var t = this, i = this.options;
            this.items || (this.items = i.items || []), this.startIndex = this.startIndex || 0;
            for (var a = 0, s = !0; a < i.limitData;) {
                if (this.startIndex >= this.items.length) {
                    s = !1;
                    break
                }
                var n = this.items[this.startIndex];
                this.startIndex++, !1 !== t._onItemCreate(n, a, e) && a++
            }
            s && t._bindLoadMore(e)
        }, _bindLoadMore: function (e) {
            var t = this;
            this.$listView.bind("scroll.loadMore", function () {
                t.$listView.scrollTop() + t.$listView.height() + 100 >= 26 * t.startIndex && (t.$listView.unbind("scroll.loadMore"), t._createItemList(e))
            })
        }, _createLoadingIcon: function (t) {
            var i = this.$listView.children(".loading-text");
            return 0 === i.length && (i = e('<div class="loading-text"/>').appendTo(this.$listView), e("<span/>").text(t).appendTo(i)), i
        }, _onAfterItemsLoaded: function () {
            var t = this.options, i = this.$listView.children(e(".x-dropdown-item")), a = t.allowBlank ? 1 : 0;
            t.emptyTip && i.length <= a && this.$listView.empty().append(e('<div class="empty-tip"/>').text(t.emptyTip))
        }, _onBeforeItemsLoaded: function () {
            var t = this;
            this.options.allowBlank && e('<a class="x-dropdown-item"/>').text("--请选择--").appendTo(t.$listView)
        }, _onItemCreate: function (t, i, a) {
            var s = this.options, n = this;
            if (!1 === FX.Utils.applyFunc(this, s.onItemCreate, [t, i], !1)) {
                var o = FX.Utils.applyFunc(this, s.onDataFilter, [t, i], !1);
                !1 !== o && (t = o);
                var l = t[s.textField], r = t[s.valueField];
                if (this.valueMap[r] = l, !FX.Utils.isEmpty(a) && !new RegExp(FX.Utils.escapeRegexp(a), "i").test(l + "")) return !1;
                var c = e('<a class="x-dropdown-item"/>').data("item", t).attr("option", r).attr("title", l).text(l).appendTo(this.$listView);
                if ((t.selected || !FX.Utils.isEmpty(r) && this._isSelected(r)) && (e(".select", this.triggerView).removeClass("select"), c.addClass("select"), this.value = r, this.text = l, this.editComp && this.editComp.val(l)), t.isOther) {
                    var d = e('<div class="fui-text-other"/>');
                    s.subform && d.addClass("subform-other"), this.element.after(d), this.textOther = FX.createWidget({
                        renderEl: d,
                        width: s.width ? s.width : 240,
                        type: "text",
                        visible: !!t.selected,
                        onStopEdit: function () {
                            FX.Utils.applyFunc(n, s.onStopEdit, [], !1)
                        }
                    }), c.addClass("item-other")
                }
            }
        }, _isSelected: function (e) {
            return this.value == e
        }, _bindViewEvts: function () {
            var t = this, i = !1;
            this.triggerView.bind("click", function (a) {
                if (i) i = !1; else {
                    var s = e(a.target).closest("a");
                    if (s.length > 0) {
                        var n = s.data("item");
                        t._onItemClick(s, n), a.stopEvent()
                    }
                }
            })
        }, _onItemClick: function (t, i) {
            var a = this.options;
            e(".select", this.triggerView).removeClass("select"), i ? (t.addClass("select"), this.value = i[a.valueField], this.text = i[a.textField]) : (this.value = null, this.text = null), this.editComp && this.editComp.val(this.text), t.hasClass("item-other") ? this.setOtherItemSelect() : this.setOtherItemRemove(), FX.Utils.applyFunc(this, a.onAfterItemSelect, [t, i], !1), FX.Utils.applyFunc(this, a.onAfterEdit, [t, i], !1), this.changed = !0, this._hideTriggerView()
        }, effectItemLinkWidgets: function () {
            var t = this.options;
            if (!t.async && this.triggerView) {
                var i = e(".select", this.triggerView);
                FX.Utils.applyFunc(this, t.onAfterItemSelect, [i, i.data("item")], !1)
            }
        }, checkValidate: function () {
            return !(!this.options.allowBlank && FX.Utils.isEmpty(this.getValue()))
        }, setEnable: function (e) {
            FX.ComboBox.superclass.setEnable.apply(this, [e]), this.textOther && this.textOther.setEnable(e)
        }, setValue: function (t) {
            var i = this.options;
            if (this.value = t, this.valueMap && this.valueMap[t] ? this.text = this.valueMap[t] : this.text = t, this.triggerView) if (e(".select", this.triggerView).removeClass("select"), FX.Utils.isEmpty(t)) this.setOtherItemRemove(); else {
                var a = [];
                if (e("a.x-dropdown-item", this.$listView).each(function (s, n) {
                        var o = e(n).data("item");
                        o && (o[i.valueField] != t || o.isOther || (a = e(n).addClass("select")))
                    }), this.textOther) {
                    if (0 === a.length) return void this.setOtherItemSelect(t);
                    this.setOtherItemRemove()
                }
            }
            this.editComp && this.editComp.val(this.text)
        }, setOtherItemSelect: function (e) {
            var t = this.options;
            this.$listView.children(".item-other").addClass("select"), this.editComp.val("其他");
            var i = t.width;
            this.options.subform && (this.textOther && this.textOther.doResize({width: .63 * t.width}), this.doResize({width: .35 * t.width})), t.width = i, this.textOther && (this.textOther.setVisible(!0), this.textOther.setValue(e))
        }, setOtherItemRemove: function () {
            var e = this.options;
            this.options.subform && this.doResize({width: e.width}), this.textOther && this.textOther.setVisible(!1)
        }, setText: function (e) {
            this.text = e, this.editComp && this.editComp.val(e)
        }, getValue: function () {
            return this.textOther && this.textOther.isVisible() ? this.textOther.getValue() : this.value
        }, getText: function () {
            return this.textOther && this.textOther.isVisible() ? this.textOther.getValue() : this.text
        }, rebuild: function () {
            this.triggerView && (this.triggerView.remove(), this.triggerView = null, this.$listView = null, this.textOther && (this.textOther.destroy(), this.textOther = null)), FX.ComboBox.superclass.rebuild.apply(this, arguments)
        }, getOptions: function () {
            var t = this.options, i = {noRepeat: t.noRepeat};
            return t.async && t.async.url ? i.async = t.async : i.items = t.items, e.extend(FX.ComboBox.superclass.getOptions.apply(this, arguments), i)
        }
    }), e.shortcut("combo", FX.ComboBox)
}(jQuery), function (e) {
    FX.ComboCheckBox = FX.extend(FX.ComboBox, {
        _defaultConfig: function () {
            return e.extend(FX.ComboCheckBox.superclass._defaultConfig.apply(), {
                baseCls: "fui_combocheck",
                triggerList: "combocheck-list",
                limitData: 300,
                hasSelectAll: !0,
                onAfterItemCreate: null
            })
        }, _initStoreValue: function () {
            this.value = [], this.text = []
        }, _hasDefaultValue: function () {
            var e = this.options.value;
            return !FX.Utils.isNull(e) && e.length > 0
        }, _onBeforeItemsLoaded: function () {
            if (this.options.hasSelectAll) {
                var e = {selectAll: !0};
                e[this.options.textField] = "全选", this._onItemCreate(e)
            }
        }, _onAfterItemsLoaded: function () {
            FX.ComboCheckBox.superclass._onAfterItemsLoaded.apply(this, arguments), this._setEditCompText()
        }, _createItemList: function (e) {
            FX.ComboCheckBox.superclass._createItemList.apply(this, arguments), this._checkSelectAll()
        }, _onItemCreate: function (t, i, a) {
            var s = this.options, n = t[s.valueField], o = t[s.textField];
            if (!FX.Utils.isEmpty(a) && !new RegExp(FX.Utils.escapeRegexp(a), "i").test(o + "")) return !1;
            var l = e('<a class="x-dropdown-item x-check"/>').data("item", t).attr("option", n).attr("title", o).appendTo(this.$listView);
            e('<i class="icon-blank"/>').appendTo(l), e("<span/>").text(o).appendTo(l), (t.selected || this._getValueIndex(n) > -1) && (l.addClass("select"), t.selected && (this.value.push(n), this.text.push(o))), t.selectAll ? (l.addClass("select-all field-meta"), this.$selectAllItem = l) : this.valueMap[n] = o, FX.Utils.applyFunc(this, s.onAfterItemCreate, [t, i, l], !1)
        }, _getValueIndex: function (e) {
            var t = -1;
            return FX.Utils.forEach(this.value, function (i, a) {
                if (a == e) return t = i, !1
            }), t
        }, _onItemClick: function (t, i) {
            var a = this, s = this.options, n = t.hasClass("select");
            if (i.selectAll) {
                var o = e(".x-dropdown-item", this.triggerView);
                n ? (FX.Utils.isEmpty(this.searchValue) ? (this.value = [], this.text = []) : FX.Utils.forEach(o, function (t, i) {
                    var s = e(i).data("item");
                    a._removeItem(s)
                }), o.removeClass("select")) : (FX.Utils.forEach(o, function (t, i) {
                    var s = e(i).data("item");
                    a._addItem(s)
                }), o.addClass("select"))
            } else n ? (t.removeClass("select"), this._removeItem(t.data("item")), this.$selectAllItem && this.$selectAllItem.removeClass("select")) : (t.addClass("select"), this._addItem(t.data("item")), this._checkSelectAll());
            this._setEditCompText(), FX.Utils.applyFunc(this, s.onAfterItemSelect, [this.value, this.text], !1), FX.Utils.applyFunc(this, s.onAfterEdit, [this.value, this.text], !1), this.changed = !0
        }, _addItem: function (e) {
            var t = this.options;
            if (!e.selectAll) {
                var i = e[t.valueField], a = e[t.textField];
                this._getValueIndex(i) > -1 || (this.value.push(i), this.text.push(a))
            }
        }, _removeItem: function (e) {
            var t = this.options;
            if (!e.selectAll) {
                var i = this._getValueIndex(e[t.valueField]);
                i < 0 || (this.value.splice(i, 1), this.text.splice(i, 1))
            }
        }, _checkSelectAll: function () {
            this.$listView && this.$selectAllItem && (this.$selectAllItem.hasClass("select") ? this.$listView.children().not(".select").length >= 1 && this.$selectAllItem.removeClass("select") : this.$listView.children().not(".select").length <= 1 && this.$selectAllItem.addClass("select"))
        }, _setEditCompText: function () {
            this.editComp && this.editComp.val(this.text.join(","))
        }, effectItemLinkWidgets: function () {
        }, checkValidate: function () {
            return !(!this.options.allowBlank && 0 === this.value.length)
        }, setValue: function (t) {
            var i = this, a = (this.options, e.makeArray(t));
            this.text = [], this.value = a, this.valueMap ? (e(".select", i.triggerView).removeClass("select"), FX.Utils.forEach(a, function (t, a) {
                var s = i.valueMap[a];
                FX.Utils.isNull(s) ? i.text.push(a) : i.text.push(s), i.triggerView && e("a.x-dropdown-item", i.$listView).each(function (t, i) {
                    e(i).attr("option") == a && e(i).addClass("select")
                })
            })) : this.text = a.slice(0), this._setEditCompText()
        }, setText: function (t) {
            this.text = e.makeArray(t), this.value = e.makeArray(t), this._setEditCompText()
        }, getValue: function () {
            return this.value
        }, getNullValue: function () {
            return []
        }, getText: function () {
            return this.text
        }
    }), e.shortcut("combocheck", FX.ComboCheckBox)
}(jQuery), function (e) {
    FX.XComboCheckBox = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.XComboCheckBox.superclass._defaultConfig.apply(), {
                baseCls: "fui_xcombocheck",
                waterMark: null,
                hasSelectAll: !0,
                hasSelectEmpty: !0,
                emptySelectText: "未填写",
                textField: "text",
                valueField: "value",
                async: null,
                asyncResultKey: "items",
                searchable: !0,
                onStopEdit: null,
                height: 30,
                width: 240,
                edge: {width: 240, height: 200},
                limit: 100,
                hasLimit: !1,
                searchKey: "keyword",
                hasScrollLoad: !1
            })
        }, _init: function () {
            FX.XComboCheckBox.superclass._init.apply(this, arguments);
            var t = this.options;
            this.values = [], this.texts = [], this.valueMap = {}, t.hasSelectEmpty && (this.valueMap[FX.CONST.PARAMETER.EMPTY] = t.emptySelectText), this.editComp = e('<input class="fui_trigger-input" />').attr("readonly", "readonly").attr("placeholder", t.waterMark).appendTo(this.element), e('<i class="fui_trigger-btn icon-caret-down" />').appendTo(this.element), this._bindEvents()
        }, _bindEvents: function () {
            var t = this;
            this.element.unbind("click.trigger"), this.element.bind("click.trigger", function (i) {
                var a = e(i.target);
                (a.closest(".fui_trigger-input").length > 0 || a.closest(".fui_trigger-btn").length > 0) && t._onTriggerClick()
            })
        }, _onTriggerClick: function () {
            var t = this;
            this._showTriggerView(), e(document).bind("mousedown.trigger", function (i) {
                var a = i.target;
                0 === e(a).closest(t.$triggerView).length && t._hideTriggerView()
            })
        }, _showTriggerView: function () {
            var e = this.options;
            this.$triggerView ? e.hasLimit && !FX.Utils.isObjectEmpty(this.values) && (this._clearItems(), this._createItems(this.items)) : this._createTriggerView(), this.$triggerView.appendTo("body").css(this._calTriggerViewPos()).show()
        }, _hideTriggerView: function () {
            var t = this.options;
            this.$triggerView && (e(document).unbind("mousedown.trigger"), this.$triggerView.detach(), FX.Utils.applyFunc(this, t.onStopEdit, [], !1))
        }, _calTriggerViewPos: function () {
            var e = {"z-Index": FX.STATIC.zIndex++}, t = this.element.offset(), i = this.options.edge,
                a = document.body.clientWidth - t.left;
            return a < i.width ? (e.right = a - this.element.outerWidth(), e.left = "auto") : (e.right = "auto", e.left = t.left), document.body.clientHeight + document.body.scrollTop - t.top - this.element.outerHeight() < i.height ? (e.top = "auto", e.bottom = document.body.clientHeight - t.top) : (e.top = t.top + this.element.outerHeight(), e.bottom = "auto"), e
        }, _createTriggerView: function () {
            var t = this, i = this.options;
            if (this.$triggerView = e('<div class="x-dropdown" />'), i.searchable) {
                var a = e('<div class="fui_combo-search"/>').appendTo(this.$triggerView);
                e("<input />").bind("input propertychange", function () {
                    t.searchValue !== this.value && t._doSearch(this.value)
                }).appendTo(a), a.append(e('<i class="icon-search search-icon"/>'))
            }
            this.$listView = e('<div class="x-dropdown-list combocheck-list"/>').appendTo(this.$triggerView), this.$listView.on("click", ".x-dropdown-item", function (i) {
                t._onItemClick(e(i.currentTarget))
            }), this.itemsMap = {}, this._loadItems()
        }, _loadItems: function (t) {
            var i = this, a = this.options;
            if (t = t || 0, this.items = this.items || [], a.async && a.async.url) {
                this.ajaxObj && this.ajaxObj.abort && this.ajaxObj.abort();
                var s = e('<div class="loading-text" />').append(e("<span />").text("加载中...")).appendTo(i.$listView),
                    n = {hasLimit: a.hasLimit, skip: t, limit: a.limit};
                FX.Utils.isEmpty(this.searchValue) || (n[a.searchKey] = this.searchValue, n.hasCurrentUser = !1), this.ajaxObj = FX.Utils.dataAjax({
                    url: a.async.url,
                    data: e.extend({}, a.async.data, n)
                }, function (e) {
                    var s = e[a.asyncResultKey];
                    i.items = i.items.concat(s), i._createItems(s), a.hasScrollLoad && s.length >= a.limit && i._bindLoadMore(t + a.limit)
                }, null, function () {
                    s.remove(), i.ajaxObj = null
                })
            } else a.items && (this.items = a.items, i._createItems(this.items))
        }, _createItems: function (t) {
            var i = this, a = this.options, s = [], n = [];
            this._beforeCreateItems(), FX.Utils.forEach(t, function (e, t) {
                var o = {};
                o[a.textField] = t[a.textField] || t, o[a.valueField] = t[a.valueField] || t;
                var l = i._createItem(o);
                l.hasClass("select") ? s.push(l) : n.push(l)
            }), FX.Utils.isEmpty(this.searchValue) && FX.Utils.forEach(this.values, function (e, t) {
                if (!i.itemsMap[t]) {
                    var n = {};
                    n[a.valueField] = t, n[a.textField] = i.valueMap[t] || t, s.push(i._createItem(n))
                }
            }), FX.Utils.forEach(s, function (e, t) {
                i.$listView.append(t)
            }), FX.Utils.forEach(n, function (e, t) {
                i.$listView.append(t)
            }), this.$selectAllItem = e(".select-all", this.$listView), FX.Utils.isEmpty(this.searchValue) || (this.$selectAllItem.find("span").text("搜索结果全选"), this.$listView.children("a.select-empty").addClass("hide")), i._checkSelectAll()
        }, _clearItems: function () {
            this.$listView.empty(), this.$selectAllItem = null, this.itemsMap = {}
        }, _bindLoadMore: function (e) {
            var t = this, i = this.options, a = 0;
            i.hasSelectAll && (a += 26), i.hasSelectEmpty && (a += 26), this.$listView.on("scroll.loadMore", function () {
                t.$listView.scrollTop() + t.$listView.height() >= 26 * e + a && (t.$listView.unbind("scroll.loadMore"), t._loadItems(e))
            })
        }, _doSearch: function (e) {
            var t = this, i = this.options;
            t.searchValue = e, t.$listView.children().addClass("hide");
            var a = t._createLoadingIcon("搜索中...");
            t.searchinterval && clearTimeout(t.searchinterval), i.async && i.hasLimit ? t.searchinterval = setTimeout(function () {
                a.remove(), t.items = null, t._clearItems(), t._loadItems()
            }, 600) : (t.searchinterval = setTimeout(function () {
                a.remove(), t.$listView.children().removeClass("hide"), FX.Utils.isEmpty(t.searchValue) || t._hideItems(t.searchValue)
            }, 500), FX.Utils.isEmpty(e) ? this.$selectAllItem.find("span").text("全选") : (this.$selectAllItem.find("span").text("搜索结果全选"), this.$listView.children("a.select-empty").addClass("hide")))
        }, _createLoadingIcon: function (t) {
            var i = this.$listView.children(".loading-text");
            return 0 === i.length && (i = e('<div class="loading-text"/>').appendTo(this.$listView), e("<span/>").text(t).appendTo(i)), i
        }, _createItem: function (t) {
            var i = this.options, a = t[i.valueField], s = t[i.textField];
            FX.Utils.isNull(a) || (this.valueMap[a] = s), this.itemsMap[a] = !0;
            var n = e('<a class="x-dropdown-item x-check"/>').attr("option", a).attr("title", s).append(e('<i class="icon-blank"/>')).append(e("<span />").text(s));
            return this.values.indexOf(a) > -1 && n.addClass("select"), t.selectAll ? n.addClass("select-all field-meta") : t.selectEmpty && n.addClass("select-empty field-meta"), n
        }, _beforeCreateItems: function () {
            var e = this.options;
            if (!this.$selectAllItem) {
                if (e.hasSelectAll) {
                    var t = {selectAll: !0};
                    t[e.textField] = "全选", this.$listView.append(this._createItem(t))
                }
                if (e.hasSelectEmpty) {
                    var i = {selectEmpty: !0};
                    i[e.valueField] = FX.CONST.PARAMETER.EMPTY, i[e.textField] = this.valueMap[FX.CONST.PARAMETER.EMPTY], this.$listView.append(this._createItem(i))
                }
            }
        }, _hideItems: function (t) {
            var i = this.$listView.children("a").not(".select-all").not(".select-empty");
            FX.Utils.forEach(i, function (i, a) {
                var s = e(a);
                new RegExp(FX.Utils.escapeRegexp(t), "i").test(s.text()) || s.addClass("hide")
            })
        }, _onItemClick: function (t) {
            var i = this, a = t.hasClass("select");
            if (t.hasClass("select-all")) {
                var s = this.$listView.children("a").not(".hide").not(".select-all");
                a ? (t.removeClass("select"), this.selectAll = !1, FX.Utils.isEmpty(this.searchValue) && (this.values = [])) : (t.addClass("select"), FX.Utils.isEmpty(this.searchValue) && (this.selectAll = !0)), FX.Utils.forEach(s, function (t, s) {
                    i._handleItemClick(e(s), a)
                })
            } else this._handleItemClick(t, a);
            this._refreshData()
        }, _refreshData: function () {
            var e = this;
            this.valueMap && (e.texts = [], FX.Utils.forEach(this.values, function (t, i) {
                var a = e.valueMap[i];
                a && e.texts.push(a)
            })), this.editComp.val(this.texts.join(","))
        }, _handleItemClick: function (e, t) {
            this.options;
            var i = e.attr("option");
            if (t) {
                e.removeClass("select");
                var a = this.values.indexOf(i);
                a > -1 && this.values.splice(a, 1), this.$selectAllItem && this.$selectAllItem.removeClass("select"), this.selectAll = !1
            } else e.addClass("select"), this.values.indexOf(i) < 0 && this.values.push(i), this._checkSelectAll()
        }, _checkSelectAll: function () {
            var e = this.$listView.children("a").not(".hide").not(".select-all"),
                t = this.$listView.children("a.select").not(".hide").not(".select-all");
            e.length === t.length && (this.$selectAllItem && this.$selectAllItem.addClass("select"), FX.Utils.isEmpty(this.searchValue) && (this.selectAll = !0))
        }, doResize: function () {
            FX.XComboCheckBox.superclass.doResize.apply(this, arguments);
            var e = this.options.height;
            this.element.css({"line-height": e - 2 + "px"})
        }, setValue: function (e) {
            var t = this;
            e || (e = []);
            var i = [];
            FX.Utils.isArray(e) ? i = e : (i = i.concat(e.items || []), e.hasEmpty && i.indexOf(FX.CONST.PARAMETER.EMPTY) < 0 && i.unshift(FX.CONST.PARAMETER.EMPTY)), t.values = [], t.texts = [], FX.Utils.forEach(i, function (e, i) {
                var a = t.valueMap[i];
                FX.Utils.isNull(a) ? t.texts.push(i) : t.texts.push(a), t.values.push(i)
            }), this.editComp.val(this.texts.join(","))
        }, getValue: function () {
            if (FX.Utils.isObjectEmpty(this.values)) return {};
            var e = [].concat(this.values), t = !1, i = e.indexOf(FX.CONST.PARAMETER.EMPTY);
            return i > -1 && (t = !0, e.splice(i, 1)), {hasEmpty: t, items: e}
        }
    }), e.shortcut("xcombocheck", FX.XComboCheckBox)
}(jQuery), function (e) {
    FX.XComboBox = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.XComboBox.superclass._defaultConfig.apply(), {
                baseCls: "fui_combo",
                waterMark: null,
                textField: "text",
                valueField: "value",
                async: null,
                asyncResultKey: "items",
                allowBlank: !0,
                searchable: !0,
                onStopEdit: null,
                height: 30,
                width: 240,
                edge: {width: 240, height: 200},
                limit: 100,
                hasLimit: !1,
                searchKey: "keyword",
                hasScrollLoad: !1,
                onAsyncSuccess: null
            })
        }, _init: function () {
            FX.XComboBox.superclass._init.apply(this, arguments);
            var t = this.options;
            this.valueMap = {}, this.editComp = e('<input class="fui_trigger-input" />').attr("readonly", "readonly").attr("placeholder", t.waterMark).appendTo(this.element), e('<i class="fui_trigger-btn icon-caret-down" />').appendTo(this.element), this._bindEvents()
        }, _bindEvents: function () {
            var t = this;
            this.element.unbind("click.trigger"), this.element.bind("click.trigger", function (i) {
                var a = e(i.target);
                (a.closest(".fui_trigger-input").length > 0 || a.closest(".fui_trigger-btn").length > 0) && t._onTriggerClick()
            })
        }, _onTriggerClick: function () {
            var t = this;
            this._showTriggerView(), e(document).bind("mousedown.trigger", function (i) {
                var a = i.target;
                0 === e(a).closest(t.$triggerView).length && t._hideTriggerView()
            })
        }, _showTriggerView: function () {
            var e = this.options;
            this.$triggerView ? e.hasLimit && this.value && (this._clearItems(), this._createItems(this.items)) : this._createTriggerView(), this.$triggerView.appendTo("body").css(this._calTriggerViewPos()).show()
        }, _hideTriggerView: function () {
            var t = this.options;
            this.$triggerView && (e(document).unbind("mousedown.trigger"), this.$triggerView.detach(), FX.Utils.applyFunc(this, t.onStopEdit, [], !1))
        }, _calTriggerViewPos: function () {
            var e = {"z-Index": FX.STATIC.zIndex++}, t = this.element.offset(), i = this.options.edge,
                a = document.body.clientWidth - t.left;
            return a < i.width ? (e.right = a - this.element.outerWidth(), e.left = "auto") : (e.right = "auto", e.left = t.left), document.body.clientHeight + document.body.scrollTop - t.top - this.element.outerHeight() < i.height ? (e.top = "auto", e.bottom = document.body.clientHeight - t.top) : (e.top = t.top + this.element.outerHeight(), e.bottom = "auto"), e
        }, _createTriggerView: function () {
            var t = this, i = this.options;
            if (this.$triggerView = e('<div class="x-dropdown" />'), i.searchable) {
                var a = e('<div class="fui_combo-search"/>').appendTo(this.$triggerView);
                e("<input />").bind("input propertychange", function () {
                    t.searchValue !== this.value && t._doSearch(this.value)
                }).appendTo(a), a.append(e('<i class="icon-search search-icon"/>'))
            }
            this.$listView = e('<div class="x-dropdown-list combo-list"/>').appendTo(this.$triggerView), this.$listView.on("click", ".x-dropdown-item", function (i) {
                t._onItemClick(e(i.currentTarget))
            }), this.itemsMap = {}, this._loadItems()
        }, _loadItems: function (t) {
            var i = this, a = this.options;
            if (t = t || 0, this.items = this.items || [], a.async && a.async.url) {
                this.ajaxObj && this.ajaxObj.abort && this.ajaxObj.abort();
                var s = e('<div class="loading-text" />').append(e("<span />").text("加载中...")).appendTo(i.$listView),
                    n = {hasLimit: a.hasLimit, skip: t, limit: a.limit};
                FX.Utils.isEmpty(this.searchValue) || (n[a.searchKey] = this.searchValue, n.hasCurrentUser = !1), this.ajaxObj = FX.Utils.dataAjax({
                    url: a.async.url,
                    data: e.extend({}, a.async.data, n)
                }, function (e) {
                    var s = FX.Utils.applyFunc(i, a.onAsyncSuccess, [e], !1);
                    !1 === s && (s = e[a.asyncResultKey]), i.items = i.items.concat(s), i._createItems(s), a.hasScrollLoad && s.length >= a.limit && i._bindLoadMore(t + a.limit)
                }, null, function () {
                    s.remove(), i.ajaxObj = null
                })
            } else a.items && (this.items = a.items, i._createItems(this.items))
        }, _createItems: function (e) {
            var t = this, i = this.options;
            this._onBeforeItemsLoaded();
            var a = [], s = [];
            if (FX.Utils.forEach(e, function (e, n) {
                    var o = {};
                    o[i.textField] = n[i.textField] || n, o[i.valueField] = n[i.valueField] || n;
                    var l = t._createItem(o);
                    l.hasClass("select") ? a.push(l) : s.push(l)
                }), FX.Utils.isEmpty(this.searchValue) && this.value && !this.itemsMap[this.value]) {
                var n = {};
                n[i.valueField] = this.value, n[i.textField] = t.valueMap[this.value] || this.value, a.push(t._createItem(n))
            }
            FX.Utils.forEach(a, function (e, i) {
                t.$listView.append(i)
            }), FX.Utils.forEach(s, function (e, i) {
                t.$listView.append(i)
            })
        }, _onBeforeItemsLoaded: function () {
            var t = this;
            this.options.allowBlank && !this.$selectEmpty && (this.$selectEmpty = e('<a class="x-dropdown-item"/>').text("--请选择--").appendTo(t.$listView))
        }, _clearItems: function () {
            this.$listView.empty(), this.$selectEmpty = null, this.itemsMap = {}
        }, _bindLoadMore: function (e) {
            var t = this;
            this.$listView.on("scroll.loadMore", function () {
                t.$listView.scrollTop() + t.$listView.height() >= 26 * e + 0 && (t.$listView.unbind("scroll.loadMore"), t._loadItems(e))
            })
        }, _doSearch: function (e) {
            var t = this, i = this.options;
            t.searchValue = e, t.$listView.children().addClass("hide");
            var a = t._createLoadingIcon("搜索中...");
            t.searchinterval && clearTimeout(t.searchinterval), i.async && i.hasLimit ? t.searchinterval = setTimeout(function () {
                a.remove(), t.items = null, t._clearItems(), t._loadItems()
            }, 600) : t.searchinterval = setTimeout(function () {
                a.remove(), t.$listView.children().removeClass("hide"), FX.Utils.isEmpty(t.searchValue) || t._hideItems(t.searchValue)
            }, 500)
        }, _createLoadingIcon: function (t) {
            var i = this.$listView.children(".loading-text");
            return 0 === i.length && (i = e('<div class="loading-text"/>').appendTo(this.$listView), e("<span/>").text(t).appendTo(i)), i
        }, _createItem: function (t) {
            var i = this.options, a = t[i.valueField], s = t[i.textField];
            FX.Utils.isNull(a) || (this.valueMap[a] = s), this.itemsMap[a] = !0;
            var n = e('<a class="x-dropdown-item"/>').attr("option", a).attr("title", s).append(e("<span />").text(s));
            return this.value === a && n.addClass("select"), n
        }, _hideItems: function (t) {
            var i = this.$listView.children("a");
            FX.Utils.forEach(i, function (i, a) {
                var s = e(a);
                new RegExp(FX.Utils.escapeRegexp(t), "i").test(s.text()) || s.addClass("hide")
            })
        }, _onItemClick: function (t) {
            this.value = t.attr("option"), e(".select", this.$listView).removeClass("select"), t.addClass("select"), this._hideTriggerView(), this._refreshData()
        }, _refreshData: function () {
            var e = this;
            this.valueMap && (e.text = this.valueMap[this.value]), this.editComp.val(this.text)
        }, doResize: function () {
            FX.XComboBox.superclass.doResize.apply(this, arguments);
            var e = this.options.height;
            this.element.css({"line-height": e - 2 + "px"})
        }, setValue: function (e) {
            this.value = e, this.valueMap && this.valueMap[e] ? this.text = this.valueMap[e] : this.text = e, this.editComp && this.editComp.val(this.text)
        }, getValue: function () {
            return this.value
        }
    }), e.shortcut("xcombobox", FX.XComboBox)
}(jQuery), function (e) {
    FX.UserComboBox = FX.extend(FX.XComboBox, {
        _createItem: function (t) {
            var i = this.options, a = t[i.valueField], s = t[i.textField];
            FX.Utils.isNull(a) || (this.valueMap[a] = s), this.itemsMap[a] = !0;
            var n = e('<a class="x-dropdown-item"/>').attr("option", a).attr("title", s).append(e("<span />").text(s));
            return this.value === a && n.addClass("select"), a === FX.USER_ID.CurrentUser && n.addClass("field-meta"), n
        }, setValue: function (e) {
            var t = this;
            this.value = e;
            var i = [];
            this.valueMap[e] || i.push(e), this.valueMap[FX.USER_ID.CurrentUser] = "当前用户", FX.Utils.isObjectEmpty(i) || FX.Utils.ajax({
                url: FX.Utils.getApi(FX.API.corp.list_member_name),
                data: {isUserOnly: !0, members: i}
            }, function (i) {
                FX.Utils.forEach(i.users, function (e, i) {
                    t.valueMap[i._id] = i.nickname
                }), t.text = t.valueMap[e], t.editComp.val(t.text)
            })
        }
    }), e.shortcut("usercombobox", FX.UserComboBox)
}(jQuery), function (e) {
    FX.DeptCheckBox = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.DeptCheckBox.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fx_dept_check",
                waterMark: null,
                hasSelectAll: !0,
                hasSelectCurrent: !0,
                hasSelectEmpty: !0,
                textField: "name",
                valueField: "_id",
                searchable: !0,
                onStopEdit: null,
                height: 30,
                width: 240,
                edge: {width: 240, height: 330},
                value: {items: []},
                dynamicType: "select",
                limit: {},
                searchKey: "keyword",
                hasScrollLoad: !1,
                multiSelect: !0,
                allowBlank: !1
            })
        }, _init: function () {
            FX.DeptCheckBox.superclass._init.apply(this, arguments), this._initData()
        }, _initData: function () {
            var t = this.options;
            this.values = [], this.texts = [], this.valueMap = {}, t.hasSelectEmpty && (this.valueMap[FX.CONST.PARAMETER.EMPTY] = "未填写"), this.editComp = e('<input class="fui_trigger-input" />').attr("readonly", "readonly").attr("placeholder", t.waterMark).appendTo(this.element), e('<i class="fui_trigger-btn icon-caret-down" />').appendTo(this.element), FX.Utils.isObjectEmpty(this.value) && (this.value = {items: []}), FX.Utils.isObjectEmpty(this.value.items) && (this.items = []), this._bindEvents()
        }, _bindEvents: function () {
            var t = this;
            this.element.unbind("click.trigger"), this.element.bind("click.trigger", function (i) {
                var a = e(i.target);
                (a.closest(".fui_trigger-input").length > 0 || a.closest(".fui_trigger-btn").length > 0) && t._onTriggerClick()
            })
        }, _onTriggerClick: function () {
            var t = this;
            this._showTriggerView(), e(document).bind("mousedown.dept-check", function (i) {
                var a = i.target;
                0 === e(a).closest(t.$triggerView).length && t._hideTriggerView()
            })
        }, _showTriggerView: function () {
            this.options;
            this.$triggerView || this._createTriggerView(), this.$triggerView.appendTo("body").css(this._calTriggerViewPos()).show()
        }, _hideTriggerView: function () {
            var t = this.options;
            this.$triggerView && (e(document).unbind("mousedown.dept-check"), this.$triggerView.detach(), FX.Utils.applyFunc(this, t.onStopEdit, [], !1))
        }, _calTriggerViewPos: function () {
            var e = {"z-Index": FX.STATIC.zIndex++}, t = this.element.offset(), i = this.options.edge,
                a = document.body.clientWidth - t.left;
            return a < i.width ? (e.right = a - this.element.outerWidth(), e.left = "auto") : (e.right = "auto", e.left = t.left), document.body.clientHeight + document.body.scrollTop - t.top - this.element.outerHeight() < i.height ? (e.top = "auto", e.bottom = document.body.clientHeight - t.top) : (e.top = t.top + this.element.outerHeight(), e.bottom = "auto"), e
        }, _createTriggerView: function () {
            var t = this, i = this.options;
            if (this.$triggerView = e('<div class="x-dropdown dept-dropdown" />'), i.searchable) {
                var a = e('<div class="fui_combo-search"/>').appendTo(this.$triggerView);
                e("<input />").bind("input propertychange", function () {
                    t.searchValue !== this.value && t._doSearch(this.value)
                }).appendTo(a), a.append(e('<i class="icon-search search-icon"/>'))
            }
            this.$listView = e('<div class="x-dropdown-list combocheck-list"/>').appendTo(this.$triggerView), this.$listView.on("click", ".x-dropdown-item", function (i) {
                t._onItemClick(e(i.currentTarget))
            }), this.itemsMap = {}, this._loadItems()
        }, _loadItems: function () {
            var t = this, i = this.options;
            this.items = this.items || [], FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.departments)}, function (a) {
                t.departments = e.extend(!0, [], a.departments), t.departments[0] && !t.departments[0]._id && t.departments.shift(), FX.Utils.forEach(t.departments, function (e, a) {
                    var s = a[i.valueField], n = a[i.textField];
                    FX.Utils.isNull(s) || (t.valueMap[s] = n)
                }), t.items = t.items.concat(t.departments || []), t._createItems(t.items), t._createDepartmentList()
            })
        }, _createDepartmentList: function () {
            var t = this, i = this.options;
            this.departmentTree = new FX.Tree({
                renderEl: e("<div/>").appendTo(this.$triggerView),
                customCls: "x-department-tree select-department dept-checkbox",
                Nodes: e.extend(!0, [], this.departments),
                setting: {
                    view: {expandSpeed: 100},
                    data: {simpleData: {enable: !0, idKey: "departmentId", pIdKey: "parentId"}},
                    callback: {
                        onCheck: function (e, i) {
                            t._doSelectItem(i)
                        }, onClick: function (e, i) {
                            t._doSelectItem(i)
                        }, beforeNodeCreate: function (e) {
                            t._checkLimit(e) || (e.nocheck = !0), e.checked = t._checkSelectState(e)
                        }, onNodeCreated: function (e, i) {
                            i.isParent && !i.open && i.level < 1 && this.expandNode(i, !0), i.departmentId == t.currentDepartment && this.selectNode(i)
                        }
                    },
                    check: {enable: i.multiSelect, chkboxType: {Y: "", N: ""}}
                }
            }), i.multiSelect && this.departmentTree.element.addClass("multiSelect")
        }, _createItems: function (t) {
            var i = this, a = this.options, s = [], n = [];
            this._beforeCreateItems(), FX.Utils.forEach(t, function (e, t) {
                var o = {};
                o[a.textField] = t[a.textField] || t, o[a.valueField] = t[a.valueField] || t;
                var l = i._createItem(o);
                l.hasClass("select") ? s.push(l) : n.push(l)
            }), FX.Utils.isEmpty(this.searchValue) && FX.Utils.forEach(this.values, function (e, t) {
                if (!i.itemsMap[t]) {
                    var n = {};
                    n[a.valueField] = t, n[a.textField] = i.valueMap[t] || t, s.push(i._createItem(n))
                }
            }), FX.Utils.forEach(s, function (e, t) {
                i.$listView.append(t.addClass("x-ui-hidden"))
            }), FX.Utils.forEach(n, function (e, t) {
                i.$listView.append(t.addClass("x-ui-hidden"))
            }), this.$selectAllItem = e(".select-all", this.$listView), i._checkSelectAll()
        }, _doSearch: function (e) {
            var t = this;
            this.options;
            t.searchValue = e, t.$listView.children().addClass("x-ui-hidden");
            var i = t._createLoadingIcon("搜索中...");
            t.searchinterval && clearTimeout(t.searchinterval), FX.Utils.isEmpty(e) ? t.searchinterval = setTimeout(function () {
                i.remove(), t.inSearch = !1, t.departmentTree && t.departmentTree.setVisible(!0), t.$selectAllItem.find("span").text("全选"), t.$listView.children("a.select-empty, a.select-all, a.curDept, a.placeholder").removeClass("x-ui-hidden"), t._checkSelectAll()
            }, 500) : t.searchinterval = setTimeout(function () {
                i.remove(), t.inSearch = !0, t.departmentTree && t.departmentTree.setVisible(!1), t.$selectAllItem.find("span").text("搜索结果全选"), t.$listView.children("a.select-all").removeClass("x-ui-hidden"), t._showItems(e), t._checkSelectAll()
            }, 500)
        }, _createLoadingIcon: function (t) {
            var i = this.$listView.children(".loading-text");
            return 0 === i.length && (i = e('<div class="loading-text"/>').appendTo(this.$listView), e("<span/>").text(t).appendTo(i)), i
        }, _createItem: function (t) {
            var i = this.options, a = t[i.valueField], s = t[i.textField];
            FX.Utils.isNull(a) || (this.valueMap[a] = s), this.itemsMap[a] = !0;
            var n = e('<a class="x-dropdown-item x-check"/>').attr("option", a).attr("title", s).append(i.multiSelect ? '<i class="icon-blank"/>' : "").append(e("<span />").text(s));
            return this.values.indexOf(a) > -1 && n.addClass("select"), t.selectAll ? n.addClass("select-all field-meta") : t.selectEmpty ? n.addClass("select-empty field-meta") : t.curDept && n.addClass("curDept field-meta"), n
        }, _beforeCreateItems: function () {
            var t = this, i = this.options;
            if (!this.$selectAllItem) {
                if (i.allowBlank && e('<a class="x-dropdown-item x-check placeholder field-meta"><span>--请选择--</span></a>').appendTo(t.$listView), i.hasSelectAll) {
                    var a = {selectAll: !0};
                    a[i.textField] = "全选", this.$listView.append(this._createItem(a))
                }
                if ("set" === i.dynamicType && i.hasSelectCurrent) {
                    var s = {_id: FX.CONST.DEPT_ID.CURRENT, name: "当前用户所处部门", curDept: !0};
                    this.$listView.append(this._createItem(s))
                }
                if (i.hasSelectEmpty) {
                    var n = {selectEmpty: !0};
                    n[i.valueField] = FX.CONST.PARAMETER.EMPTY, n[i.textField] = this.valueMap[FX.CONST.PARAMETER.EMPTY], this.$listView.append(this._createItem(n))
                }
            }
        }, _showItems: function (t) {
            var i = this.$listView.children("a").not(".select-all, .curDept, .select-empty, .placeholder");
            FX.Utils.forEach(i, function (i, a) {
                var s = e(a);
                new RegExp(FX.Utils.escapeRegexp(t), "i").test(s.text()) && s.removeClass("x-ui-hidden")
            })
        }, _onItemClick: function (t) {
            var i, a = this, s = t.hasClass("select");
            t.hasClass("select-all") ? a.inSearch ? (i = this.$listView.children("a").not(".x-ui-hidden").not(".select-all"), s ? t.removeClass("select") : t.addClass("select"), FX.Utils.forEach(i, function (t, i) {
                a._handleItemClick(e(i), s)
            })) : (i = this.$listView.children("a").not(".select-all"), s ? (t.removeClass("select"), this.selectAll = !1, FX.Utils.isEmpty(this.searchValue) && (this.values = [])) : (t.addClass("select"), FX.Utils.isEmpty(this.searchValue) && (this.selectAll = !0)), FX.Utils.forEach(i, function (t, i) {
                a._handleItemClick(e(i), s)
            })) : this._handleItemClick(t, s), this._refreshData()
        }, _refreshData: function () {
            var e = this;
            this.departmentTree && this.departmentTree.refresh(), this.valueMap && (e.texts = [], FX.Utils.forEach(this.values, function (t, i) {
                var a = e.valueMap[i];
                a && e.texts.push(a)
            })), this.editComp.val(this.texts.join(","))
        }, _handleItemClick: function (e, t) {
            var i = this.options, a = e.attr("option");
            if (t) {
                if (!i.multiSelect) return void this._hideTriggerView();
                e.removeClass("select");
                var s = this.values.indexOf(a);
                s > -1 && this.values.splice(s, 1), this.$selectAllItem && this.$selectAllItem.removeClass("select"), this.selectAll = !1
            } else this.values.indexOf(a) < 0 && (i.multiSelect || (this.$listView.children("a").removeClass("select"), this.values = []), FX.Utils.isNull(a) || this.values.push(a)), e.addClass("select"), this._checkSelectAll();
            i.multiSelect || this._hideTriggerView()
        }, _checkSelectAll: function () {
            var e, t;
            this.inSearch ? (e = this.$listView.children("a").not(".x-ui-hidden").not(".select-all"), t = this.$listView.children("a.select").not(".x-ui-hidden").not(".select-all")) : (e = this.$listView.children("a").not(".select-all"), t = this.$listView.children("a.select").not(".select-all")), e.length === t.length ? (this.$selectAllItem && this.$selectAllItem.addClass("select"), FX.Utils.isEmpty(this.searchValue) && (this.selectAll = !0)) : (this.$selectAllItem && this.$selectAllItem.removeClass("select"), this.selectAll = !1)
        }, _checkLimit: function () {
            return !0
        }, _checkSelectState: function (e) {
            this.options;
            switch (e._id) {
                case FX.CONST.PARAMETER.EMPTY:
                    return this.value.hasEmpty;
                case FX.CONST.DEPT_ID.CURRENT:
                    return this.value.hasCurrentDept;
                default:
                    return this.values.indexOf(e._id) > -1
            }
        }, _doSelectItem: function (t) {
            var i = this;
            this.options;
            if (this._checkLimit(t)) {
                var a = {name: t.name, _id: t._id}, s = e("[option=" + t._id + "]");
                this.values.indexOf(a._id) > -1 ? i._handleItemClick(s, !0) : i._handleItemClick(s, !1), this._refreshData(), this._checkSelectAll()
            }
        }, doResize: function () {
            FX.DeptCheckBox.superclass.doResize.apply(this, arguments);
            var e = this.options.height;
            this.element.css({"line-height": e - 2 + "px"})
        }, setCurDept: function () {
            var e = this, t = this.options;
            if (this.value.hasEmpty && this.values.indexOf(FX.CONST.PARAMETER.EMPTY) < 0 && (this.values.unshift(FX.CONST.PARAMETER.EMPTY), t.hasSelectEmpty && (this.valueMap[FX.CONST.PARAMETER.EMPTY] = "未填写")), this.value.hasCurrentDept) if ("set" === t.dynamicType && t.hasSelectCurrent && this.values.indexOf(FX.CONST.DEPT_ID.CURRENT) < 0) this.values.unshift(FX.CONST.DEPT_ID.CURRENT), this.valueMap[FX.CONST.DEPT_ID.CURRENT] = "当前用户所处部门", this._setEditCompText(); else {
                var i = FX.Utils.createMask(this.element, {isLight: !0, hasLoader: !0});
                FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.current_departments)}, function (t) {
                    i.remove();
                    var a = [];
                    FX.Utils.forEach(t.departmentList, function (t, i) {
                        a.push(i._id), e.valueMap[i._id] = i.name
                    }), e.values = a.concat(e.values).unique(), e._setEditCompText()
                })
            } else this._setEditCompText()
        }, _setEditCompText: function () {
            var e = this;
            FX.Utils.forEach(this.values, function (t, i) {
                var a = e.valueMap[i];
                FX.Utils.isNull(a) || e.texts.push(a)
            }), this.editComp && this.editComp.val(this.texts.join(","))
        }, setValue: function (e) {
            var t = this;
            this.options;
            if (this.values = [], this.texts = [], this.value = e, FX.Utils.isObjectEmpty(this.value) && (this.value = {items: []}), FX.Utils.isObjectEmpty(this.value.items)) this.setCurDept(); else {
                var i = FX.Utils.createMask(this.element, {isLight: !0, hasLoader: !0});
                FX.Utils.ajax({
                    url: FX.Utils.getApi(FX.API.corp.list_member_name),
                    data: {isDepartmentOnly: !0, members: this.value.items}
                }, function (e) {
                    i.remove();
                    var a = [];
                    FX.Utils.forEach(e.departments, function (e, i) {
                        a.push(i._id), t.valueMap[i._id] = i.name
                    }), t.values = a.concat(t.values), t.setCurDept()
                })
            }
        }, getValue: function () {
            if (FX.Utils.isObjectEmpty(this.values)) return {};
            var e = [].concat(this.values), t = !1, i = !1, a = [];
            return FX.Utils.forEach(e, function (e, s) {
                switch (s) {
                    case FX.CONST.PARAMETER.EMPTY:
                        t = !0;
                        break;
                    case FX.CONST.DEPT_ID.CURRENT:
                        i = !0;
                        break;
                    default:
                        a.push(s)
                }
            }), {hasCurrentDept: i, hasEmpty: t, items: a}
        }, rebuild: function (e) {
            this.value = e, this._initData(), this._refreshData()
        }
    }), e.shortcut("deptcheck", FX.DeptCheckBox)
}(jQuery), function (e) {
    FX.UserCheckBox = FX.extend(FX.XComboCheckBox, {
        _createItem: function (t) {
            var i = this.options, a = t[i.valueField], s = t[i.textField];
            FX.Utils.isNull(a) || (this.valueMap[a] = s), this.itemsMap[a] = !0;
            var n = e('<a class="x-dropdown-item x-check"/>').attr("option", a).attr("title", s).append(e('<i class="icon-blank"/>')).append(e("<span />").text(s));
            return this.values.indexOf(a) > -1 && n.addClass("select"), a === FX.USER_ID.CurrentUser && n.addClass("field-meta"), t.selectAll ? n.addClass("select-all field-meta") : t.selectEmpty && n.addClass("select-empty field-meta"), n
        }, setValue: function (e) {
            var t = this;
            e || (e = []);
            var i = [];
            FX.Utils.isArray(e) ? i = e : (i = i.concat(e.items || []), e.hasEmpty && i.indexOf(FX.CONST.PARAMETER.EMPTY) < 0 && i.unshift(FX.CONST.PARAMETER.EMPTY)), this.values = i;
            var a = [];
            FX.Utils.forEach(this.values, function (e, i) {
                t.valueMap[i] || a.push(i)
            }), this.valueMap[FX.USER_ID.CurrentUser] = "当前用户", FX.Utils.isObjectEmpty(a) || FX.Utils.ajax({
                url: FX.Utils.getApi(FX.API.corp.list_member_name),
                data: {isUserOnly: !0, members: a}
            }, function (e) {
                FX.Utils.forEach(e.users, function (e, i) {
                    t.valueMap[i._id] = i.nickname
                }), t.texts = [], FX.Utils.forEach(t.values, function (e, i) {
                    t.texts.push(t.valueMap[i])
                }), t.editComp.val(t.texts.join(","))
            })
        }
    }), e.shortcut("usercheck", FX.UserCheckBox)
}(jQuery), function (e) {
    FX.ButtonGroup = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.ButtonGroup.superclass._defaultConfig.apply(), {
                baseCls: "x-group",
                btnCls: "btn_group",
                allowBlank: !0,
                layout: null,
                items: [{value: "选项1", text: "选项1"}, {value: "选项2", text: "选项2"}, {value: "选项3", text: "选项3"}]
            })
        }, _init: function () {
            FX.ButtonGroup.superclass._init.apply(this, arguments);
            var e = this.options, t = this;
            this.$btns = [], this.$btnOther = null, e.items && FX.Utils.forEach(e.items, function (e, i) {
                t._createItem(i)
            }), this._bindEvt()
        }, _createItem: function (t) {
            var i = this.options,
                a = e('<div class="group_item"/>').attr("value", t.value).data("item", t).addClass(this.options.btnCls).appendTo(this.element);
            return i.layout && a.addClass(i.layout), e('<i class="icon-blank"/>').appendTo(a), t.selected && a.addClass("select"), e("<span/>").text(t.text).appendTo(a), this.$btns.push(a), a
        }, _bindEvt: function () {
            var t = this;
            this.element.unbind("click.group"), this.element.bind("click.group", function (i) {
                if (t.isEnabled()) {
                    var a = i.target.tagName ? i.target.tagName.toUpperCase() : "";
                    if ("INPUT" !== a && "TEXTAREA" !== a) {
                        var s = e(i.target).closest(".group_item");
                        s && s.length > 0 && t._doItemClick(s)
                    }
                }
            })
        }, _doItemClick: function (e) {
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.ButtonGroup.superclass.getOptions.apply(this, arguments), {items: t.items})
        }
    })
}(jQuery), function (e) {
    FX.RadioGroup = FX.extend(FX.ButtonGroup, {
        _defaultConfig: function () {
            return e.extend(FX.RadioGroup.superclass._defaultConfig.apply(), {
                btnCls: "x-radio",
                onAfterItemSelect: null,
                otherInputWidth: 180
            })
        }, _doItemClick: function (t) {
            var i = this.options, a = !0;
            if (t.hasClass("select") ? (t.removeClass("select"), a = !1) : (e(".select", this.element).removeClass("select"), t.addClass("select"), a = !0), t.hasClass("item-other")) {
                var s = t.data("widget");
                s.setEnable(a), a && s.select()
            } else this.$btnOther && this.$btnOther.data("widget").setEnable(!1);
            var n = e(".select", this.element);
            FX.Utils.applyFunc(this, i.onAfterItemSelect, [n, n.data("item")], !1), FX.Utils.applyFunc(this, i.onStopEdit, [], !1)
        }, _createItem: function (t) {
            var i = FX.RadioGroup.superclass._createItem.apply(this, arguments), a = this.options, s = this;
            if (t.isOther) {
                var n = FX.createWidget({
                    renderEl: e('<div class="text-other"/>').appendTo(i),
                    width: a.otherInputWidth,
                    type: "text",
                    enable: !!t.selected,
                    onStopEdit: function () {
                        FX.Utils.applyFunc(s, a.onStopEdit, [], !1)
                    }
                });
                i.addClass("item-other"), this.$btnOther = i, i.data("widget", n)
            }
        }, setEnable: function (e) {
            if (FX.RadioGroup.superclass.setEnable.apply(this, [e]), this.$btnOther) {
                var t = this.$btnOther.data("widget");
                this.$btnOther.hasClass("select") && e ? t.setEnable(!0) : t.setEnable(!1)
            }
        }, effectItemLinkWidgets: function () {
            var t = this.options, i = e(".select", this.element);
            FX.Utils.applyFunc(this, t.onAfterItemSelect, [i, i.data("item")], !1)
        }, setValue: function (t) {
            if (e(".select", this.element).removeClass("select"), FX.Utils.isEmpty(t)) this.$btnOther && this.$btnOther.removeClass("select"); else {
                var i = !1;
                FX.Utils.forEach(this.$btns, function (e, a) {
                    var s = a.data("item");
                    if (s.value === t && !s.isOther) return a.addClass("select"), i = !0, !1
                }), !i && this.$btnOther && (this.$btnOther.addClass("select"), this.$btnOther.data("widget").setValue(t))
            }
        }, checkValidate: function () {
            return !(!this.options.allowBlank && FX.Utils.isEmpty(this.getValue()))
        }, getValue: function () {
            var t = [], i = e(".select", this.element);
            return FX.Utils.forEach(i, function (i, a) {
                var s = e(a).data("item");
                s.isOther ? t.push(e(a).data("widget").getValue()) : t.push(s.value)
            }), t.length > 0 ? t.join("") : null
        }, setText: function (t) {
            var i = this;
            e(".select", this.element).removeClass("select"), FX.Utils.forEach(this.$btns, function (e, a) {
                if (a.data("item").text === t) return a.addClass("select"), !1;
                i.$btnOther && (i.$btnOther.addClass("select"), i.$btnOther.data("widget").setValue(t))
            })
        }, getText: function () {
            var t = [], i = e(".select", this.element);
            return FX.Utils.forEach(i, function (i, a) {
                var s = e(a).data("item");
                s.isOther ? t.push(e(a).data("widget").getValue()) : t.push(s.text)
            }), t.length > 0 ? t.join("") : null
        }
    }), e.shortcut("radiogroup", FX.RadioGroup)
}(jQuery), function (e) {
    FX.CheckBoxGroup = FX.extend(FX.ButtonGroup, {
        _defaultConfig: function () {
            return e.extend(FX.CheckBoxGroup.superclass._defaultConfig.apply(), {
                btnCls: "x-check",
                onAfterItemSelect: null
            })
        }, _doItemClick: function (e) {
            FX.CheckBoxGroup.superclass._doItemClick.apply(this, arguments);
            var t = this.options;
            e.toggleClass("select");
            var i = e.data("item"), a = e.hasClass("select");
            FX.Utils.applyFunc(this, t.onAfterItemSelect, [e, i, a], !1), FX.Utils.applyFunc(this, t.onStopEdit, [], !1)
        }, checkValidate: function () {
            return !(!this.options.allowBlank && 0 === e(".select", this.element).length)
        }, setValue: function (t) {
            e(".select", this.element).removeClass("select");
            var i = e.makeArray(t);
            FX.Utils.forEach(this.$btns, function (t, a) {
                var s = e(a).data("item");
                i.indexOf(s.value) > -1 && e(a).addClass("select")
            })
        }, getValue: function () {
            var t = [], i = e(".select", this.element);
            return FX.Utils.forEach(i, function (i, a) {
                var s = e(a).data("item");
                t.push(s.value)
            }), t
        }, setText: function (t) {
            e(".select", this.element).removeClass("select");
            var i = e.makeArray(t);
            FX.Utils.forEach(this.$btns, function (t, a) {
                var s = e(a).data("item");
                i.indexOf(s.text) > -1 && e(a).addClass("select")
            })
        }, getText: function () {
            var t = [], i = e(".select", this.element);
            return FX.Utils.forEach(i, function (i, a) {
                var s = e(a).data("item");
                t.push(s.text)
            }), t
        }, getNullValue: function () {
            return []
        }
    }), e.shortcut("checkboxgroup", FX.CheckBoxGroup)
}(jQuery), function (e) {
    FX.Address = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Address.superclass._defaultConfig.apply(), {
                baseCls: "fui_address",
                needDetail: !0,
                allowBlank: !0,
                width: 420,
                width4province: "45%",
                width4city: "24%",
                width4district: "24%",
                width4detail: "100%"
            })
        }, _init: function () {
            FX.Address.superclass._init.apply(this, arguments), FX.AddressData || (FX.AddressData = {
                "北京市": {"北京市": ["昌平区", "朝阳区", "大兴区", "东城区", "房山区", "丰台区", "海淀区", "怀柔区", "平谷区", "顺义区", "通州区", "西城区", "门头沟区", "石景山区", "密云区", "延庆区"]},
                "天津市": {"天津市": ["宝坻区", "北辰区", "东丽区", "汉沽区", "和平区", "河北区", "河东区", "河西区", "红桥区", "津南区", "南开区", "塘沽区", "武清区", "西青区", "蓟县", "静海县", "宁河县", "滨海新区"]},
                "河北省": {
                    "石家庄市": ["藁城市", "晋州市", "鹿泉市", "辛集市", "新乐市", "高新区", "桥东区", "桥西区", "新华区", "裕华区", "长安区", "赵县", "高邑县", "行唐县", "井陉县", "灵寿县", "栾城县", "平山县", "深泽县", "无极县", "元氏县", "赞皇县", "正定县", "井陉矿区", "石家庄经济技术开发区"],
                    "保定市": ["安国市", "定州市", "涿州市", "高碑店市", "北市区", "南市区", "新市区", "蠡县", "唐县", "雄县", "易县", "安新县", "博野县", "定兴县", "阜平县", "高阳县", "涞水县", "涞源县", "满城县", "清苑县", "曲阳县", "容城县", "顺平县", "望都县", "徐水县"],
                    "沧州市": ["泊头市", "河间市", "黄骅市", "任丘市", "新华区", "运河区", "沧县", "青县", "献县", "东光县", "海兴县", "南皮县", "肃宁县", "吴桥县", "盐山县", "孟村回族自治县"],
                    "承德市": ["双滦区", "双桥区", "大学城", "承德县", "隆化县", "滦平县", "平泉县", "兴隆县", "丰宁满族自治县", "宽城满族自治县", "围场满族蒙古族自治县", "开发东区", "开发西区", "鹰手营子矿区", "承德高教园区"],
                    "邯郸市": ["武安市", "丛台区", "复兴区", "邯山区", "磁县", "邱县", "涉县", "魏县", "成安县", "大名县", "肥乡县", "馆陶县", "广平县", "邯郸县", "鸡泽县", "临漳县", "曲周县", "永年县", "峰峰矿区", "邯郸经济开发区", "马头生态工业园"],
                    "衡水市": ["冀州市", "深州市", "桃城区", "景县", "安平县", "阜城县", "故城县", "饶阳县", "武强县", "武邑县", "枣强县", "路北新区", "衡水高新技术开发区"],
                    "廊坊市": ["霸州市", "三河市", "安次区", "广阳区", "大城县", "固安县", "文安县", "香河县", "永清县", "大厂回族自治县"],
                    "唐山市": ["迁安市", "遵化市", "丰南区", "丰润区", "古冶区", "开平区", "路北区", "路南区", "曹妃甸区", "滦县", "乐亭县", "滦南县", "迁西县", "玉田县", "高新技术开发区"],
                    "邢台市": ["南宫市", "沙河市", "高开区", "桥东区", "桥西区", "任县", "威县", "柏乡县", "广宗县", "巨鹿县", "临城县", "临西县", "隆尧县", "南和县", "内丘县", "宁晋县", "平乡县", "清河县", "新河县", "邢台县"],
                    "秦皇岛市": ["抚宁区", "海港区", "北戴河区", "山海关区", "昌黎县", "卢龙县", "青龙满族自治县"],
                    "张家口市": ["桥东区", "桥西区", "宣化区", "下花园区", "蔚县", "赤城县", "崇礼县", "沽源县", "怀安县", "怀来县", "康保县", "尚义县", "万全县", "宣化县", "阳原县", "张北县", "涿鹿县", "察北管理区", "塞北管理区", "高新技术开发区"]
                },
                "山西省": {
                    "太原市": ["古交市", "晋源区", "小店区", "迎泽区", "尖草坪区", "万柏林区", "杏花岭区", "娄烦县", "清徐县", "阳曲县"],
                    "长治市": ["潞城市", "城区", "郊区", "沁县", "壶关县", "黎城县", "沁源县", "屯留县", "武乡县", "襄垣县", "长治县", "长子县", "高新技术开发区"],
                    "大同市": ["城区", "矿区", "南郊区", "新荣区", "大同县", "广灵县", "浑源县", "灵丘县", "天镇县", "阳高县", "左云县"],
                    "晋城市": ["高平市", "城区", "陵川县", "沁水县", "阳城县", "泽州县"],
                    "晋中市": ["介休市", "榆次区", "祁县", "和顺县", "灵石县", "平遥县", "寿阳县", "太谷县", "昔阳县", "榆社县", "左权县"],
                    "临汾市": ["侯马市", "霍州市", "尧都区", "古县", "吉县", "蒲县", "隰县", "安泽县", "大宁县", "汾西县", "浮山县", "洪洞县", "曲沃县", "乡宁县", "襄汾县", "翼城县", "永和县"],
                    "吕梁市": ["汾阳市", "孝义市", "离石区", "岚县", "临县", "兴县", "方山县", "交城县", "交口县", "柳林县", "石楼县", "文水县", "中阳县"],
                    "朔州市": ["平鲁区", "朔城区", "应县", "怀仁县", "山阴县", "右玉县"],
                    "忻州市": ["原平市", "忻府区", "代县", "保德县", "定襄县", "繁峙县", "河曲县", "静乐县", "岢岚县", "宁武县", "偏关县", "神池县", "五台县", "五寨县"],
                    "阳泉市": ["城区", "郊区", "矿区", "盂县", "平定县"],
                    "运城市": ["河津市", "永济市", "盐湖区", "绛县", "夏县", "稷山县", "临猗县", "平陆县", "芮城县", "万荣县", "闻喜县", "新绛县", "垣曲县", "空港新区", "禹都经济技术开发区"]
                },
                "内蒙古自治区": {
                    "呼和浩特市": ["回民区", "赛罕区", "新城区", "玉泉区", "武川县", "清水河县", "托克托县", "和林格尔县", "土默特左旗"],
                    "包头市": ["东河区", "九原区", "青山区", "石拐区", "昆都仑区", "白云鄂博矿区", "固阳县", "土默特右旗", "达尔罕茂明安联合旗"],
                    "赤峰市": ["红山区", "松山区", "元宝山区", "林西县", "宁城县", "敖汉旗", "巴林右旗", "巴林左旗", "喀喇沁旗", "翁牛特旗", "克什克腾旗", "阿鲁科尔沁旗"],
                    "通辽市": ["霍林郭勒市", "科尔沁区", "开鲁县", "库伦旗", "奈曼旗", "扎鲁特旗", "科尔沁左翼中旗", "科尔沁左翼后旗"],
                    "乌海市": ["海南区", "乌达区", "海勃湾区"],
                    "巴彦淖尔市": ["临河区", "磴口县", "五原县", "杭锦后旗", "乌拉特后旗", "乌拉特前旗", "乌拉特中旗"],
                    "鄂尔多斯市": ["东胜区", "杭锦旗", "乌审旗", "达拉特旗", "鄂托克旗", "准格尔旗", "鄂托克前旗", "伊金霍洛旗"],
                    "呼伦贝尔市": ["根河市", "满洲里市", "牙克石市", "扎兰屯市", "额尔古纳市", "海拉尔区", "阿荣旗", "陈巴尔虎旗", "鄂伦春自治旗", "新巴尔虎右旗", "新巴尔虎左旗", "鄂温克族自治旗", "莫力达瓦达斡尔族自治旗"],
                    "乌兰察布市": ["丰镇市", "集宁区", "化德县", "凉城县", "商都县", "兴和县", "卓资县", "四子王旗", "察哈尔右翼后旗", "察哈尔右翼前旗", "察哈尔右翼中旗"],
                    "兴安盟": ["阿尔山市", "乌兰浩特市", "突泉县", "扎赉特旗", "科尔沁右翼前旗", "科尔沁右翼中旗"],
                    "阿拉善盟": ["额济纳旗", "阿拉善右旗", "阿拉善左旗"],
                    "锡林郭勒盟": ["二连浩特市", "锡林浩特市", "多伦县", "镶黄旗", "正蓝旗", "阿巴嘎旗", "太仆寺旗", "正镶白旗", "苏尼特右旗", "苏尼特左旗", "东乌珠穆沁旗", "西乌珠穆沁旗"]
                },
                "辽宁省": {
                    "沈阳市": ["新民市", "大东区", "东陵区", "和平区", "皇姑区", "沈河区", "铁西区", "于洪区", "苏家屯区", "法库县", "康平县", "辽中县", "浑南新区", "沈北新区"],
                    "大连市": ["庄河市", "普兰店市", "瓦房店市", "长海县", "金州区", "西岗区", "中山区", "甘井子区", "旅顺口区", "沙河口区", "高新园区"],
                    "鞍山市": ["海城市", "立山区", "千山区", "铁东区", "铁西区", "台安县", "岫岩满族自治县", "鞍山经济开发区", "鞍山经济开发区西区"],
                    "本溪市": ["明山区", "南芬区", "平山区", "溪湖区", "本溪满族自治县", "桓仁满族自治县"],
                    "朝阳市": ["北票市", "凌源市", "龙城区", "双塔区", "朝阳县", "建平县", "喀喇沁左翼蒙古族自治县"],
                    "丹东市": ["东港市", "凤城市", "元宝区", "振安区", "振兴区", "宽甸满族自治县"],
                    "抚顺市": ["东洲区", "顺城区", "望花区", "新抚区", "抚顺县", "清原满族自治县", "新宾满族自治县", "高湾开发区"],
                    "阜新市": ["海州区", "太平区", "细河区", "新邱区", "清河门区", "彰武县", "阜新蒙古族自治县"],
                    "锦州市": ["北镇市", "凌海市", "古塔区", "凌河区", "太和区", "义县", "黑山县", "经济技术开发区"],
                    "辽阳市": ["灯塔市", "白塔区", "宏伟区", "文圣区", "弓长岭区", "太子河区", "辽阳县"],
                    "盘锦市": ["双台子区", "兴隆台区", "大洼县", "盘山县"],
                    "铁岭市": ["开原市", "调兵山市", "清河区", "银州区", "昌图县", "铁岭县", "西丰县", "凡河新区"],
                    "营口市": ["盖州市", "大石桥市", "老边区", "西市区", "站前区", "鲅鱼圈区"],
                    "葫芦岛市": ["兴城市", "连山区", "龙港区", "南票区", "建昌县", "绥中县"]
                },
                "吉林省": {
                    "长春市": ["德惠市", "九台市", "榆树市", "朝阳区", "二道区", "宽城区", "绿园区", "南关区", "双阳区", "农安县", "高新技术产业开发区", "经济技术产业开发区", "长春汽车产业开发区", "净月潭旅游经济开发区"],
                    "白城市": ["大安市", "洮南市", "洮北区", "通榆县", "镇赉县"],
                    "白山市": ["临江市", "浑江区", "江源区", "抚松县", "靖宇县", "长白朝鲜族自治县"],
                    "吉林市": ["桦甸市", "蛟河市", "磐石市", "舒兰市", "昌邑区", "船营区", "丰满区", "龙潭区", "永吉县"],
                    "辽源市": ["龙山区", "西安区", "东丰县", "东辽县"],
                    "四平市": ["双辽市", "公主岭市", "铁东区", "铁西区", "梨树县", "伊通满族自治县"],
                    "松原市": ["扶余市", "宁江区", "乾安县", "长岭县", "前郭尔罗斯蒙古自治县"],
                    "通化市": ["集安市", "梅河口市", "东昌区", "二道江区", "辉南县", "柳河县", "通化县"],
                    "延边朝鲜族自治州": ["敦化市", "和龙市", "珲春市", "龙井市", "图们市", "延吉市", "安图县", "汪清县"]
                },
                "黑龙江省": {
                    "哈尔滨市": ["尚志市", "双城市", "五常市", "阿城区", "道里区", "道外区", "呼兰区", "南岗区", "平房区", "松北区", "香坊区", "宾县", "巴彦县", "方正县", "木兰县", "通河县", "延寿县", "依兰县"],
                    "大庆市": ["大同区", "红岗区", "龙凤区", "让胡路区", "萨尔图区", "林甸县", "肇源县", "肇州县", "杜尔伯特蒙古族自治县", "乙烯地区"],
                    "鹤岗市": ["东山区", "工农区", "南山区", "向阳区", "兴安区", "兴山区", "萝北县", "绥滨县"],
                    "黑河市": ["北安市", "五大连池市", "爱辉区", "嫩江县", "孙吴县", "逊克县"],
                    "绥化市": ["安达市", "海伦市", "肇东市", "北林区", "兰西县", "明水县", "青冈县", "庆安县", "绥棱县", "望奎县"],
                    "鸡西市": ["虎林市", "密山市", "滴道区", "恒山区", "鸡冠区", "梨树区", "麻山区", "城子河区", "鸡东县"],
                    "伊春市": ["铁力市", "翠峦区", "带岭区", "红星区", "美溪区", "南岔区", "五营区", "西林区", "新青区", "伊春区", "友好区", "金山屯区", "上甘岭区", "汤旺河区", "乌马河区", "乌伊岭区", "嘉荫县"],
                    "佳木斯市": ["富锦市", "同江市", "郊区", "东风区", "前进区", "向阳区", "抚远县", "桦川县", "桦南县", "汤原县"],
                    "牡丹江市": ["海林市", "穆棱市", "宁安市", "绥芬河市", "爱民区", "东安区", "西安区", "阳明区", "东宁县", "林口县"],
                    "七台河市": ["桃山区", "新兴区", "茄子河区", "勃利县"],
                    "双鸭山市": ["宝山区", "尖山区", "岭东区", "四方台区", "宝清县", "集贤县", "饶河县", "友谊县"],
                    "齐齐哈尔市": ["讷河市", "建华区", "龙沙区", "铁锋区", "昂昂溪区", "碾子山区", "富拉尔基区", "拜泉县", "富裕县", "甘南县", "克东县", "克山县", "龙江县", "泰来县", "依安县", "梅里斯达斡尔族区"],
                    "大兴安岭地区": ["呼中区", "松岭区", "新林区", "加格达奇区", "呼玛县", "漠河县", "塔河县"]
                },
                "上海市": {"上海市": ["宝山区", "奉贤区", "虹口区", "黄浦区", "嘉定区", "金山区", "静安区", "闵行区", "普陀区", "青浦区", "松江区", "徐汇区", "杨浦区", "闸北区", "长宁区", "浦东新区", "崇明县"]},
                "江苏省": {
                    "南京市": ["白下区", "高淳区", "鼓楼区", "建邺区", "江宁区", "溧水区", "六合区", "浦口区", "栖霞区", "秦淮区", "下关区", "玄武区", "雨花台区"],
                    "常州市": ["金坛市", "溧阳市", "天宁区", "武进区", "新北区", "钟楼区", "戚墅堰区"],
                    "淮安市": ["淮安区", "淮阴区", "清河区", "清浦区", "洪泽县", "金湖县", "涟水县", "盱眙县", "经济开发区"],
                    "南通市": ["海门市", "启东市", "如皋市", "崇川区", "港闸区", "开发区", "通州区", "海安县", "如东县", "南通经济技术开发区"],
                    "苏州市": ["常熟市", "昆山市", "太仓市", "张家港市", "姑苏区", "虎丘区", "吴江区", "吴中区", "相城区", "工业园"],
                    "宿迁市": ["宿城区", "宿豫区", "沭阳县", "泗洪县", "泗阳县"],
                    "泰州市": ["靖江市", "泰兴市", "兴化市", "高港区", "海陵区", "姜堰区", "开发区", "滨江工业园"],
                    "无锡市": ["江阴市", "宜兴市", "新区", "北塘区", "滨湖区", "崇安区", "惠山区", "南长区", "锡山区"],
                    "徐州市": ["邳州市", "新沂市", "鼓楼区", "贾汪区", "泉山区", "铜山区", "云龙区", "丰县", "沛县", "睢宁县"],
                    "盐城市": ["大丰市", "东台市", "亭湖区", "盐都区", "滨海县", "阜宁县", "建湖县", "射阳县", "响水县"],
                    "扬州市": ["高邮市", "仪征市", "广陵区", "邗江区", "江都区", "开发区", "宝应县"],
                    "镇江市": ["丹阳市", "句容市", "扬中市", "丹徒区", "京口区", "润州区"],
                    "连云港市": ["海州区", "连云区", "新浦区", "东海县", "赣榆县", "灌南县", "灌云县"]
                },
                "浙江省": {
                    "杭州市": ["建德市", "临安市", "滨江区", "富阳区", "拱墅区", "江干区", "上城区", "西湖区", "下城区", "萧山区", "余杭区", "淳安县", "桐庐县"],
                    "湖州市": ["南浔区", "吴兴区", "安吉县", "德清县", "长兴县"],
                    "嘉兴市": ["海宁市", "平湖市", "桐乡市", "南湖区", "秀洲区", "海盐县", "嘉善县"],
                    "金华市": ["东阳市", "兰溪市", "义乌市", "永康市", "金东区", "婺城区", "磐安县", "浦江县", "武义县"],
                    "丽水市": ["龙泉市", "莲都区", "缙云县", "青田县", "庆元县", "松阳县", "遂昌县", "云和县", "景宁畲族自治县"],
                    "宁波市": ["慈溪市", "奉化市", "余姚市", "北仑区", "海曙区", "江北区", "江东区", "鄞州区", "镇海区", "宁海县", "象山县"],
                    "绍兴市": ["嵊州市", "诸暨市", "柯桥区", "上虞区", "越城区", "新昌县"],
                    "台州市": ["临海市", "温岭市", "黄岩区", "椒江区", "路桥区", "三门县", "天台县", "仙居县", "玉环县"],
                    "温州市": ["乐清市", "瑞安市", "龙湾区", "鹿城区", "瓯海区", "苍南县", "洞头县", "平阳县", "泰顺县", "文成县", "永嘉县"],
                    "舟山市": ["定海区", "普陀区", "岱山县", "嵊泗县"],
                    "衢州市": ["江山市", "柯城区", "衢江区", "常山县", "开化县", "龙游县"]
                },
                "安徽省": {
                    "合肥市": ["巢湖市", "包河区", "庐阳区", "蜀山区", "瑶海区", "肥东县", "肥西县", "庐江县", "长丰县", "滨湖新区"],
                    "安庆市": ["桐城市", "大观区", "宜秀区", "迎江区", "枞阳县", "怀宁县", "潜山县", "太湖县", "望江县", "宿松县", "岳西县"],
                    "蚌埠市": ["蚌山区", "淮上区", "禹会区", "龙子湖区", "固镇县", "怀远县", "五河县", "高新技术开发区", "高新技术产业开发区"],
                    "池州市": ["贵池区", "东至县", "青阳县", "石台县"],
                    "滁州市": ["明光市", "天长市", "琅琊区", "南谯区", "定远县", "凤阳县", "来安县", "全椒县"],
                    "阜阳市": ["界首市", "颍东区", "颍泉区", "颍州区", "阜南县", "临泉县", "太和县", "颍上县", "阜阳经济技术开发区"],
                    "淮北市": ["杜集区", "烈山区", "相山区", "濉溪县"],
                    "淮南市": ["大通区", "潘集区", "八公山区", "田家庵区", "谢家集区", "凤台县", "高新技术产业开发区"],
                    "黄山市": ["黄山区", "徽州区", "屯溪区", "歙县", "黟县", "祁门县", "休宁县"],
                    "六安市": ["金安区", "裕安区", "寿县", "霍邱县", "霍山县", "金寨县", "舒城县"],
                    "宿州市": ["埇桥区", "泗县", "萧县", "砀山县", "灵璧县"],
                    "铜陵市": ["新城区", "狮子山区", "铜官山区", "铜陵县"],
                    "芜湖市": ["镜湖区", "鸠江区", "三山区", "弋江区", "繁昌县", "南陵县", "无为县", "芜湖县", "经济开发区", "经济技术开发区"],
                    "宣城市": ["宁国市", "宣州区", "泾县", "广德县", "绩溪县", "旌德县", "郎溪县"],
                    "亳州市": ["谯城区", "利辛县", "蒙城县", "涡阳县"],
                    "马鞍山市": ["博望区", "花山区", "雨山区", "和县", "当涂县", "含山县"]
                },
                "福建省": {
                    "福州市": ["福清市", "长乐市", "仓山区", "鼓楼区", "晋安区", "马尾区", "台江区", "连江县", "罗源县", "闽侯县", "闽清县", "平潭县", "永泰县"],
                    "龙岩市": ["漳平市", "新罗区", "永定区", "连城县", "上杭县", "武平县", "长汀县"],
                    "南平市": ["建瓯市", "建阳市", "邵武市", "武夷山市", "延平区", "光泽县", "浦城县", "顺昌县", "松溪县", "政和县"],
                    "宁德市": ["福安市", "福鼎市", "蕉城区", "古田县", "屏南县", "寿宁县", "霞浦县", "柘荣县", "周宁县"],
                    "莆田市": ["城厢区", "涵江区", "荔城区", "秀屿区", "仙游县"],
                    "泉州市": ["晋江市", "南安市", "石狮市", "丰泽区", "鲤城区", "洛江区", "泉港区", "安溪县", "德化县", "惠安县", "永春县"],
                    "三明市": ["永安市", "梅列区", "三元区", "沙县", "大田县", "建宁县", "将乐县", "明溪县", "宁化县", "清流县", "泰宁县", "尤溪县"],
                    "厦门市": ["海沧区", "湖里区", "集美区", "思明区", "同安区", "翔安区"],
                    "漳州市": ["龙海市", "龙文区", "芗城区", "东山县", "华安县", "南靖县", "平和县", "云霄县", "漳浦县", "长泰县", "诏安县"]
                },
                "江西省": {
                    "南昌市": ["东湖区", "湾里区", "西湖区", "青山湖区", "青云谱区", "安义县", "进贤县", "南昌县", "新建县", "红谷滩新区", "昌北经济技术开发区", "南昌高新技术开发区"],
                    "抚州市": ["临川区", "崇仁县", "东乡县", "广昌县", "金溪县", "乐安县", "黎川县", "南城县", "南丰县", "宜黄县", "资溪县", "金巢经济开发区"],
                    "赣州市": ["南康市", "瑞金市", "章贡区", "赣县", "安远县", "崇义县", "大余县", "定南县", "会昌县", "龙南县", "宁都县", "全南县", "上犹县", "石城县", "信丰县", "兴国县", "寻乌县", "于都县", "章江新区", "赣州市经济技术开发区"],
                    "吉安市": ["井冈山市", "吉州区", "青原区", "安福县", "吉安县", "吉水县", "遂川县", "泰和县", "万安县", "峡江县", "新干县", "永丰县", "永新县"],
                    "九江市": ["瑞昌市", "共青城市", "庐山区", "浔阳区", "德安县", "都昌县", "湖口县", "九江县", "彭泽县", "武宁县", "星子县", "修水县", "永修县", "城西港区", "九江经济开发区"],
                    "萍乡市": ["安源区", "湘东区", "莲花县", "芦溪县", "上栗县", "萍乡高新技术工业园区"],
                    "上饶市": ["德兴市", "信州区", "广丰县", "横峰县", "鄱阳县", "铅山县", "上饶县", "万年县", "婺源县", "弋阳县", "余干县", "玉山县", "上饶经济技术开发区"],
                    "新余市": ["渝水区", "分宜县", "高新经济技术开发区"],
                    "宜春市": ["丰城市", "高安市", "樟树市", "袁州区", "奉新县", "靖安县", "上高县", "铜鼓县", "万载县", "宜丰县", "马王塘经济开发区"],
                    "鹰潭市": ["贵溪市", "月湖区", "余江县", "鹰潭工业园"],
                    "景德镇市": ["乐平市", "昌江区", "珠山区", "浮梁县"]
                },
                "山东省": {
                    "济南市": ["章丘市", "槐荫区", "历城区", "历下区", "市中区", "天桥区", "长清区", "济阳县", "平阴县", "商河县", "高新技术开发区"],
                    "滨州市": ["滨城区", "博兴县", "惠民县", "无棣县", "阳信县", "沾化县", "邹平县", "滨州高新区", "滨州经济开发区"],
                    "德州市": ["乐陵市", "禹城市", "德城区", "陵县", "临邑县", "宁津县", "平原县", "齐河县", "庆云县", "武城县", "夏津县", "天衢工业园", "商贸开发区", "经济开发区"],
                    "东营市": ["东营区", "河口区", "广饶县", "垦利县", "利津县"],
                    "菏泽市": ["牡丹区", "曹县", "单县", "成武县", "定陶县", "东明县", "巨野县", "鄄城县", "郓城县"],
                    "济宁市": ["曲阜市", "兖州市", "邹城市", "任城区", "市中区", "嘉祥县", "金乡县", "梁山县", "泗水县", "微山县", "汶上县", "鱼台县"],
                    "莱芜市": ["钢城区", "莱城区"],
                    "聊城市": ["临清市", "东昌府区", "冠县", "莘县", "茌平县", "东阿县", "高唐县", "阳谷县", "经济技术开发区", "聊城经济技术开发区"],
                    "临沂市": ["河东区", "兰山区", "罗庄区", "费县", "苍山县", "莒南县", "临沭县", "蒙阴县", "平邑县", "郯城县", "沂南县", "沂水县"],
                    "青岛市": ["即墨市", "胶州市", "莱西市", "平度市", "城阳区", "黄岛区", "崂山区", "李沧区", "市北区", "市南区"],
                    "日照市": ["东港区", "岚山区", "莒县", "五莲县"],
                    "泰安市": ["肥城市", "新泰市", "岱岳区", "泰山区", "东平县", "宁阳县"],
                    "威海市": ["荣成市", "乳山市", "文登市", "环翠区", "高新技术开发区", "经济技术开发区", "高新技术产业开发区"],
                    "潍坊市": ["安丘市", "昌邑市", "高密市", "青州市", "寿光市", "诸城市", "坊子区", "寒亭区", "奎文区", "潍城区", "昌乐县", "临朐县", "高新技术开发区", "经济技术开发区", "高新技术产业开发区"],
                    "烟台市": ["海阳市", "莱阳市", "莱州市", "龙口市", "蓬莱市", "栖霞市", "招远市", "长岛县", "福山区", "高新区", "莱山区", "牟平区", "芝罘区"],
                    "枣庄市": ["滕州市", "高新区", "山亭区", "市中区", "薛城区", "峄城区", "台儿庄区"],
                    "淄博市": ["博山区", "临淄区", "张店区", "周村区", "淄川区", "高青县", "桓台县", "沂源县"]
                },
                "河南省": {
                    "郑州市": ["登封市", "巩义市", "新密市", "新郑市", "荥阳市", "二七区", "高新区", "惠济区", "金水区", "上街区", "中原区", "管城回族区", "中牟县", "郑东新区", "经济技术开发区"],
                    "安阳市": ["林州市", "北关区", "龙安区", "文峰区", "殷都区", "滑县", "安阳县", "内黄县", "汤阴县"],
                    "鹤壁市": ["鹤山区", "淇滨区", "山城区", "浚县", "淇县", "金山工业开发区"],
                    "焦作市": ["孟州市", "沁阳市", "解放区", "马村区", "山阳区", "中站区", "温县", "博爱县", "武陟县", "修武县"],
                    "济源市": ["北海街道", "济水街道", "沁园街道", "天坛街道", "五龙口镇", "玉泉街道", "承留镇", "大峪", "克井镇", "梨林镇", "坡头镇", "邵原镇", "思礼镇", "王屋镇", "下冶镇", "轵城镇"],
                    "开封市": ["鼓楼区", "金明区", "龙亭区", "禹王台区", "顺河回族区", "杞县", "开封县", "兰考县", "通许县", "尉氏县"],
                    "洛阳市": ["偃师市", "吉利区", "涧西区", "老城区", "洛龙区", "西工区", "瀍河回族区", "嵩县", "栾川县", "洛宁县", "孟津县", "汝阳县", "新安县", "伊川县", "宜阳县", "高新技术开发区", "经济技术开发区"],
                    "南阳市": ["邓州市", "高新区", "宛城区", "卧龙区", "方城县", "南召县", "内乡县", "社旗县", "唐河县", "桐柏县", "西峡县", "淅川县", "新野县", "镇平县"],
                    "商丘市": ["永城市", "梁园区", "睢阳区", "睢县", "民权县", "宁陵县", "夏邑县", "虞城县", "柘城县"],
                    "新乡市": ["辉县市", "卫辉市", "凤泉区", "红旗区", "牧野区", "卫滨区", "封丘县", "获嘉县", "新乡县", "延津县", "原阳县", "长垣县"],
                    "信阳市": ["平桥区", "浉河区", "息县", "新县", "固始县", "光山县", "淮滨县", "潢川县", "罗山县", "商城县", "羊山新区"],
                    "许昌市": ["禹州市", "长葛市", "魏都区", "襄城县", "许昌县", "鄢陵县"],
                    "周口市": ["项城市", "川汇区", "郸城县", "扶沟县", "淮阳县", "鹿邑县", "商水县", "沈丘县", "太康县", "西华县", "经济技术开发区"],
                    "漯河市": ["郾城区", "源汇区", "召陵区", "临颍县", "舞阳县"],
                    "濮阳市": ["华龙区", "范县", "南乐县", "濮阳县", "清丰县", "台前县"],
                    "三门峡市": ["灵宝市", "义马市", "湖滨区", "陕州区", "卢氏县", "渑池县"],
                    "平顶山市": ["汝州市", "舞钢市", "石龙区", "卫东区", "新城区", "新华区", "湛河区", "郏县", "叶县", "宝丰县", "鲁山县", "高新技术开发区"],
                    "驻马店市": ["驿城区", "泌阳县", "平舆县", "确山县", "汝南县", "上蔡县", "遂平县", "西平县", "新蔡县", "正阳县", "高新技术开发区"]
                },
                "湖北省": {
                    "武汉市": ["蔡甸区", "汉南区", "汉阳区", "洪山区", "黄陂区", "江岸区", "江汉区", "江夏区", "硚口区", "青山区", "武昌区", "新洲区", "东西湖区", "东湖新技术开发区", "武汉经济技术开发区", "武汉吴家山经济技术开发区"],
                    "鄂州市": ["鄂城区", "华容区", "梁子湖区", "葛店经济技术开发区"],
                    "黄冈市": ["麻城市", "武穴市", "黄州区", "红安县", "黄梅县", "罗田县", "蕲春县", "团风县", "浠水县", "英山县"],
                    "黄石市": ["大冶市", "铁山区", "下陆区", "黄石港区", "西塞山区", "阳新县"],
                    "荆门市": ["钟祥市", "东宝区", "掇刀区", "京山县", "沙洋县"],
                    "荆州市": ["洪湖市", "石首市", "松滋市", "荆州区", "沙市区", "公安县", "监利县", "江陵县"],
                    "十堰市": ["丹江口市", "茅箭区", "张湾区", "房县", "郧县", "郧西县", "竹山县", "竹溪县"],
                    "随州市": ["广水市", "曾都区", "随县"],
                    "咸宁市": ["赤壁市", "咸安区", "崇阳县", "嘉鱼县", "通城县", "通山县"],
                    "襄阳市": ["宜城市", "枣阳市", "老河口市", "襄城区", "襄州区", "樊城区", "保康县", "谷城县", "南漳县"],
                    "孝感市": ["安陆市", "汉川市", "应城市", "孝南区", "大悟县", "孝昌县", "云梦县"],
                    "宜昌市": ["当阳市", "宜都市", "枝江市", "点军区", "西陵区", "猇亭区", "夷陵区", "伍家岗区", "兴山县", "远安县", "秭归县", "长阳土家族自治县", "五峰土家族自治县"],
                    "神农架林区": ["红坪镇", "木鱼镇", "松柏镇", "新华镇", "阳日镇", "九湖乡", "宋洛乡", "下谷坪土家族乡"],
                    "潜江市": ["浩口镇", "老新镇", "龙湾镇", "王场镇", "熊口镇", "渔洋镇", "张金镇", "高石碑镇", "积玉口镇", "竹根滩镇", "园林高新技术开发区"],
                    "天门市": ["竟陵街道", "杨林街道", "侯口街道", "多宝镇", "干驿镇", "横林镇", "胡市镇", "黄潭镇", "蒋场镇", "九真镇", "卢市镇", "麻洋镇", "马湾镇", "彭市镇", "石河镇", "拖市镇", "汪场镇", "小板镇", "渔薪镇", "岳口镇", "皂市镇", "张港镇", "佛子山镇", "净潭乡", "天门工业园", "天门经济开发区", "国营蒋湖农场", "白茅湖棉花原种场"],
                    "仙桃市": ["沙嘴街道", "干河街道", "龙华山街道", "陈场镇", "剅河镇", "郭河镇", "彭场镇", "沙湖镇", "郑场镇", "通海口镇", "西流河镇", "长埫口镇", "沔城回族镇"],
                    "恩施土家族苗族自治州": ["恩施市", "利川市", "巴东县", "鹤峰县", "建始县", "来凤县", "咸丰县", "宣恩县"]
                },
                "湖南省": {
                    "长沙市": ["浏阳市", "芙蓉区", "开福区", "天心区", "望城区", "雨花区", "岳麓区", "长沙县", "宁乡县"],
                    "常德市": ["津市市", "鼎城区", "武陵区", "澧县", "安乡县", "汉寿县", "临澧县", "石门县", "桃源县", "西洞庭管理区"],
                    "郴州市": ["资兴市", "北湖区", "苏仙区", "安仁县", "桂东县", "桂阳县", "嘉禾县", "临武县", "汝城县", "宜章县", "永兴县"],
                    "衡阳市": ["常宁市", "耒阳市", "南岳区", "石鼓区", "雁峰区", "蒸湘区", "珠晖区", "衡东县", "衡南县", "衡山县", "衡阳县", "祁东县"],
                    "怀化市": ["洪江市", "鹤城区", "洪江区", "辰溪县", "会同县", "溆浦县", "沅陵县", "中方县", "麻阳苗族自治县", "通道侗族自治县", "新晃侗族自治县", "芷江侗族自治县", "靖州苗族侗族自治县"],
                    "娄底市": ["涟源市", "冷水江市", "娄星区", "双峰县", "新化县", "娄底经济开发区"],
                    "邵阳市": ["武冈市", "北塔区", "大祥区", "双清区", "洞口县", "隆回县", "邵东县", "邵阳县", "绥宁县", "新宁县", "新邵县", "城步苗族自治县"],
                    "湘潭市": ["韶山市", "湘乡市", "雨湖区", "岳塘区", "湘潭县"],
                    "益阳市": ["沅江市", "赫山区", "资阳区", "南县", "安化县", "桃江县"],
                    "永州市": ["零陵区", "冷水滩区", "道县", "东安县", "江永县", "蓝山县", "宁远县", "祁阳县", "双牌县", "新田县", "江华瑶族自治县"],
                    "岳阳市": ["临湘市", "汨罗市", "君山区", "岳阳楼区", "云溪区", "华容县", "平江县", "湘阴县", "岳阳县", "屈原管理区", "洞庭湖旅游度假区", "岳阳经济技术开发区"],
                    "株洲市": ["醴陵市", "荷塘区", "芦淞区", "石峰区", "天元区", "攸县", "茶陵县", "炎陵县", "株洲县", "云龙示范区"],
                    "张家界市": ["永定区", "武陵源区", "慈利县", "桑植县"],
                    "湘西土家族苗族自治州": ["吉首市", "保靖县", "凤凰县", "古丈县", "花垣县", "龙山县", "泸溪县", "永顺县"]
                },
                "广东省": {
                    "广州市": ["从化市", "增城市", "白云区", "番禺区", "海珠区", "花都区", "黄埔区", "荔湾区", "萝岗区", "南沙区", "天河区", "越秀区"],
                    "东莞市": ["东城街道", "莞城街道", "南城街道", "万江街道", "茶山镇", "常平镇", "大朗镇", "道滘镇", "东坑镇", "凤岗镇", "高埗镇", "横沥镇", "洪梅镇", "厚街镇", "虎门镇", "黄江镇", "寮步镇", "麻涌镇", "企石镇", "桥头镇", "清溪镇", "沙田镇", "石碣镇", "石龙镇", "石排镇", "塘厦镇", "谢岗镇", "长安镇", "中堂镇", "大岭山镇", "望牛墩镇", "樟木头镇"],
                    "潮州市": ["枫溪区", "湘桥区", "潮安县", "饶平县"],
                    "佛山市": ["禅城区", "高明区", "南海区", "三水区", "顺德区"],
                    "河源市": ["高新区", "源城区", "东源县", "和平县", "连平县", "龙川县", "紫金县", "高新技术开发区"],
                    "惠州市": ["惠城区", "惠阳区", "大亚湾区", "博罗县", "惠东县", "龙门县"],
                    "江门市": ["恩平市", "鹤山市", "开平市", "台山市", "江海区", "蓬江区", "新会区"],
                    "揭阳市": ["普宁市", "东山区", "揭东区", "普侨区", "榕城区", "大南山区", "惠来县", "揭西县", "试验区", "渔湖经济开发试验区"],
                    "茂名市": ["高州市", "化州市", "信宜市", "茂港区", "茂南区", "电白县"],
                    "梅州市": ["兴宁市", "梅江区", "梅县", "大埔县", "丰顺县", "蕉岭县", "平远县", "五华县"],
                    "清远市": ["连州市", "英德市", "清城区", "清新区", "佛冈县", "阳山县", "连南瑶族自治县", "连山壮族瑶族自治县"],
                    "汕头市": ["潮南区", "潮阳区", "澄海区", "濠江区", "金平区", "龙湖区", "南澳县"],
                    "汕尾市": ["陆丰市", "城区", "华侨区", "红海湾区", "海丰县", "陆河县"],
                    "韶关市": ["乐昌市", "南雄市", "曲江区", "武江区", "浈江区", "仁化县", "始兴县", "翁源县", "新丰县", "乳源瑶族自治县"],
                    "深圳市": ["宝安区", "福田区", "龙岗区", "罗湖区", "南山区", "盐田区", "光明新区", "龙华新区", "坪山新区", "大鹏新区"],
                    "阳江市": ["阳春市", "江城区", "阳东县", "阳西县", "海陵岛经济开发试验区"],
                    "云浮市": ["罗定市", "云城区", "新兴县", "郁南县", "云安县"],
                    "湛江市": ["雷州市", "廉江市", "吴川市", "赤坎区", "麻章区", "坡头区", "霞山区", "遂溪县", "徐闻县", "湛江经济技术开发区"],
                    "肇庆市": ["高要市", "四会市", "鼎湖区", "端州区", "德庆县", "封开县", "广宁县", "怀集县", "大旺高新技术开发区"],
                    "中山市": ["石岐区", "东区街道", "南区街道", "西区街道", "五桂山街道", "板芙镇", "大涌镇", "东凤镇", "东升镇", "阜沙镇", "港口镇", "古镇镇", "横栏镇", "黄圃镇", "民众镇", "南朗镇", "南头镇", "三角镇", "三乡镇", "沙溪镇", "神湾镇", "坦洲镇", "小榄镇", "火炬开发区"],
                    "珠海市": ["斗门区", "金湾区", "香洲区"]
                },
                "广西壮族自治区": {
                    "南宁市": ["江南区", "良庆区", "青秀区", "兴宁区", "邕宁区", "西乡塘区", "横县", "宾阳县", "隆安县", "马山县", "上林县", "武鸣县"],
                    "百色市": ["右江区", "德保县", "靖西县", "乐业县", "凌云县", "那坡县", "平果县", "田东县", "田林县", "田阳县", "西林县", "隆林各族自治县"],
                    "北海市": ["海城区", "银海区", "铁山港区", "合浦县"],
                    "崇左市": ["凭祥市", "江洲区", "大新县", "扶绥县", "龙州县", "宁明县", "天等县"],
                    "桂林市": ["叠彩区", "临桂区", "七星区", "象山区", "秀峰区", "雁山区", "灌阳县", "荔蒲县", "灵川县", "平乐县", "全州县", "兴安县", "阳朔县", "永福县", "资源县", "恭城瑶族自治县", "龙胜各族自治县"],
                    "贵港市": ["桂平市", "港北区", "港南区", "覃塘区", "平南县"],
                    "河池市": ["宜州市", "金城江区", "东兰县", "凤山县", "南丹县", "天峨县", "巴马瑶族自治县", "大化瑶族自治县", "都安瑶族自治县", "环江毛南族自治县", "罗城仫佬族自治县"],
                    "贺州市": ["八步区", "昭平县", "钟山县", "富川瑶族自治县", "平桂管理区"],
                    "来宾市": ["合山市", "兴宾区", "武宣县", "象州县", "忻城县", "金秀瑶族自治县"],
                    "柳州市": ["城中区", "柳北区", "柳南区", "鱼峰区", "柳城县", "柳江县", "鹿寨县", "融安县", "融水苗族自治县", "三江侗族自治县"],
                    "钦州市": ["钦北区", "钦南区", "灵山县", "浦北县", "钦州港经济技术开发区"],
                    "梧州市": ["岑溪市", "蝶山区", "龙圩区", "万秀区", "长洲区", "藤县", "苍梧县", "蒙山县"],
                    "玉林市": ["北流市", "福绵区", "玉州区", "容县", "博白县", "陆川县", "兴业县"],
                    "防城港市": ["东兴市", "防城区", "港口区", "上思县", "行政中心区"]
                },
                "海南省": {
                    "海口市": ["龙华区", "美兰区", "琼山区", "秀英区"],
                    "三亚市": ["河东区", "河西区", "凤凰镇", "吉阳镇", "海棠湾镇"],
                    "白沙黎族自治县": ["牙叉镇", "其它"],
                    "保亭黎族苗族自治县": ["保城镇", "其它"],
                    "昌江黎族自治县": ["石碌镇", "其它"],
                    "澄迈县": ["金江镇", "老城镇", "其它"],
                    "儋州市": ["大成镇", "海头镇", "和庆镇", "那大镇", "南丰镇", "王五镇", "洋浦经济开发区", "其它"],
                    "定安县": ["定城镇", "翰林镇", "龙河镇", "龙门镇", "其它"],
                    "东方市": ["八所镇", "其它"],
                    "乐东黎族自治县": ["抱由镇", "其它"],
                    "临高县": ["波莲镇", "博厚镇", "东英镇", "多文镇", "和舍镇", "皇桐镇", "临城镇", "南宝镇", "调楼镇", "新盈镇", "其它"],
                    "陵水黎族自治县": ["本号镇", "椰林镇", "英州镇", "群英乡", "提蒙乡", "其它"],
                    "琼海市": ["博鳌镇", "嘉积镇", "其它"],
                    "琼中黎族苗族自治县": ["营根镇", "其它"],
                    "屯昌县": ["屯昌镇", "屯城镇", "其它"],
                    "万宁市": ["万城镇", "兴隆镇", "其它"],
                    "文昌市": ["昌洒镇", "会文镇", "锦山镇", "铺前镇", "清澜镇", "潭牛镇", "文城镇", "翁田镇", "其它"],
                    "五指山市": ["冲山镇", "其它"],
                    "三沙市": ["南沙群岛的岛礁及其海域", "西沙群岛的岛礁及其海域", "中沙群岛的岛礁及其海域"]
                },
                "重庆市": {"重庆市": ["巴南区", "北碚区", "大足区", "涪陵区", "高新区", "合川区", "江北区", "江津区", "南岸区", "南川区", "綦江区", "黔江区", "双桥区", "万盛区", "万州区", "永川区", "渝北区", "渝中区", "长寿区", "大渡口区", "九龙坡区", "沙坪坝区", "开县", "忠县", "璧山县", "城口县", "垫江县", "丰都县", "奉节县", "梁平县", "荣昌县", "铜梁县", "潼南县", "巫山县", "巫溪县", "武隆县", "云阳县", "石柱土家族自治县", "彭水苗族土家族自治县", "秀山土家族苗族自治县", "酉阳土家族苗族自治县"]},
                "四川省": {
                    "成都市": ["崇州市", "彭州市", "邛崃市", "都江堰市", "成华区", "高新区", "金牛区", "锦江区", "青羊区", "温江区", "武侯区", "新都区", "高新西区", "龙泉驿区", "青白江区", "郫县", "大邑县", "金堂县", "蒲江县", "双流县", "新津县"],
                    "巴中市": ["巴州区", "恩阳区", "南江县", "平昌县", "通江县"],
                    "达州市": ["万源市", "通川区", "达县", "渠县", "大竹县", "开江县", "宣汉县"],
                    "德阳市": ["广汉市", "绵竹市", "什邡市", "旌阳区", "罗江县", "中江县"],
                    "广安市": ["华蓥市", "广安区", "前锋区", "邻水县", "武胜县", "岳池县"],
                    "广元市": ["朝天区", "利州区", "昭化区", "苍溪县", "剑阁县", "青川县", "旺苍县"],
                    "乐山市": ["峨眉山市", "沙湾区", "市中区", "金口河区", "五通桥区", "夹江县", "犍为县", "井研县", "沐川县", "峨边彝族自治县", "马边彝族自治县"],
                    "眉山市": ["东坡区", "丹棱县", "洪雅县", "彭山县", "青神县", "仁寿县"],
                    "绵阳市": ["江油市", "涪城区", "游仙区", "安县", "平武县", "三台县", "盐亭县", "梓潼县", "北川羌族自治县", "高新技术开发区"],
                    "南充市": ["阆中市", "高坪区", "嘉陵区", "顺庆区", "南部县", "蓬安县", "西充县", "仪陇县", "营山县"],
                    "内江市": ["东兴区", "市中区", "隆昌县", "威远县", "资中县"],
                    "遂宁市": ["安居区", "船山区", "河东新区", "大英县", "蓬溪县", "射洪县"],
                    "雅安市": ["名山区", "雨城区", "宝兴县", "汉源县", "芦山县", "石棉县", "天全县", "荥经县"],
                    "宜宾市": ["翠屏区", "南溪区", "高县", "珙县", "江安县", "筠连县", "屏山县", "兴文县", "宜宾县", "长宁县"],
                    "资阳市": ["简阳市", "雁江区", "安岳县", "乐至县"],
                    "自贡市": ["大安区", "贡井区", "沿滩区", "自流井区", "荣县", "富顺县", "汇东新区"],
                    "泸州市": ["江阳区", "纳溪区", "龙马潭区", "泸县", "古蔺县", "合江县", "叙永县"],
                    "攀枝花市": ["东区", "西区", "仁和区", "米易县", "盐边县"],
                    "甘孜藏族自治州": ["巴塘县", "白玉县", "丹巴县", "道孚县", "稻城县", "得荣县", "德格县", "甘孜县", "九龙县", "康定县", "理塘县", "炉霍县", "泸定县", "色达县", "石渠县", "乡城县", "新龙县", "雅江县"],
                    "凉山彝族自治州": ["西昌市", "布拖县", "德昌县", "甘洛县", "会东县", "会理县", "金阳县", "雷波县", "美姑县", "冕宁县", "宁南县", "普格县", "喜德县", "盐源县", "越西县", "昭觉县", "木里藏族自治县"],
                    "阿坝藏族羌族自治州": ["理县", "茂县", "阿坝县", "黑水县", "红原县", "金川县", "壤塘县", "松潘县", "汶川县", "小金县", "九寨沟县", "马尔康县", "若尔盖县"]
                },
                "贵州省": {
                    "贵阳市": ["清镇市", "白云区", "花溪区", "南明区", "乌当区", "云岩区", "开阳县", "息烽县", "修文县", "金阳新区"],
                    "安顺市": ["开发区", "西秀区", "平坝县", "普定县", "关岭布依族苗族自治县", "镇宁布依族苗族自治县", "紫云苗族布依族自治县"],
                    "遵义市": ["赤水市", "仁怀市", "汇川区", "红花岗区", "凤冈县", "湄潭县", "绥阳县", "桐梓县", "习水县", "余庆县", "正安县", "遵义县", "道真仡佬族苗族自治县", "务川仡佬族苗族自治县"],
                    "六盘水市": ["钟山区", "六枝特区", "盘县", "水城县", "红桥新区"],
                    "铜仁市": ["碧江区", "万山区", "德江县", "江口县", "石阡县", "思南县", "松桃苗族自治县", "玉屏侗族自治县", "沿河土家族自治县", "印江土家族苗族自治县"],
                    "毕节市": ["七星关区", "大方县", "赫章县", "金沙县", "纳雍县", "黔西县", "织金县", "威宁彝族回族苗族自治县"],
                    "黔东南苗族侗族自治州": ["凯里市", "岑巩县", "从江县", "丹寨县", "黄平县", "剑河县", "锦屏县", "雷山县", "黎平县", "麻江县", "榕江县", "三穗县", "施秉县", "台江县", "天柱县", "镇远县"],
                    "黔南布依族苗族自治州": ["都匀市", "福泉市", "独山县", "贵定县", "惠水县", "荔波县", "龙里县", "罗甸县", "平塘县", "瓮安县", "长顺县", "三都水族自治县"],
                    "黔西南布依族苗族自治州": ["兴义市", "安龙县", "册亨县", "普安县", "晴隆县", "望谟县", "兴仁县", "贞丰县"]
                },
                "云南省": {
                    "昆明市": ["安宁市", "呈贡区", "东川区", "官渡区", "盘龙区", "五华区", "西山区", "富民县", "晋宁县", "嵩明县", "宜良县", "石林彝族自治县", "禄劝彝族苗族自治县", "寻甸回族彝族自治县"],
                    "保山市": ["隆阳区", "昌宁县", "龙陵县", "施甸县", "腾冲县"],
                    "丽江市": ["古城区", "华坪县", "永胜县", "宁蒗彝族自治县", "玉龙纳西族自治县"],
                    "普洱市": ["思茅区", "景东彝族自治县", "西盟佤族自治县", "宁蒗彝族自治县", "墨江哈尼族自治县", "景谷傣族彝族自治县", "江城哈尼族彝族自治县", "宁洱哈尼族彝族自治县", "孟连傣族拉祜族佤族自治县", "镇沅彝族哈尼族拉祜族自治县"],
                    "临沧市": ["临翔区", "云县", "凤庆县", "永德县", "镇康县", "沧源佤族自治县", "耿马傣族佤族自治县", "双江拉祜族佤族布朗族傣族自治县"],
                    "曲靖市": ["宣威市", "麒麟区", "富源县", "会泽县", "陆良县", "罗平县", "马龙县", "师宗县", "沾益县"],
                    "玉溪市": ["红塔区", "澄江县", "华宁县", "江川县", "通海县", "易门县", "峨山彝族自治县", "新平彝族傣族自治县", "元江哈尼族彝族傣族自治县"],
                    "昭通市": ["昭阳区", "大关县", "鲁甸县", "巧家县", "水富县", "绥江县", "威信县", "盐津县", "彝良县", "永善县", "镇雄县"],
                    "楚雄彝族自治州": ["楚雄市", "大姚县", "禄丰县", "牟定县", "南华县", "双柏县", "武定县", "姚安县", "永仁县", "元谋县"],
                    "迪庆藏族自治州": ["德钦县", "香格里拉县", "维西傈僳族自治县"],
                    "大理白族自治州": ["大理市", "宾川县", "洱源县", "鹤庆县", "剑川县", "弥渡县", "祥云县", "永平县", "云龙县", "漾濞彝族自治县", "南涧彝族自治县", "巍山彝族回族自治县"],
                    "文山壮族苗族自治州": ["文山市", "富宁县", "广南县", "马关县", "丘北县", "西畴县", "砚山县", "麻栗坡县"],
                    "怒江傈僳族自治州": ["福贡县", "泸水县", "贡山独龙族怒族自治县", "兰坪白族普米族自治县"],
                    "西双版纳傣族自治州": ["景洪市", "勐海县", "勐腊县"],
                    "德宏傣族景颇族自治州": ["芒市", "瑞丽市", "梁河县", "陇川县", "盈江县"],
                    "红河哈尼族彝族自治州": ["个旧市", "开远市", "蒙自市", "红河县", "建水县", "泸西县", "绿春县", "弥勒县", "石屏县", "元阳县", "河口瑶族自治县", "屏边苗族自治县", "金平苗族瑶族傣族自治县"]
                },
                "西藏自治区": {
                    "拉萨市": ["城关区", "达孜县", "当雄县", "林周县", "尼木县", "曲水县", "堆龙德庆县", "墨竹工卡县"],
                    "阿里地区": ["措勤县", "噶尔县", "改则县", "革吉县", "普兰县", "日土县", "札达县"],
                    "昌都市": ["卡若区", "八宿县", "边坝县", "察雅县", "丁青县", "贡觉县", "江达县", "洛隆县", "芒康县", "左贡县", "类乌齐县"],
                    "林芝地区": ["朗县", "波密县", "察隅县", "林芝县", "米林县", "墨脱县", "工布江达县"],
                    "那曲地区": ["索县", "安多县", "巴青县", "班戈县", "比如县", "嘉黎县", "那曲县", "尼玛县", "聂荣县", "申扎县"],
                    "山南地区": ["措美县", "错那县", "贡嘎县", "加查县", "隆子县", "洛扎县", "乃东县", "琼结县", "曲松县", "桑日县", "扎囊县", "浪卡子县"],
                    "日喀则市": ["桑珠孜区", "昂仁县", "白朗县", "定结县", "定日县", "岗巴县", "吉隆县", "江孜县", "康马县", "拉孜县", "仁布县", "萨嘎县", "萨迦县", "亚东县", "仲巴县", "南木林县", "聂拉木县", "谢通门县"]
                },
                "陕西省": {
                    "西安市": ["灞桥区", "碑林区", "莲湖区", "临潼区", "未央区", "新城区", "阎良区", "雁塔区", "长安区", "户县", "高陵县", "蓝田县", "周至县", "高新技术开发区", "西安经济技术开发区"],
                    "宝鸡市": ["陈仓区", "金台区", "渭滨区", "凤县", "陇县", "眉县", "凤翔县", "扶风县", "麟游县", "岐山县", "千阳县", "太白县", "高新技术产业开发区"],
                    "安康市": ["汉滨区", "白河县", "汉阴县", "岚皋县", "宁陕县", "平利县", "石泉县", "旬阳县", "镇坪县", "紫阳县"],
                    "汉中市": ["汉台区", "勉县", "洋县", "城固县", "佛坪县", "留坝县", "略阳县", "南郑县", "宁强县", "西乡县", "镇巴县", "北开发区"],
                    "商洛市": ["商州区", "丹凤县", "洛南县", "山阳县", "商南县", "柞水县", "镇安县"],
                    "铜川市": ["王益区", "耀州区", "印台区", "宜君县", "铜川新区"],
                    "渭南市": ["韩城市", "华阴市", "临渭区", "华县", "白水县", "澄城县", "大荔县", "富平县", "合阳县", "蒲城县", "潼关县", "高新经济开发区"],
                    "咸阳市": ["兴平市", "秦都区", "渭城区", "杨陵区", "彬县", "乾县", "淳化县", "泾阳县", "礼泉县", "三原县", "武功县", "旬邑县", "永寿县", "长武县"],
                    "延安市": ["宝塔区", "富县", "安塞县", "甘泉县", "黄陵县", "黄龙县", "洛川县", "吴起县", "延川县", "延长县", "宜川县", "志丹县", "子长县"],
                    "榆林市": ["榆阳区", "佳县", "定边县", "府谷县", "横山县", "靖边县", "米脂县", "清涧县", "神木县", "绥德县", "吴堡县", "子洲县"]
                },
                "甘肃省": {
                    "兰州市": ["安宁区", "城关区", "红古区", "西固区", "七里河区", "皋兰县", "永登县", "榆中县"],
                    "白银市": ["白银区", "平川区", "会宁县", "景泰县", "靖远县"],
                    "定西市": ["安定区", "岷县", "漳县", "临洮县", "陇西县", "通渭县", "渭源县"],
                    "陇南市": ["武都区", "成县", "徽县", "康县", "礼县", "文县", "宕昌县", "两当县", "西和县"],
                    "金昌市": ["金川区", "永昌县"],
                    "酒泉市": ["敦煌市", "玉门市", "肃州区", "瓜州县", "金塔县", "肃北蒙古族自治县", "阿克塞哈萨克族自治县"],
                    "庆阳市": ["西峰区", "环县", "宁县", "合水县", "华池县", "庆城县", "镇原县", "正宁县"],
                    "天水市": ["北道区", "秦城区", "甘谷县", "秦安县", "清水县", "武山县", "张家川回族自治县"],
                    "武威市": ["凉州区", "古浪县", "民勤县", "天祝藏族自治县"],
                    "张掖市": ["甘州区", "高台县", "临泽县", "民乐县", "山丹县", "肃南裕固族自治县"],
                    "平凉市": ["崆峒区", "崇信县", "华亭县", "泾川县", "静宁县", "灵台县", "庄浪县"],
                    "嘉峪关市": ["朝阳街道", "建设街道", "前进街道", "胜利街道", "五一街道", "新华街道", "峪苑街道"],
                    "临夏回族自治州": ["临夏市", "广河县", "和政县", "康乐县", "临夏县", "永靖县", "东乡族自治县", "积石山保安族东乡族撒拉族自治县"],
                    "甘南藏族自治州": ["合作市", "迭部县", "临潭县", "碌曲县", "玛曲县", "夏河县", "舟曲县", "卓尼县"]
                },
                "青海省": {
                    "西宁市": ["城北区", "城东区", "城西区", "城中区", "湟源县", "湟中县", "大通回族土族自治县"],
                    "海东市": ["乐都县", "平安县", "互助土族自治县", "化隆回族自治县", "循化撒拉族自治县", "民和回族土族自治县"],
                    "果洛藏族自治州": ["班玛县", "达日县", "甘德县", "久治县", "玛多县", "玛沁县"],
                    "海北藏族自治州": ["刚察县", "海晏县", "祁连县", "门源回族自治县"],
                    "海南藏族自治州": ["共和县", "贵德县", "贵南县", "同德县", "兴海县"],
                    "黄南藏族自治州": ["尖扎县", "同仁县", "泽库县", "河南蒙古族自治县"],
                    "玉树藏族自治州": ["玉树市", "称多县", "囊谦县", "杂多县", "治多县", "曲麻莱县"],
                    "海西蒙古族藏族自治州": ["德令哈市", "格尔木市", "都兰县", "天峻县", "乌兰县", "冷湖行政区", "茫崖行政区", "大柴旦行政区"]
                },
                "宁夏回族自治区": {
                    "银川市": ["灵武市", "金凤区", "西夏区", "兴庆区", "贺兰县", "永宁县"],
                    "固原市": ["原州区", "泾源县", "隆德县", "彭阳县", "西吉县"],
                    "吴忠市": ["青铜峡市", "利通区", "红寺堡区", "同心县", "盐池县"],
                    "中卫市": ["沙坡头区", "海原县", "中宁县"],
                    "石嘴山市": ["惠农区", "大武口区", "平罗县"]
                },
                "新疆维吾尔自治区": {
                    "乌鲁木齐市": ["米东区", "天山区", "新市区", "达坂城区", "水磨沟区", "头屯河区", "沙依巴克区", "乌鲁木齐县", "经济技术开发区"],
                    "石河子市": ["东城街道", "红山街道", "老街街道", "向阳街道", "其它"],
                    "克拉玛依市": ["白碱滩区", "独山子区", "乌尔禾区", "克拉玛依区"],
                    "哈密地区": ["哈密市", "伊吾县", "巴里坤哈萨克自治县"],
                    "和田地区": ["和田市", "策勒县", "和田县", "洛浦县", "民丰县", "墨玉县", "皮山县", "于田县"],
                    "塔城地区": ["塔城市", "乌苏市", "额敏县", "沙湾县", "托里县", "裕民县", "和布克赛尔蒙古自治县"],
                    "喀什地区": ["喀什市", "巴楚县", "伽师县", "莎车县", "疏附县", "疏勒县", "叶城县", "泽普县", "麦盖提县", "英吉沙县", "岳普湖县", "塔什库尔干塔吉克自治县"],
                    "阿克苏地区": ["阿克苏市", "拜城县", "柯坪县", "库车县", "沙雅县", "温宿县", "乌什县", "新和县", "阿瓦提县"],
                    "阿勒泰地区": ["阿勒泰市", "福海县", "富蕴县", "青河县", "布尔津县", "哈巴河县", "吉木乃县"],
                    "吐鲁番地区": ["吐鲁番市", "鄯善县", "托克逊县"],
                    "阿拉尔市": ["其它"],
                    "五家渠市": ["军垦路街道", "人民路街道", "其它"],
                    "图木舒克市": ["其它"],
                    "北屯市": ["其它"],
                    "铁门关市": ["其它"],
                    "双河市": ["其它"],
                    "昌吉回族自治州": ["昌吉市", "阜康市", "奇台县", "呼图壁县", "玛纳斯县", "吉木萨尔县", "木垒哈萨克自治县"],
                    "伊犁哈萨克自治州": ["奎屯市", "伊宁市", "霍尔果斯市", "巩留县", "霍城县", "新源县", "伊宁县", "昭苏县", "尼勒克县", "特克斯县", "察布查尔锡伯自治县"],
                    "巴音郭楞蒙古自治州": ["库尔勒市", "博湖县", "和静县", "和硕县", "轮台县", "且末县", "若羌县", "尉犁县", "焉耆回族自治县"],
                    "博尔塔拉蒙古自治州": ["博乐市", "阿拉山口市", "精河县", "温泉县"],
                    "克孜勒苏柯尔克孜自治州": ["阿图什市", "乌恰县", "阿合奇县", "阿克陶县"]
                },
                "香港特别行政区": {"香港特别行政区": ["香港岛", "新界", "九龙", "离岛"]},
                "澳门特别行政区": {"澳门特别行政区": ["澳门半岛", "氹仔", "路环"]},
                "台湾": {
                    "台北市": ["大安区", "大同区", "内湖区", "南港区", "松山区", "万华区", "文山区", "信义区", "中山区", "中正区", "北投区", "士林区"],
                    "新北市": ["林口区", "莺歌区", "八里区", "板桥区", "淡水区", "芦洲区", "三重区", "深坑区", "树林区", "泰山区", "土城区", "五股区", "新庄区", "永和区", "中和区", "万里区", "金山区", "石碇区", "瑞芳区", "贡寮区", "坪林区", "乌来区", "三芝区", "石门区", "平溪区", "双溪区", "三峡区", "汐止区", "新店区"],
                    "台中市": ["北区", "北屯区", "大安区", "大肚区", "大甲区", "大里区", "大雅区", "东区", "丰原区", "后里区", "龙井区", "南区", "南屯区", "清水区", "三义乡", "沙鹿区", "神冈区", "石冈区", "潭子区", "通宵镇", "外埔区", "乌日区", "梧栖区", "西区", "西屯区", "苑里镇", "中区", "太平区", "雾峰区", "东势镇", "和平乡", "新社乡"],
                    "台南市": ["安定区", "安南区", "安平区", "北区", "东区", "永康区", "归仁区", "仁德区", "关庙区", "官田区", "佳里区", "六甲区", "麻豆区", "南区山", "上区", "善化区", "西港区", "西区", "新市区", "中区", "新化区", "新营区", "左镇区", "玉井区", "南化区", "楠西区", "龙崎区", "七股区", "将军区", "学甲区", "北门区", "后壁区", "白河区", "东山区", "下营区", "柳营区", "盐水区", "大内区"],
                    "高雄市": ["阿莲区", "大寮区", "大社区", "大树区", "凤山区", "冈山区", "鼓山区", "湖内区", "林园区", "苓雅区", "路竹区", "楠梓区", "鸟松区", "旗津区", "前金区", "前镇区", "桥头区", "仁武区", "三民区", "小港区", "新兴区", "盐埕区", "燕巢区", "永安区", "梓官区", "左营区", "田寮乡", "六龟乡", "内门乡", "茂林乡", "桃源乡", "甲仙乡", "弥陀乡", "旗山镇", "美浓镇", "那玛夏乡", "茄萣乡", "杉林乡"],
                    "基隆市": ["七堵区", "中山区", "中正区", "仁爱区", "信义区", "安乐区", "暖暖区"],
                    "新竹市": ["东区", "北区", "香山区"],
                    "嘉义市": ["东区", "西区"],
                    "桃园县": ["桃园市", "中坜市", "平镇市", "八德市", "大溪镇", "大园乡", "观音乡", "龟山乡", "复兴乡", "龙潭乡", "芦竹乡", "新屋乡", "杨梅市"],
                    "新竹县": ["竹北市", "湖口乡", "新丰乡", "新埔镇", "关西镇", "芎林乡", "竹东镇", "峨眉乡", "宝山乡", "五峰乡", "横山乡", "北埔乡", "尖石乡"],
                    "苗栗县": ["竹南镇", "头份镇", "三湾乡", "后龙镇", "通霄镇", "苑里镇", "苗栗市", "造桥乡", "头屋乡", "公馆乡", "铜锣乡", "三义乡", "西湖乡", "南庄乡", "狮潭乡", "大湖乡", "泰安乡", "卓兰镇"],
                    "彰化县": ["北斗镇", "草屯镇", "大村乡", "二水乡", "芳苑乡", "芬园乡", "福兴乡", "和美镇", "花坛乡", "鹿港镇", "南投市", "埤头乡", "埔心乡", "埔盐乡", "社头乡", "伸港乡", "田尾乡", "田中镇", "溪湖镇", "线西乡", "秀水乡", "永靖乡", "员林镇", "彰化市", "二林镇", "大城乡", "竹塘乡", "溪州乡"],
                    "南投县": ["埔里镇", "竹山镇", "集集镇", "名间乡", "鹿谷乡", "中寮乡", "鱼池乡", "国姓乡", "水里乡", "信义乡", "仁爱乡", "南投巿", "草屯镇", "琉球乡"],
                    "云林县": ["大埤乡", "土库镇", "林内乡", "莿桐乡", "西螺镇", "仑背乡", "古坑乡", "褒忠乡", "东势乡", "台西乡", "麦寮乡", "二仑乡", "北港镇", "水林乡", "口湖乡", "四湖乡", "元长乡", "斗六市", "斗南镇", "虎尾镇"],
                    "嘉义县": ["竹崎乡", "番路乡", "梅山乡", "阿里山乡", "东石乡", "大埔乡", "溪口乡", "义竹乡", "布袋镇", "大林镇", "六脚乡", "鹿草乡", "民雄乡", "朴子市", "水上乡", "太保市", "新港乡", "中埔乡"],
                    "屏东县": ["屏东市", "万丹乡", "长治乡", "内埔乡", "潮州镇", "三地门乡", "来义乡", "狮子乡", "牡丹乡", "高树乡", "满州乡", "万峦乡", "春日乡", "雾台乡", "泰武乡", "玛家乡", "恒春镇", "枋寮乡", "东港镇", "林边乡", "枋山乡", "里港乡", "车城乡", "盐埔乡", "九如乡", "新园乡", "新埤乡", "佳冬乡", "竹田乡", "南州乡", "崁顶乡", "麟洛乡"],
                    "宜兰县": ["头城镇", "宜兰市", "礁溪乡", "壮围乡", "五结乡", "罗东镇", "员山乡", "南澳乡", "冬山乡", "大同乡", "三星乡", "苏澳镇"],
                    "花莲县": ["花莲巿", "光复乡", "玉里镇", "新城乡", "吉安乡", "寿丰乡", "凤林镇", "丰滨乡", "瑞穗乡", "富里乡", "秀林乡", "万荣乡", "卓溪乡"],
                    "台东县": ["台东巿", "成功镇", "关山镇", "卑南乡", "大武乡", "太麻里乡", "东河乡", "长滨乡", "鹿野乡", "池上乡", "延平乡", "海端乡", "达仁乡", "金峰乡"],
                    "澎湖县": ["马公市", "湖西乡", "白沙乡", "西屿乡", "望安乡", "七美乡"],
                    "金门县": ["金城镇", "金湖镇", "金沙镇", "金宁乡", "烈屿乡", "乌丘乡"],
                    "连江县": ["南竿乡", "北竿乡", "莒光乡", "东引乡"]
                },
                "海外": {"其它": ["其它"]}
            });
            var t = e('<div class="fui_address-select"/>').appendTo(this.element), i = this, a = this.options, s = [];
            FX.Utils.forEach(FX.AddressData, function (e) {
                s.push({value: e, text: e})
            }), this.province = FX.createWidget({
                type: "combo",
                customCls: "sel-province",
                items: s,
                renderEl: e("<div/>").appendTo(t),
                allowBlank: a.allowBlank,
                width: a.width4province,
                waterMark: "省/自治区/直辖市",
                onAfterItemSelect: function () {
                    i.linkByProvince(this.getValue()), FX.Utils.applyFunc(i, a.onStopEdit, [], !1)
                }
            }), this.city = FX.createWidget({
                type: "combo",
                customCls: "sel-city",
                items: [],
                renderEl: e("<div/>").appendTo(t),
                allowBlank: a.allowBlank,
                width: a.width4city,
                waterMark: "市",
                onAfterItemSelect: function () {
                    i.linkByProvinceAndCity(i.province.getValue(), this.getValue()), FX.Utils.applyFunc(i, a.onStopEdit, [], !1)
                }
            }), this.district = FX.createWidget({
                type: "combo",
                renderEl: e("<div/>").appendTo(t),
                customCls: "sel-district",
                allowBlank: a.allowBlank,
                width: a.width4district,
                waterMark: "区/县",
                items: [],
                onAfterItemSelect: function () {
                    FX.Utils.applyFunc(i, a.onStopEdit, [], !1)
                }
            }), a.needDetail ? this.detail = FX.createWidget({
                type: "textarea",
                customCls: "address-detail",
                waterMark: "详细地址",
                allowBlank: a.allowBlank,
                width: a.width4detail,
                renderEl: e("<div/>").appendTo(this.element),
                onStopEdit: function () {
                    FX.Utils.applyFunc(i, a.onStopEdit, [], !1)
                }
            }) : this.element.addClass("no-detail")
        }, linkByProvince: function (e) {
            var t = [];
            FX.Utils.forEach(FX.AddressData[e], function (e) {
                t.push({value: e, text: e})
            }), this.city.options.items = t, this.district.options.items = [], this.city.rebuild(), this.district.rebuild()
        }, linkByProvinceAndCity: function (e, t) {
            var i = FX.AddressData[e];
            if (i) {
                var a = [];
                FX.Utils.forEach(i[t], function (e, t) {
                    a.push({value: t, text: t})
                }), this.district.options.items = a
            } else this.district.options.items = [];
            this.district.rebuild()
        }, setEnable: function (e) {
            this.options.enable = !!e, this.province.setEnable(e), this.city.setEnable(e), this.district.setEnable(e), this.detail && this.detail.setEnable(e)
        }, checkValidate: function () {
            var e = this.province.checkValidate() && this.city.checkValidate() && this.district.checkValidate();
            return this.detail && (e = this.detail.checkValidate() && e), e
        }, setValue: function (e) {
            if (e && (FX.Utils.isEmpty(e.detail) || this.detail && this.detail.setValue(e.detail), !FX.Utils.isEmpty(e.province))) return this.province.setValue(e.province), this.linkByProvince(e.province), void(FX.Utils.isEmpty(e.city) || (this.city.setValue(e.city), this.linkByProvinceAndCity(e.province, e.city), FX.Utils.isEmpty(e.district) || this.district.setValue(e.district)));
            this.province.setValue(null), this.linkByProvince(null), this.detail && this.detail.setValue(null)
        }, getValue: function () {
            var e = {}, t = this.province.getValue(), i = this.city.getValue(), a = this.district.getValue(),
                s = this.detail ? this.detail.getValue() : null;
            return FX.Utils.isEmpty(t) || (e.province = t), FX.Utils.isEmpty(i) || (e.city = i), FX.Utils.isEmpty(a) || (e.district = a), FX.Utils.isEmpty(s) || (e.detail = s), e
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Address.superclass.getOptions.apply(this, arguments), {needDetail: t.needDetail})
        }, getNullValue: function () {
            return {}
        }
    }), e.shortcut("address", FX.Address)
}(jQuery), function (e) {
    FX.Location = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Location.superclass._defaultConfig.apply(), {
                baseCls: "fui_location",
                allowBlank: !0,
                locationText: "获取当前位置",
                hasBrief: !0,
                btnWidth: 240,
                btnHeight: 36,
                isValueVisible: !0
            })
        }, _init: function () {
            FX.Location.superclass._init.apply(this, arguments);
            var t = this.options;
            this.button = new FX.Button({
                renderEl: e('<div class="location-btn"/>').appendTo(this.element),
                text: t.locationText,
                style: "white",
                width: t.btnWidth,
                height: t.btnHeight
            }), t.hasBrief && e('<span class="location-tip"/>').text("请在移动端打开表单获取位置信息").appendTo(this.element)
        }, checkValidate: function () {
            return this.options.allowBlank || !FX.Utils.isObjectEmpty(this.value)
        }, setValue: function (t) {
            var i = this.options;
            if (this.value = t, !FX.Utils.isObjectEmpty(t) && i.isValueVisible) {
                var a = t.province + t.city + t.district + t.detail;
                if (this.$info) this.$info.text(a); else if (this.$info = e('<div class="location-info"/>').prependTo(this.element).append("<span>" + a + "</span>"), i.lnglatVisible) {
                    var s = "";
                    t.lnglatXY && t.lnglatXY.length && (s = "经度：" + FX.Utils.fixDecimalPrecision(t.lnglatXY[0], 6) + "，纬度：" + FX.Utils.fixDecimalPrecision(t.lnglatXY[1], 6)), e('<div class="sub-info">' + s + "</div>").appendTo(this.$info)
                }
            }
        }, getValue: function () {
            return this.value || {}
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Location.superclass.getOptions.apply(this, arguments), {
                adjustable: t.adjustable,
                radius: t.radius,
                limits: t.limits,
                lnglatVisible: t.lnglatVisible
            })
        }, getNullValue: function () {
            return {}
        }
    }), e.shortcut("location", FX.Location)
}(jQuery), function (e) {
    FX.Upload = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Upload.superclass._defaultConfig.apply(), {
                files: [],
                fileType: [],
                maxFileSize: 5242880,
                maxFileCount: FX.CONST.UPLOAD_FILE_COUNT.SINGLE,
                uploadURL: "/upload",
                uploadTokenURL: FX.Utils.getApi(FX.API.file.get_token),
                uploadSite: "qn",
                uploadToMedia: !1,
                uploadToForm: !1,
                allowBlank: !0,
                onFileSizeLimit: null,
                onValidateSuccess: null,
                onValidateFail: null,
                onAfterValidate: null,
                onUpload: null,
                onUploadSuccess: null,
                onUploadFail: null,
                onAfterUpload: null
            })
        }, _init: function () {
            FX.Upload.superclass._init.apply(this, arguments);
            var e = this.options;
            this.tokenKey = e.uploadToMedia ? "imageUploadToken" : "fileUploadToken", this.tokenExpireKey = this.tokenKey + "Expires", this._initUploadForm(), this._initUploadInput()
        }, _initUploadForm: function () {
            var t = this.options;
            switch (t.uploadSite) {
                case"qn":
                    t.uploadURL = "https://up.qbox.me/";
                    break;
                case"oss":
                    t.uploadURL = "https://jdy-image.oss-cn-hangzhou.aliyuncs.com"
            }
            this.$uploadForm = e('<form class="upload-form" action="' + t.uploadURL + '" enctype="multipart/form-data" method="post"/>')
        }, _initUploadInput: function () {
            var t = this.options;
            this.files = t.files || [], this.$uploadInput = e('<input type="file" name="file" class="upload-btn-input"/>').appendTo(this.$uploadForm), t.maxFileCount > 1 && this.$uploadInput.attr("multiple", !0)
        }, doUpload: function () {
            var e = this;
            if (!this.upFiles) {
                if (!this.$uploadInput[0].files.length > 1) return;
                this.upFiles = this.$uploadInput[0].files
            }
            this._checkUploadToken(function () {
                e._doDataUpload()
            })
        }, _isTokenValid: function () {
            return FX.STATIC[this.tokenKey] && Date.now() < FX.STATIC[this.tokenExpireKey]
        }, _checkUploadToken: function (e) {
            var t = this, i = this.options;
            return "local" === i.uploadSite ? e() : this._isTokenValid() ? e() : void FX.Utils.dataAjax({
                url: i.uploadTokenURL,
                data: {site: i.uploadSite, isMedia: i.uploadToMedia}
            }, function (i) {
                FX.STATIC[t.tokenKey] = i.token, FX.STATIC[t.tokenExpireKey] = 18e5 + Date.now(), e()
            }, function (e) {
                FX.Vip.showUpgradeTip(e.responseJSON)
            })
        }, _doDataUpload: function () {
            var e = this;
            if (FX.Utils.isFormDataSupported()) {
                var t = 0, i = [], a = 0, s = 0, n = function () {
                    return i.reduce(function (e, t) {
                        return e + t
                    })
                }, o = function () {
                    a + s === e.upFiles.length && (s > 0 ? e.onFail({failCount: s}) : e.onSuccess())
                };
                if (this.upFiles) for (var l = 0, r = this.upFiles.length; l < r; l++) {
                    var c = this.upFiles[l];
                    t += c.size, e._doXhrUpload(c, function (a, s) {
                        i[l] = a, e.onUpload(n(), t)
                    }, function (s) {
                        i[l] = c.size, e.onUpload(n(), t), e.files.push(s.file), a++, o()
                    }, function (a) {
                        i[l] = 0, e.onUpload(n(), t), s++, o()
                    })
                }
            } else FX.Msg.toast({type: "warning", msg: "您使用的浏览器版本过低，无法使用文件上传功能！"})
        }, _doXhrUpload: function (e, t, i, a) {
            var s, n = this.options, o = e.name, l = new FormData, r = FX.STATIC.user ? FX.STATIC.user._id : "";
            if ("qn" === n.uploadSite) l.append("file", e), l.append("token", FX.STATIC[this.tokenKey]), l.append("x:bucketType", n.uploadToMedia ? FX.CONST.QN_BUCKET.PUBLIC_IMAGE : FX.CONST.QN_BUCKET.PRIVATE_FILE), l.append("x:uploader", r), n.uploadToForm && (l.append("x:appId", FX.STATIC.APPID), l.append("x:entryId", FX.STATIC.ENTRYID), l.append("x:field", n.widgetName)); else if ("oss" === n.uploadSite) {
                s = FX.Utils.UUID();
                var c = FX.STATIC[this.tokenKey].split(":");
                l.append("Signature", c[2]), l.append("OSSAccessKeyId", c[0]), l.append("policy", c[1]), l.append("callback", c[3]), l.append("x:file_name", o), l.append("x:bucket_type", FX.CONST.OSS_BUCKET.PUBLIC_IMAGE), l.append("x:uploader", r), l.append("key", s), l.append("file", e)
            } else l.append("file", e);
            FX.Utils.ajaxUpload({url: n.uploadURL, data: l, onUpload: t}, function (e, t) {
                if (!e.file) return a();
                "qn" === n.uploadSite ? i(e) : "oss" === n.uploadSite ? i(e) : i && i.apply(this, arguments)
            }, a)
        }, checkValidate: function () {
            var e = this.options, t = !0;
            return e.allowBlank || (t = this.isUploaded()), t ? FX.Utils.applyFunc(this, e.onValidateSuccess, [], !1) : FX.Utils.applyFunc(this, e.onValidateFail, [], !1), FX.Utils.applyFunc(this, e.onAfterValidate, [], !1), t
        }, checkFile: function (e) {
            var t = this.options;
            if (!e) return !1;
            var i = e.name.split(".").pop(), a = !0;
            a && t.fileType.length > 0 && -1 === t.fileType.indexOf(i.toLowerCase()) && (FX.Msg.toast({
                msg: "不支持选择的文件类型",
                type: "warning"
            }), a = !1);
            var s = t.maxFileSize, n = FX.Utils.applyFunc(this, t.onFileSizeLimit, [], !1);
            return FX.Utils.isNumber(n) && (s = n), a && e.size > s && (FX.Msg.toast({
                msg: "文件大小超出限制",
                type: "warning"
            }), a = !1), a
        }, doClear: function () {
            this.resetUploadInput(), this.files = []
        }, resetUploadInput: function () {
            this.$uploadInput.replaceWith(this.$uploadInput = this.$uploadInput.clone(!0).val(""))
        }, onUpload: function (e, t) {
            var i = this.options;
            FX.Utils.applyFunc(this, i.onUpload, [e, t], !1)
        }, onSuccess: function () {
            var e = this.options;
            FX.Utils.applyFunc(this, e.onUpload, [1, 1], !1), FX.Utils.applyFunc(this, e.onUploadSuccess, [this.files], !1), this.resetUploadInput()
        }, onFail: function (e) {
            var t = this.options;
            FX.Utils.applyFunc(this, t.onUploadFail, [e], !1), 413 === e ? FX.Msg.toast({
                type: "warning",
                msg: "文件大小超出限制"
            }) : FX.Msg.toast({type: "warning", msg: "文件上传失败"})
        }, onFinish: function () {
            var e = this.options;
            FX.Utils.applyFunc(this, e.onAfterUpload, [], !1)
        }, isUploaded: function () {
            return !FX.Utils.isObjectEmpty(this.files)
        }, setEnable: function (e) {
            this.options.enable = !!e, e ? this.$uploadInput.removeAttr("disabled").removeAttr("readonly") : this.$uploadInput.attr("disabled", "disabled").attr("readonly", "readonly")
        }, getValue: function () {
            return this.files
        }, getUpFiles: function () {
            return this.upFiles
        }, getNullValue: function () {
            return []
        }, setValue: function (t) {
            var i = this.options;
            this.files = e.makeArray(t), this.files.length > i.maxFileCount && (this.files = this.files.slice(0, i.maxFileCount))
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Upload.superclass.getOptions.apply(this, arguments), {maxFileCount: t.maxFileCount})
        }
    })
}(jQuery), function (e) {
    FX.FileUpload = FX.extend(FX.Upload, {
        _defaultConfig: function () {
            return e.extend(FX.FileUpload.superclass._defaultConfig.apply(), {
                baseCls: "fui_upload",
                files: [],
                fileType: [],
                maxFileSize: 5242880,
                maxFileCount: FX.CONST.UPLOAD_FILE_COUNT.SINGLE,
                uploadURL: "/upload",
                uploadSite: "qn",
                uploadToForm: !0,
                style: "white",
                size: "normal",
                mode: "upload",
                iconCls: "icon-widget-upload",
                tipText: "文件",
                fileThumbSize: "",
                allowBlank: !0,
                thumbWidth: 65,
                thumbHeight: 65,
                hasProgress: !0,
                progressWidth: 420,
                progressHeight: 30,
                hasPreview: !0,
                hasPreviewList: !0,
                hasEmptyTip: !1,
                onBeforeUpload: null,
                onUpload: null,
                onAfterUpload: null,
                onUploadFail: null,
                onFileThumbCreate: null,
                onFileRemove: null,
                onStopEdit: null
            })
        }, _init: function () {
            FX.FileUpload.superclass._init.apply(this, arguments);
            var t = this.options;
            "upload" === t.mode && this._createUploadBtn(), t.hasProgress && (this.progress = FX.createWidget({
                type: "progress",
                renderEl: e("<div/>").appendTo(this.element),
                width: t.progressWidth,
                height: t.progressHeight,
                visible: !1
            })), this.$previewList = e('<div class="upload-preview-list"/>').appendTo(this.element), "small" === t.size && this.$previewList.addClass("small"), this._bindFileEvent()
        }, _createUploadBtn: function () {
            var t = this.options;
            if (this.$uploadBtn = e('<div class="upload-btn x-btn"/>').addClass("style-" + t.style).appendTo(this.element), e('<i class="' + t.iconCls + ' upload-icon"/>').appendTo(this.$uploadBtn), e("<span/>").text("选择" + t.tipText).appendTo(this.$uploadBtn), this.$uploadForm.appendTo(this.$uploadBtn), t.fileType.length > 0) {
                var i = "." + t.fileType.join(",.");
                this.$uploadInput.prop("accept", i)
            }
        }, _checkUploadFiles: function (e) {
            var t = this, i = this.options;
            if (this.files.length + e.length > i.maxFileCount) return FX.Msg.toast({
                msg: "最多允许选择 " + i.maxFileCount + " 个" + i.tipText,
                type: "warning"
            }), !1;
            var a = !0;
            if (e) for (var s = 0, n = e.length; s < n && (a = a && t.checkFile(e[s])); s++) ;
            return a
        }, _previewFiles: function (e) {
            var t = this, i = this.options;
            if (i.hasPreviewList) {
                e || (e = this.files);
                var a = e && e.length > 0;
                if (a) for (var s = 0, n = e.length; s < n; s++) t._createFilePreview(e[s]).appendTo(t.$previewList);
                i.hasEmptyTip && this._renderEmpty(!a)
            }
        }, _createFilePreview: function (t) {
            var i = this, a = this.options, s = FX.Utils.formatFileSize(t.size), n = i._trimFileName(t.name),
                o = t.name ? t.name.split(".").pop() : "", l = FX.Utils.date2Str(new Date(t.uploadTime), "yyyy/MM/dd");
            if ("print" === a.mode) return e("<div/>").text([n, "文件大小:" + s, "上传时间:" + l].join(" "));
            var r = e('<div class="upload-info"/>'), c = e('<div class="upload-preview"/>').appendTo(r),
                d = e('<div class="upload-file-info"/>').appendTo(r);
            return FX.Utils.isImageExt(o) ? t instanceof File ? (i.drawLocalPreview(t, a.thumbWidth, a.thumbHeight).appendTo(c), FX.Utils.applyFunc(this, a.onFileThumbCreate, [{
                type: "local",
                ext: t
            }], !1)) : t.qnKey && i._drawRemotePreview(t, function (e) {
                e.appendTo(c);
                var t = e.clone();
                FX.Utils.applyFunc(i, a.onFileThumbCreate, [{type: "remote", ext: t}], !1)
            }) : (FX.Utils.createFileThumb(o, a.fileThumbSize).appendTo(c), FX.Utils.applyFunc(this, a.onFileThumbCreate, [{
                type: "normal",
                ext: o
            }], !1)), e('<div class="info-text"/>').text(n).appendTo(d), e('<div class="info-sub"/>').text(s).appendTo(d), a.enable && "upload" === a.mode && e('<div class="upload-info-btn remove-btn"/>').append(e('<i class="icon-trasho"/>')).appendTo(r), r
        }, _renderEmpty: function (e) {
            var t = this.$previewList.next(".upload-empty");
            t && t.length ? !e && t.hide() : e && this.$previewList.after('<div class="upload-empty">当前没有' + this.options.tipText + "上传</div>")
        }, _bindFileEvent: function () {
            var t = this, i = this.options;
            this.$previewList.unbind(".file-op"), this.$previewList.bind({
                "click.file-op": function (a) {
                    var s = a.target, n = a.type, o = e(s).closest(".upload-info-btn.remove-btn"),
                        l = e(s).closest(".upload-info");
                    if ("upload" === i.mode && o && o.length > 0) {
                        if ("click" === n) {
                            var r = l.index();
                            t.files.splice(r, 1), l.remove(), FX.Utils.applyFunc(t, i.onFileRemove, [r], !1), FX.Utils.applyFunc(t, i.onStopEdit, [], !1)
                        }
                    } else i.hasPreview && l && l.length > 0 && new FX.FilePreview({
                        files: t.files,
                        currentItem: l.index(),
                        autoClose: !1
                    })
                }
            }), this.$uploadInput.unbind("change.file-upload"), this.$uploadInput.bind("change.file-upload", function () {
                if (t.upFiles = this.files, !t.upFiles && !FX.Utils.isFormDataSupported()) {
                    if (!this.value) return;
                    t.upFiles = [{name: this.value.split("\\").pop(), size: this.size}]
                }
                i.maxFileCount === FX.CONST.UPLOAD_FILE_COUNT.SINGLE && (t.files = [], t.$previewList.empty(), t.$subWrapper && t.$subWrapper.empty()), t._checkUploadFiles(t.upFiles) ? t.doUpload() : t.upFiles = null
            })
        }, _trimFileName: function (e) {
            if (FX.Utils.isEmpty(e)) return "";
            var t = e ? e.split(".").pop() : "";
            return e.length - t.length - 1 > 20 && (e = (e = e.slice(0, 19)) + "..." + t), e
        }, drawLocalPreview: function (t, i, a) {
            var s = e("<canvas/>"), n = window.URL || window.webkitURL, o = s[0].getContext("2d"), l = new Image,
                r = n.createObjectURL(t);
            l.src = r;
            var c = 2 * i, d = 2 * a;
            return o.canvas.width = c, o.canvas.height = d, l.onload = function () {
                var e = l.width / c, t = l.height / d;
                e > t ? o.drawImage(l, (l.width - c * t) / 2, 0, c * t, l.height, 0, 0, c, d) : o.drawImage(l, 0, (l.height - d * e) / 2, l.width, d * e, 0, 0, c, d), n.revokeObjectURL(r)
            }, s
        }, _drawRemotePreview: function (t, i) {
            var a = this.options, s = e("<img/>").hide(),
                n = e.extend({thumb: {mode: 1, width: a.thumbWidth, height: a.thumbHeight}}, t);
            if (t.thumbPcUrl) return s.attr("src", t.thumbPcUrl).show(), i(s);
            FX.Utils.getFileDownloadURL(n, function (e) {
                return s.attr("src", e).show(), i(s)
            })
        }, doUpload: function () {
            FX.FileUpload.superclass.doUpload.apply(this, arguments);
            var e = this.options;
            !this.upFiles || this.upFiles.length <= 0 || (this.$uploadBtn.hide(), e.hasProgress && this.progress.setVisible(!0), FX.Utils.applyFunc(this, e.onBeforeUpload, [{
                files: null,
                up: 0,
                total: 0
            }], !1), this._setProgress(0, 1))
        }, _setProgress: function (e, t) {
            if (this.options.hasProgress) {
                var i = parseInt(e / t * 100);
                i < 100 ? this.progress.setMessage("正在上传...") : this.progress.setMessage("上传完成"), this.progress.setProgress(i)
            }
        }, onUpload: function (e, t) {
            FX.FileUpload.superclass.onUpload.apply(this, arguments), FX.Utils.applyFunc(this, this.options.onUpload, [{
                files: null,
                up: e,
                total: t
            }], !1), this._setProgress(e, t)
        }, onSuccess: function () {
            FX.FileUpload.superclass.onSuccess.apply(this, arguments);
            var e = this.options;
            FX.Utils.isCanvasSupported() ? this._previewFiles(this.upFiles) : this._previewFiles(), e.hasProgress && this.progress.setVisible(!1), FX.Utils.applyFunc(this, e.onAfterUpload, [{
                files: this.files,
                up: 0,
                total: 0
            }], !1), FX.Utils.applyFunc(this, e.onStopEdit, [], !1), this.$uploadBtn.show()
        }, onFail: function (e) {
            FX.FileUpload.superclass.onFail.apply(this, arguments);
            var t = this.options;
            t.hasProgress && this.progress.setVisible(!1), this.$uploadBtn.show(), FX.Utils.applyFunc(this, t.onUploadFail, [], !1)
        }, doClear: function () {
            FX.FileUpload.superclass.doClear.apply(this, arguments), this.$previewList.empty()
        }, setEnable: function (e) {
            FX.FileUpload.superclass.setEnable.apply(this, [e]), this.$uploadBtn && (e ? this.$uploadBtn.removeClass("x-ui-disable") : this.$uploadBtn.addClass("x-ui-disable")), this.$previewList.empty(), this._previewFiles()
        }, setValue: function (e) {
            FX.FileUpload.superclass.setValue.apply(this, arguments), e && (this.$previewList.empty(), this._previewFiles())
        }
    }), e.shortcut("upload", FX.FileUpload)
}(jQuery), jQuery, FX.ImageUpload = FX.extend(FX.FileUpload, {
    _defaultConfig: function () {
        return $.extend(FX.ImageUpload.superclass._defaultConfig.apply(), {
            baseCls: "fui_upload fui_image",
            fileType: ["jpg", "jpeg", "png", "gif"],
            iconCls: "icon-widget-image",
            tipText: "图片",
            compressed: !1,
            onlyCamera: !1
        })
    }, _createUploadBtn: function () {
        FX.ImageUpload.superclass._createUploadBtn.apply(this, arguments), this.options.onlyCamera && $('<span class="upload-tip">启用了「仅允许拍照上传」功能，该功能只支持微信服务号/企业微信和钉钉移动客户端</span>').appendTo(this.element)
    }, setEnable: function (e) {
        FX.ImageUpload.superclass.setEnable.apply(this, [e]), !this.options.onlyCamera && e ? (this.$uploadBtn.removeClass("x-ui-disable"), this.$uploadInput.removeAttr("disabled").removeAttr("readonly")) : (this.$uploadBtn.addClass("x-ui-disable"), this.$uploadInput.attr("disabled", "disabled").attr("readonly", "readonly"))
    }, getOptions: function () {
        var e = this.options;
        return $.extend(FX.ImageUpload.superclass.getOptions.apply(this, arguments), {
            compressed: e.compressed,
            onlyCamera: e.onlyCamera
        })
    }
}), $.shortcut("image", FX.ImageUpload), function (e) {
    FX.SubForm = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.SubForm.superclass._defaultConfig.apply(), {
                baseCls: "fui_subform",
                allowBlank: !0,
                ignoreOptAuth: !1,
                items: [],
                itemPadding: 10,
                itemShowCount: 10,
                maxItemCount: 200,
                newItemText: "添加",
                noFieldText: "请添加字段",
                needEvent: !0,
                label: "",
                onBeforeRowEdit: null,
                onBeforeWidgetCreate: null,
                onAfterWidgetCreate: null,
                rowHeadWidth: 66,
                rowHeight: 40,
                rowBottom: 25,
                tipWidth: null,
                subform_create: !0,
                subform_edit: !0,
                subform_delete: !0
            })
        }, _init: function () {
            FX.SubForm.superclass._init.apply(this, arguments), this.ps = null, this.rowIdx = 0, this._createContent()
        }, _createContent: function () {
            var t = this.options;
            if (!t.items.length) return this.$content = e('<div class="subform-none-tip"/>').text(t.noFieldText).appendTo(this.element), void(t.tipWidth && this.$content.css("width", t.tipWidth));
            this._createHead(), this.$content = e('<div class="subform-content"/>').appendTo(this.element).css({
                "max-height": t.rowHeight * t.itemShowCount + t.rowHeight / 2 + t.rowBottom,
                "max-width": this.maxWidth
            }), this.$rowHead = e('<div class="fix-row-head"/>').appendTo(this.element), e('<div class="fix-col-head"/>').appendTo(this.element), this._allowCreate() && !t.value && this._createLine(null, !0), this._createAddBtn(), this._bindEvent()
        }, _createAddBtn: function () {
            var t = this.options, i = this;
            this.$btnPane = e('<div class="btn-pane"/>').appendTo(this.element), this.addBtn = new FX.Button({
                renderEl: e('<div class="btn-add"/>').appendTo(this.$btnPane),
                style: "none",
                iconCls: "icon-add",
                text: t.newItemText,
                enable: this._allowCreate(),
                onClick: function () {
                    i._allowCreate() && t.needEvent && (i._createLine(null, !0), i._checkItemLimit(), i.$content[0].scrollTop = i.$content[0].scrollHeight, FX.Utils.applyFunc(i, t.onStopEdit, [], !1))
                }
            })
        }, _createHead: function () {
            var t = this, i = this.options, a = e('<div class="subform-head"/>').appendTo(this.element),
                s = e('<div class="subform-row"><div class="row-head"/></div>').appendTo(a), n = 0;
            n += i.rowHeadWidth, FX.Utils.forEach(i.items, function (a, o) {
                var l = '<div class="subform-cell">', r = 0;
                switch (o.widget.type) {
                    case"linkquery":
                    case"linkdata":
                        var c = t._getLinkFieldConfig(o.widget);
                        r = c.width, l += c.linkField + '<span class="form-cell">' + o.label + "</span>";
                        break;
                    default:
                        l += '<span class="form-cell">' + o.label + "</span>", !1 === o.widget.allowBlank && (l += '<span class="label-notnull">*</span>'), r += t.getWidgetWidth(o.widget) + i.itemPadding
                }
                var d = e(l).css({left: n, width: r}).appendTo(s);
                i.ignoreOptAuth || !1 !== o.widget.visible ? n += r : d.addClass("x-ui-hidden")
            }), this.maxWidth = n + 2, this.$head = a.css("max-width", this.maxWidth)
        }, _createLine: function (t, i) {
            var a = this.options, s = this;
            if (0 !== a.items.length) {
                var n = e('<div class="subform-row"/>').appendTo(this.$content).data({
                    editable: i,
                    "row-idx": this.rowIdx
                });
                this.rowIdx++;
                var o = 0;
                o += a.rowHeadWidth, FX.Utils.forEach(a.items, function (l, r) {
                    FX.Utils.applyFunc(s, a.onBeforeWidgetCreate, [r.widget, t], !1);
                    var c = s.getWidgetWidth(r.widget), d = e.extend(!0, {}, r.widget);
                    switch (a.ignoreOptAuth ? (d.enable = !0, d.visible = !0) : s._allowEdit() || i || (d.enable = !1), d.type) {
                        case"location":
                            e.extend(d, {
                                locationText: "移动端获取当前位置",
                                hasBrief: !1,
                                btnWidth: 150,
                                btnHeight: 30,
                                isValueVisible: !1
                            });
                            break;
                        case"linkdata":
                        case"linkquery":
                            c = s._getLinkFieldWidth(d)
                    }
                    var u = c + a.itemPadding, h = "subform-cell";
                    !1 === d.visible && (h += " x-ui-hidden");
                    var p = e('<div class="' + h + '"/>').css({
                        left: o,
                        width: u
                    }).attr("namecol", d.widgetName).appendTo(n);
                    !1 !== d.visible && (o += u);
                    var f = s._createSubformWidget(e.extend(d, {
                        renderEl: e("<div/>").appendTo(p),
                        subform: a.widgetName,
                        width: c
                    }));
                    if (FX.Utils.applyFunc(s, a.onAfterWidgetCreate, [f], !1), t) {
                        var m = t[f.options.widgetName];
                        FX.Utils.isNull(m) || (m.hasOwnProperty("widgetType") ? f.setValue(m.data) : f.setValue(m))
                    }
                    p.data("widget", f)
                });
                var l = "head-icon icon-remove";
                s._allowDelete() || i || (l += " x-ui-disable"), n.append(e('<div class="row-head" style="left: ' + this.$content[0].scrollLeft + 'px;"><i class="head-icon icon-expand" role="edit"/><i class="' + l + '" role="delete"/></div>')).css({width: o}), e('<div class="row-head"><div class="row-num">' + this.rowIdx + '</div><i class="head-icon icon-expand" role="edit"/><i class="head-icon icon-remove" role="delete"/></div>').appendTo(this.$rowHead).attr("row-idx", this.rowIdx - 1), n.hover(function () {
                    var t = e(this).data("row-idx");
                    s.$rowHead.children('.row-head[row-idx="' + t + '"]').addClass("edit")
                }, function () {
                    var t = e(this).data("row-idx");
                    s.$rowHead.children('.row-head[row-idx="' + t + '"]').removeClass("edit")
                })
            }
        }, _getLinkFieldConfig: function (e) {
            var t = this.options, i = this, a = "", s = 0;
            return FX.Utils.forEach(e.linkFields, function (t, n) {
                var o = i.getWidgetWidth(n);
                a += '<div class="sub-link-title sub-' + e.type + '" style="width:' + o + 'px;">' + n.text + "</div>", s += o + 4
            }), s += t.itemPadding - 4, "linkdata" === e.type && (s += 35), s = Math.max(s, i.getWidgetWidth({type: e.type}) + t.itemPadding), {
                linkField: a,
                width: s
            }
        }, _getLinkFieldWidth: function (e) {
            var t = this, i = -4;
            return FX.Utils.forEach(e.linkFields, function (e, a) {
                var s = t.getWidgetWidth(a);
                i += s + 4
            }), "linkdata" === e.type && (i += 35), Math.max(i, t.getWidgetWidth({type: e.type}))
        }, _createSubformWidget: function (e) {
            switch (e.oriType = e.type, e.type) {
                case"address":
                case"user":
                case"usergroup":
                case"dept":
                case"deptgroup":
                case"radiogroup":
                case"checkboxgroup":
                case"upload":
                case"image":
                    e.type = "subform_" + e.type;
                    break;
                case"textarea":
                    e.height = 30
            }
            return FX.createWidget(e)
        }, _checkItemLimit: function () {
            var e = this.options;
            e.maxItemCount && this.addBtn && (this.rowIdx > e.maxItemCount && FX.Msg.toast({
                type: "warning",
                msg: "子表单数据量已超过200条最大限制"
            }), this.addBtn.setEnable(this._allowCreate() && this.rowIdx < e.maxItemCount)), this.doResize()
        }, setEnable: function (e) {
            if (this.options.enable = !!e, this.$content) {
                var t = this.$content.find(".row-head > icon-remove");
                this._allowDelete() ? t.removeClass("x-ui-disable") : t.addClass("x-ui-disable")
            }
            this.addBtn && this.addBtn.setEnable(this._allowCreate())
        }, _allowCreate: function () {
            var e = this.options;
            return e.ignoreOptAuth || e.enable && e.subform_create
        }, _allowEdit: function () {
            var e = this.options;
            return e.ignoreOptAuth || e.enable && e.subform_edit
        }, _allowDelete: function () {
            var e = this.options;
            return e.ignoreOptAuth || e.enable && e.subform_delete
        }, getOptions: function () {
            var t = this.options, i = this;
            if (this.$content) {
                var a = this.$content.children(".subform-row").eq(0);
                if (a.length > 0) {
                    var s = [], n = a.children(".subform-cell");
                    FX.Utils.forEach(n, function (t, a) {
                        var n = e(a).data("widget");
                        n && s.push({
                            label: i.$head.find(".subform-cell").eq(t).children(".form-cell").text(),
                            widget: n.getOptions()
                        })
                    }), t.items = s
                }
            }
            return e.extend(FX.SubForm.superclass.getOptions.apply(this, arguments), {
                items: t.items,
                subform_create: t.subform_create,
                subform_edit: t.subform_edit,
                subform_delete: t.subform_delete
            })
        }, getWidgetByName: function (t, i) {
            var a = [];
            return FX.Utils.forEach(this.$content.find('.subform-cell[namecol="' + t + '"]'), function (t, i) {
                var s = e(i).data("widget");
                s && a.push(s)
            }), FX.Utils.isNull(i) ? a : a[i]
        }, getWidgetWidth: function (e) {
            return FX.Utils.getSubformWidgetWidth(e)
        }, getEditWidgetSize: function (e) {
            var t = {width: 420, height: null};
            switch (e.type) {
                case"textarea":
                    t.height = 140;
                    break;
                case"address":
                    t.width4province = 200, t.width4city = 105, t.width4district = 105;
                    break;
                case"text":
                case"number":
                case"combo":
                case"combocheck":
                case"datetime":
                    t.height = 30
            }
            return t
        }, getValue: function () {
            var t = [];
            return this.$content.find(".subform-row").each(function (i, a) {
                var s = {}, n = !0;
                e(a).find(".subform-cell").each(function (t, i) {
                    var a = e(i).data("widget");
                    if (a) {
                        var o = a.getValue();
                        n = FX.Utils.isObjectEmpty(o) && n, s[a.getWidgetName()] = {
                            data: o,
                            widgetType: a.getWidgetType()
                        }
                    }
                }), n || t.push(s)
            }), t
        }, _rebuildRowHead: function () {
            this.$rowHead.empty();
            for (var t = 0; t < this.rowIdx; t++) e('<div class="row-head"><div class="row-num">' + (t + 1) + '</div><i class="head-icon icon-expand" role="edit"/><i class="head-icon icon-remove" role="delete"/></div>').appendTo(this.$rowHead).attr("row-idx", t);
            FX.Utils.forEach(this.$content.children(".subform-row"), function (t, i) {
                e(i).data({"row-idx": t}).attr("row-idx", t)
            })
        }, _clearContent: function () {
            this.$content && this.$content.find(".subform-row").remove(), this.$rowHead && this.$rowHead.empty(), this.rowIdx = 0
        }, _bindEvent: function () {
            var t = this;
            this.options.needEvent ? (this.element.on("mouseenter", function () {
                t.ps ? t.ps.update() : t.ps = new PerfectScrollbar(t.$content[0])
            }), this.$content && this.$content.on("click", ".subform-row", function (i) {
                var a = e(i.currentTarget), s = a.data("editable"), n = e(i.target).closest(".head-icon");
                switch (n.attr("role")) {
                    case"delete":
                        if (!t._allowDelete() && !s) break;
                        t._deleteRowConfirm(a, n);
                        break;
                    case"edit":
                        t._createRowEditor(a)
                }
            }), this.$content[0].addEventListener("ps-scroll-x", function () {
                var i = e(this).scrollLeft();
                t.$head.children(".subform-row").css({left: -i}), t.$content.find(".row-head").css({left: i})
            }), this.$content[0].addEventListener("ps-scroll-y", function () {
                t.$rowHead.css({top: -e(this).scrollTop()})
            })) : this.element.addClass("no-event")
        }, _deleteRowConfirm: function (t, i) {
            var a = this;
            if (this._isRowEmpty(t)) this._deleteRow(t); else {
                t.addClass("select");
                var s = a.$rowHead.children(".edit").addClass("select");
                FX.Msg.bubble({
                    anchor: i,
                    contentHTML: e('<div style="max-width:210px"/>').text("该条记录存在数据，数据删除后将无法恢复，确定删除？"),
                    type: "error",
                    text4Ok: "删除",
                    onOk: function () {
                        a._deleteRow(t)
                    },
                    onClose: function () {
                        return t.removeClass("select"), s.removeClass("select"), !1
                    }
                })
            }
        }, _isRowEmpty: function (t) {
            var i = !0;
            return FX.Utils.forEach(e(".subform-cell", t), function (t, a) {
                var s = e(a).data("widget");
                if (s && s.isVisible()) return FX.Utils.isObjectEmpty(s.getValue()) ? void 0 : (i = !1, !1)
            }), i
        }, _deleteRow: function (e) {
            var t = this.options;
            e.remove(), this.rowIdx--, this._checkItemLimit(), this._rebuildRowHead(), FX.Utils.applyFunc(this, t.onStopEdit, [], !1)
        }, _createRowEditor: function (t) {
            var i = this, a = this.options, s = FX.Utils.applyFunc(this, a.onBeforeRowEdit, [], !1);
            s || (s = e("<div/>").appendTo(e("body")));
            var n = t.data("row-idx"), o = {};
            t.find(".subform-cell").each(function (t, i) {
                var a = e(i).data("widget");
                a && (o[a.getWidgetName()] = a)
            });
            var l = e('<div class="subform-row-editor">').appendTo(s).css({"z-index": FX.STATIC.zIndex++}),
                r = e('<div class="edit-content"><div class="row-title"><span class="label">' + a.label + '</span><i class="close-btn icon-contract"/></div></div>').appendTo(l).on("click", ".close-btn", function () {
                    FX.Utils.forEach(o, function (e, t) {
                        t.unbindWidgetEvent("onRelyDone")
                    }), l.addClass("close"), setTimeout(function () {
                        s.remove()
                    }, 300)
                }), c = e('<div class="subform-row"/>').appendTo(r).data("row-idx", n);
            FX.Utils.forEach(a.items, function (t, a) {
                var s = o[a.widget.widgetName];
                if (s) {
                    var n = e('<div class="subform-cell"/>').appendTo(c),
                        l = e('<div class="fl-label"><span class="cell-title">' + a.label + "</span></div>").appendTo(n);
                    !1 === a.widget.allowBlank && e('<span class="label-notnull"/>').text("*").appendTo(l);
                    var r = s.getOptions();
                    r.visible || n.addClass("x-ui-hidden");
                    var d = s.getCacheValue(), u = e.extend(!0, {}, a.widget, {
                        renderEl: e('<div class="cell-widget"/>').appendTo(n),
                        subform: null,
                        enable: r.enable,
                        visible: r.visible,
                        onStopEdit: function () {
                            s.setCacheValue(this.getCacheValue()), FX.Utils.applyFunc(s, s.options.onStopEdit, [], !1)
                        },
                        onBeforeAsync: function () {
                            FX.Utils.applyFunc(s, s.options.onBeforeAsync, [], !1), this.options.async = s.options.async
                        }
                    }, i.getEditWidgetSize(a.widget)), h = FX.createWidget(u);
                    h.setCacheValue(d), s.bindWidgetEvent("onRelyDone", function (e) {
                        switch (e.getWidgetType()) {
                            case"combo":
                            case"combocheck":
                                h.items = null, h.rebuild();
                                break;
                            case"dept":
                            case"deptgroup":
                                h.options.limit = e.getOptions().limit;
                                break;
                            default:
                                h.setCacheValue(e.getCacheValue())
                        }
                    }), n.attr("namecol", s.options.widgetName), n.data("widget", s)
                }
            })
        }, getCacheValue: function () {
            var t = [];
            return this.$content.find(".subform-row").each(function (i, a) {
                var s = {}, n = !0;
                e(a).find(".subform-cell").each(function (t, i) {
                    var a = e(i).data("widget");
                    if (!(FX.LimitFields.noCache.indexOf(a.getWidgetType()) > -1)) {
                        var o = a.getCacheValue();
                        n = FX.Utils.isObjectEmpty(o) && n, s[a.getWidgetName()] = {
                            data: o,
                            widgetType: a.getWidgetType()
                        }
                    }
                }), s.editable = e(a).data("editable"), n || t.push(s)
            }), t
        }, setCacheValue: function (e) {
            var t = this;
            this._clearContent(), FX.Utils.forEach(e, function (e, i) {
                t._createLine(i, i.editable)
            }), this._checkItemLimit()
        }, getText: function () {
            var t = [];
            return this.$content.find(".subform-row").each(function (i, a) {
                var s = {}, n = !0;
                e(a).find(".subform-cell").each(function (t, i) {
                    var a = e(i).data("widget"), o = a.getText();
                    n = FX.Utils.isObjectEmpty(o) && n, "linkdata" === a.getWidgetType() ? e.extend(s, o) : s[a.getWidgetName()] = o
                }), n || t.push(s)
            }), t
        }, setValue: function (e) {
            var t = this;
            this._clearContent(), FX.Utils.forEach(e, function (e, i) {
                t._createLine(i)
            }), this._checkItemLimit()
        }, checkValidate: function () {
            var t = this.options, i = [], a = !0;
            return this.$content && this.$content.find(".subform-row").each(function (t, s) {
                var n = {}, o = !0, l = !0;
                e(s).find(".subform-cell").each(function (t, i) {
                    var a = e(i).data("widget");
                    if (a && a.isVisible()) {
                        l = a.checkValidate() && l;
                        var s = a.getValue();
                        o = FX.Utils.isObjectEmpty(s) && o, n[a.getWidgetName()] = {
                            data: s,
                            widgetType: a.getWidgetType()
                        }
                    }
                }), o ? l = !0 : i.push(n), a = l && a
            }), !(!t.allowBlank && i.length <= 0) && (a || this.setInvalidateType("regex"), a)
        }, getNullValue: function () {
            return []
        }, doResize: function () {
            this.ps && this.ps.update(), this.$btnPane && (this.rowIdx > 0 ? this.$btnPane.removeClass("no-border") : this.$btnPane.addClass("no-border"), this.$btnPane.css({"max-width": this.maxWidth}))
        }
    }), e.shortcut("subform", FX.SubForm)
}(jQuery), function (e) {
    FX.Separator = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Separator.superclass._defaultConfig.apply(), {
                baseCls: "fui_separator",
                allowBlank: !0,
                lineStyle: FX.CONST.SEP_LINE_STYLE.THIN
            })
        }, _init: function () {
            FX.Separator.superclass._init.apply(this, arguments);
            var t = this.options;
            e('<div class="sep-line ' + t.lineStyle + '"/>').appendTo(this.element), this.$description = e("<div/>").appendTo(this.element)
        }, setValue: function (e) {
            FX.Separator.superclass.setValue.apply(this, arguments), this.$description.empty(), FX.Utils.isEmpty(e) || this.$description.append(e)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Separator.superclass.getOptions.apply(this, arguments), {lineStyle: t.lineStyle})
        }
    }), e.shortcut("separator", FX.Separator)
}(jQuery), function (e) {
    FX.User = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.User.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_user",
                title: "成员列表",
                msg: "点击选择成员",
                width: 240,
                height: 40,
                value: null,
                allowBlank: !0,
                noRepeat: !1,
                editable: !1,
                count: 100,
                limit: {},
                dynamicFields: [{id: FX.USER_ID.CurrentUser, name: "当前用户", type: "dynamic"}],
                dynamicKey: FX.USER_ID.CurrentUser,
                dynamicType: "select",
                onStopEdit: null,
                onBeforeEdit: null
            })
        }, _init: function () {
            FX.User.superclass._init.apply(this, arguments);
            var e = this.options;
            e.limit = e.limit || {}, this._initSelectPane()
        }, _initData: function () {
            if (!FX.Utils.isExternalLink()) {
                var e = this.options;
                e.items && (this.items = e.items), this._initSelectPane()
            }
        }, _initSelectPane: function () {
            if (FX.Utils.isExternalLink()) return this.element.empty(), void e('<div class="nonsupport-msg"/>').text("外链不支持成员控件").appendTo(this.element);
            var t = this, i = this.options;
            this.selectMap = {}, FX.Utils.forEach(this.items, function (e, i) {
                t.selectMap[i.id] = i
            }), this._createSelectList(), i.editable ? this._createSelectPane() : this._bindEditEvent()
        }, _bindEditEvent: function () {
            var e = this, t = this.options;
            this.$selectList.unbind("click"), this.$selectList.bind("click", function () {
                if (e.isEnabled()) {
                    FX.Utils.applyFunc(e, t.onBeforeEdit, [], !1);
                    var i = new FX.ConfirmDialog({
                        title: t.title,
                        height: 550,
                        width: 590,
                        contentWidget: {
                            rowSize: [440],
                            colSize: [570],
                            padding: 10,
                            items: [[{
                                widgetName: t.widgetName,
                                type: t.type,
                                editable: !0,
                                limit: t.limit,
                                limitWidget: t.limitWidget,
                                items: e.items,
                                value: e.value
                            }]]
                        },
                        onOk: function () {
                            var a = i.getWidgetByName(t.widgetName);
                            return e.value = a.getValue(), e.items = a.getItems(), e._initSelectPane(), FX.Utils.applyFunc(e, t.onStopEdit, [], !1), !1
                        }
                    });
                    i.show()
                }
            })
        }, _createSelectList: function () {
            var t = this, i = this.options;
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<ul class="select-list"/>').appendTo(this.element), this.value) {
                var a = t.selectMap[this.value];
                t._createSelectItem(a)
            } else i.editable || this.$selectList.append(e('<div class="select-empty"/>').text(i.msg))
        }, _setSelectItem: function (e) {
            this.$selectList.empty(), this._createSelectItem(e), this.value = e.id, this.selectMap[e.id] = e, this.refresh()
        }, _clearSelectItem: function () {
            this.$selectList.empty(), this.value = null, this.refresh()
        }, _createSelectItem: function (t) {
            var i = this.options, a = this;
            if (t) {
                var s = e('<li class="select-item"/>').append(e("<span/>").text(t.name)).appendTo(this.$selectList).attr("id", t.id).data("item", t);
                s.prepend(e('<i class="select-icon icon-member-normal"/>')), i.editable && e('<span class="remove-btn"/>').append(e('<i class="icon-close-large"/>')).click(function () {
                    a._clearSelectItem()
                }).appendTo(s)
            }
        }, _createSelectPane: function () {
            if (!this.$selectPane) {
                var t = this.options, i = this,
                    a = e('<div class="select-menu"/>').on("click", ".select-btn", function (t) {
                        var a = e(t.currentTarget);
                        i._switchTab(a.attr("role"))
                    }).appendTo(this.element);
                this.$selectPane = e('<div class="select-pane"/>').appendTo(this.element), this._hasType("organization") && e('<div class="select-btn"/>').attr("role", "organization").text("组织架构").appendTo(a), this._hasType("role") && e('<div class="select-btn"/>').attr("role", "role").text("角色").appendTo(a), this._hasType("member") && e('<div class="select-btn"/>').attr("role", "member").text("成员").appendTo(a), this._hasType("dynamic") && ("set" === t.dynamicType ? e('<div class="select-btn"/>').attr("role", "dynamic").text("动态参数").appendTo(a) : e('<div class="select-btn"/>').attr("role", "curUser").text("当前用户").appendTo(a)), e('<i class="icon-search"/>').appendTo(a).on("click", function () {
                    return e(".search-info").hide(), e(".search-input").show(), e("input", a).val("").focus(), e(document).on("click.search", function (t) {
                        var a = t.target;
                        0 === e(a).closest(".search-input").length && (e(".search-info").show(), e(".search-input").hide(), e(document).off("click.search"), 0 === e(a).closest(".search-list li").length && i._switchOriginTab())
                    }), !1
                });
                var s = e("<input />").on("input propertychange", function () {
                    i.searchInterval && clearTimeout(i.searchInterval), i.searchInterval = setTimeout(function () {
                        i.$searchList && (i.$searchList.remove(), i.$searchList = null), i._createSearchList(s.val())
                    }, 500)
                });
                a.append(e('<div class="search-input"/>').append(s).append(e('<i class="icon-search"/>'))), i._switchTab()
            }
        }, _switchTab: function (t) {
            if (t || (t = this.types[0]), e('.select-menu [role="' + t + '"]', this.element).addClass("select").siblings().removeClass("select"), this._isRelyLimitEmpty()) {
                var i = e(".tip-empty", this.$selectPane);
                i.length ? i.show() : e('<span class="tip-empty"/>').text("没有可选成员").appendTo(this.$selectPane)
            } else switch (t) {
                case"organization":
                    this._createOrganizationPane();
                    break;
                case"role":
                    this._createRolePane();
                    break;
                case"member":
                    this._createMemberPane();
                    break;
                case"dynamic":
                    this._createDynamicPane();
                    break;
                case"curUser":
                    this._createCurrentUserPane()
            }
        }, _switchOriginTab: function () {
            var t = e(".select-menu .select-btn.select");
            this._switchTab(t.attr("role"))
        }, _isRelyLimitEmpty: function () {
            var e = this.options;
            return FX.Utils.isObjectEmpty(e.limit) && !FX.Utils.isObjectEmpty(e.limitWidget)
        }, _initLimitMap: function (e) {
            var t = this.options, i = this, a = {};
            FX.Utils.forEach(e, function (e, t) {
                a[t._id] = t
            }), this.limitMap = {}, FX.Utils.forEach(t.limit, function (e, t) {
                var s = a[t];
                s && s.departmentId && (i.limitMap[s.departmentId] = !0)
            })
        }, _createOrganizationPane: function () {
            var t = this;
            this.options;
            this.$selectPane.children().hide(), this.$organizationPane ? this.$organizationPane.show() : this.$organizationPane = e('<div class="organization-pane"/>').appendTo(this.$selectPane), this._createMemberMenu().appendTo(this.$organizationPane), t._createOrganizationUserList()
        }, _createOrganizationUserList: function (t) {
            t = t || 0;
            var i = this, a = this.options;
            FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.user_dept_role),
                data: {departmentLimit: a.limit.departs, departmentId: i._getDepartmentId(), limit: a.count, skip: t}
            }, function (s) {
                var n;
                0 === t ? (e(".user-list", i.$organizationPane).remove(), n = i._createUserList(s.users).appendTo(i.$organizationPane)) : (n = e(".user-list", i.$organizationPane), FX.Utils.forEach(s.users, function (e, t) {
                    i._createUserItem(t).appendTo(n)
                })), s.users.length === a.count && i._createLoadMoreBtn(t + s.users.length, i._createOrganizationUserList).appendTo(n)
            })
        }, _createMemberMenu: function () {
            var t = this, i = this.options;
            return this.$memberMenu ? (this.$memberMenu.show(), this.$memberMenu) : (this.$memberMenu = e('<div class="member-menu"/>'), FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.departments),
                data: {departmentLimit: i.limit.departs}
            }, function (i) {
                t.memberTree = new FX.Tree({
                    renderEl: e("<div/>").appendTo(t.$memberMenu),
                    customCls: "x-department-tree select-department",
                    Nodes: i.departments,
                    setting: {
                        view: {expandSpeed: 100},
                        data: {simpleData: {enable: !0, idKey: "departmentId", pIdKey: "parentId"}},
                        callback: {
                            onNodeCreated: function (e, t) {
                                t.isParent && !t.open && t.level < 1 && this.expandNode(t, !0)
                            }, onClick: function (e, i) {
                                t.currentDepartment = i.departmentId, t._createOrganizationUserList()
                            }
                        }
                    }
                })
            }), this.$memberMenu)
        }, _createRolePane: function () {
            var t = this, i = this.options;
            this.$selectPane.children().hide(), this.$rolePane ? this.$rolePane.show() : (this.$rolePane = e('<div class="role-pane"/>').appendTo(this.$selectPane), FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.roles),
                data: {roleLimit: i.limit.roles}
            }, function (e) {
                t.curRole = e.roles[0].role_id, t._createRoleList(e.roles).appendTo(t.$rolePane), t._createRoleUserList()
            }))
        }, _createRoleList: function (t) {
            var i = this, a = (this.options, e('<ul class="role-list"/>'));
            return FX.Utils.forEach(t, function (t, s) {
                var n = e('<li class="role-item"/>').append(e("<span />").text(s.name)).data("role", s.role_id).appendTo(a);
                s.role_id === i.curRole && n.addClass("select")
            }), a.on("click", ".role-item", function (t) {
                var a = e(t.currentTarget);
                a.addClass("select").siblings().removeClass("select");
                var s = a.data("role");
                s !== i.curRole && (i.curRole = s, i._createRoleUserList())
            }), a
        }, _createRoleUserList: function (t) {
            t = t || 0;
            var i = this, a = this.options;
            FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.user_dept_role),
                data: {roleId: this.curRole, roleLimit: a.limit.roles, limit: a.count, skip: t}
            }, function (s) {
                var n;
                0 === t ? (e(".user-list", i.$rolePane).remove(), n = i._createUserList(s.users).appendTo(i.$rolePane)) : (n = e(".user-list", i.$rolePane), FX.Utils.forEach(s.users, function (e, t) {
                    i._createUserItem(t).appendTo(n)
                })), s.users.length === a.count && i._createLoadMoreBtn(t + s.users.length, i._createRoleUserList).appendTo(n)
            })
        }, _createMemberPane: function () {
            var t = this;
            this.options;
            this.$selectPane.children().hide(), this.$memberPane ? this.$memberPane.show() : (this.$memberPane = e('<div class="member-pane"/>').appendTo(this.$selectPane), t._createMemberUserList())
        }, _createMemberUserList: function (t) {
            t = t || 0;
            var i = this, a = this.options;
            FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.users),
                data: {
                    departmentLimit: a.limit.departs,
                    roleLimit: a.limit.roles,
                    userLimit: a.limit.users,
                    hasCurrentUser: a.limit.hasCurrentUser,
                    limit: a.count,
                    skip: t
                }
            }, function (s) {
                var n;
                0 === t ? (e(".user-list", i.$memberPane).remove(), n = i._createUserList(s.users).appendTo(i.$memberPane)) : (n = e(".user-list", i.$memberPane), FX.Utils.forEach(s.users, function (e, t) {
                    i._createUserItem(t).appendTo(n)
                }), s.users.length === a.count && i._createLoadMoreBtn(t + s.users.length, i._createMemberUserList).appendTo(n))
            })
        }, _createLoadMoreBtn: function (t, i) {
            var a = this;
            return e('<div class="load-more"/>').text("点击加载更多...").click(function (s) {
                e(s.currentTarget).remove(), FX.Utils.applyFunc(a, i, [t], !1)
            })
        }, _getSelectItem: function (e) {
            return {id: e._id || e.id, name: e.nickname || e.name}
        }, _getDynamicFields: function () {
            return this.options.dynamicFields
        }, _createCurrentUserPane: function () {
            if (this.$selectPane.children().hide(), this.$currentUserPane) this.$currentUserPane.show(); else {
                this.$currentUserPane = e('<div class="current-pane"/>').appendTo(this.$selectPane);
                var t = [{_id: FX.STATIC.user._id, nickname: FX.STATIC.user.nickname}];
                this._createUserList(t).appendTo(this.$currentUserPane)
            }
        }, _createDynamicPane: function () {
            this.$selectPane.children().hide(), this.$dynamicPane ? this.$dynamicPane.show() : (this.$dynamicPane = e('<div class="dynamic-pane"/>').appendTo(this.$selectPane), this._createUserList(this._getDynamicFields()).appendTo(this.$dynamicPane))
        }, _createSearchList: function (t) {
            var i = this.options, a = this;
            if (!this._isRelyLimitEmpty()) {
                this.$selectPane.children().hide(), this.$searchList ? this.$selectList.empty() : this.$searchList = e('<div class="select-search"/>').appendTo(this.$selectPane);
                var s = this.$searchList;
                FX.Utils.dataAjax({
                    url: FX.Utils.getApi(FX.API.data.users),
                    data: {
                        departmentLimit: i.limit.departs,
                        roleLimit: i.limit.roles,
                        userLimit: i.limit.users,
                        hasCurrentUser: i.limit.hasCurrentUser,
                        keyword: t,
                        limit: i.count
                    }
                }, function (t) {
                    var i = t.users || [];
                    if (i.length <= 0) s.append(e('<span class="search-empty"/>').text("暂无相关成员")); else {
                        var n = e('<ul class="search-list"/>').appendTo(s);
                        FX.Utils.forEach(i, function (t, i) {
                            var s = a._getSelectItem(i);
                            e("<li/>").appendTo(n).text(i.nickname).data("user", s)
                        })
                    }
                }), s.bind("click", function (t) {
                    var i = t.target, s = e(i).closest("li"), n = s.data("user");
                    s.length > 0 && n && (a._switchOriginTab(), a._setSelectItem(n))
                })
            }
        }, _getDepartmentId: function () {
            return FX.Utils.isEmpty(this.currentDepartment) && (this.currentDepartment = 1), this.currentDepartment
        }, getItems: function () {
            var t = [];
            return e(".select-item", this.$selectList).each(function (i, a) {
                t.push(e(a).data("item"))
            }), t
        }, _dealCurrentUser: function (e) {
            var t = this.options;
            if (!e) return null;
            var i = e;
            return "select" === t.dynamicType && e._id === t.dynamicKey && (i = FX.STATIC.user ? {
                _id: FX.STATIC.user._id,
                nickname: FX.STATIC.user.nickname
            } : null), i
        }, setValue: function (e) {
            e = this._dealCurrentUser(e), this.value = this._parseDefaultValue(e), e && (this.items = this._getDynamicFields().concat([{
                id: e._id,
                name: e.nickname || e.name
            }])), this._initData()
        }, getValue: function () {
            return this.value
        }, getCacheValue: function () {
            var e = this.selectMap[this.value];
            return e ? {_id: e.id, name: e.name} : null
        }, getText: function () {
            return this.value && this.selectMap[this.value] ? this.selectMap[this.value].name : ""
        }, refresh: function () {
            var t = this;
            e(".user-item", this.$selectPane).each(function (i, a) {
                var s = e(a).data("user");
                if (s) {
                    var n = e(a).children(".select-btn");
                    t.value === s.id ? n.addClass("select") : n.removeClass("select")
                }
            })
        }, checkValidate: function () {
            if (FX.Utils.isExternalLink()) return this.setInvalidateType("regex"), !1;
            var e = this.options;
            return !FX.Utils.isEmpty(this.getValue()) || e.allowBlank
        }, rebuild: function (e) {
            this.setValue(e), this.refresh()
        }, getOptions: function (t) {
            var i = this.options;
            return e.extend(FX.User.superclass.getOptions.apply(this, arguments), {
                noRepeat: i.noRepeat,
                limit: i.limit,
                limitWidget: i.limitWidget,
                value: "save" === t ? this._parseDefaultValue(i.value) : i.value
            })
        }, _parseDefaultValue: function (e) {
            var t = e;
            return e && e._id && (t = e._id), t
        }, _createUserList: function (t) {
            var i = this, a = e('<ul class="user-list"/>');
            return t.length ? (FX.Utils.forEach(t, function (e, t) {
                i._createUserItem(t).appendTo(a)
            }), a.on("click", ".user-item", function (t) {
                var s = e(t.currentTarget), n = e(".select-btn", s);
                n.hasClass("select") ? (n.removeClass("select"), i._clearSelectItem()) : (e(".select", a).removeClass("select"), n.addClass("select"), i._setSelectItem(s.data("user")))
            }), a) : (e('<span class="tip-empty"/>').text("没有可选成员").appendTo(a), a)
        }, _createUserItem: function (t) {
            var i = this._getSelectItem(t),
                a = e('<li class="user-item"/>').append(e("<span />").text(i.name)).append(e('<div class="select-btn x-radio"/>').append('<i class="icon-blank"/>')).data("user", i);
            return this.value === i.id && a.children(".select-btn").addClass("select"), a
        }, _hasType: function (e) {
            var t = this.options;
            return this.types || (this.types = [], FX.Utils.isObjectEmpty(t.limit) ? this.types = ["organization", "member", "dynamic"] : (FX.Utils.isObjectEmpty(t.limit.departs) || this.types.push("organization"), FX.Utils.isObjectEmpty(t.limit.roles) || this.types.push("role"), this.types.push("member"), t.limit.hasCurrentUser && this.types.push("dynamic"))), this.types.indexOf(e) > -1
        }
    }), e.shortcut("user", FX.User)
}(jQuery), function (e) {
    FX.UserGroup = FX.extend(FX.User, {
        _defaultConfig: function () {
            return e.extend(FX.UserGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_user fui_user_group ",
                title: "成员列表",
                msg: "点击设置成员",
                width: 420,
                height: 80,
                value: [],
                onStopEdit: null
            })
        }, _init: function () {
            this.value = [], FX.UserGroup.superclass._init.apply(this, arguments)
        }, _initData: function () {
            if (!FX.Utils.isExternalLink()) {
                var e = this.options;
                this.selectMap = {}, e.items && (this.items = e.items), this._initSelectPane()
            }
        }, _createSelectList: function () {
            var t = this, i = this.options;
            this.$selectList ? this.$selectList.empty() : this.$selectList = e('<ul class="select-list"/>').appendTo(this.element), this.value && this.value.length > 0 ? FX.Utils.forEach(this.value, function (e, i) {
                var a = t.selectMap[i];
                t._createSelectItem(a)
            }) : i.editable || this.$selectList.append(e('<div class="select-empty"/>').text(i.msg))
        }, _addSelectItem: function (e) {
            this.options;
            this.value.indexOf(e.id) > -1 || (this._createSelectItem(e), this.value = this.getValue(), this.selectMap[e.id] = e, this.refresh())
        }, _setSelectItem: function (e) {
            this._addSelectItem(e)
        }, _removeSelectItem: function (t) {
            this.options;
            e("#" + t.id, this.$selectList).remove(), this.value = this.getValue(), this.refresh()
        }, _createSelectItem: function (t) {
            var i = this.options, a = this;
            if (t) {
                var s = e('<li class="select-item"/>').append(e("<span/>").text(t.name)).appendTo(this.$selectList).attr("id", t.id).data("item", t);
                s.prepend(e('<i class="select-icon icon-member-normal"/>')), i.editable && e('<span class="remove-btn"/>').append(e('<i class="icon-close-large"/>')).click(function () {
                    a._removeSelectItem(t), a.refresh()
                }).appendTo(s)
            }
        }, _createUserList: function (t) {
            var i = this, a = e('<ul class="user-list"/>');
            return t.length ? (FX.Utils.forEach(t, function (e, t) {
                i._createUserItem(t).appendTo(a)
            }), a.on("click", ".user-item", function (t) {
                var a = e(t.currentTarget), s = e(".select-btn", a);
                s.hasClass("select") ? (s.removeClass("select"), i._removeSelectItem(a.data("user"))) : (s.addClass("select"), i._addSelectItem(a.data("user")))
            }), a) : (e('<span class="tip-empty"/>').text("没有可选成员").appendTo(a), a)
        }, _createUserItem: function (t) {
            var i = this._getSelectItem(t),
                a = e('<li class="user-item"/>').data("user", i).append(e("<span/>").text(i.name)).append(e('<div class="select-btn x-check"/>').append(e('<i class="icon-blank"/>')));
            return this.value.indexOf(i.id) > -1 && a.children(".select-btn").addClass("select"), a
        }, checkValidate: function () {
            return FX.Utils.isExternalLink() ? (this.setInvalidateType("regex"), !1) : !(!this.options.allowBlank && 0 === this.getValue().length)
        }, setValue: function (e) {
            var t = this;
            this.value = [], this.items = [].concat(this._getDynamicFields());
            var i = {};
            FX.Utils.forEach(e, function (e, a) {
                (a = t._dealCurrentUser(a)) && (a._id ? i[a._id] || (i[a._id] = !0, t.value.push(a._id), t.items.push({
                    id: a._id,
                    name: a.nickname || a.name
                })) : i[a] || (i[a] = !0, t.value.push(a)))
            }), this._initData()
        }, getValue: function () {
            this.options;
            var t = this.value;
            return this.$selectList && (t = [], e(".select-item", this.$selectList).each(function (i, a) {
                t.push(e(a).attr("id"))
            })), t
        }, getCacheValue: function () {
            var e = this, t = [];
            return FX.Utils.forEach(this.getValue(), function (i, a) {
                var s = e.selectMap[a];
                t.push({_id: s.id, name: s.name})
            }), t
        }, getText: function () {
            var e = this, t = [];
            return FX.Utils.forEach(this.value, function (i, a) {
                e.selectMap[a] && t.push(e.selectMap[a].name)
            }), t
        }, getNullValue: function () {
            return []
        }, refresh: function () {
            var t = this;
            e(".user-item", this.$selectPane).each(function (i, a) {
                var s = e(a).data("user");
                if (s) {
                    var n = e(a).children(".select-btn");
                    t.value.indexOf(s.id) > -1 ? n.addClass("select") : n.removeClass("select")
                }
            })
        }, _parseDefaultValue: function (e) {
            var t = [];
            return FX.Utils.forEach(e, function (e, i) {
                i && i._id ? t.push(i._id) : t.push(i)
            }), t
        }
    }), e.shortcut("usergroup", FX.UserGroup)
}(jQuery), function (e) {
    FX.Dept = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Dept.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_dept",
                title: "部门列表",
                msg: "点击选择部门",
                width: 240,
                height: 40,
                value: null,
                allowBlank: !0,
                noRepeat: !1,
                editable: !1,
                count: 100,
                limit: {},
                dynamicFields: [{_id: FX.CONST.DEPT_ID.CURRENT, name: "当前用户所处部门", type: "dynamic"}],
                dynamicKey: FX.CONST.DEPT_ID.CURRENT,
                dynamicType: "select",
                onStopEdit: null
            })
        }, _init: function () {
            FX.Dept.superclass._init.apply(this, arguments), this._initSelectPane()
        }, _initData: function () {
            if (!FX.Utils.isExternalLink()) {
                var e = this.options;
                e.items && (this.items = e.items), this._initSelectPane()
            }
        }, _initSelectPane: function () {
            if (FX.Utils.isExternalLink()) return this.element.empty(), void e('<div class="nonsupport-msg"/>').text("外链不支持部门控件").appendTo(this.element);
            var t = this, i = this.options;
            this.selectMap = {}, FX.Utils.forEach(this.items, function (e, i) {
                t.selectMap[i._id] = i
            }), this._createSelectList(), i.editable ? (this._createSelectPane(), this._bindSelectEvent()) : this._bindEditEvent()
        }, _bindEditEvent: function () {
            var e = this, t = this.options;
            this.$selectList.unbind("click"), this.$selectList.bind("click", function () {
                if (e.isEnabled()) {
                    var i = new FX.ConfirmDialog({
                        title: t.title,
                        height: 550,
                        width: 590,
                        contentWidget: {
                            rowSize: [440],
                            colSize: [570],
                            padding: 10,
                            items: [[{
                                widgetName: t.widgetName,
                                type: t.type,
                                editable: !0,
                                limit: t.limit,
                                rely: t.rely,
                                items: e.items,
                                value: e.value
                            }]]
                        },
                        onOk: function () {
                            var a = i.getWidgetByName(t.widgetName);
                            return e.value = a.getValue(), e.items = a.getItems(), e._initSelectPane(), FX.Utils.applyFunc(e, t.onStopEdit, [], !1), !1
                        }
                    });
                    i.show()
                }
            })
        }, _createSelectList: function () {
            var t = this, i = this.options;
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<ul class="select-list"/>').appendTo(this.element), this.value) {
                var a = t.selectMap[this.value];
                t._createSelectItem(a)
            } else i.editable || this.$selectList.append(e('<div class="select-empty"/>').text(i.msg))
        }, _bindSelectEvent: function () {
            var t = this;
            this.$selectList.unbind("click"), this.$selectList.bind("click", function (i) {
                var a = e(i.target).closest(".select-item").data("item");
                a && e(i.target).closest(".remove-btn").length > 0 && t._removeSelectItem(a)
            })
        }, _addSelectItem: function (e) {
            this.$selectList.empty(), this._createSelectItem(e), this.value = e._id, this.selectMap[e._id] = e, this.refresh()
        }, _removeSelectItem: function () {
            this.$selectList.empty(), this.value = null, this.refresh()
        }, _createSelectItem: function (t) {
            var i = this.options;
            if (t) {
                var a = e('<li class="select-item"/>').append(e("<span/>").text(t.name)).appendTo(this.$selectList).attr("id", t._id).data("item", t);
                a.prepend(e('<i class="select-icon icon-department"/>')), i.editable && e('<span class="remove-btn"/>').append(e('<i class="icon-close-large"/>')).appendTo(a)
            }
        }, _createSelectPane: function () {
            if (!this.$selectPane) {
                var t = this.options, i = this, a = e('<div class="select-menu"/>').appendTo(this.element);
                this.$selectPane = e('<div class="select-pane"/>').appendTo(this.element);
                var s = e('<div class="select-btn"/>').attr("role", "depart").click(function () {
                    e(".select-btn", a).removeClass("select"), e(this).addClass("select"), i._createDepartmentList()
                }).text("组织架构").appendTo(a);
                (FX.Utils.isObjectEmpty(t.limit) || t.limit.hasCurrentDept) && ("set" === t.dynamicType ? (e('<div class="select-btn"/>').attr("role", "dynamic").click(function () {
                    e(".select-btn", a).removeClass("select"), e(this).addClass("select"), i._createDynamicList()
                }).text("动态参数").appendTo(a), this._createDynamicList()) : e('<div class="select-btn"/>').attr("role", "curDepart").click(function () {
                    e(".select-btn", a).removeClass("select"), e(this).addClass("select"), i._createCurrentDepartmentList()
                }).text("当前用户所处部门").appendTo(a)), e('<i class="icon-search" />').appendTo(a).on("click", function () {
                    return e(".search-info").hide(), e(".search-input").show(), e("input", a).val("").focus(), e(document).bind("click.search", function (t) {
                        var a = t.target;
                        0 === e(a).closest(".search-input").length && (e(".search-info").show(), e(".search-input").hide(), e(document).unbind("click.search"), 0 === e(a).closest(".select-search li").length && i._switchOriginTab())
                    }), !1
                });
                var n = e("<input />").on("input propertychange", function () {
                    i.searchInterval && clearTimeout(i.searchInterval), i.searchInterval = setTimeout(function () {
                        i.$searchList && (i.$searchList.remove(), i.$searchList = null), i._createSearchList(n.val())
                    })
                });
                a.append(e('<div class="search-input"/>').append(n).append(e('<i class="icon-search"/>'))), s.addClass("select"), this._createDepartmentList()
            }
        }, _switchOriginTab: function () {
            switch (e(".select-menu .select-btn.select").attr("role")) {
                case"depart":
                    this._createDepartmentList();
                    break;
                case"dynamic":
                    this._createDynamicList();
                    break;
                case"curDepart":
                    this._createCurrentDepartmentList()
            }
        }, _isRelyLimitEmpty: function () {
            var e = this.options;
            return FX.Utils.isObjectEmpty(e.limit) && !FX.Utils.isObjectEmpty(e.rely)
        }, _initLimitMap: function (e) {
            var t = this.options, i = this;
            if (!FX.Utils.isObjectEmpty(t.limit)) {
                var a = {};
                FX.Utils.forEach(e, function (e, t) {
                    a[t._id] = t
                }), this.limitMap = {}, FX.Utils.forEach(t.limit.departs, function (e, t) {
                    var s = a[t];
                    s && s.departmentId && (i.limitMap[s.departmentId] = !0)
                }), FX.Utils.forEach(e, function (e, t) {
                    i.limitMap[t.departmentId] || FX.Utils.forEach(t.path, function (e, a) {
                        i.limitMap[a] && (i.limitMap[t.departmentId] = !0)
                    })
                })
            }
        }, _doSelectItem: function (e) {
            if (this._checkLimit(e)) {
                var t = {name: e.name, _id: e._id};
                this.value !== t._id ? this._addSelectItem(t) : this._removeSelectItem(t), this.departmentTree.refresh()
            }
        }, _createDepartmentList: function () {
            var t = this, i = this.options;
            this._isRelyLimitEmpty() || (this.$selectPane.children().hide(), this.$memberMenu ? this.$memberMenu.show() : (this.$memberMenu = e('<div class="select-department"/>').appendTo(t.$selectPane), FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.departments),
                data: {departmentLimit: i.limit.departs, hasCurrentDept: i.limit.hasCurrentDept}
            }, function (i) {
                t.departments = e.extend(!0, [], i.departments), t.departments[0] && !t.departments[0]._id && t.departments.shift(), t._initLimitMap(t.departments), t.departmentTree = new FX.Tree({
                    renderEl: e("<div/>").appendTo(t.$memberMenu),
                    customCls: "x-department-tree select-department",
                    Nodes: t.departments,
                    setting: {
                        view: {expandSpeed: 100},
                        data: {simpleData: {enable: !0, idKey: "departmentId", pIdKey: "parentId"}},
                        callback: {
                            onCheck: function (e, i) {
                                t._doSelectItem(i)
                            }, onClick: function (e, i) {
                                t._doSelectItem(i)
                            }, beforeNodeCreate: function (e) {
                                t._checkLimit(e) || (e.nocheck = !0), e.checked = e._id === t.value
                            }, onNodeCreated: function (e, i) {
                                i.isParent && !i.open && i.level < 1 && this.expandNode(i, !0), i.departmentId == t.currentDepartment && this.selectNode(i)
                            }
                        },
                        check: {enable: !0, chkStyle: "x-radio", chkboxType: {Y: "", N: ""}}
                    }
                })
            })))
        }, _checkLimit: function (e) {
            var t = this.options;
            return !!e && (!!FX.Utils.isObjectEmpty(t.limit) || this.limitMap[e.departmentId])
        }, _getDynamicFields: function () {
            return this.options.dynamicFields
        }, _createDepartmentItem: function (t) {
            var i = this,
                a = e("<li/>").append(e('<i class="icon-department"/>')).append(e("<span/>").text(t.name)).append(e('<div class="select-btn x-radio"/>').append(e('<i class="icon-blank"/>'))).data("item", t).click(function () {
                    var e = a.children(".select-btn");
                    if (e.hasClass("select")) e.removeClass("select"), i._removeSelectItem(); else {
                        e.addClass("select");
                        var t = a.data("item");
                        i._addSelectItem(t)
                    }
                });
            return this.value === t._id && a.children(".select-btn").addClass("select"), a
        }, _createCurrentDepartmentList: function () {
            var t = this;
            this._isRelyLimitEmpty() || (this.$selectPane.children().hide(), this.$currentDepartmentList ? this.$currentDepartmentList.empty().show() : this.$currentDepartmentList = e('<ul class="department-list"/>').appendTo(this.$selectPane), this.currentDepartments ? FX.Utils.forEach(this.currentDepartments, function (e, i) {
                t.$currentDepartmentList.append(t._createDepartmentItem(i))
            }) : FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.current_departments)}, function (e) {
                t.currentDepartments = e.departmentList, t._createCurrentDepartmentList()
            }))
        }, _createDynamicList: function () {
            var t = this;
            this.$selectPane.children().hide(), this.$dynamicList ? this.$dynamicList.empty().show() : this.$dynamicList = e('<ul class="department-list"/>').appendTo(this.$selectPane), FX.Utils.forEach(this._getDynamicFields(), function (e, i) {
                t.$dynamicList.append(t._createDepartmentItem(i))
            })
        }, _createSearchList: function (t) {
            var i = this;
            if (!this._isRelyLimitEmpty()) {
                this.$selectPane.children().hide();
                var a = [], s = e('<div class="select-search"/>').appendTo(this.$selectPane),
                    n = new RegExp(FX.Utils.escapeRegexp(t), "i");
                FX.Utils.forEach(this.departments, function (e, t) {
                    n.test(t.name) && a.push(t)
                }), a.length <= 0 ? s.append(e('<span class="search-empty"/>').text("暂无相关部门")) : (this.$searchList = e('<ul class="department-list"/>').appendTo(s), FX.Utils.forEach(a, function (t, a) {
                    i._checkLimit(a) && e('<li class="search-item"/>').text(a.name).data("depart", a).appendTo(i.$searchList)
                })), s.bind("click", function (t) {
                    var a = e(t.target).closest("li"), s = a.data("depart");
                    a.length > 0 && (i._addSelectItem(s), i._createDepartmentList())
                })
            }
        }, getItems: function () {
            var t = [];
            return e(".select-item", this.$selectList).each(function (i, a) {
                t.push(e(a).data("item"))
            }), t
        }, _dealCurrentDept: function (e, t) {
            if (!e) return t && t(e);
            var i = this.options;
            if ("select" === i.dynamicType && e._id === i.dynamicKey) {
                var a = FX.Utils.createMask(this.element, {isLight: !0, hasLoader: !0});
                FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.current_departments), async: !1}, function (a) {
                    e && e._id === i.dynamicKey && (e = FX.Utils.isObjectEmpty(a.departmentList) ? null : a.departmentList[0]), t && t(e)
                }, function () {
                    t && t(null)
                }, function () {
                    a.remove()
                })
            } else t && t(e)
        }, setValue: function (e) {
            var t = this;
            this._dealCurrentDept(e, function (e) {
                t.value = t._parseDefaultValue(e), e && (t.items = t._getDynamicFields().concat([e])), t._initData()
            })
        }, getValue: function () {
            return this.value
        }, getCacheValue: function () {
            var e = this.selectMap[this.value];
            return e ? {_id: e._id, name: e.name} : null
        }, getText: function () {
            return this.value && this.selectMap[this.value] ? this.selectMap[this.value].name : ""
        }, _refreshDepartmentList: function (t) {
            var i = this;
            e("li", t).each(function (t, a) {
                var s = e(a).data("item");
                s && (i.value === s._id ? e(a).children(".select-btn").addClass("select") : e(a).children(".select-btn").removeClass("select"))
            })
        }, refresh: function () {
            this.departmentTree.refresh(), this.$dynamicList && this._refreshDepartmentList(this.$dynamicList), this.$currentDepartmentList && this._refreshDepartmentList(this.$currentDepartmentList), this.$searchList && this._refreshDepartmentList(this.$searchList)
        }, checkValidate: function () {
            if (FX.Utils.isExternalLink()) return this.setInvalidateType("regex"), !1;
            var e = this.options;
            return !FX.Utils.isEmpty(this.getValue()) || e.allowBlank
        }, rebuild: function (e) {
            this.setValue(e), this.refresh()
        }, getOptions: function (t) {
            var i = this.options;
            return e.extend(FX.Dept.superclass.getOptions.apply(this, arguments), {
                noRepeat: i.noRepeat,
                limit: i.limit,
                value: "save" === t ? this._parseDefaultValue(i.value) : i.value
            })
        }, _parseDefaultValue: function (e) {
            var t = e;
            return e && e._id && (t = e._id), t
        }
    }), e.shortcut("dept", FX.Dept)
}(jQuery), function (e) {
    FX.DeptGroup = FX.extend(FX.Dept, {
        _defaultConfig: function () {
            return e.extend(FX.DeptGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_dept fui_dept_group",
                width: 420,
                height: 80,
                value: []
            })
        }, _init: function () {
            this.value = [], FX.DeptGroup.superclass._init.apply(this, arguments)
        }, _initData: function () {
            if (!FX.Utils.isExternalLink()) {
                var e = this.options;
                this.selectMap = {}, e.items && (this.items = e.items), this._initSelectPane()
            }
        }, _createSelectList: function () {
            var t = this, i = this.options;
            this.$selectList ? this.$selectList.empty() : this.$selectList = e('<ul class="select-list"/>').appendTo(this.element), this.value && this.value.length > 0 ? FX.Utils.forEach(this.value, function (e, i) {
                var a = t.selectMap[i];
                t._createSelectItem(a)
            }) : i.editable || this.$selectList.append(e('<div class="select-empty"/>').text(i.msg))
        }, _addSelectItem: function (e) {
            this.value.indexOf(e._id) > -1 || (this._createSelectItem(e), this.value = this.getValue(), this.selectMap[e._id] = e, this.refresh())
        }, _removeSelectItem: function (t) {
            e("#" + t._id, this.$selectList).remove(), this.value = this.getValue(), this.refresh()
        }, _doSelectItem: function (e) {
            if (this._checkLimit(e)) {
                var t = {name: e.name, _id: e._id};
                this.value.indexOf(t._id) > -1 ? this._removeSelectItem(t) : this._addSelectItem(t)
            }
        }, _createDepartmentList: function () {
            var t = this, i = this.options;
            this._isRelyLimitEmpty() || (this.$selectPane.children().hide(), this.$memberMenu ? this.$memberMenu.show() : (this.$memberMenu = e('<div class="select-department"/>').appendTo(t.$selectPane), FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.departments),
                data: {departmentLimit: i.limit.departs, hasCurrentDept: i.limit.hasCurrentDept}
            }, function (i) {
                t.departments = e.extend(!0, [], i.departments), t.departments[0] && !t.departments[0]._id && t.departments.shift(), t._initLimitMap(t.departments), t.departmentTree = new FX.Tree({
                    renderEl: e("<div/>").appendTo(t.$memberMenu),
                    customCls: "x-department-tree select-department",
                    Nodes: t.departments,
                    setting: {
                        view: {expandSpeed: 100},
                        data: {simpleData: {enable: !0, idKey: "departmentId", pIdKey: "parentId"}},
                        callback: {
                            onCheck: function (e, i) {
                                t._doSelectItem(i)
                            }, onClick: function (e, i) {
                                t._doSelectItem(i)
                            }, beforeNodeCreate: function (e) {
                                t._checkLimit(e) || (e.nocheck = !0), e.checked = t.value.indexOf(e._id + "") > -1
                            }, onNodeCreated: function (e, i) {
                                i.isParent && !i.open && i.level < 1 && this.expandNode(i, !0), i.departmentId == t.currentDepartment && this.selectNode(i)
                            }
                        },
                        check: {enable: !0, chkboxType: {Y: "", N: ""}}
                    }
                })
            })))
        }, _createDepartmentItem: function (t) {
            var i = this,
                a = e("<li/>").append(e('<i class="icon-department"/>')).append(e("<span/>").text(t.name)).append(e('<div class="select-btn x-check"/>').append(e('<i class="icon-blank"/>'))).data("item", t).click(function () {
                    var e = a.children(".select-btn");
                    if (e.hasClass("select")) e.removeClass("select"), i._removeSelectItem(a.data("item")); else {
                        e.addClass("select");
                        var t = a.data("item");
                        i._addSelectItem(t)
                    }
                });
            return this.value.indexOf(t._id) > -1 && a.children(".select-btn").addClass("select"), a
        }, getItems: function () {
            var t = [];
            return e(".select-item", this.$selectList).each(function (i, a) {
                t.push(e(a).data("item"))
            }), t
        }, checkValidate: function () {
            return FX.Utils.isExternalLink() ? (this.setInvalidateType("regex"), !1) : !(!this.options.allowBlank && 0 === this.getValue().length)
        }, _dealCurrentDept: function (e, t) {
            if (!e || !e.length) return t && t([]);
            var i = this.options, a = -1;
            if (FX.Utils.forEach(e, function (e, t) {
                    if (t && t._id === i.dynamicKey) return a = e, !1
                }), "select" === i.dynamicType && a > -1) {
                var s = FX.Utils.createMask(this.element, {isLight: !0, hasLoader: !0});
                FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.current_departments), async: !1}, function (s) {
                    e[a] && e[a]._id === i.dynamicKey && (e.splice(a, 1), e = e.concat(s.departmentList)), t && t(e)
                }, function () {
                    e[a] && e[a]._id === i.dynamicKey && e.splice(a, 1), t && t(e)
                }, function () {
                    s.remove()
                })
            } else t && t(e)
        }, setValue: function (e) {
            var t = this;
            this._dealCurrentDept(e, function (e) {
                t.value = [], t.items = [].concat(t._getDynamicFields());
                var i = {};
                FX.Utils.forEach(e, function (e, a) {
                    a && a._id ? i[a._id] || (i[a._id] = !0, t.value.push(a._id), t.items.push(a)) : i[a] || (i[a] = !0, t.value.push(a))
                }), t._initData()
            })
        }, getValue: function () {
            var t = this.value;
            return this.$selectList && (t = [], e(".select-item", this.$selectList).each(function (i, a) {
                t.push(e(a).attr("id"))
            })), t
        }, getCacheValue: function () {
            var e = this, t = [];
            return FX.Utils.forEach(this.getValue(), function (i, a) {
                var s = e.selectMap[a];
                t.push({_id: s._id, name: s.name})
            }), t
        }, getText: function () {
            var e = this, t = [];
            return FX.Utils.forEach(this.value, function (i, a) {
                e.selectMap[a] && t.push(e.selectMap[a].name)
            }), t
        }, getNullValue: function () {
            return []
        }, _refreshDepartmentList: function (t) {
            var i = this;
            e("li", t).each(function (t, a) {
                var s = e(a).data("item");
                s && (i.value.indexOf(s._id) > -1 ? e(a).children(".select-btn").addClass("select") : e(a).children(".select-btn").removeClass("select"))
            })
        }, _parseDefaultValue: function (e) {
            var t = [];
            return FX.Utils.forEach(e, function (e, i) {
                i && i._id ? t.push(i._id) : t.push(i)
            }), t
        }
    }), e.shortcut("deptgroup", FX.DeptGroup)
}(jQuery), function (e) {
    FX.LinkQuery = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.LinkQuery.superclass._defaultConfig.apply(), {
                baseCls: "fui_link_query",
                allowBlank: !0,
                linkFields: [],
                linkFilter: [],
                linkForm: null,
                layout: "",
                itemPadding: 4
            })
        }, _init: function () {
            FX.LinkQuery.superclass._init.apply(this, arguments);
            var t = this.options, i = this;
            this.widgetsMap = {}, this.typeMap = {}, FX.Utils.forEach(t.linkFields, function (a, s) {
                var n = e('<div class="link-field"/>').appendTo(i.element), o = i._formatSubFormItems(s), l = {},
                    r = i._formatWidgetType(s.type);
                t.subform ? (n.addClass("sub-link"), l.width = FX.Utils.getSubformWidgetWidth(s)) : (n.append(e('<div class="fl-label"/>').text(s.text)), FX.Utils.isEmpty(t.layout) || FX.Utils.setLayoutSize(l, t.layout, r)), i.widgetsMap[s.name] = FX.createWidget(e.extend(l, {
                    renderEl: e("<div/>").appendTo(n),
                    widgetName: s.name,
                    type: r,
                    items: o,
                    format: s.format,
                    enable: !1
                })), i.typeMap[s.name] = s.type
            })
        }, _formatSubFormItems: function (t) {
            if ("subform" === t.type) {
                var i = this, a = [];
                return FX.Utils.forEach(t.items, function (t, s) {
                    if (s.widget) {
                        i.typeMap[s.widget.widgetName] = s.widget.type;
                        var n = e.extend(!0, {}, s);
                        n.widget.type = i._formatWidgetType(s.widget.type), a.push(n)
                    }
                }), a
            }
        }, _formatWidgetType: function (e) {
            switch (e) {
                case"combo":
                case"combocheck":
                case"radiogroup":
                case"checkboxgroup":
                case"address":
                case"location":
                    return "text";
                default:
                    return e
            }
        }, _formatWidgetData: function (e, t) {
            var i = this;
            switch (e) {
                case"address":
                    return FX.Utils.address2Str(t, "", "pcda");
                case"location":
                    var a = FX.Utils.formatData({type: e}, t);
                    return a.address + " " + a.lngLat;
                case"subform":
                    return FX.Utils.forEach(t, function (e, t) {
                        FX.Utils.forEach(t, function (e, a) {
                            t[e] = i._formatWidgetData(i.typeMap[e], a)
                        })
                    }), t;
                default:
                    return t
            }
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.LinkQuery.superclass.getOptions.apply(this, arguments), {
                linkFilter: t.linkFilter,
                linkFields: t.linkFields,
                linkForm: t.linkForm,
                refAppId: t.refAppId
            })
        }, reload: function (e) {
            var t = this.options, i = this, a = [];
            FX.Utils.forEach(t.linkFields, function (e, t) {
                a.push(t.name)
            }), !t.linkForm || a.length <= 0 || FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.filter_link),
                data: {formId: t.linkForm, fields: a, filter: e, refAppId: t.refAppId}
            }, function (e) {
                var a = {};
                FX.Utils.isObjectEmpty(e.dataList) ? FX.Utils.forEach(i.widgetsMap, function (e, t) {
                    t.setValue(null)
                }) : (a = e.dataList[0], FX.Utils.forEach(i.widgetsMap, function (e, t) {
                    var s = i._formatWidgetData(i.typeMap[e], a[e]);
                    t.setValue(s)
                })), FX.Utils.applyFunc(i, t.onRelyDone, [i], !1)
            })
        }, getCacheValue: function () {
            var e = {};
            return FX.Utils.forEach(this.widgetsMap, function (t, i) {
                e[t] = i.getCacheValue()
            }), e
        }, setCacheValue: function (e) {
            FX.Utils.forEach(this.widgetsMap, function (t, i) {
                e ? i.setCacheValue(e[t]) : i.setCacheValue(null)
            })
        }, doResize: function (e) {
            var t = this.options;
            if (t.subform) {
                var i = -t.itemPadding;
                FX.Utils.forEach(t.linkFields, function (e, a) {
                    i += FX.Utils.getSubformWidgetWidth(a) + t.itemPadding
                }), i = Math.max(i, FX.Utils.getSubformWidgetWidth({type: t.type})), this.element.css({width: i})
            }
        }, supportLayout: function () {
            var e = this.options, t = !0;
            return FX.Utils.forEach(e.linkFields, function (e, i) {
                if ("subform" === i.type) return t = !1, !1
            }), t
        }
    }), e.shortcut("linkquery", FX.LinkQuery)
}(jQuery), function (e) {
    FX.LinkData = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.LinkData.superclass._defaultConfig.apply(), {
                baseCls: "fui_link_data",
                allowBlank: !0,
                linkFields: [],
                linkKey: null,
                linkFilter: [],
                linkForm: null,
                itemsPerPage: 20,
                layout: "",
                onBeforeLinkData: null,
                itemPadding: 4,
                selectWidth: 35,
                btnWidth: 240
            })
        }, _init: function () {
            FX.LinkData.superclass._init.apply(this, arguments);
            var t = this.options, i = this;
            this._createSelectBtn(), this.widgetsMap = {}, this.typeMap = {}, FX.Utils.forEach(t.linkFields, function (a, s) {
                var n = e('<div class="link-field"/>').appendTo(i.element), o = i._formatSubFormItems(s), l = {},
                    r = i._formatWidgetType(s.type);
                t.subform ? (n.addClass("sub-link"), l.width = FX.Utils.getSubformWidgetWidth(s)) : (n.append(e('<div class="fl-label"/>').text(s.text)), FX.Utils.isEmpty(t.layout) || FX.Utils.setLayoutSize(l, t.layout, r)), i.widgetsMap[s.name] = FX.createWidget(e.extend(l, {
                    renderEl: e("<div/>").appendTo(n),
                    widgetName: s.name,
                    type: r,
                    items: o,
                    format: s.format,
                    enable: !1
                })), i.typeMap[s.name] = s.type
            })
        }, _setWidgetsValue: function (e) {
            var t = this;
            FX.Utils.forEach(this.widgetsMap, function (i, a) {
                var s = t._formatWidgetData(t.typeMap[i], e[i]);
                a.setValue(s)
            })
        }, _formatSubFormItems: function (t) {
            if ("subform" === t.type) {
                var i = this, a = [];
                return FX.Utils.forEach(t.items, function (t, s) {
                    if (s.widget) {
                        i.typeMap[s.widget.widgetName] = s.widget.type;
                        var n = e.extend(!0, {}, s);
                        n.widget.type = i._formatWidgetType(s.widget.type), a.push(n)
                    }
                }), a
            }
        }, _formatWidgetType: function (e) {
            switch (e) {
                case"combo":
                case"combocheck":
                case"radiogroup":
                case"checkboxgroup":
                case"address":
                case"location":
                    return "text";
                default:
                    return e
            }
        }, _formatWidgetData: function (e, t) {
            var i = this;
            switch (e) {
                case"address":
                    return FX.Utils.address2Str(t, "", "pcda");
                case"location":
                    var a = FX.Utils.formatData({type: e}, t);
                    return a.address + " " + a.lngLat;
                case"subform":
                    return FX.Utils.forEach(t, function (e, t) {
                        FX.Utils.forEach(t, function (e, a) {
                            t[e] = i._formatWidgetData(i.typeMap[e], a)
                        })
                    }), t;
                default:
                    return t
            }
        }, _createSelectBtn: function () {
            var t = this.options, i = this;
            t.subform ? e('<div class="data-select select-btn"/>').append(e('<i class="icon-data-picker"/>')).appendTo(this.element).click(function () {
                i.isEnabled() && FX.Utils.applyFunc(i, t.onBeforeLinkData, [t.linkFilter], !1)
            }) : new FX.Button({
                text: "选择数据",
                width: t.btnWidth,
                style: "white",
                renderEl: e('<div class="select-btn"/>').appendTo(this.element),
                onClick: function () {
                    i.isEnabled() && FX.Utils.applyFunc(i, t.onBeforeLinkData, [t.linkFilter], !1)
                }
            })
        }, _createDataList: function (t) {
            var i = this;
            this.datalist && this.datalist.remove(), this.items = t, this.datalist = e('<ul class="link-data-list"/>'), this.datalist.append(e('<li class="data-item data-clear"/>').text("清空")), t.length <= 0 ? this.datalist.append(e('<div class="link-empty-list"/>').text("没有符合条件的数据")) : FX.Utils.forEach(t, function (e, t) {
                i._createDataItem(t)
            });
            var a = FX.Msg.bubble({
                anchor: e(".select-btn", this.element),
                text4Ok: null,
                text4Cancel: null,
                minWidth: 230,
                contentHTML: this.datalist,
                hAdjust: 113,
                contentPadding: 0,
                edge: 240,
                hasTriangle: !1
            });
            this._bindListEvent(a)
        }, _createDataItem: function (t) {
            var i = this.options, a = this, s = t.label;
            if (FX.Utils.isEmpty(s)) {
                var n = [];
                FX.Utils.forEach(i.linkFields, function (e, i) {
                    var s = a._formatData(i.type, t[i.name], i.format);
                    s && n.push(s)
                }), s = n.join(",")
            }
            var o = e('<li class="data-item" title="' + s + '"/>').text(s).appendTo(this.datalist).data("data", t);
            this.value && this.value.id === t._id && o.addClass("select")
        }, _bindListEvent: function (t) {
            var i = this, a = this.options;
            this.datalist.click(function (s) {
                var n = s.target, o = e(n).closest(".data-item");
                if (o && o.length > 0) {
                    if (o.hasClass("data-clear")) i.value = {}, FX.Utils.forEach(i.widgetsMap, function (e, t) {
                        t.setValue(null)
                    }); else {
                        var l = o.data("data");
                        i.value = {id: l._id, key: l[a.linkKey]}, i._setWidgetsValue(l)
                    }
                    FX.Utils.applyFunc(i, a.onStopEdit, [], !1), t.close()
                }
                return !1
            }), this.datalist.scroll(function () {
                this.scrollTop + e(this).height() > this.scrollHeight - 5 && i.loadMore()
            })
        }, _formatData: function (e, t, i) {
            if (FX.Utils.isObjectEmpty(t)) return "";
            var a = t.toString();
            switch (e) {
                case"address":
                case"location":
                    a = FX.Utils.address2Str(t, "", "pcda");
                    break;
                case"datetime":
                    a = FX.Utils.date2Str(new Date(t), i || "yyyy-MM-dd");
                    break;
                case"subform":
                    a = "";
                    break;
                case"user":
                    a = t && t.name;
                    break;
                case"usergroup":
                    a = t && t.map(function (e) {
                        return e.name
                    })
            }
            return a
        }, checkValidate: function () {
            return this.options.allowBlank || !FX.Utils.isObjectEmpty(this.value)
        }, setValue: function (e) {
            var t = this.options, i = this;
            this.value = e, !FX.Utils.isObjectEmpty(e) && e.hasOwnProperty("id") && FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.read_link),
                data: {formId: e.entryId || t.linkForm, linkId: e.id, refAppId: e.appId || t.refAppId}
            }, function (e, t) {
                i._setWidgetsValue(e.data)
            })
        }, getValue: function () {
            var t = this.options;
            return this.value && this.value.id ? e.extend({appId: t.refAppId, entryId: t.linkForm}, this.value) : {}
        }, getText: function () {
            var e = {};
            return FX.Utils.forEach(this.widgetsMap, function (t, i) {
                e[t] = i.getText()
            }), e
        }, getLinkValue: function () {
            return this.value && this.value.key
        }, getLinkType: function () {
            return this.options.linkType
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.LinkData.superclass.getOptions.apply(this, arguments), {
                linkFilter: t.linkFilter,
                linkFields: t.linkFields,
                linkForm: t.linkForm,
                linkKey: t.linkKey,
                linkType: t.linkType,
                refAppId: t.refAppId
            })
        }, getNullValue: function () {
            return {}
        }, _loadData: function (e) {
            var t = this.options, i = this;
            this.loading = !0, FX.Utils.dataAjax({
                url: FX.Utils.getApi(FX.API.data.filter_link),
                data: {
                    multi: !0,
                    formId: t.linkForm,
                    fields: this.fields,
                    filter: this.filter,
                    limit: t.itemsPerPage,
                    skip: this.skip,
                    refAppId: t.refAppId
                }
            }, function (a) {
                var s = [];
                FX.Utils.isObjectEmpty(a.dataList) || (s = a.dataList), s.length < t.itemsPerPage && (i.hasMore = !1), e ? i._createDataList(s) : FX.Utils.forEach(s, function (e, t) {
                    i._createDataItem(t)
                })
            }, function () {
            }, function () {
                i.skip += t.itemsPerPage, i.loading = !1
            })
        }, loadMore: function () {
            !this.loading && this.hasMore && this._loadData()
        }, reload: function (e) {
            var t = this.options, i = [];
            FX.Utils.forEach(t.linkFields, function (e, t) {
                i.push(t.name)
            }), t.linkKey && i.push(t.linkKey), !t.linkForm || i.length <= 0 || (this.filter = e, this.fields = i, this.skip = 0, this.hasMore = !0, this._loadData(!0))
        }, doResize: function (e) {
            var t = this.options;
            if (t.subform) {
                var i = t.selectWidth - t.itemPadding;
                FX.Utils.forEach(t.linkFields, function (e, a) {
                    i += FX.Utils.getSubformWidgetWidth(a) + t.itemPadding
                }), i = Math.max(i, FX.Utils.getSubformWidgetWidth({type: t.type})), this.element.css({width: i})
            }
        }, supportLayout: function () {
            var e = this.options, t = !0;
            return FX.Utils.forEach(e.linkFields, function (e, i) {
                if ("subform" === i.type) return t = !1, !1
            }), t
        }
    }), e.shortcut("linkdata", FX.LinkData)
}(jQuery), function (e) {
    FX.Block = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Block.superclass._defaultConfig.apply(), {
                title: "",
                visible4Title: !0,
                cls4FullScreen: "block-fullscreen",
                hasHeader: !0,
                hasBorder: !0,
                height4Head: 35,
                height: 230,
                width: 200,
                forms: [],
                filter: null,
                linkWidgets: null,
                allowDataLoad: !0,
                onAfterHeadCreate: null,
                scalable: !1
            })
        }, _init: function () {
            FX.Block.superclass._init.apply(this, arguments);
            var e = this.options;
            this.element.addClass("x-block-bg"), e.hasBorder || this.element.addClass("no-border"), e.hasHeader && this._onCreateHead(), this._onCreateBody()
        }, _onCreateHead: function () {
            var t = this.options;
            if (t.height4Head) {
                this.$head = e('<div class="x-block-head"/>').height(t.height4Head).css({"line-height": t.height4Head + "px"}).appendTo(this.element);
                var i = e('<div class="x-block-head-title"/>').appendTo(this.$head);
                t.visible4Title && i.text(t.title)
            }
            return FX.Utils.applyFunc(this, t.onAfterHeadCreate, [this.$head], !1), this.$head
        }, createHeadTools: function () {
            var t = this, i = this.options;
            if (this.$head.children("a").remove(), i.scalable) {
                var a = "全屏", s = e("<a />").append('<i class="icon-enlarge">');
                t.element.hasClass(i.cls4FullScreen) && (s = e("<a />").append('<i class="icon-shrink">'), a = "缩小"), s.appendTo(this.$head).click(function () {
                    t.doFullScreen() ? (s.children("i").removeClass().addClass("icon-shrink"), a = "缩小") : (s.children("i").removeClass().addClass("icon-enlarge"), a = "全屏")
                }).hover(function () {
                    FX.UI.showPopover({
                        position: "bottomLeft",
                        anchor: e(this).children("i"),
                        content: e("<span/>").text(a),
                        type: "dark"
                    })
                }, function () {
                    FX.UI.closePopover()
                })
            }
        }, _onCreateBody: function () {
            return this.$body = e('<div class="x-block-body"/>').appendTo(this.element), this._resizeBody(), this._initContent(this.$body), this.$body
        }, _resizeBody: function () {
            var e = this.options, t = {};
            if (FX.Utils.isNumber(e.width)) {
                var i = e.width;
                e.hasBorder && (i -= 2), t.width = i
            } else FX.Utils.isNull(e.width) || (t.width = e.width);
            if (FX.Utils.isNumber(e.height)) {
                var a = e.height;
                e.hasBorder && (a -= 2), e.hasHeader && (a -= e.height4Head), t.height = a, this.$body.addClass("fixed-height")
            } else FX.Utils.isNull(e.height) ? (this.$body.removeClass("fixed-height"), t.height = "auto") : (this.$body.removeClass("fixed-height"), t.height = e.height);
            this.$body.css(t)
        }, _initContent: function (e) {
        }, isAllowDataLoad: function () {
            return this.options.allowDataLoad
        }, setAllowDataLoad: function (e) {
            this.options.allowDataLoad = !!e
        }, loadingAjax: function (e, t, i) {
            var a = this;
            if (this.isAllowDataLoad() && !this.isLoading) {
                this.isLoading = !0;
                var s = this.createLoadingMask();
                FX.Utils.dataAjax(e, function (e, i) {
                    return FX.Utils.applyFunc(a, t, [e, i], !1)
                }, function (e, t) {
                    return FX.Utils.applyFunc(a, i, [e, t], !1)
                }, function () {
                    s.remove(), a.isLoading = !1
                })
            }
        }, createLoadingMask: function () {
            return FX.Utils.createMask(this.element, {hasLoader: !0, isLight: !0})
        }, _makeGroups: function (t) {
            var i = [], a = function (t, a) {
                t.forEach(function (t) {
                    var s = e.extend({}, a), n = a.tag || a.name;
                    s.groupName = n + "_" + t, s.groupBy = t, i.push(s)
                })
            };
            return FX.Utils.forEach(t, function (e, t) {
                switch (t.type) {
                    case"datetime":
                        var s = t.dateType || "year";
                        a(s.split("&"), t);
                        break;
                    case"address":
                    case"location":
                        var n = t.addressType || "province";
                        a(n.split("&"), t);
                        break;
                    default:
                        i.push(t)
                }
            }), i
        }, reload: function (e) {
        }, rebuild: function () {
            this.$body.remove(), this._onCreateBody()
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Block.superclass.getOptions.apply(this, arguments), {
                title: t.title,
                linkWidgets: t.linkWidgets,
                forms: t.forms,
                filter: t.filter
            })
        }, _getWidgetNameByTag: function (e) {
            var t = this.options, i = e;
            return FX.Utils.forEach([].concat(t.xFields, t.yFields), function (t, a) {
                if (a.tag && a.tag === e) return i = a.name, !1
            }), i
        }, _getLinkFilterParams: function (t) {
            var i = this.options, a = this, s = [], n = [];
            return FX.Utils.forEach(t, function (t, o) {
                var l = a._getWidgetNameByTag(o.field);
                if (i.relations[l]) {
                    var r = i.relations[l];
                    FX.Utils.forEach(r, function (t, i) {
                        var a = FX.Utils.pick(o, ["method", "type", "value"]);
                        e.extend(a, FX.Utils.dealFilterInfoByField({id: t, name: i})), s.push(a)
                    })
                } else n = i.forms[0].split("@"), o.entryId = n.shift(), n.length && (o.appId = n.shift()), s.push(o)
            }), s
        }, getFilterData: function (e) {
            var t = this, i = this.options, a = FX.Utils.applyFunc(this, i.onDataFilter, [], !1), s = [];
            return a && (s = s.concat(a)), FX.Utils.isObjectEmpty(e) || FX.Utils.forEach(e, function (e, a) {
                FX.Utils.forEach(i.forms, function (e, i) {
                    t._isSameEntry(i, a) && s.push(a)
                })
            }), i.filter && "edit" === i.mode && (s = s.concat(i.filter.cond)), FX.Utils.isObjectEmpty(s) ? {} : {
                cond: s,
                rel: FX.CONST.FILTER_RELATION.AND
            }
        }, _isSameEntry: function (e, t) {
            var i = FX.Utils.getFieldInfoById(e), a = i.entryId, s = i.appId || t.appId;
            return a === t.entryId && s === t.appId
        }, doResize: function (e) {
            FX.Block.superclass.doResize.apply(this, arguments), this._resizeBody()
        }, doFullScreen: function () {
            var e = this.options;
            return this.element.hasClass(e.cls4FullScreen) ? (this.element.removeClass(e.cls4FullScreen), this.doResize({
                width: FX.Utils.isEmpty(this.originStyle.w) ? "auto" : this.originStyle.w,
                height: FX.Utils.isEmpty(this.originStyle.h) ? "auto" : this.originStyle.h
            }), !1) : (this.originStyle = {
                w: this.element.outerWidth(),
                h: e.height
            }, this.element.addClass(e.cls4FullScreen), this.doResize({
                width: document.body.clientWidth,
                height: document.body.clientHeight
            }), !0)
        }
    })
}(jQuery), function (e) {
    FX.Table = FX.extend(FX.Block, {
        _defaultConfig: function () {
            return e.extend(FX.Table.superclass._defaultConfig.apply(), {
                baseCls: "fui_table",
                tableHead: null,
                tableRowHead: null,
                tableData: [],
                hasMenu: !1,
                isHeadSticky: !1,
                isRowHeadSticky: !1,
                onScroll: null,
                onAfterTableCreate: null,
                onCheckValid: null,
                exportable: !0,
                scalable: !0,
                tableClass: "x-table"
            })
        }, _initContent: function (t) {
            FX.Table.superclass._initContent.apply(this, arguments);
            var i = this.options;
            this.$wrapper = e('<div class="fui_table-wrapper"/>').appendTo(t), i.hasMenu && (this.$wrapper.addClass("has-menu"), this.$menu = e('<div class="fui-table-menu"/>').appendTo(t)), this._removeTable()
        }, createHeadTools: function () {
            FX.Table.superclass.createHeadTools.apply(this, arguments);
            var t = this;
            this.options.exportable && e("<a/>").append('<i class="icon-export">').append(e("<span/>").text("导出Excel")).appendTo(this.$head).click(function () {
                t.doExcelExport()
            })
        }, createTable: function () {
            var t = this, i = this.options;
            if (this.$tableScroller = e('<div class="table-scroller"/>').scroll(function () {
                    t._scrollStickyHead()
                }).appendTo(this.$wrapper), this.$table = e('<table cellpadding="0" cellspacing="0" class="' + i.tableClass + ' x-table-bordered x-table-striped t-main"/>').appendTo(this.$tableScroller), i.tableHead && i.tableHead.length > 0) {
                var a = e('<thead class="t-head"/>').appendTo(this.$table);
                FX.Utils.forEach(i.tableHead, function (i, s) {
                    var n = e('<tr class="t-row th-row"/>').appendTo(a);
                    FX.Utils.forEach(s, function (e, i) {
                        t._createCell(i, {tag: "th", cls: "th-cell"}).appendTo(n)
                    })
                })
            }
            this.$tableBody = e('<tbody class="t-body"/>').appendTo(this.$table), this._appendTableData(), this._setEvent(), this._createStickyHead(), FX.Utils.applyFunc(this, i.onAfterTableCreate, [], !1)
        }, _appendTableData: function () {
            var t = this, i = this.options;
            FX.Utils.forEach(i.tableData, function (a, s) {
                var n = a % 2 == 0 ? "odd" : "even",
                    o = e('<tr class="t-row tb-row"/>').addClass(n).appendTo(t.$tableBody);
                t._bindRowData(t.$tableBody, o, a), i.tableRowHead && i.tableRowHead.length > 0 && i.tableRowHead.forEach(function (e) {
                    var i = e[a];
                    i && t._createCell(i, {tag: "th", cls: "rh-cell"}).appendTo(o)
                }), FX.Utils.forEach(s, function (e, i) {
                    t._formatCell(i), i.row = a, i.col = e, t._createCell(i, {tag: "td", cls: "td-cell"}).appendTo(o)
                })
            })
        }, _bindRowData: function (e, t, i) {
        }, _formatCell: function (e) {
        }, _createCell: function (t, i) {
            var a = i || {tag: "td"};
            a.cls && t.cls && (t.cls = a.cls + " " + t.cls);
            var s = e.extend(a, t.text || t.html || !FX.Utils.isString(t) ? t : {text: t}),
                n = e("<" + s.tag + ' class="t-cell"/>');
            switch (n.attr({
                row: s.row,
                col: s.col
            }), s.hasOwnProperty("html") ? n.html(s.html) : n.text(s.text), s.align) {
                case"center":
                    n.addClass("h-center");
                    break;
                case"right":
                    n.addClass("h-right")
            }
            if (s.data) for (var o in s.data) s.data.hasOwnProperty(o) && n.data(o, s.data[o]);
            return s.cls && n.addClass(s.cls), s.colspan && n.attr("colspan", s.colspan), s.rowspan && n.attr("rowspan", s.rowspan), s.width && n.width(s.width), s.height && n.width(s.height), n
        }, _createStickyHead: function () {
            var t = this, i = this.options;
            !0 === i.isHeadSticky && (this.$stickyHead = e('<table cellpadding="0" cellspacing="0" class="' + i.tableClass + ' x-table-bordered x-table-striped"/>').append(this.$table.children(".t-head").clone(!0)).outerWidth(this.$table.outerWidth()), this.$stickyHead.find(".t-head .th-cell").each(function (i, a) {
                var s = t.$table.find(".t-head .th-cell").eq(i);
                e(a).outerWidth(s.outerWidth())
            }), e('<div class="table-sticky-head"/>').css({width: this.$tableScroller[0].clientWidth}).append(this.$stickyHead).appendTo(this.$wrapper)), !0 === i.isRowHeadSticky && (this.$stickyRowHead = e('<table cellpadding="0" cellspacing="0" class="' + i.tableClass + ' x-table-bordered x-table-striped"/>').append(this.$table.children(".t-head, .t-body").clone(!0)), this.$stickyRowHead.find(".t-head .th-cell").each(function (i, a) {
                var s = t.$table.find(".t-head .th-cell").eq(i);
                e(a).outerWidth(s.outerWidth())
            }), this.$stickyRowHead.find(".t-row").each(function (i, a) {
                var s = t.$table.find(".t-row").eq(i);
                e(a).outerHeight(s.outerHeight())
            }), this.$stickyRowHead.children(".t-head").children("tr.t-row").each(function (t, i) {
                e(i).children(".th-cell").not(".group-head").remove()
            }), this.$stickyRowHead.find(".t-body .td-cell").remove(), e('<div class="table-sticky-row-head"/>').css({height: this.$tableScroller[0].clientHeight}).append(this.$stickyRowHead).appendTo(this.$wrapper)), !0 === i.isHeadSticky && !0 === i.isRowHeadSticky && (this.$stickyIntersect = e('<table cellpadding="0" cellspacing="0" class="' + i.tableClass + ' x-table-bordered x-table-striped"/>').append(this.$stickyRowHead.children(".t-head").clone(!0)), e('<div class="table-sticky-intersect"/>').append(this.$stickyIntersect).appendTo(this.$wrapper))
        }, rebuildStickyHead: function () {
            this.element.find(".table-sticky-head, .table-sticky-row-head, .table-sticky-intersect").remove(), this._createStickyHead()
        }, _scrollStickyHead: function () {
            var e = this.options, t = this.$tableScroller.scrollTop(), i = this.$tableScroller.scrollLeft();
            !1 === FX.Utils.applyFunc(this, e.onScroll, [i, t], !1) && (this.$stickyHead && this.$stickyHead.css({"margin-left": -i}), this.$stickyRowHead && this.$stickyRowHead.css({"margin-top": -t}))
        }, _setEvent: function () {
        }, _removeTable: function () {
            this.$wrapper.children().remove(), this.$menu && this.$menu.children().remove()
        }, reload: function (e) {
            FX.Table.superclass.reload.apply(this, arguments), this._removeTable()
        }, refresh: function () {
            this.options.tableRowHead = [], this._removeTable(), this.createTable()
        }, doResize: function (e) {
            this.options;
            FX.Table.superclass.doResize.apply(this, arguments), this.$table && (this.$stickyHead && this.$stickyHead.parent().remove(), this.$stickyRowHead && this.$stickyRowHead.parent().remove(), this.$stickyIntersect && this.$stickyIntersect.parent().remove(), this._createStickyHead(), this._scrollStickyHead())
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Table.superclass.getOptions.apply(this, arguments), {exportable: t.exportable})
        }
    })
}(jQuery), function (e) {
    FX.DataTableTemplate = FX.extend(FX.Table, {
        _defaultConfig: function () {
            return e.extend(FX.DataTableTemplate.superclass._defaultConfig.apply(), {
                itemEditable: !1,
                itemRemovable: !1,
                hasCheck: !1,
                isHeadSticky: !0,
                isRowHeadSticky: !0,
                tableRowHead: []
            })
        }, createTable: function () {
            this._initHeadCount(), this._createTableHead(), this._extendTableHead(), this._createTableData(), FX.DataTableTemplate.superclass.createTable.call(this)
        }, appendData: function () {
            var e = this.options;
            e.tableRowHead = [], this._extendTableHead(), this._createTableData(), this._appendTableData(), (e.isHeadSticky || e.isRowHeadSticky) && this.rebuildStickyHead()
        }, _initHeadCount: function () {
            var e = this;
            this.headRowCount = 1, FX.Utils.forEach(e.header, function (t, i) {
                if ("subform" === i.type) return e.headRowCount = 2, !1
            })
        }, getSortedFieldIdx: function (e) {
            var t = -1;
            return FX.Utils.forEach(this.sort, function (i, a) {
                if (a) return a[e] ? (t = i, !1) : void 0
            }), t
        }, _getFieldTargetName: function (e) {
            return e ? e.tag || e.name : ""
        }, _createTableHead: function () {
            for (var e = this, t = this.options, i = [], a = 0; a < this.headRowCount; a++) i.push([]);
            this.cols = [], this.fieldTypeMap = {_removeCheck: "_removeCheck"}, FX.Utils.forEach(e.header, function (t, a) {
                if (a && !a.detailOnly) {
                    var s, n = e._getFieldTargetName(a), o = {text: a.text, cls: a.type + "-col", colspan: 1},
                        l = {field: n};
                    a.cellFmt && (s = a.cellFmt.data), l.format = s || a.format, a.regex && (l.regex = a.regex);
                    var r = e.getSortedFieldIdx(n);
                    if (~r) switch (e.sort[r][n]) {
                        case 1:
                            o.cls += " sort sort-asc";
                            break;
                        case-1:
                            o.cls += " sort sort-desc"
                    }
                    switch (e.fieldTypeMap[n] = a.type, a.type) {
                        case"image":
                        case"upload":
                        case"address":
                        case"location":
                        case"user":
                        case"usergroup":
                        case"dept":
                        case"deptgroup":
                        case"id":
                        case"did":
                        case"combocheck":
                        case"checkboxgroup":
                            o.rowspan = e.headRowCount, o.data = {field: n}, i[0].push(o), e.cols.push(l);
                            break;
                        case"subform":
                            if (!a.items) return;
                            o.colspan = a.items.length, o.cls += " combined-col", FX.Utils.forEach(a.items, function (t, a) {
                                var s = {field: n, subField: e._getFieldTargetName(a)},
                                    o = [s.field, s.subField].join(".");
                                e.fieldTypeMap[o] = a.type;
                                var l = {text: a.text, rowspan: e.headRowCount - 1};
                                l.rowspan = e.headRowCount - 1;
                                var r;
                                a.cellFmt && (r = a.cellFmt.data), "linkdata" === a.type && (s.linkType = a.linkType), s.format = r || a.format, e.cols.push(s), i[1].push(l)
                            }), a.items.length > 0 && i[0].push(o);
                            break;
                        case"datetime":
                            o.rowspan = e.headRowCount, o.data = {field: n}, o.cls += " clickable sortable", e.cols.push(l), i[0].push(o);
                            break;
                        case"chargers":
                            e.cols.push({show: "node", field: l.field}), i[0].push({
                                colspan: o.colspan,
                                rowspan: e.headRowCount,
                                data: {resizeCol: n},
                                text: "当前节点"
                            }), e.cols.push({show: "user", field: l.field}), i[0].push({
                                colspan: o.colspan,
                                rowspan: e.headRowCount,
                                data: {resizeCol: n},
                                text: "当前负责人"
                            });
                            break;
                        default:
                            if ("flowVer" === a.name) break;
                            "linkdata" === a.type && (l.linkType = a.linkType), "label" === a.name ? o.cls += " group-head" : o.cls += " clickable sortable", o.rowspan = e.headRowCount, o.data = {field: n}, e.cols.push(l), i[0].push(o)
                    }
                }
            }), t.tableHead = i
        }, _extendTableHead: function () {
            var t = this.options;
            if (t.hasCheck) {
                var i = e('<div class="x-check table-op-btn"><i class="icon-blank"/></div>').click(function () {
                    i.toggleClass("select")
                });
                t.tableHead[0].unshift({
                    rowspan: this.headRowCount,
                    cls: "table-op-btn-cell group-head",
                    html: i
                }), this.cols.unshift({field: "_removeCheck"}), this.removeCheckList = [], t.tableRowHead.push(this.removeCheckList)
            }
        }, _createTableData: function () {
            var e = this, t = this.options;
            t.tableData = [], this.dataMap = [], this.labelHeads = [], FX.Utils.forEach(e.data, function (i, a) {
                for (var s = [], n = e._calculateDataRowCount(a), o = 0; o < n; o++) s.push([]);
                FX.Utils.forEach(e.cols, function (t, i) {
                    var o = e._createCellData(a, i, !1);
                    if ("label" === i.field) return e._createTableRowHeadCell(o, n);
                    switch (e.fieldTypeMap[i.field]) {
                        case"subform":
                            var l = a[i.field];
                            FX.Utils.isObjectEmpty(l) && (l = [{}]);
                            for (var r = 0; r < n; r++) {
                                var c = l[r], d = e._createCellData(c, i, !0);
                                s[r].push(d)
                            }
                            break;
                        case"_removeCheck":
                            o.rowspan = n, e.removeCheckList.push(o), e.removeCheckList.length += n - 1;
                            break;
                        default:
                            o.rowspan = n, s[0].push(o)
                    }
                }), a && FX.Utils.forEach(s, function (t, a) {
                    e.dataMap.push(i)
                }), t.tableData = t.tableData.concat(s)
            }), t.tableRowHead.push(this.labelHeads)
        }, _createTableRowHeadCell: function (t, i) {
            var a = e.extend(t, {col: 0, rowspan: i});
            if (this.labelHeads.push(a), i > 1) for (var s = 0; s < i - 1; s++) this.labelHeads.push(null)
        }, _calculateDataRowCount: function (e) {
            var t = this, i = [1];
            for (FX.Utils.forEach(e, function (e, a) {
                a && "subform" === t.fieldTypeMap[e] && i.push(a.length || 1)
            }); i.length >= 2;) i.push(Math.max(i.pop(), i.pop()));
            return i[0]
        }, _createCellData: function (t, i, a) {
            var s, n;
            if (FX.Utils.isNull(t)) return {text: ""};
            a ? (s = t[i.subField], n = this.fieldTypeMap[i.field + "." + i.subField]) : (s = t[i.field], n = this.fieldTypeMap[i.field]);
            var o = {text: ""};
            switch (n) {
                case"checkboxgroup":
                case"combocheck":
                case"array":
                    o = {text: FX.Utils.isNull(s) ? "" : s.join(", ")};
                    break;
                case"text":
                    if (i.regex && new RegExp(i.regex).test(s)) {
                        var l = FX.CONST.TEXT_TYPE_REGEXP;
                        i.regex === l.email && (o = {html: '<a href="mailto:' + s + '">' + s + "</a>"})
                    }
                    o = !s || FX.Utils.isString(s) ? {text: s || ""} : {text: s.name || ""};
                    break;
                case"radiogroup":
                case"combo":
                case"string":
                case"id":
                case"did":
                    o = {text: FX.Utils.isNull(s) ? "" : s};
                    break;
                case"user":
                case"dept":
                    o = !s || FX.Utils.isString(s) ? {text: s || ""} : {text: s.name || ""};
                    break;
                case"usergroup":
                case"deptgroup":
                    var r = [];
                    FX.Utils.forEach(s, function (e, t) {
                        !t || FX.Utils.isString(t) ? r.push(t || "") : r.push(t.name)
                    }), o = {text: r.join(",")};
                    break;
                case"number":
                case"formula":
                    var c = FX.Utils.fixDecimalPrecision(s);
                    o = {text: FX.Utils.num2Str(c, i.format)};
                    break;
                case"address":
                case"location":
                    var d = [];
                    s && (s.province && (d.push(s.province), s.city && s.province !== s.city && d.push(s.city), s.district && d.push(s.district)), s.detail && d.push(s.detail)), o = {text: FX.Utils.address2Str(s, d.join(""), i.format)};
                    break;
                case"textarea":
                    o = {html: s ? e("<pre/>").text(s) : ""};
                    break;
                case"datetime":
                    s && (o = {text: FX.Utils.date2Str(new Date(s), i.format)});
                    break;
                case"_removeCheck":
                    o = {
                        cls: "table-op-btn-cell",
                        html: e('<div class="x-check table-op-btn"/>').append(e('<i class="icon-blank"/>')).data({
                            op: "remove_check",
                            dataId: t._id
                        })
                    };
                    break;
                case"image":
                case"upload":
                    var u = e('<a class="table-op-btn table-file-btn"/>').data("file", s);
                    FX.Utils.isObjectEmpty(s) ? u.text("") : u.text("查看").data("op", "file"), o = {html: u};
                    break;
                case"linkdata":
                    var h = s && s.key;
                    if (!h) break;
                    "datetime" === i.linkType && (h = FX.Utils.date2Str(new Date(h), "yyyy-MM-dd")), o = {text: h};
                    break;
                case"flowState":
                    s === FX.CONST.WORKFLOW.FLOWSTATE.INPROCESS ? o = {text: "进行中"} : s === FX.CONST.WORKFLOW.FLOWSTATE.COMPLETE && (o = {text: "已结束"});
                    break;
                case"chargers":
                    var p = {}, f = {};
                    FX.Utils.forEach(s, function (e, t) {
                        t.flowName && (p[t.flowName] || (p[t.flowName] = !0), f[t.userNickname] || (f[t.userNickname] = !0))
                    });
                    var m = [];
                    "node" === i.show ? FX.Utils.forEach(p, function (e) {
                        m.push(e)
                    }) : FX.Utils.forEach(f, function (e) {
                        m.push(e)
                    }), o = {text: m.join(",")}
            }
            return o
        }, rebuildStickyHead: function () {
            if (this.$stickyHead) {
                var e = this.$stickyHead.attr("class");
                this.$stickyHead.parent().remove()
            }
            if (this.$stickyRowHead) {
                var t = this.$stickyRowHead.attr("class");
                this.$stickyRowHead.parent().remove()
            }
            if (this.$stickyIntersect) {
                var i = this.$stickyIntersect.attr("class");
                this.$stickyIntersect.parent().remove()
            }
            this._createStickyHead(), this.$stickyHead && this.$stickyHead.addClass(e), this.$stickyRowHead && this.$stickyRowHead.addClass(t), this.$stickyIntersect && this.$stickyIntersect.addClass(i)
        }, _formatCell: function () {
        }
    })
}(jQuery), function (e) {
    FX.DataTable = FX.extend(FX.DataTableTemplate, {
        _defaultConfig: function () {
            return e.extend(FX.DataTable.superclass._defaultConfig.apply(), {
                baseCls: "fui_datatable",
                hasMenu: !0,
                itemEditable: !1,
                itemRemovable: !1,
                itemPrintable: !0,
                hasCheck: !1,
                itemsPerPage: 20,
                filterParam: {},
                fields: [],
                data: [],
                asyncExportURL: FX.Utils.getApi(FX.API.data.list_excel_export),
                mode: "visit"
            })
        }, _initContent: function (e) {
            FX.DataTable.superclass._initContent.apply(this, arguments), this.sort = [], this.page = 0, this.count = 0, this._initDataTable()
        }, _initDataTable: function (e) {
            var t = this, i = this.options;
            i.itemEditable && t._isMultiForm() && (i.itemEditable = !1), i.itemRemovable && t._isMultiForm() && (i.itemRemovable = !1), FX.Utils.isObjectEmpty(e) || (i.filterParam = e), i.tableRowHead = [], this._loadData(function () {
                t.createTable()
            }), this._setTitle()
        }, _setTitle: function (e) {
            e && (this.title = e), FX.Utils.isEmpty(this.title) ? this.title = document.title : FX.Utils.setPageTitle(this.title)
        }, _isMultiForm: function () {
            var e = this.options;
            return e.forms.length > 1 || !FX.Utils.isObjectEmpty(e.relations)
        }, _loadData: function (e) {
            var t = this, i = this.options;
            if (this._isFieldsValid()) {
                var a, s;
                "edit" === i.mode ? (a = FX.Utils.getApi(FX.API.data.preview_list), s = {
                    fields: i.fields,
                    forms: i.forms,
                    relations: i.relations,
                    sort: this.sort,
                    skip: this.page * i.itemsPerPage,
                    limit: i.itemsPerPage,
                    filter: this.getFilterData(i.filterParam),
                    hasCount: !1 !== this.hasCount
                }) : (a = FX.Utils.getApi(FX.API.data.list), s = {
                    widgetId: i.widgetName,
                    sort: this.sort,
                    skip: this.page * i.itemsPerPage,
                    limit: i.itemsPerPage,
                    filter: this.getFilterData(i.filterParam),
                    hasCount: !1 !== this.hasCount
                }), this.loadingAjax({url: a, data: s}, function (i) {
                    !1 !== t.hasCount && (t.count = i.count), t.header = i.header, t.data = i.data, e && e()
                }, function (e) {
                    var t = e.responseJSON || {};
                    FX.Utils.isEmpty(t.msg) || FX.Msg.toast({type: "warning", msg: t.msg})
                })
            }
        }, _isFieldsValid: function () {
            var e = this.options, t = !0;
            return t &= e.forms && e.forms.length > 0, t &= e.fields && e.fields.length > 0, FX.Utils.applyFunc(this, e.onCheckValid, [], !1), t
        }, createTable: function () {
            FX.DataTable.superclass.createTable.call(this), this.options.hasMenu && this._createPagination()
        }, _createCell: function (t, i) {
            this.options;
            var a = i || {tag: "td"};
            a.cls && t.cls && (t.cls = a.cls + " " + t.cls);
            var s = e.extend(a, t.text || t.html || !FX.Utils.isString(t) ? t : {text: t}),
                n = e("<" + s.tag + ' class="t-cell"/>');
            switch (n.attr({
                row: s.row,
                col: s.col
            }), s.hasOwnProperty("html") ? n.html(s.html) : n.text(s.text), s.align) {
                case"center":
                    n.addClass("h-center");
                    break;
                case"right":
                    n.addClass("h-right")
            }
            if (s.data) for (var o in s.data) s.data.hasOwnProperty(o) && n.data(o, s.data[o]);
            return s.cls && n.addClass(s.cls), s.colspan && n.attr("colspan", s.colspan), s.rowspan && n.attr("rowspan", s.rowspan), s.width && n.width(s.width), s.height && n.width(s.height), n
        }, _createPagination: function () {
            var t = this, i = this.options, a = {};
            a = "edit" === i.mode ? {
                url: FX.Utils.getApi(FX.API.data.preview_list),
                data: {
                    fields: i.fields,
                    forms: i.forms,
                    relations: i.relations,
                    filter: this.getFilterData(i.filterParam),
                    isCountOnly: !0
                }
            } : {
                url: FX.Utils.getApi(FX.API.data.list),
                data: {widgetId: i.widgetName, filter: this.getFilterData(i.filterParam), isCountOnly: !0}
            }, new FX.DataCountPane({
                renderEl: e("<div />").appendTo(this.$menu),
                itemsPerPage: i.itemsPerPage,
                count: this.count,
                async: a,
                onItemPerPageChange: function (e) {
                    i.itemsPerPage = e, t.page = 0, t.reload(i.filterParam)
                }
            });
            var s = this.data && this.data.length >= i.itemsPerPage;
            new FX.Pagination({
                renderEl: e("<div />").appendTo(this.$menu),
                count: t.count,
                limit: i.itemsPerPage,
                curPage: t.page + 1,
                maxCount: FX.CONST.MAX_COUNT,
                hasMore: s,
                onChangePage: function (e, i) {
                    t.page = e - 1, t.turnPage()
                }
            })
        }, _doShowReport: function () {
            this.element.closest(".fui-report").show(), this._setTitle()
        }, _doHideReport: function () {
            this.element.closest(".fui-report").hide()
        }, _doShowData: function (t, i) {
            var a = this.data[t];
            if (a) {
                var s = this.options, n = this, o = a._id, l = this.header, r = s.title;
                this._switchCurrentRow(t);
                var c = e('<div class="x-window-mask modal light"/>').css({"z-index": FX.STATIC.zIndex++}).appendTo("body");
                e(document).bind("keydown.left keydown.right", function (t) {
                    if (e(".x-window-mask", "body").length) return t.preventDefault(), !1;
                    e(document).unbind("keydown.left keydown.right")
                });
                var d = new FX.ReportFormDataPane({
                    appId: s.appId,
                    renderEl: e("<div class='x-shadow-content'/>").appendTo(c),
                    entryId: s.forms[0],
                    formId: s.forms[0],
                    forms: s.forms,
                    fields: s.fields,
                    header: l,
                    data: a,
                    dataId: o,
                    title: r,
                    height: "100%",
                    hasPrintBtn: s.itemPrintable,
                    hasEditBtn: "visit" === s.mode && s.itemEditable,
                    hasDeleteBtn: "visit" === s.mode && s.itemRemovable,
                    hasSwitchBtn: !0,
                    hasCustomPrint: !1,
                    dataIndex: t + 1,
                    dataCount: this.data.length,
                    onEditData: function () {
                        c.remove()
                    },
                    onAfterEditData: function (e) {
                        n._doShowReport(), n._reloadWithoutCount(s.filterParam, !0)
                    },
                    onSwitchData: function (e, t) {
                        n.data[e - 1] && c.parent().length && (c.remove(), n._doShowData(e - 1, t))
                    },
                    onAfterDeleteData: function () {
                        n.turnPage(), c.remove()
                    },
                    onAfterCancel: function () {
                        n._doShowReport(), c.remove(), n._doShowData(t)
                    },
                    onClose: function (e) {
                        n._doShowReport(), c.remove(), e && n.reload(s.filterParam, !0)
                    }
                });
                i && (c.remove(), d._doEditData())
            }
        }, _switchCurrentRow: function (t) {
            e("tbody > tr", this.element).removeClass("current-row"), e('tbody > tr[data-idx="' + t + '"]', this.element).addClass("current-row")
        }, _setEvent: function () {
            FX.DataTable.superclass._setEvent.apply(this, arguments);
            var t = this, i = this.options;
            this.$wrapper.unbind(".data-table"), this.$wrapper.bind({
                "click.data-table": function (a) {
                    var s = a.target, n = a.type, o = e(s).closest("tr");
                    if (o && o.length > 0) if (o.hasClass("th-row")) {
                        var l = e(s).closest(".th-cell");
                        if (l && l.length > 0 && "click" === n) {
                            var r = l.data("field");
                            if (r) {
                                if (!l.hasClass("sortable")) return;
                                var c = {}, d = -1;
                                l.hasClass("sort-asc") ? (l.removeClass("sort-asc").addClass("sort-desc"), c[r] = -1, ~(d = t.getSortedFieldIdx(r)) ? t.sort[d] = c : t.sort.push(c)) : l.hasClass("sort-desc") ? (l.removeClass("sort sort-desc"), ~(d = t.getSortedFieldIdx(r)) && t.sort.splice(d, 1)) : (l.removeClass("sort-desc").addClass("sort sort-asc"), d = t.getSortedFieldIdx(r), c[r] = 1, ~d ? t.sort[d] = c : t.sort.push(c)), t.page = 0, t._reloadWithoutCount()
                            }
                            var u = l.find(".x-check");
                            u && u.length > 0 && (u.toggleClass("select"), u.hasClass("select") ? t.setRemoveCheckResult(!0) : t.setRemoveCheckResult(!1))
                        }
                    } else if (o.hasClass("tb-row")) {
                        var h = e(s).closest(".table-op-btn");
                        if ("click" === n) if (h && h.length > 0) {
                            var p = h.data("op");
                            if (!i.forms) return;
                            if ("remove_check" === p) h.hasClass("select") && t.setRemoveCheckSelectAll(!1), h.toggleClass("select"); else if ("file" === p) {
                                var f = h.data("file");
                                new FX.FilePreview({files: e.makeArray(f)})
                            }
                        } else {
                            if (!FX.Utils.isEmpty(FX.Utils.getSelectionText())) return;
                            t._doShowData(parseInt(o.attr("data-idx")))
                        }
                    }
                }, "mouseover.data-table": function (i) {
                    var a = e(i.target).closest("tr").attr("data-idx");
                    FX.Utils.isNull(a) || e('tbody > tr[data-idx="' + a + '"]', t.element).addClass("hover")
                }, "mouseout.data-table": function (i) {
                    var a = e(i.target).closest("tr").attr("data-idx");
                    FX.Utils.isNull(a) || e('tbody > tr[data-idx="' + a + '"]', t.element).removeClass("hover")
                }
            })
        }, _bindRowData: function (e, t, i) {
            if (this.dataMap && this.dataMap.length > i) {
                var a = this.dataMap[i];
                t.attr("data-idx", a)
            }
        }, doExcelExport: function () {
            var e = this.options;
            if (this._isFieldsValid()) {
                var t = this.createLoadingMask();
                FX.Utils.dataAjax({
                    url: e.asyncExportURL,
                    data: {widgetId: e.widgetName, filter: this.getFilterData(e.filterParam), sort: this.sort}
                }, function (e) {
                    t.remove(), window.location.href = e.url
                }, function (e) {
                    t.remove();
                    var i = e.responseJSON || {};
                    FX.Msg.toast({type: "error", msg: i.msg || "导出失败"})
                })
            }
        }, turnPage: function () {
            var e = this.options;
            this._removeTable(), this._initDataTable(e.filterParam)
        }, reload: function (e, t, i) {
            FX.DataTable.superclass.reload.apply(this, arguments), t || (this.page = 0), i ? this.hasCount = !1 : (this.hasCount = !0, this.count = 0), this._initDataTable(e)
        }, _reloadWithoutCount: function (e, t) {
            this.reload(e, t, !0)
        }, loadMore: function (e) {
            var t = this;
            this.hasMore() && !this.isLoading && (t.page++, this._loadData(function () {
                t.appendData(), e && e()
            }))
        }, hasMore: function () {
            var e = this.options;
            return (this.page + 1) * e.itemsPerPage < this.count
        }, setHasCheck: function (e) {
            this.options.hasCheck = e
        }, setRemoveCheckSelectAll: function (e) {
            e || this.$stickyRowHead.children(".t-head").find(".x-check").removeClass("select")
        }, setRemoveCheckResult: function (t) {
            t ? this.$stickyRowHead.find(".x-check").each(function (t, i) {
                e(i).addClass("select")
            }) : this.$stickyRowHead.find(".x-check").each(function (t, i) {
                e(i).removeClass("select")
            })
        }, getCheckResult: function () {
            var t = [];
            return this.$stickyRowHead.find(".t-body .x-check").each(function (i, a) {
                e(a).hasClass("select") && t.push(e(a).data("dataId"))
            }), t
        }, createHeadTools: function () {
            FX.DataTable.superclass.createHeadTools.apply(this, arguments);
            var t = this;
            this.options.itemRemovable && e("<a/>").append('<i class="icon-trasho">').append(e("<span/>").text("批量删除")).appendTo(this.$head).click(function () {
                t.createTableDeleteButtons()
            })
        }, createTableDeleteButtons: function () {
            var t = this;
            t.setHasCheck(!0), this.fieldCheck = null, this.refresh(), this.$head.children("a").remove(), e("<a />").append('<i class="icon-signout">').append(e("<span />").text("退出编辑")).appendTo(this.$head).click(function () {
                t.setHasCheck(!1), t.refresh(), t.createHeadTools()
            }), e("<a />").append('<i class="icon-trasho">').append(e("<span />").text("删除选中")).appendTo(this.$head).click(function () {
                var e = t.getCheckResult().length;
                t.deleteCheckResult(!1, "选中" + e + "条数据，删除后将无法恢复，确定删除？")
            }), e("<a />").append('<i class="icon-clear">').append(e("<span />").text("清空数据")).appendTo(this.$head).click(function () {
                t.deleteCheckResult(!0, "清空数据后将无法恢复，确定清空？")
            })
        }, deleteCheckResult: function (e, t, i) {
            var a = this, s = this.options;
            FX.Msg.alert({
                title: "删除数据", msg: t, type: "warning", onOk: function () {
                    var t = {formId: s.forms[0], widgetId: s.widgetName}, n = !0;
                    if (e) t.clearAll = !0, t.filter = a.getFilterData(s.filterParam); else {
                        var o = a.getCheckResult();
                        o && o.length > 0 ? t.idList = o : n = !1
                    }
                    n && FX.Utils.dataAjax({url: FX.Utils.getApi(FX.API.data.remove), data: t}, function () {
                        !1 === FX.Utils.applyFunc(a, i, [], !1) && (a.setHasCheck(!1), a.createHeadTools(), a.reload())
                    })
                }
            })
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.DataTable.superclass.getOptions.apply(this, arguments), {
                relations: t.relations,
                joinedFields: t.joinedFields,
                fields: t.fields,
                itemEditable: t.itemEditable,
                itemRemovable: t.itemRemovable
            })
        }
    }), e.shortcut("datatable", FX.DataTable)
}(jQuery), function (e) {
    FX.CombinedTable = FX.extend(FX.Table, {
        _defaultConfig: function () {
            return e.extend(FX.CombinedTable.superclass._defaultConfig.apply(), {
                baseCls: "fui_combinedtable",
                hasMenu: !0,
                isHeadSticky: !0,
                isRowHeadSticky: !0,
                chunkSize: {x: 2e3, y: 50},
                forms: [],
                relations: {},
                joinedFields: [],
                xFields: [],
                yFields: [],
                valueFields: [],
                asyncExportURL: FX.Utils.getApi(FX.API.data.excel_export),
                onItemClick: null,
                mode: "visit"
            })
        }, _initContent: function () {
            FX.DataTable.superclass._initContent.apply(this, arguments), this._initCombinedTable()
        }, _initCombinedTable: function (t) {
            var i = this, a = this.options;
            if (this.tablePart = {x: 0, y: 0}, this.count = {x: 0, y: 0}, this.filterParam = t, this._isFieldsValid()) {
                this.xGroups = this._makeGroups(a.xFields), this.yGroups = this._makeGroups(a.yFields);
                var s, n;
                "edit" === a.mode ? (s = FX.Utils.getApi(FX.API.data.preview_combined_group), n = {
                    forms: a.forms,
                    relations: a.relations,
                    xFields: this.xGroups,
                    yFields: this.yGroups,
                    valFields: a.valueFields,
                    linkWidgets: a.linkWidgets,
                    filter: this.getFilterData(this.filterParam)
                }) : (s = FX.Utils.getApi(FX.API.data.combined_group), n = {
                    widgetId: a.widgetName,
                    filter: this.getFilterData(this.filterParam)
                }), this.loadingAjax({url: s, data: n}, function (t, s) {
                    if (FX.Utils.isObjectEmpty(t.table)) i.table = null, a.tableHead = [], a.tableRowHead = [], a.tableData = []; else {
                        i.table = t.table, i._chunkTable(), i._getTablePart();
                        var n = i._getTablePart();
                        e.extend(a, i._assembleTable(n))
                    }
                    i.createTable()
                })
            } else this.createTable()
        }, _assembleTable: function (e) {
            var t = [];
            FX.Utils.forEach(e.headBase, function (i, a) {
                t[i] = [].concat(a || [], e.head[i] || [], e.headGroup[i] || [])
            });
            var i = e.rowHead || [];
            e.rowHeadGroup && (i[0] = i[0] || [], i[0].push(e.rowHeadGroup));
            for (var a = [], s = Math.max(e.data.length || e.dataGroupCol.length), n = 0; n < s; n++) a[n] = [].concat(e.data[n] || [], e.dataGroupCol[n] || []);
            if (!this.hasMore()) {
                var o = e.dataGroupRow || [];
                FX.Utils.isObjectEmpty(e.dataGroupAll) || (o = o.concat(e.dataGroupAll)), a.push(o)
            }
            return {tableHead: t, tableRowHead: i, tableData: a}
        }, _chunkTable: function () {
            var t = this.options;
            if (t.chunkSize.x && t.chunkSize.y) {
                var i = [];
                FX.Utils.forEach(this.table.head, function (a, s) {
                    var n = 0;
                    FX.Utils.forEach(s, function (s, o) {
                        for (var l = o.colspan || 1, r = parseInt(n / t.chunkSize.x), c = (r + 1) * t.chunkSize.x - n; l > 0;) {
                            var d = Math.min(c, l);
                            i[r] = i[r] || [], i[r][a] = i[r][a] || [], i[r][a].push(e.extend({}, o, {colspan: d})), l -= d, r++, n += d
                        }
                    })
                }), this.tableHeadChunks = i;
                var a = [];
                FX.Utils.forEach(this.table.rowHead, function (i, s) {
                    var n = null, o = FX.Utils.chunkArray(s, t.chunkSize.y);
                    FX.Utils.forEach(o, function (t, i) {
                        n && n.rowspan > 0 && (i[0] = n);
                        for (var s = i.length - 1; s > -1; s--) {
                            var o = i[s];
                            if (o && o.rowspan > 1) {
                                n = e.extend({}, o);
                                var l = Math.min(i.length - s, o.rowspan);
                                o.rowspan = l, n.rowspan -= l;
                                break
                            }
                        }
                        a[t] = a[t] || [], a[t].push(i)
                    })
                }), this.tableRowHeadChunks = a;
                var s = {};
                this.count.y = this.table.data.length;
                var n = FX.Utils.chunkArray(this.table.data, t.chunkSize.y);
                FX.Utils.forEach(n, function (e, i) {
                    FX.Utils.forEach(i, function (i, a) {
                        var n = FX.Utils.chunkArray(a, t.chunkSize.x);
                        FX.Utils.forEach(n, function (t, a) {
                            var n = t + "-" + e;
                            s[n] = s[n] || [], s[n][i] = a
                        })
                    })
                }), this.tableDataChunkMap = s, this.tableDataGroupColChunks = FX.Utils.chunkArray(this.table.dataGroupCol, t.chunkSize.y), this.tableDataGroupRowChunks = FX.Utils.chunkArray(this.table.dataGroupRow, t.chunkSize.x)
            }
        }, _getTablePart: function () {
            var e = this.tablePart.x, t = this.tablePart.y;
            return {
                headBase: this.table.headBase,
                head: this.tableHeadChunks[e] || [],
                headGroup: this.table.headGroup,
                rowHead: this.tableRowHeadChunks[t] || [],
                rowHeadGroup: this.table.rowHeadGroup,
                data: this.tableDataChunkMap[e + "-" + t] || [],
                dataGroupRow: this.tableDataGroupRowChunks[e] || [],
                dataGroupCol: this.tableDataGroupColChunks[t] || [],
                dataGroupAll: this.table.dataGroupAll
            }
        }, _isFieldsValid: function () {
            var e = this.options, t = !0;
            return t &= e.forms.length > 0, t &= 0 !== e.valueFields.length, t &= 0 !== e.xFields.length || 0 !== e.yFields.length, FX.Utils.applyFunc(this, e.onCheckValid, [], !1), !!t
        }, _setEvent: function () {
            FX.CombinedTable.superclass._setEvent.apply(this, arguments);
            var t = this, i = this.options;
            this.$wrapper.unbind(".combined-table"), this.$wrapper.bind({
                "click.combined-table": function (a) {
                    var s = a.target, n = a.type, o = e(s).closest(".t-cell");
                    if (o && o.length > 0 && "click" === n) {
                        var l = o.data("id");
                        if (l && t._isFieldsValid()) {
                            var r = t._getGroupIdCondition(l), c = t._getLinkParams(r);
                            c = t._getLinkFilterParams(c), FX.Utils.applyFunc(t, i.onItemClick, [c], !1)
                        }
                    }
                }
            })
        }, _getGroupIdCondition: function (e) {
            var t = {};
            for (var i in e) if (e.hasOwnProperty(i)) {
                var a = i, s = i.match(/(createTime|updateTime|\d{13})_([a-zA-Z]+)/);
                if (s && s.length > 1) {
                    var n = s[s.length - 1];
                    a = i.replace("_" + n, ""), t.hasOwnProperty(a) || (t[a] = {}), t[a][n] = e[i]
                } else t[a] = e[i]
            }
            return t
        }, _getLinkParams: function (e) {
            var t = this;
            if (e) {
                var i = [];
                return FX.Utils.forEach(e, function (a) {
                    var s = t._getFieldByName(a), n = e[a];
                    switch (s.type) {
                        case"datetime":
                            n = FX.Utils.getDateRange(n.year, n.month, n.day);
                            break;
                        case"address":
                        case"location":
                            n = FX.Utils.getArrayFromRange(n, "address")
                    }
                    i.push(FX.Utils.getReportLinkFilter(s, n))
                }), i
            }
        }, _getFieldByName: function (e) {
            var t = this.options, i = [].concat(t.xFields, t.yFields), a = null;
            return FX.Utils.forEach(i, function (t, i) {
                if ((i.tag || i.name) === e) return a = i, !1
            }), a
        }, createTable: function () {
            FX.CombinedTable.superclass.createTable.call(this), this.options.hasMenu && this._createPagination()
        }, _createPagination: function () {
            var t = this, i = this.options;
            new FX.Pagination({
                renderEl: e("<div />").appendTo(this.$menu),
                count: this.count.y,
                limit: i.chunkSize.y,
                curPage: this.tablePart.y + 1,
                hasTurnLast: !0,
                onChangePage: function (e, i) {
                    t.tablePart.y = e - 1, t.turnPage()
                }
            })
        }, turnPage: function () {
            var t = this.options;
            if (this.table) {
                this._removeTable();
                var i = this._getTablePart();
                e.extend(t, this._assembleTable(i)), this.createTable(), this.$wrapper.scrollTop(0), this.$wrapper.scrollLeft(0)
            }
        }, hasMore: function () {
            var e = this.options;
            return (this.tablePart.y + 1) * e.chunkSize.y < this.count.y
        }, doExcelExport: function () {
            var e = this.options;
            if (this._isFieldsValid()) {
                var t = this.createLoadingMask();
                FX.Utils.dataAjax({
                    url: e.asyncExportURL,
                    data: {widgetId: e.widgetName, filter: this.getFilterData(this.filterParam)}
                }, function (e) {
                    t.remove(), window.location.href = e.url
                }, function (e) {
                    t.remove();
                    var i = e.responseJSON || {};
                    FX.Msg.toast({type: "error", msg: i.msg || "导出失败"})
                })
            }
        }, reload: function (e) {
            FX.CombinedTable.superclass.reload.apply(this, arguments), this.count = {
                x: 0,
                y: 0
            }, this._initCombinedTable(e)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.CombinedTable.superclass.getOptions.apply(this, arguments), {
                isHeadSticky: t.isHeadSticky,
                isRowHeadSticky: t.isRowHeadSticky,
                forms: t.forms,
                relations: t.relations,
                joinedFields: t.joinedFields,
                xFields: t.xFields,
                yFields: t.yFields,
                valueFields: t.valueFields
            })
        }, _appendTableData: function () {
            var e = this, t = this.options;
            this.formatMap = {}, FX.Utils.forEach(t.valueFields, function (t, i) {
                i.cellFmt && (e.formatMap[i.name] = i.cellFmt.data)
            }), FX.CombinedTable.superclass._appendTableData.apply(this, arguments)
        }, _formatCell: function (e) {
            var t = e.field;
            t && (t = t.replace("%", "."));
            var i = this.formatMap[t];
            if (i) {
                var a = FX.Utils.fixDecimalPrecision(e.value);
                e.text = FX.Utils.num2Str(a, i) || "-"
            }
        }
    }), e.shortcut("combinedtable", FX.CombinedTable)
}(jQuery), function (e) {
    FX.Parameter = FX.extend(FX.Block, {
        _defaultConfig: function () {
            return e.extend(FX.Parameter.superclass._defaultConfig.apply(), {
                baseCls: "fui_parameter",
                height: null,
                width: null,
                fields: [],
                showFields: null,
                filter: null,
                authGroupId: null,
                onBeforeConvertField: null,
                onStopEdit: null,
                onAfterShowFieldsSelected: null
            })
        }, _initContent: function (e) {
            FX.Parameter.superclass._initContent.apply(this, arguments);
            var t = this.options, i = this;
            this.fieldMap = {};
            var a = this._dealFields(t.fields);
            FX.Utils.forEach(a, function (e, t) {
                i._createItem(t)
            })
        }, _dealFields: function (t) {
            var i = [];
            return FX.Utils.forEach(t, function (t, a) {
                "subform" === a.type ? FX.Utils.forEach(a.items, function (t, s) {
                    i.push(e.extend({}, s, {text: [a.text, s.text].join("."), name: [a.name, s.name].join(".")}))
                }) : i.push(a)
            }), i
        }, setFields: function (e) {
            var t = this.options, i = [], a = this._dealFields(t.showFields);
            FX.Utils.forEach(a, function (t, a) {
                e.indexOf(a.name) >= 0 && i.push(a)
            }), t.fields = i, this.rebuild()
        }, _createItem: function (t) {
            var i = this.options, a = this, s = e('<div class="fui_parameter_cell"/>').appendTo(this.$body),
                n = a.getConfigFromItem(t);
            if (n) {
                e('<div class="cell-title"/>').text(n.title).appendTo(s), n.renderEl = e("<div/>").appendTo(s);
                n.onStopEdit = function () {
                    var e = JSON.stringify(this.getValue());
                    this.oldValue && this.oldValue == e || (this.oldValue = e, FX.Utils.applyFunc(a, i.onStopEdit, [t.id], !1))
                };
                var o = FX.createWidget(n);
                s.data("widget", o), this.fieldMap[o.getWidgetName()] = t
            }
        }, _resizeBody: function () {
        }, getConfigFromItem: function (t) {
            var i = this.options, a = {title: t.text, value: this._parseDefaultValue(t)};
            if (!1 === FX.Utils.applyFunc(this, i.onBeforeConvertField, [a, t], !1)) switch (t.type) {
                case"text":
                case"radiogroup":
                case"combo":
                    "creator" === t.name ? e.extend(a, this._getUserConfig(t)) : e.extend(a, this._getComboConfig(t));
                    break;
                case"number":
                    a.type = "numberlimit";
                    break;
                case"datetime":
                    a.type = "datelimit";
                    break;
                case"address":
                    a.type = "address", a.needDetail = !1;
                    break;
                case"dept":
                    a.type = "deptselect", a.limit = this._getComboConfig(t).async;
                    break;
                case"user":
                    e.extend(a, this._getUserConfig(t));
                    break;
                default:
                    "creator" === t.name && e.extend(a, this._getUserConfig(t))
            }
            return FX.Utils.isNull(a.type) ? null : a
        }, _parseDefaultValue: function (t) {
            if (t.defaultValue) {
                var i;
                if ("datetime" === t.type && t.defaultValue) {
                    i = {};
                    var a = t.defaultValue, s = new Date, n = s.getTime();
                    switch (a.type) {
                        case"today":
                            i.min = n, i.max = n;
                            break;
                        case"yesterday":
                            i.min = n - 864e5, i.max = n - 864e5;
                            break;
                        case"lastWeek":
                            i.min = n - 6048e5, i.max = n;
                            break;
                        case"thisWeek":
                            i.min = FX.Utils.getWeekStartDate(s).getTime(), i.max = FX.Utils.getWeekEndDate(s).getTime();
                            break;
                        case"thisMonth":
                            i.min = FX.Utils.getMonthStartDate(s).getTime(), i.max = FX.Utils.getMonthEndDate(s).getTime();
                            break;
                        case"formula":
                            var o, l;
                            o = "before" === a.min.type ? -1 * a.min.value : a.min.value, l = "before" === a.max.type ? -1 * a.max.value : a.max.value, i.min = n + o, i.max = n + l;
                            break;
                        default:
                            i.min = a.min, i.max = a.max
                    }
                } else if ("user" !== t.type && "creator" !== t.name || !t.defaultValue) i = e.extend(!0, {}, t.defaultValue); else {
                    var r = [].concat(t.defaultValue.items || []), c = r.indexOf(FX.USER_ID.CurrentUser);
                    c > -1 && (!FX.STATIC.user._id || r.indexOf(FX.STATIC.user._id) > -1 ? r.splice(c, 1) : r[c] = FX.STATIC.user._id), i = {
                        items: r,
                        hasEmpty: t.defaultValue.hasEmpty
                    }
                }
                return i
            }
        }, _getComboConfig: function (e) {
            var t = this.options, i = FX.Utils.getFieldInfoById(e.id);
            return {
                type: "xcombocheck",
                async: {
                    url: FX.Utils.getApi(FX.API.data.distinct),
                    data: {
                        refAppId: i.appId,
                        formId: i.entryId,
                        field: e.name,
                        type: e.type,
                        authGroupId: t.authGroupId,
                        filter: t.filter
                    }
                },
                hasLimit: !0,
                searchable: !0,
                width: 150
            }
        }, _getUserConfig: function (t) {
            return e.extend(this._getComboConfig(t), {type: "usercheck", textField: "nickname", valueField: "_id"})
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.Parameter.superclass.getOptions.apply(this, arguments), {fields: t.fields})
        }, removeField: function (t) {
            e(".fui_parameter_cell", this.element).eq(t).remove()
        }, updateField: function (t, i) {
            FX.Utils.isNull(i) || (e(".fui_parameter_cell", this.element).eq(i).children(".cell-title").text(t.text), e(".fui_parameter_cell", this.element).eq(i).data("widget").setValue(this._parseDefaultValue(t)))
        }, addField: function (e) {
            this._createItem(e)
        }, checkValidate: function () {
            if (!this.options.allowBlank) {
                var t = e(".fui_parameter_cell", this.element), i = !0;
                return FX.Utils.forEach(t, function (t, a) {
                    var s = e(a).data("widget");
                    if (s) {
                        var n = s.getValue();
                        return FX.Utils.isObjectEmpty(n) ? (i = !1, !1) : void 0
                    }
                }), i
            }
            return !0
        }, _checkWidgetValue: function (e, t) {
            var i = !1;
            switch (e) {
                case"xcombocheck":
                case"usercheck":
                case"deptselect":
                    i = t.hasEmpty || !FX.Utils.isObjectEmpty(t.value);
                    break;
                default:
                    t.value.length > 0 && FX.Utils.forEach(t.value, function (e, t) {
                        if (!FX.Utils.isNull(t)) return i = !0, !1
                    })
            }
            return i
        }, _getFilterByWidget: function (t, i) {
            var a = {type: i.type};
            e.extend(a, FX.Utils.dealFilterInfoByField(i));
            var s = t.getValue();
            switch (t.options.type) {
                case"usercheck":
                    e.extend(a, {
                        type: "user",
                        method: FX.CONST.FILTER_METHOD.IN,
                        value: s.items,
                        hasEmpty: !!s.hasEmpty
                    });
                    break;
                case"xcombocheck":
                    e.extend(a, {
                        type: "text",
                        method: FX.CONST.FILTER_METHOD.IN,
                        value: s.items,
                        hasEmpty: !!s.hasEmpty
                    });
                    break;
                case"deptselect":
                    e.extend(a, {
                        method: FX.CONST.FILTER_METHOD.IN,
                        value: s.items,
                        hasEmpty: !!s.hasEmpty,
                        hasCurrentDept: !!s.hasCurrentDept
                    });
                    break;
                case"datelimit":
                    e.extend(a, {method: FX.CONST.FILTER_METHOD.RG, value: FX.Utils.getArrayFromRange(s, "datetime")});
                    break;
                case"numberlimit":
                    e.extend(a, {method: FX.CONST.FILTER_METHOD.RG, value: FX.Utils.getArrayFromRange(s, "number")});
                    break;
                case"address":
                    e.extend(a, {method: FX.CONST.FILTER_METHOD.ALL, value: FX.Utils.getArrayFromRange(s, "address")});
                    break;
                default:
                    e.extend(a, {method: FX.CONST.FILTER_METHOD.EQ, value: e.makeArray(s)})
            }
            return a
        }, getValue: function () {
            var t = e(".fui_parameter_cell", this.element), i = [], a = this;
            this.options;
            return FX.Utils.forEach(t, function (t, s) {
                var n = e(s).data("widget");
                if (n) {
                    var o = a.fieldMap[n.getWidgetName()], l = a._getFilterByWidget(n, o);
                    a._checkWidgetValue(n.options.type, l) && i.push(l)
                }
            }), i
        }
    }), e.shortcut("parameter", FX.Parameter)
}(jQuery), function (e) {
    FX.SubformBase = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.SubformBase.superclass._defaultConfig.apply(), {oriType: ""})
        }, _init: function () {
            FX.SubformBase.superclass._init.apply(this, arguments), this._createOriWidget()
        }, _createOriWidget: function () {
        }, getValue: function () {
            return this.oriWidget.getValue()
        }, setValue: function (e) {
            this.oriWidget.setValue(e)
        }, getWidgetType: function () {
            return this.options.oriType
        }, getNullValue: function () {
            return this.oriWidget.getNullValue()
        }, checkValidate: function () {
            return this.oriWidget.checkValidate()
        }, getCacheValue: function () {
            return this.oriWidget.getCacheValue()
        }, setCacheValue: function (e) {
            this.oriWidget.setCacheValue(e)
        }
    }), e.shortcut("subform_base", FX.SubformBase)
}(jQuery), function (e) {
    FX.SubformUser = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformUser.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_user",
                oriType: "user",
                title: "成员列表",
                limit: {},
                limitWidget: "",
                value: null,
                allowBlank: !0,
                dynamicFields: [{id: FX.USER_ID.CurrentUser, name: "当前用户"}],
                dynamicType: "select",
                onBeforeEdit: null,
                onStopEdit: null
            })
        }, _init: function () {
            FX.SubformUser.superclass._init.apply(this, arguments), this._createTriggerBtn(), this._createSelectList()
        }, _createOriWidget: function () {
            var e = this.options, t = {
                type: e.oriType,
                limit: e.limit,
                limitWidget: e.limitWidget,
                allowBlank: e.allowBlank,
                visible: e.visible,
                enable: e.enable,
                dynamicType: e.dynamicType
            };
            this.oriWidget = FX.createWidget(t)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><i class="widget-icon icon-widget-user"/></div>').click(function () {
                t._createSelectDialog()
            }).appendTo(this.element)
        }, _createSelectDialog: function () {
            var e = this.oriWidget, t = this.options, i = this;
            if (e.isEnabled()) {
                FX.Utils.applyFunc(i, t.onBeforeEdit, [], !1);
                var a = new FX.ConfirmDialog({
                    title: t.title,
                    height: 550,
                    width: 590,
                    contentWidget: {
                        rowSize: [440],
                        colSize: [570],
                        padding: 10,
                        items: [[{
                            widgetName: t.widgetName,
                            type: t.oriType,
                            editable: !0,
                            limit: t.limit,
                            limitWidget: t.limitWidget,
                            items: e.items,
                            value: e.value,
                            onStopEdit: t.onStopEdit
                        }]]
                    },
                    onOk: function () {
                        var s = a.getWidgetByName(t.widgetName);
                        return e.value = s.getValue(), e.items = s.getItems(), e._initSelectPane(), i._createSelectList(), FX.Utils.applyFunc(i, t.onStopEdit, [], !1), !1
                    }
                });
                a.show()
            }
        }, _createSelectList: function () {
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<span class="select-list"/>').prependTo(this.$selectTrigger), FX.Utils.isExternalLink()) e('<div class="nonsupport-msg"/>').text("外链不支持成员控件").appendTo(this.element.empty()); else {
                var t = this.oriWidget.getCacheValue();
                t && e('<span class="select-item"><i class="select-icon icon-member-normal"/>' + t.name + "</span>").appendTo(this.$selectList)
            }
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, _getLimit: function () {
            return FX.Utils.applyFunc(this, this.oriWidget._getLimit, arguments, !1)
        }, _setLimit: function () {
            FX.Utils.applyFunc(this, this.oriWidget._setLimit, arguments, !1)
        }, _getDeptWidgets: function () {
            return FX.Utils.applyFunc(this, this.oriWidget._getDeptWidgets, arguments, !1)
        }, _setDefaultValue: function () {
            FX.Utils.applyFunc(this, this.oriWidget._setDefaultValue, arguments, !1)
        }, _getLimitConfig: function () {
            return FX.Utils.applyFunc(this, this.oriWidget._getLimitConfig, arguments, !1)
        }, getOptions: function (t) {
            var i = this.options;
            return e.extend(FX.SubformUser.superclass.getOptions.apply(this, arguments), {
                limit: i.limit,
                limitWidget: i.limitWidget,
                value: "save" === t ? this.oriWidget._parseDefaultValue(i.value) : i.value,
                type: i.oriType
            })
        }, setCacheValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformUser.superclass.setCacheValue, [e], !1), this._createSelectList()
        }, setValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformUser.superclass.setValue, [e], !1), this._createSelectList()
        }
    }), e.shortcut("subform_user", FX.SubformUser)
}(jQuery), function (e) {
    FX.SubformUserGroup = FX.extend(FX.SubformUser, {
        _defaultConfig: function () {
            return e.extend(FX.SubformUserGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_usergroup",
                oriType: "usergroup"
            })
        }, _init: function () {
            FX.SubformUserGroup.superclass._init.apply(this, arguments)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><i class="widget-icon icon-widget-usergroup"/></div>').click(function () {
                t._createSelectDialog()
            }).appendTo(this.element)
        }, _createSelectList: function () {
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<span class="select-list"/>').prependTo(this.$selectTrigger), FX.Utils.isExternalLink()) e('<div class="nonsupport-msg"/>').text("外链不支持成员控件").appendTo(this.element.empty()); else {
                var t = this, i = this.oriWidget.getCacheValue();
                FX.Utils.isObjectEmpty(i) || FX.Utils.forEach(i, function (i, a) {
                    e('<span class="select-item"><i class="select-icon icon-member-normal"/>' + a.name + "</span>").appendTo(t.$selectList)
                })
            }
        }
    }), e.shortcut("subform_usergroup", FX.SubformUserGroup)
}(jQuery), function (e) {
    FX.SubformDept = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformDept.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_dept",
                oriType: "dept",
                title: "部门列表",
                value: null,
                allowBlank: !0,
                limit: {},
                dynamicType: "select"
            })
        }, _init: function () {
            FX.SubformDept.superclass._init.apply(this, arguments), this._createTriggerBtn(), this._createSelectList()
        }, _createOriWidget: function () {
            var e = this.options, t = {
                type: e.oriType,
                limit: e.limit,
                rely: e.rely,
                allowBlank: e.allowBlank,
                visible: e.visible,
                enable: e.enable,
                dynamicType: e.dynamicType
            };
            this.oriWidget = FX.createWidget(t)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><i class="widget-icon icon-widget-dept"/></div>').click(function () {
                t._createSelectDialog()
            }).appendTo(this.element)
        }, _createSelectDialog: function () {
            var e = this.oriWidget, t = this.options, i = this;
            if (e.isEnabled()) {
                var a = new FX.ConfirmDialog({
                    title: t.title,
                    height: 550,
                    width: 590,
                    contentWidget: {
                        rowSize: [440],
                        colSize: [570],
                        padding: 10,
                        items: [[{
                            widgetName: t.widgetName,
                            type: t.oriType,
                            editable: !0,
                            limit: t.limit,
                            rely: t.rely,
                            items: e.items,
                            value: e.value,
                            onStopEdit: t.onStopEdit
                        }]]
                    },
                    onOk: function () {
                        var s = a.getWidgetByName(t.widgetName);
                        return e.value = s.getValue(), e.items = s.getItems(), e._initSelectPane(), i._createSelectList(), FX.Utils.applyFunc(i, t.onStopEdit, [], !1), !1
                    }
                });
                a.show()
            }
        }, _createSelectList: function () {
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<span class="select-list"/>').prependTo(this.$selectTrigger), FX.Utils.isExternalLink()) e('<div class="nonsupport-msg"/>').text("外链不支持部门控件").appendTo(this.element.empty()); else {
                var t = this.oriWidget.getCacheValue();
                t && e('<span class="select-item"><i class="select-icon dept-icon icon-department"/>' + t.name + "</span>").appendTo(this.$selectList)
            }
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, _getLimit: function () {
            return FX.Utils.applyFunc(this, this.oriWidget._getLimit, arguments, !1)
        }, _setLimit: function () {
            FX.Utils.applyFunc(this, this.oriWidget._setLimit, arguments, !1)
        }, _setDefaultValue: function () {
            FX.Utils.applyFunc(this, this.oriWidget._setDefaultValue, arguments, !1)
        }, _getLimitConfig: function () {
            return FX.Utils.applyFunc(this, this.oriWidget._getLimitConfig, arguments, !1)
        }, getOptions: function (t) {
            var i = this.options;
            return e.extend(FX.SubformDept.superclass.getOptions.apply(this, arguments), {
                limit: i.limit,
                value: "save" === t ? this._parseDefaultValue(i.value) : i.value,
                type: i.oriType
            })
        }, setCacheValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformDept.superclass.setCacheValue, [e], !1), this._createSelectList()
        }, setValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformDept.superclass.setValue, [e], !1), this._createSelectList()
        }
    }), e.shortcut("subform_dept", FX.SubformDept)
}(jQuery), function (e) {
    FX.SubformDeptGroup = FX.extend(FX.SubformDept, {
        _defaultConfig: function () {
            return e.extend(FX.SubformDeptGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_deptgroup",
                oriType: "deptgroup"
            })
        }, _init: function () {
            FX.SubformDeptGroup.superclass._init.apply(this, arguments)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><i class="widget-icon icon-widget-deptgroup"/></div>').click(function () {
                t._createSelectDialog()
            }).appendTo(this.element)
        }, _createSelectList: function () {
            if (this.$selectList ? this.$selectList.empty() : this.$selectList = e('<span class="select-list"/>').prependTo(this.$selectTrigger), FX.Utils.isExternalLink()) e('<div class="nonsupport-msg"/>').text("外链不支持部门控件").appendTo(this.element.empty()); else {
                var t = this, i = this.oriWidget.getCacheValue();
                FX.Utils.isObjectEmpty(i) || FX.Utils.forEach(i, function (i, a) {
                    e('<span class="select-item"><i class="select-icon dept-icon icon-department"/>' + a.name + "</span>").appendTo(t.$selectList)
                })
            }
        }
    }), e.shortcut("subform_deptgroup", FX.SubformDeptGroup)
}(jQuery), function (e) {
    FX.SubformAddress = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformAddress.superclass._defaultConfig.apply(), {
                baseCls: "fui_subform_address",
                needDetail: !0,
                allowBlank: !0
            })
        }, _init: function () {
            FX.SubformAddress.superclass._init.apply(this, arguments);
            var t = this;
            this.$input = e('<input readonly onfocus="this.blur()" unselectable="on"/>').appendTo(this.element), e('<i class="icon-widget-address"/>').appendTo(this.element), this.element.on("click", function (i) {
                t.oriWidget.isEnabled() && t._showTriggerView(e(i.currentTarget))
            })
        }, _createOriWidget: function () {
            var e = this.options, t = this, i = {
                type: e.oriType,
                allowBlank: e.allowBlank,
                needDetail: e.needDetail,
                visible: e.visible,
                enable: e.enable,
                onStopEdit: function () {
                    t._showSelectValue()
                }
            };
            e.needDetail ? (i.width = 370, i.width4province = 150, i.width4city = 105, i.width4district = 105) : (i.width = 310, i.width4province = "100%", i.width4city = 150, i.width4district = 150), this.oriWidget = FX.createWidget(i)
        }, _showTriggerView: function (t) {
            var i = this;
            this.$triggerView || (this.$triggerView = e('<div class="subform-address-trigger"/>'), this.oriWidget.element.appendTo(this.$triggerView)), FX.Msg.bubble({
                anchor: t,
                contentHTML: this.$triggerView,
                text4Cancel: null,
                text4Ok: null,
                contentPadding: 0,
                hasTriangle: !1,
                hAdjust: 120,
                animation: !1,
                edge: 240,
                minWidth: 340,
                onClose: function () {
                    i.$triggerView.detach(), i._showSelectValue()
                }
            })
        }, _showSelectValue: function () {
            this.$input.val(this.getText())
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.SubformAddress.superclass.getOptions.apply(this, arguments), {
                type: this.oriWidget.getWidgetType(),
                needDetail: t.needDetail
            })
        }, getText: function () {
            var e = this.getValue();
            return [e.province || "", e.city || "", e.district || "", e.detail || ""].join("")
        }, setCacheValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformAddress.superclass.setCacheValue, [e], !1), this._showSelectValue()
        }, setValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformAddress.superclass.setValue, [e], !1), this._showSelectValue()
        }
    }), e.shortcut("subform_address", FX.SubformAddress)
}(jQuery), function (e) {
    FX.SubformRadioGroup = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformRadioGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_radiogroup",
                type: "radiogroup",
                items: [{value: "选项1", text: "选项1"}, {value: "选项2", text: "选项2"}, {value: "选项3", text: "选项3"}]
            })
        }, _init: function () {
            FX.SubformRadioGroup.superclass._init.apply(this, arguments), this._createTriggerBtn(), this._showSelectValue()
        }, _createOriWidget: function () {
            var e = this, t = this.options, i = {
                type: t.oriType,
                items: t.items,
                allowBlank: t.allowBlank,
                visible: t.visible,
                enable: t.enable,
                onAfterItemSelect: function (t, i) {
                    i && i.isOther || e.bubble && e.bubble.close()
                }
            };
            this.oriWidget = FX.createWidget(i)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><span class="select-val"></span><i class="widget-icon icon-widget-radiogroup"/></div>').click(function () {
                t.oriWidget.isEnabled() && t._createTriggerView()
            }).appendTo(this.element)
        }, _createTriggerView: function () {
            var t = this, i = this.options;
            this.$triggerView || (this.$triggerView = e('<div class="trigger-view"></div>').append(this.oriWidget.element)), this.bubble = FX.Msg.bubble({
                anchor: this.$selectTrigger,
                contentHTML: this.$triggerView,
                text4Ok: "",
                text4Cancel: "",
                hasTriangle: !1,
                hAdjust: 70,
                onClose: function () {
                    return t.$triggerView.detach(), t._showSelectValue(), FX.Utils.applyFunc(t, i.onStopEdit, [], !1), !1
                }
            })
        }, _showSelectValue: function () {
            var t = this.oriWidget.getValue();
            e(".select-val", this.$selectTrigger).text(t)
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.SubformRadioGroup.superclass.getOptions.apply(this, arguments), {
                items: t.items,
                type: t.oriType
            })
        }, setCacheValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformRadioGroup.superclass.setCacheValue, [e], !1), this._showSelectValue()
        }, setValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformRadioGroup.superclass.setValue, [e], !1), this._showSelectValue()
        }
    }), e.shortcut("subform_radiogroup", FX.SubformRadioGroup)
}(jQuery), function (e) {
    FX.SubformCheckboxGroup = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformCheckboxGroup.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_checkboxgroup",
                oriType: "checkboxgroup",
                items: [{value: "选项1", text: "选项1"}, {value: "选项2", text: "选项2"}, {value: "选项3", text: "选项3"}]
            })
        }, _init: function () {
            FX.SubformCheckboxGroup.superclass._init.apply(this, arguments), this._createTriggerBtn(), this._showSelectValue()
        }, _createOriWidget: function () {
            var e = this.options, t = this, i = {
                type: e.oriType,
                items: e.items,
                allowBlank: e.allowBlank,
                visible: e.visible,
                enable: e.enable,
                onAfterItemSelect: function () {
                    t._showSelectValue(), FX.Utils.applyFunc(t, e.onStopEdit, [], !1)
                }
            };
            this.oriWidget = FX.createWidget(i)
        }, _createTriggerBtn: function () {
            var t = this;
            this.$selectTrigger = e('<div class="select-trigger"><span class="select-val"></span><i class="widget-icon icon-widget-checkboxgroup"/></div>').click(function () {
                t.oriWidget.isEnabled() && t._createTriggerView()
            }).appendTo(this.element)
        }, _createTriggerView: function () {
            var t = this;
            this.$triggerView || (this.$triggerView = e('<div class="trigger-view"></div>').append(this.oriWidget.element)), this.bubble = FX.Msg.bubble({
                anchor: this.$selectTrigger,
                contentHTML: this.$triggerView,
                text4Ok: "",
                text4Cancel: "",
                hasTriangle: !1,
                hAdjust: 95,
                onClose: function () {
                    return t.$triggerView.detach(), t._showSelectValue(), !1
                }
            })
        }, _showSelectValue: function () {
            var t = this.oriWidget.getValue();
            e(".select-val", this.$selectTrigger).text(t)
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.SubformCheckboxGroup.superclass.getOptions.apply(this, arguments), {
                items: t.items,
                type: t.oriType
            })
        }, setCacheValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformCheckboxGroup.superclass.setCacheValue, [e], !1), this._showSelectValue()
        }, setValue: function (e) {
            FX.Utils.applyFunc(this, FX.SubformCheckboxGroup.superclass.setValue, [e], !1), this._showSelectValue()
        }
    }), e.shortcut("subform_checkboxgroup", FX.SubformCheckboxGroup)
}(jQuery), function (e) {
    FX.SubformFileUpload = FX.extend(FX.SubformBase, {
        _defaultConfig: function () {
            return e.extend(FX.SubformFileUpload.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "fui_subform_file_upload",
                iconCls: "icon-widget-upload",
                uploadTokenURL: FX.Utils.getApi(FX.API.file.upload_token, FX.STATIC.APPID)
            })
        }, _init: function () {
            FX.SubformFileUpload.superclass._init.apply(this, arguments), this._createSubformUploadBtn(), this._createUpload()
        }, _createSubformUploadBtn: function () {
            var t = this.options, i = this;
            this.$btn = e('<div class="upload-subform-btn"><div class="btn-icon-wrapper"><i class="' + t.iconCls + '"/></div></div>').on("click", function (a) {
                var s = e(a.target).closest(".thumbnail");
                if (s && s.length) return new FX.FilePreview({
                    files: i.oriWidget.files,
                    currentItem: s.index(),
                    autoClose: !1
                }), !1;
                t.enable && FX.Msg.bubble({
                    anchor: i.$btn,
                    contentHTML: i.$triggerView,
                    text4Ok: "",
                    text4Cancel: "",
                    hAdjust: 53,
                    minWidth: 340,
                    hasTriangle: !1,
                    contentPadding: 0,
                    onClose: function () {
                        return i.$triggerView.detach(), !1
                    }
                })
            }).toggleClass("x-ui-disable", !t.enable).appendTo(this.element), this.$subWrapper = e('<div class="subform-thumb-wrapper"/>').prependTo(this.$btn)
        }, _createUpload: function () {
            var t = this.options, i = this;
            this.$triggerView = e('<div class="' + t.baseCls + '"/>');
            var a = {
                renderEl: e('<div class="upload-bubble"/>').appendTo(this.$triggerView),
                type: t.oriType,
                baseCls: "fui_upload",
                uploadTokenURL: t.uploadTokenURL,
                thumbWidth: 60,
                thumbHeight: 60,
                progressWidth: 310,
                progressHeight: 20,
                hasEmptyTip: !0,
                fileThumbSize: "small",
                width: "100%",
                height: "100%",
                enable: t.enable,
                maxFileCount: t.maxFileCount,
                visible: t.visible,
                allowBlank: t.allowBlank,
                compressed: t.compressed,
                onlyCamera: t.onlyCamera,
                onFileSizeLimit: t.onFileSizeLimit,
                onFileThumbCreate: function (a) {
                    switch (t.maxFileCount === FX.CONST.UPLOAD_FILE_COUNT.SINGLE && i.$subWrapper.empty(), a.type) {
                        case"normal":
                            var s = e('<div class="thumbnail"/>').appendTo(i.$subWrapper);
                            FX.Utils.createFileThumb(a.ext, "tiny").appendTo(s);
                            break;
                        case"local":
                            var n = this.drawLocalPreview(a.ext, 13, 13);
                            e('<div class="thumbnail"/>').append(n).appendTo(i.$subWrapper);
                            break;
                        case"remote":
                            e('<div class="thumbnail"/>').append(a.ext.css({
                                width: 26,
                                height: 26
                            })).appendTo(i.$subWrapper)
                    }
                },
                onFileRemove: function (t) {
                    e(".thumbnail", i.$subWrapper).eq(t).remove()
                }
            };
            this.oriWidget = FX.createWidget(a)
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, getOptions: function () {
            return e.extend(FX.SubformFileUpload.superclass.getOptions.apply(this, arguments), {
                type: this.oriWidget.getWidgetType(),
                maxFileCount: this.options.maxFileCount
            })
        }, setCacheValue: function (e) {
            this.$subWrapper.empty(), FX.Utils.applyFunc(this, FX.SubformFileUpload.superclass.setCacheValue, [e], !1)
        }
    }), e.shortcut("subform_upload", FX.SubformFileUpload)
}(jQuery), function (e) {
    FX.SubformImage = FX.extend(FX.SubformFileUpload, {
        _defaultConfig: function () {
            return e.extend(FX.SubformImage.superclass._defaultConfig.apply(this, arguments), {iconCls: "icon-widget-image"})
        }, getConfigItems: function () {
            return FX.Utils.applyFunc(this, this.oriWidget.getConfigItems, arguments, !1)
        }, getOptions: function () {
            var t = this.options;
            return e.extend(FX.SubformImage.superclass.getOptions.apply(this, arguments), {
                type: this.oriWidget.getWidgetType(),
                maxFileCount: t.maxFileCount,
                compressed: t.compressed,
                onlyCamera: t.onlyCamera
            })
        }
    }), e.shortcut("subform_image", FX.SubformImage)
}(jQuery), function (e) {
    FX.TableContainer = FX.extend(FX.Container, {
        _defaultConfig: function () {
            return e.extend(FX.TableContainer.superclass._defaultConfig.apply(this, arguments), {
                baseCls: "x-layout-table",
                rowSize: [],
                colSize: [],
                hgap: 0,
                vgap: 0,
                items: [],
                padding: 0
            })
        }, _init: function () {
            FX.TableContainer.superclass._init.apply(this, arguments), this.$rows = [];
            var t = this.options;
            t.padding && this.element.css({padding: t.padding});
            for (var i = 0, a = t.rowSize.length; i < a; i++) {
                for (var s = e('<div class="x-layout-table-row"/>').appendTo(this.element), n = 0, o = t.colSize.length; n < o; n++) {
                    var l = t.items[i][n];
                    if (l) {
                        var r = e('<div class="x-layout-table-item"/>').appendTo(s);
                        l.type ? this._addWidget(e.extend(l, {
                            width: l.width ? l.width : t.colSize[n],
                            height: l.height ? l.height : t.rowSize[i],
                            renderEl: r
                        })) : r.css({
                            width: t.colSize[n],
                            height: t.rowSize[i]
                        }).append(l), n > 0 && r.css({"margin-left": t.hgap})
                    }
                }
                i > 0 && s.css({"margin-top": t.vgap}), this.$rows.push(s)
            }
        }, getRowAt: function (e) {
            return this.$rows[e]
        }, setRowVisible: function (e, t) {
            for (var i = 0, a = e.length; i < a; i++) t ? this.$rows[e[i]].show() : this.$rows[e[i]].hide()
        }
    }), e.shortcut("tablecontainer", FX.TableContainer)
}(jQuery), function (e) {
    FX.CheckBox = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.CheckBox.superclass._defaultConfig.apply(), {
                baseCls: "x-check",
                isSelected: !1,
                onStateChange: null
            })
        }, _init: function () {
            FX.CheckBox.superclass._init.apply(this, arguments);
            var t = this.options, i = this;
            e('<i class="icon-blank"/>').appendTo(this.element), this.$text = e("<span/>").appendTo(this.element), this.element.click(function () {
                i.isEnabled() && i.setSelected(!t.isSelected) && FX.Utils.applyFunc(i, t.onStateChange, [t.isSelected], !1)
            })
        }, _initDefaultValue: function () {
            var e = this.options;
            FX.Utils.isEmpty(e.text) || this.setText(e.text), e.value && this.setValue(e.value)
        }, setSelected: function (e) {
            return this.options.isSelected !== e && (this.options.isSelected = e, e ? this.element.addClass("select") : this.element.removeClass("select"), !0)
        }, isSelected: function () {
            return this.options.isSelected
        }, setValue: function (e) {
            e ? this.setSelected(!0) : this.setSelected(!1)
        }, getValue: function () {
            return this.isSelected()
        }, setText: function (e) {
            this.$text.text(e)
        }, getText: function () {
            return this.$text.text()
        }
    }), e.shortcut("checkbox", FX.CheckBox)
}(jQuery), function (e) {
    FX.Switch = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Switch.superclass._defaultConfig.call(), {
                baseCls: "fui_switch",
                width: 44,
                height: 22,
                value: !1,
                onSwitch: null,
                btnPadding: 2,
                text4On: "开",
                text4Off: "关"
            })
        }, _init: function () {
            FX.Switch.superclass._init.apply(this, arguments);
            var t = this.options, i = this;
            this.$text = e('<span class="switch-text"/>').text(t.text4On).appendTo(this.element), this.$btn = e('<span class="switch-btn"/>').appendTo(this.element), this.element.click(function () {
                i.isEnabled() && i._doSwitch(!t.value, !0)
            })
        }, _doSwitch: function (e, t) {
            var i = this.options, a = this, s = {}, n = {}, o = "";
            i.value = e, !0 === i.value ? (this.element.addClass("on").removeClass("off"), this.$text.text(""), s.left = i.width - i.height + i.btnPadding, n["padding-left"] = 0, n["padding-right"] = i.height - 3 * i.btnPadding, o = i.text4On) : (this.element.addClass("off").removeClass("on"), this.$text.text(""), s.left = i.btnPadding, n["padding-left"] = i.height - 3 * i.btnPadding, n["padding-right"] = 0, o = i.text4Off), t ? this.$btn.animate(s, 150, function () {
                a.element.css(n), a.$text.text(o), FX.Utils.applyFunc(a, i.onSwitch, [i.value], !1)
            }) : (this.$btn.css(s), this.element.css(n), this.$text.text(o))
        }, setValue: function (e) {
            this._doSwitch(e, !1)
        }, getValue: function () {
            return this.options.value
        }, doResize: function (e) {
            FX.Switch.superclass.doResize.apply(this, arguments);
            var t = this.options, i = t.height, a = t.width, s = i - 2 * t.btnPadding, n = {};
            i && (n["line-height"] = i + "px"), a && (this.$btn.css({
                width: s,
                height: s
            }), n["border-radius"] = a / 2), this.element.css(n)
        }
    }), e.shortcut("switch", FX.Switch)
}(jQuery), function (e) {
    FX.Button = FX.extend(FX.Widget, {
        _defaultConfig: function () {
            return e.extend(FX.Button.superclass._defaultConfig.apply(), {
                baseCls: "x-btn",
                iconCls: null,
                style: "blue"
            })
        }, _init: function () {
            FX.Button.superclass._init.apply(this, arguments);
            var t = this.options, i = this;
            t.iconCls && e("<i/>").addClass(t.iconCls).appendTo(this.element), this.$text = e("<span/>").appendTo(this.element), t.style && this.element.addClass("style-" + t.style), t.hoverCls && this.element.hover(function () {
                i.isEnabled() && e(this).addClass(t.hoverCls)
            }, function () {
                i.isEnabled() && e(this).removeClass(t.hoverCls)
            }), this.element.click(function (e) {
                i.isEnabled() && FX