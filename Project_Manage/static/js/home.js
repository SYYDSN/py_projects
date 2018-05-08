$(function(){
    const url = location.pathname.replace("/view","");

    // 启动页面时,初始化#my_chart的大小
    let resize_chart = function(){
        let obj = $("#my_bar");
        let w = obj.width();
        let h = obj.height();
        $("#my_chart").css({"min-width": w, "min-height": h});
    };
    resize_chart();
    $(window).resize(function(){resize_chart();});

    // 切换甘特图和架构图
    $(".change_show span").each(function(){
        let $this = $(this);
        $this.click(function(){
            let text = $this.text();
            if(text.indexOf("甘特") !== -1){
                $(".dv-right #chart_title, .dv-right #my_chart").hide();
               $(".dv-right #bar_title, .dv-right #my_bar").show();
            }
            else{
                $(".dv-right #bar_title, .dv-right #my_bar").hide();
                $(".dv-right #chart_title, .dv-right #my_chart").show();
                if(!chart_visual){
                    draw_chart(); // 绘制图表
                }
            }
        });
    });

    //左侧导航的hover事件
    $(".p_nav").hover(function(){
        let spn = $(this).find(".spn");
        if(!spn.hasClass("actives")){
             spn.addClass("actives");
        }
    }, function(){
        let spn = $(this).find(".spn");
        if(spn.hasClass("actives")){
             spn.removeClass("actives");
        }
    });

    // 日期选择器初始化函数
    let date_picker = function (a_str) {
        /* 初始化日期函数
        * 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/index.htm
        * id_str参数是日期input的id/class
        */
        console.log(`a_str is ${a_str}`);
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

    //  显示选择项目的单选框的函数,在添加模块时调用,以提供选择项目的功能
    let show_projects = function(project_list){
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
            outer.append(`<input onclick="show_mission(this)" type="radio" name="ss_module" data-id="${m['_id']}"  value="">${m['name']}`);
        }
        if(module_list.length > 0){
            $(".select_module_title").show();
        }
        else{
            $(".select_module_title").hide();
        }
    };

    // 显示选择功能的单选框的函数,在添加任务时调用,提供选择任务对应的功能的选项
    show_mission = function(obj){
        let outer = $(".select_mission_div");
        outer.empty();
        let _id = $(obj).attr("data-id");
        let mission_list = module_mission_dict[_id];
        if(mission_list !== undefined){
            for(let m of mission_list){
                outer.append(`<input type="radio" name="ss_mission" data-id="${m['_id']}"  value="">${m['name']}`);
            }
            if(mission_list.length > 0){
                $(".mission_list").show();
            }
            else{
                $(".select_mission_title").hide();
            }
        }else{}
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

    // 添加 项目/模块/功能/任务 切换
    $(".dv-left .title .spn").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".dv-left .title .spn").removeClass("active");
            $this.addClass("active");
            if($.trim($this.text()) === "任务"){
                $("#project_list,#module_list,#mission_list").hide(0);
                $("#task_list").show(0);
                $("#add_item").attr("data-target", ".add_task_modal").text("添加任务");
            }
            else if($.trim($this.text()) === "模块"){
                $("#project_list,#task_list,#mission_list").hide(0);
                $("#module_list").show(0);
                $("#add_item").attr("data-target", ".add_project_modal").text("添加模块");
                $(".add_project_modal li:eq(1)").click();
            }
            else if($.trim($this.text()) === "功能"){
                $("#project_list,#task_list,#module_list").hide(0);
                $("#mission_list").show(0);
                $("#add_item").attr("data-target", ".add_project_modal").text("添加功能");
                $(".add_project_modal li:eq(2)").click();
            }
            else{
                $("#task_list,#module_list,#mission_list").hide(0);
                $("#project_list").show(0);
                $("#add_item").attr("data-target", ".add_project_modal").text("添加项目");
                $(".add_project_modal li:eq(0)").click();
            }

        });
    });

    // 添加任务模态框的切换角色
    $(".select_category_div span").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".select_category_div .select_category_active").removeClass("select_category_active");
            $this.addClass("select_category_active");
            let id = $this.attr("data-id");
            let ps = projects[id];
            show_projects(ps);
        });
    });

    // 添加/项目/模块/功能 顶部切换按钮，主要是对选择模块，选择项目的radio的禁用/启用
    $(".modal .my_nav li").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".modal .my_nav li").removeClass("active");
            $this.addClass("active");
        });
    });

    // 添加项目/模块
    $("#add_project_or_module").click(function(){
        let name = $.trim($(".add_project_modal .item_class").val());
        let begin_date = $.trim($(".add_project_modal .begin_date").val());
        let end_date = $.trim($(".add_project_modal .end_date").val());
        let category_id = $(".add_project_modal .select_category_div .select_category_active").attr("data-id");
        let project_id = $(".add_project_modal .select_project_div input[type='radio']:checked").attr("data-id");
        let module_id = $(".add_project_modal .select_module_div input[type='radio']:checked").attr("data-id");
        let desc = $.trim($(".add_project_modal .create_desc").val());
        let args = {};
        let post_url = "";
        let text = $(".add_project_modal .my_nav .active").text();
        console.log(text);
        if(text.indexOf("项目") !== -1){
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
            else if(category_id === undefined){
                alert("角色不能为空");
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
        else if(text.indexOf("模块") !== -1) {
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
            else if(category_id === undefined){
                alert("角色不能为空");
                return false;
            }
            else if(project_id === undefined){
                alert("没有选择模块所属的项目");
                return false;
            }
            else{
                post_url = `/home_module/add`;
                args['name'] = name;
                args['category_id'] = category_id;
                args['begin_date'] = begin_date;
                args['end_date'] = end_date;
                args['description'] = desc;
                args['project_id'] = project_id;
            }
        }
        else{
            // 添加功能
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
            else if(module_id === undefined){
                alert("没有选择功能所属的模块");
                return false;
            }
            else if(project_id === undefined){
                alert("没有选择功能所属的项目");
                return false;
            }
            else{
                post_url = `/home_mission/add`;
                args['name'] = name;
                args['module_id'] = module_id;
                args['begin_date'] = begin_date;
                args['end_date'] = end_date;
                args['description'] = desc;
                args['project_id'] = project_id;
            }
        }
        $.post(post_url, args, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
            alert(json['message']);
            if(json['message'] === "success"){
                location.reload()
            }
            else{
                // nothing ...
            }
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
        let mission_id = $(".add_task_modal .select_mission_div input[type='radio']:checked").attr("data-id");
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
            if(mission_id !== undefined){
                args['mission_id'] = mission_id;
            }else{}
            args['begin_date'] = begin_date;
            args['end_date'] = end_date;
            args['description'] = desc;
        }

        $.post(post_url, args, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
            alert(json['message']);
            if(json['message'] === "success"){
                location.reload();
            }
            else{
                // nothing ...
            }
        });
    });

    // 查看 任务/项目/模块/功能的通用函数
    view_item = function(obj, the_class, the_class_name){
        let $this = $(obj);
        // 当前类别是?
        let class_text = $(".dv-left .title .active").text();
        let html = "";
        let _id = $this.attr("data-id");
        if(the_class === undefined || the_class_name === undefined){
            the_class = "project";
            the_class_name = "项目";
            if(class_text.indexOf("功能") !== -1){
                // 查看功能
                the_class = "mission";
                the_class_name = "功能";
            }
            else if(class_text.indexOf("模块") !== -1){
                // 查看功能
                the_class = "module";
                the_class_name = "模块";
            }
            else if(class_text.indexOf("项目") !== -1){
                // 查看功能
                the_class = "project";
                the_class_name = "项目";
            }
            else if(class_text.indexOf("任务") !== -1){
                // 查看功能
                the_class = "task";
                the_class_name = "任务";
            }
            else{}
        }else{
            console.log("无需设置the_class, the_class_name");
        }

        let url = `/home_${the_class}/get`;
        $.post(url, {"_id": _id}, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
            if(json['message'] !== "success"){
                alert(json['message']);
            }
            else{
                let cur_project_id = undefined;
                let cur_module_id = undefined;
                let data = json['data'];
                $("#view_modal .modal-title").attr("data-class", the_class).text(`查看${the_class_name}`);
                let outer = $("#view_modal .my_item");
                outer.empty();

                // id
                let id = $(`<div style="display: none" class="form-group"><label>id</label>
                                     <input type="text" data-key="_id" class="form-control my_arg" value="${data['_id']}">
                                  </div>`);
                outer.append(id);
                // name
                let name = $(`<div class="form-group"><label>功能说明</label>
                                     <input type="text" data-key="name"  class="form-control my_arg" value="${data['name']}">
                                  </div>`);
                outer.append(name);
                // Category.path
                let c_path = data['path'];
                if(c_path === undefined){
                    // nothing ...
                }
                else{
                    let path = $(`<div class="form-group"><label>url_path</label>
                                     <input type="text" data-key="path"  class="form-control my_arg" value="${c_path}">
                                  </div>`);
                    outer.append(path);
                }
                // Task.type
                let t_type = data['type'];
                if(t_type === undefined){
                    // nothing ...
                }
                else{
                    let type = $(`<div class="form-group"><label>任务类型</label>
                                     <select data-key="type" class="my_arg">
                                        <option value="feature">功能</option>
                                        <option value="debug">debug</option>
                                     </select>
                                  </div>`);
                    outer.append(type);
                }
                // project
                if(the_class === "project"){
                    // nothing...  项目本身没这个属性
                }
                else{
                    let project_opts = "";
                    for(let x of all_projects){
                        project_opts += `<option value="${x['_id']}">${x['name']}</option>"`;
                    }
                    let project = $(`<div class="form-group"><label>项目</label>
                                         <select data-key="project_id" class="my_arg my_project">
                                            ${project_opts}
                                         </select>
                                      </div>`);
                    outer.append(project);
                    cur_project_id = data['project_id'];
                    cur_module_id = data['module_id'];
                    $("#view_modal .my_item .my_project").val(cur_project_id).change(function(){
                        // 选择事件
                        console.log("my_project change");
                        let p_id = $(this).val();
                        let m_html = "";
                        let ms = allow_edit_modules[p_id];
                        if(ms === undefined){
                            // nothing ...
                        }
                        else{
                            for(let m of ms){
                                m_html += `<option value="${m['_id']}">${m['name']}</option>`;
                            }
                        }
                        $("#view_modal .my_item .my_module").empty().html(m_html);
                    });

                }
                // module
                if(the_class === "project" || the_class === "module"){
                    // nothing  项目和模块没有module_id属性
                }
                else{
                    let module_opts = "";
                    for(let x of all_modules){
                        module_opts += `<option value="${x['_id']}">${x['name']}</option>"`;
                    }
                    let module = $(`<div class="form-group"><label>模块</label>
                                         <select data-key="module_id" class="my_arg my_module">
                                            ${module_opts}
                                         </select>
                                      </div>`);
                    outer.append(module);
                    $("#view_modal .my_item .my_module").val(cur_module_id);
                    // 检查是不是有mission_id,
                    let cur_mission_id = data['mission_id'];
                    if(cur_mission_id !== undefined){
                        $.post("/home_module/children", {"module_id": cur_module_id}, function(resp){
                            let ms = JSON.parse(resp)['data'];
                            if(ms.length > 0){
                                let mission_opts = "";
                                for(let x of ms){
                                    mission_opts += `<option value="${x['_id']}">${x['name']}</option>"`;
                                }
                                let mission = $(`<div class="form-group"><label>功能</label>
                                         <select data-key="mission_id" class="my_arg my_mission">
                                            ${mission_opts}
                                         </select>
                                      </div>`);
                                outer.append(mission);
                                $("#view_modal .my_item .my_mission").val(cur_mission_id);
                            }
                        });
                    }
                }
                // begin_date
                let date = $(`<div class="form-group"><label>起止时间</label>
                                     <div class="">
                                     <input data-key="begin_date" class="my_arg begin_date col-lg-6 col-md-6 col-sm-6">
                                     <input data-key="end_date" class="my_arg end_date col-lg-6 col-md-6 col-sm-6">
                                     </div>
                                  </div>`);
                outer.append(date);
                date_picker("#view_modal .my_item .begin_date");
                date_picker("#view_modal .my_item .end_date");
                $("#view_modal .my_item .begin_date").val(data['begin_date']);
                $("#view_modal .my_item .end_date").val(data['end_date']);
                // status
                let status = $(`<div class="form-group"><label>状态</label>
                                     <select data-key="status" class="my_arg">
                                        <option value="normal">正常</option>
                                        <option value="stop">停止</option>
                                        <option value="suspend">暂停</option>
                                     </select>
                                  </div>`);
                if(the_class === "mission"){
                    status = $(`<div class="form-group"><label>状态</label>
                                     <select data-key="status" class="my_arg">
                                        <option value="ready">准备</option>
                                        <option value="developing">开发中</option>
                                        <option value="complete">完成</option>
                                     </select>
                                  </div>`);
                }
                else if(the_class === "task"){
                    status = $(`<div class="form-group"><label>状态</label>
                                     <select data-key="status" class="my_arg">
                                        <option value="normal">正常</option>
                                        <option value="fail">失败</option>
                                        <option value="drop">放弃</option>
                                        <option value="suspend">暂停</option>
                                        <option value="delay">超期</option>
                                        <option value="complete">完成</option>
                                     </select>
                                  </div>`);
                }
                else{}
                outer.append(status);
                $("#view_modal .my_item .my_status").val(data['status']);
                // description
                let desc = $(`<div class="form-group">
                                     <label>备注</label>
                                     <input data-key="description" class="form-control my_arg" value="${data['description']}">
                                  </div>`);
                outer.append(desc);

                // 判断权限
                let can_edit = false;
                let cur_category = data['category_path'];
                if(cur_category !== undefined){
                    if(allow_edit.indexOf(cur_category) !== -1){
                        can_edit = true;
                    }
                    else{
                        can_edit = false;
                    }
                }else{}
                if(cur_project_id !== undefined){
                    if(allow_edit_pids.indexOf(cur_project_id) !== -1){
                        can_edit = true;
                    }
                    else{
                        can_edit = false;
                    }
                }else{}
                if(cur_module_id !== undefined){
                    if(allow_edit_mids.indexOf(cur_module_id) !== -1){
                        can_edit = true;
                    }
                    else{
                        can_edit = false;
                    }
                }else{}

                if(can_edit){
                    $("#view_modal .only_read").hide();
                    $("#view_modal .can_edit").show();
                }else{
                    $("#view_modal .can_edit").hide();
                    $("#view_modal .only_read").show();
                }

                $("#launch_view_modal").click();
            }

        });
    };

    // 双击甘特图的任务,弹出查看/编辑模态框
    $(".my_plan").each(function(){
        let $this = $(this);
        $this.dblclick(function(){
            view_item(this, "task", "任务");
        });
    });

    // 双击甘特图的空白,检查用户权限, 弹出添加任务模态框
    $(".no_plan").dblclick(function(){
        if(allow_edit.length > 0){
            $(".dv-left .title .spn:first").click();
            $("#add_item").click();
        }else{}

    });

    // 模态框的编辑提交按钮
    $("#edit_submit").click(function(){

        let the_class = $("#view_modal .modal-title").attr("data-class");
        let url = `/home_${the_class}/edit`;
        // 取参数,
        let inputs = $("#view_modal .form-group .my_arg");
        let args = {};
        for(let input of inputs){
            let cur = $(input);
            let key = cur.attr("data-key");
            args[key] = cur.val();
        }
        $.post(url, args, function(resp){
            let json = JSON.parse(resp);
            if(json['message'] === "success"){
                alert("修改成功");
                location.reload();
            }
            else{
                alert(json['message']);
                return false;
            }
        });
    });

    // 模态框的删除按钮
    $("#delete_submit").click(function(){
        let the_class = $("#view_modal .modal-title").attr("data-class");
        let url = `/home_${the_class}/delete`;
        let _id = $("#view_modal .form-group .my_arg[data-key='_id']").val();
        let args = {"_id": _id}
        $.post(url, args, function(resp){
            let json = JSON.parse(resp);
            if(json['message'] === "success"){
                alert("删除成功");
                location.reload();
            }
            else{
                alert(json['message']);
                return false;
            }
        });
    });

    // 绘制树状图
    let chart_visual = false;  // 图标是否处于可见状态?
    let draw_chart = function(){
        let my = echarts.init($("#my_chart")[0]);
        // let ss = {"type": "tree", "name": tree_dict['name'], data:tree_dict['children']};
        let ss = [
            {
                type: 'tree',
                name: tree_dict['name'],
                data: [tree_dict],

                top: '1%',
                left: '7%',
                bottom: '1%',
                right: '20%',

                symbolSize: 7,

                label: {
                    normal: {
                        position: 'left',
                        verticalAlign: 'middle',
                        align: 'right',
                        fontSize: 9
                    }
                },

                leaves: {
                    label: {
                        normal: {
                            position: 'right',
                            verticalAlign: 'middle',
                            align: 'left'
                        }
                    }
                },

                expandAndCollapse: true,
                animationDuration: 550,
                animationDurationUpdate: 750
            }
        ];
        let opt = {tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
            legend: {
                top: '2%',
                left: '3%',
                orient: 'vertical',
                data: [{
                    name: 'tree1',
                    icon: 'rectangle'
                } ,
                    {
                        name: 'tree2',
                        icon: 'rectangle'
                    }],
                borderColor: '#c23531'
            },
            series:ss
        };
        my.setOption(opt);
        chart_visual = true;
    };

//end!!!
});