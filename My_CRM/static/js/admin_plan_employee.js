/**
 * Created by walle on 17-2-8.
 */
$(function () {
    $.fn.bootstrapSwitch.defaults.size = 'mini';
    $.fn.bootstrapSwitch.defaults.onText = '自动分配';
    $.fn.bootstrapSwitch.defaults.offText = '手动分配';
    $(".switch>input[type='checkbox']").bootstrapSwitch('state', true, true);

    // 平均分配百分比
    default_plan = function () {
        var members = $("#plan_member .per_num");
        var count = 0;
        var new_member = new Array();
        members.each(function(){
            var $this = $(this);
            if($this.parents("td:first").prev().find("input").prop("checked")){
                count += 1;
                new_member.push($this);
            }else{}
        });
        var per = Math.round((1 / count) * 100);
        for(var i=0; i< new_member.length; i++){
            new_member[i].val(per);
        }
    };

    // 取消平均分配
    cancel_default_plan = function () {
        $("#plan_member .per_num").val('');
    };

    // 分配方式开关
    $("#plan_type").on('switchChange.bootstrapSwitch', function (event, state) {
        if (state) {
            default_plan();
        }
        else {
            cancel_default_plan();
        }
    });

    $("#plan_type").on("switchChange",function(event,state){console.log(event);console.log(state);});

    // 添加计划
    add_plan = function () {
        $("#myModalLabel").text("添加分配策略");
        $("#pop_modal").click();
        var members = $("#plan_member .per_num");
        var per = Math.round((1 / members.length) * 100);
        members.val(per);
    };

    // 根据plan_sn从服务器获取成员信息
    get_item = function (plan_sn) {
        $("#sn").val(plan_sn);
        $.post("/employee/plan", {"the_type": "get_item", "plan_sn": plan_sn}, function (data) {

            var is_auto = true;
            var prev_val = null;
            for (var i = 0, l = data.length; i < l; i++) {
                // 检查是不是平均分配？
                var item = data[i];
                var val = item['per_num'];
                if(prev_val != null && prev_val != val){
                    is_auto = false;
                }
                prev_val = val;
            }

            // 检查是不是所有的成员都选中了？
            var count_checked = data.length;
            var count_all = $(".is_default").length;
            if(count_all != count_checked){
                is_auto = false;
            }
            if(!is_auto){
                // 如果计算的结果是手动分配
                if($(".switch .bootstrap-switch-mini").attr("class").indexOf("bootstrap-switch-off") == -1){
                    $("#plan_type").click();
                }else{}
            }
            else{
                if($(".switch .bootstrap-switch-mini").attr("class").indexOf("bootstrap-switch-on") == -1){
                    $("#plan_type").click();
                }else{}
            }
             // 填充数据
            for (var i = 0, l = data.length; i < l; i++) {
                var item = data[i];
                var val = item['per_num'];
                $(".per_num[data-sn='"+ item['member_sn'] +"']").val(val).attr("data-recode", item['sn']).parents("td:first").prev().find("input").prop("checked", true);
            }
            var id_str = "#" + plan_sn;
            $("#plan_name").val($(id_str).find(".plan_name").text());
        });
    };

    // 弹出调整计划面板
    edit = function ($obj) {
        $("#myModalLabel").text("调整分配策略");
        /*拷贝值*/
        var plan_sn = $.trim($obj.attr("data-id"));
        get_item(plan_sn);
        $("#pop_modal").click();
    };

    // 保存计划
    $("#save_plan").click(function () {
        var the_type = $.trim($("#myModalLabel").text()) == "添加分配策略" ? "add" : "edit";
        var plan_name = $.trim($("#plan_name").val());
        if (plan_name == "") {
            alert("策略简述不能为空");
            return false;
        }
        else {
            var members = $("#plan_member .per_num");
            var member_list = new Array();
            var args = {};
            var can_commit = true;
            if (the_type == "edit") {
                // 编辑计划
                args['sn'] = $.trim($("#sn").val());
                members.each(function () {
                    var $this = $(this);
                    if($this.parents("td:first").prev().find("input").prop("checked")){
                        // 被勾选的
                        var key_str = $.trim($this.attr("data-sn"));
                        var val = $.trim($this.val());
                        if (isNaN(val) || val == "") {
                            var warning = val != "" ? (val + "不是一个有效的数字") : "分配比例不能为空";
                            alert(warning);
                            can_commit = false;
                            return false;
                        }
                        else {
                            var temp = {
                                "member_sn": key_str,
                                "per_num": parseInt(val),
                                "sn": $.trim($this.attr("data-recode"))
                            };
                            member_list.push(temp);
                        }
                    }else{}
                });
            }
            else{
                // 添加计划
                members.each(function () {
                    var $this = $(this);
                    if($this.parents("td:first").prev().find("input").prop("checked")){
                        // 被勾选的
                        var key_str = $.trim($this.attr("data-sn"));
                        var val = $.trim($this.val());
                        if (isNaN(val) || val == "") {
                            var warning = val != "" ? (val + "不是一个有效的数字") : "分配比例不能为空";
                            alert(warning);
                            can_commit = false;
                            return false;
                        }
                        else {
                            var temp = {"member_sn": key_str, "per_num": parseInt(val)};
                            member_list.push(temp);
                        }
                    }else{}
                });
            }
            args["the_type"] = the_type;
            args["plan_name"] = plan_name;
            args["member_list"] = JSON.stringify(member_list);

            if(can_commit){
                // 开始提交。
                var url = "/employee/plan";
                $.post(url, args, function (data) {
                    if (data['message'] == "success") {
                        var welcome = the_type == "edit" ? "编辑成功" : "添加成功";
                        alert(welcome);
                        location.reload();
                    }
                    else {
                        alert(data['message']);
                    }
                });
            }else{}
        }
    });

    // 删除计划
    delete_plan = function($obj){
        var plan_sn = $.trim($obj.attr("data-id"));
        var id_str = "#" + plan_sn;
        if($.trim($(id_str).find(".plan_status>a").text()) == "激活"){
            alert("正在使用的分配计划不能被删除！");
            return false;
        }
        else{
            var r = confirm("你确实向删除此计划吗？");
            if(r){
                var args = {"the_type": "delete", "sn": plan_sn};
                $.post("/employee/plan", args, function(data){
                    if(data['message'] == "success"){
                        alert("删除成功");
                        location.reload();
                    }
                    else{
                        alert(data["message"]);
                    }
                });
            }else{}
        }
    };

    // 改变计划状态
    change_status = function ($obj) {
        var plan_sn = $.trim($obj.attr("data-id"));
        var the_type = $.trim($obj.text()) == "激活" ? "down" : "up";
        var args = {"the_type": the_type, "sn": plan_sn};
        $.post("/employee/plan", args , function(data){
            if(data['message'] == "success"){
                var warning = the_type == "up" ? "启用成功" : "停用成功";
                alert(warning);
                location.reload();
            }
            else{
                alert(data['message']);
                return false;
            }
        });
    };


    //end !
});