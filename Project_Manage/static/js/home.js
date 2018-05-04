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

    // 显示选择项目的单选框的函数,在添加模块时调用,以提供选择项目的功能
    let show_projects = function(project_list){
        let outer = $(".select_project_div");
        outer.empty();
        for(let p of project_list){
            outer.append(`<input type="radio" name="mokgs" value="${p['_id']}">${p['name']}`);
        }
        if(project_list.length > 0){
            $(".select_project_title").show();
        }
        else{
            $(".select_project_title").hide();
        }
    };

    // 用于添加任务模态框的 示选择项目的单选框的函数,在添加模块时调用,以提供选择项目的功能
    let show_projects2 = function(project_list){
        let outer = $(".select_project_div");
        outer.empty();
        for(let p of project_list){
            outer.append(`<input onclick="click_select_project_radio($(this))" type="radio" data-id="${p['_id']}" name="mokgs" value="">${p['name']}`);
        }
        if(project_list.length > 0){
            $(".select_project_title").show();
        }
        else{
            $(".select_project_title").hide();
        }
    };

    // 显示选择模块的单选框的函数,在添加任务时调用,以提供选择模块的功能
    let show_modules = function(module_list){
        let outer = $(".select_module_div");
        outer.empty();
        for(let m of module_list){
            outer.append(`<input type="radio" name="ss_module" data-id="${m['_id']}"  value="">${m['name']}`);
        }
        if(module_list.length > 0){
            $(".select_module_title").show();
        }
        else{
            $(".select_module_title").hide();
        }
    };

    // 添加任务模态框,点击项目单选按钮时,变换模块显示区显示的模块单选框
    click_select_project_radio = function($this) {
            console.log("click radio");
            let id = $this.attr("data-id");
            let m_list = allow_edit_modules[id];
            m_list = m_list !== undefined? m_list: [];
            show_modules(m_list);
    };

    // 启动时,调整左侧底部按钮为添加项目
    $("#add_item").attr("data-target", ".add_task_modal").text("添加任务");

    // 添加 项目/任务 切换
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

    // 添加模块模态框的切换角色
    $(".add_project_modal .select_category_div span").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".add_project_modal .select_category_div .select_category_active").removeClass("select_category_active");
            $this.addClass("select_category_active");
            let class_str = $(".create_type input[type='radio']:checked").val();
            if(class_str === "模块"){
                let id = $this.attr("data-id");
                let ps = projects[id];
                show_projects(ps);
            }else{}
        });
    });

    // 添加任务模态框的切换角色
    $(".add_task_modal .select_category_div span").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".add_task_modal .select_category_div .select_category_active").removeClass("select_category_active");
            $this.addClass("select_category_active");
            let id = $this.attr("data-id");
            let ps = projects[id];
            show_projects2(ps);
        });
    });

    // 添加模块模态框 类别切换按钮
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
    $("#add_project_or_module").click(function(){
        let name = $.trim($(".add_task_modal .item_class").val());
        let begin_date = $.trim($(".add_task_modal .begin_date").val());
        let end_date = $.trim($(".add_task_modal .end_date").val());
        let category_id = $(".add_task_modal .select_category_div .select_category_active").attr("data-id");
        let desc = $.trim($(".add_task_modal .create_desc").val());
        let args = {};
        let post_url = "";
        if(type === "project"){
            // 新建项目
            if(begin_date === ""){
                alert("开始日期不能为空");
                return false;
            }
            else if(end_date === ""){
                alert("结束日期不能为空");
                return false;
            }
            else if(name === ""){
                alert("名字不能为空");
                return false;
            }
            else{
                post_url = `/home_project/add`;
                args['name'] = name;
                args['category_id'] = category_id;
                args['begin_date'] = begin_date;
                args['end_date'] = end_date;
                args['description'] = desc;
            }
        }
        else{
            // 新建模块
            if(begin_date === ""){
                alert("开始日期不能为空");
                return false;
            }
            else if(end_date === ""){
                alert("结束日期不能为空");
                return false;
            }
            else if(name === ""){
                alert("名字不能为空");
                return false;
            }
            else{
                post_url = `/home_module/add`;
                args['name'] = name;
                args['category_id'] = category_id;
                args['begin_date'] = begin_date;
                args['end_date'] = end_date;
                args['description'] = desc;
                args['project_id'] = $(".select_project_div input[type='radio']:checked").val();
            }
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
        // let category_id = $(".add_task_modal .select_category_div .select_category_active").attr("data-id");
        let project_id = $(".add_task_modal .select_project_div input[type='radio']:checked").attr("data-id");
        let module_id = $(".add_task_modal .select_module_div input[type='radio']:checked").attr("data-id");
        let desc = $.trim($(".add_task_modal .create_desc").val());
        let args = {};
        let post_url = "/home_task/add";
        // console.log(category_id);
        console.log(project_id);
        console.log(module_id);
        if(begin_date === ""){
            alert("开始日期不能为空");
            return false;
        }
        else if(end_date === ""){
            alert("结束日期不能为空");
            return false;
        }
        else if(name === ""){
            alert("名字不能为空");
            return false;
        }
        else if(project_id === undefined){
            alert("没有选择任务所属的项目");
            return false;
        }
        else if(module_id === undefined){
            alert("没有选择任务所属的模块");
            return false;
        }
        else{
            args['name'] = name;
            args['project_id'] = project_id;
            args['module_id'] = module_id;
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
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