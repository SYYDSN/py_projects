$(function(){
    const url = location.pathname.replace("/view","");

    // 日期选择器初始化函数
    let date_picker = function (a_str) {
        /* 初始化日期函数
        * 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/index.htm
        * id_str参数是日期input的id/class
        */
        $(`${a_str}`).datetimepicker({
            language: "zh-CN",
            weekStart: 1,  // 星期一作为一周的开始
            minView: 2,  // 不显示小时和分
            autoclose: true,  // 选定日期后立即关闭选择器
            format: "yyyy-mm-dd"
        }).on("show", function (ev) {
            // 当选择器显示时被触发.示范,无实际意义.
            console.log(ev);
            console.log("选择器面板被打开");
        }).on("hide", function (ev) {
            // 当选择器隐藏时被触发 示范,无实际意义
            console.log(ev);
            console.log("选择器面板被隐藏");
        }).on("changeDate", function (ev) {
            // 当日期被改变时被触发
            console.log(ev);
            console.log("选择器日期被改变");
        });
    };
    date_picker(".begin_date");
    date_picker(".end_date");

    // 显示类别下的项目,在添加模块时调用,以提供选择项目的功能
    let show_projects = function(project_list){
        let outer = $(".select_module");
        outer.empty();
        for(let p of project_list){
            outer.append(`<input type="radio" name="mokgs" value="${p['_id']}">${p['name']}`);
        }
        if(project_list.length > 0){
            $(".select_module_title").show();
        }
        else{
            $(".select_module_title").hide();
        }
    };

    // 启动时,调整左侧底部按钮为添加项目
    $("#add_item").attr("data-target", ".add_task_modal").text("添加任务");

    // 项目/任务切换
    $(".dv-left .title .spn").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".dv-left .title .spn").removeClass("active");
            $this.addClass("active");
            if($.trim($this.text()) === "任务"){
                $("#project_list").hide(0);
                $("#task_list").show(0);
                $("#add_item").attr("data-target", ".add_task_modal").text("添加任务");
            }
            else{
                $("#task_list").hide(0);
                $("#project_list").show(0);
                $("#add_item").attr("data-target", ".add_project_modal").text("添加项目");
            }

        });
    });

    // 切换角色
    $(".select_category_div span").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".select_category_div .select_category_active").removeClass("select_category_active");
            $this.addClass("select_category_active");
            let class_str = $(".create_type input[type='radio']:checked").val();
            if(class_str === "模块"){
                let id = $this.attr("data-id");
                let ps = projects[is];
                show_projects(ps);
            }else{}
        });
    });

    // 模块项目切换按钮
    $(".create_type input[type='radio']").each(function(){
        let $this = $(this);
        $this.click(function(){
            let class_str = $(".create_type input[type='radio']:checked").val();
            console.log(class_str);
            if(class_str === "项目"){
                $(".add_project_modal .modal_title").text("项目名称");
                show_projects([]);  // 清除模块归属
            }
            else{
                $(".add_project_modal .modal_title").text("模块名称");
                let category_id = $(".add_project_modal .select_category_div .select_category_active").attr("data-id");
                let ps = projects[category_id];
                show_projects(ps); // 显示模块归属
            }
        });
    });

    // 添加项目/模块
    $("#add_task").click(function(){
        let type = $(".add_project_modal .modal_title").text() === "项目名称"? "project": "module";
        let name = $.trim($(".add_project_modal .item_class").val());
        let begin_date = $.trim($(".add_project_modal .begin_date").val());
        let end_date = $.trim($(".add_project_modal .end_date").val());
        let category_id = $(".add_project_modal .select_category_div .select_category_active").attr("data-id");
        let desc = $.trim($(".add_project_modal .create_desc").val());
        let args = {};
        let post_url = "";
        if(type === "project"){
            // 新建项目
            post_url = `/home_project/add`;
            args['name'] = name;
            args['category_id'] = category_id;
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
        }
        else{
            post_url = `/home_module/add`;
            args['name'] = name;
            args['category_id'] = category_id;
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
            args['project_id'] = $(".select_module input[type='radio']:checked").val();
        }
        $.post(post_url, args, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
            alert(json['message']);
            location.reload();
        });
    });

    // 添加任务
    $("#add_task").click(function(){
        let name = $.trim($(".add_task_modal .item_class").val());
        let begin_date = $.trim($(".add_task_modal .begin_date").val());
        let end_date = $.trim($(".add_task_modal .end_date").val());
        let category_id = $(".add_task_modal .select_category_div .select_category_active").attr("data-id");
        let desc = $.trim($(".add_task_modal .create_desc").val());
        let args = {};
        let post_url = "";
        if(type === "project"){
            // 新建项目
            post_url = `/home_project/add`;
            args['name'] = name;
            args['category_id'] = category_id;
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
        }
        else{
            post_url = `/home_module/add`;
            args['name'] = name;
            args['category_id'] = category_id;
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
            args['project_id'] = $(".select_module input[type='radio']:checked").val();
        }
        $.post(post_url, args, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
            alert(json['message']);
            location.reload();
        });
    });

//end!!!
});