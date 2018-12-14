$(function(){
    // 初始化时间选择器
    /* 初始化日期函数,
        注意，如果你使用bootstrap,input就必须加上form-control类，否则左右选择的小箭头不显示
        * 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/index.htm
        * id_str参数是日期input的id/class
        */
    $(".date_picker").datetimepicker({
        language: "zh-CN",
        weekStart: 1,  // 星期一作为一周的开始
        minView: 2,  // 不显示小时和分
        startView: 2,
        autoclose: true,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd",
    });

    // 根据用户选择的条件过滤信息
    var filter_info = function(){
        var args = get_url_arg_dict();
        var case_type = $(".select_type .current_value").attr("data-id");
        args['case_type'] = case_type;
        var teacher_id = $(".select_teacher .current_value").attr("data-id");
        args['teacher_id'] = teacher_id;
        var begin = $.trim($("#trade_begin").val());
        args['begin'] = begin;
        var end = $.trim($("#trade_end").val());
        args['end'] = end;
        var kw = {};
        for(var k in args){
            var v = args[k];
            if(v === undefined || v === ""){
               // nothing...
            }else{
                 kw[k] = v;
            }
        }
        var url = build_url(location.pathname, kw);
        console.log(url);
        location.href = url;
    };

    $("#filter_info").click(function(){
        filter_info();
    });

    // 清除模态框残留信息
    var clear_modal = function(){
        $(".modal_outer .current_value").text("").attr("data-id", "");
        $(".modal_outer .my_input input").val("");
        $("#submit_task").attr("data-id", "");
    };

    // 弹出模态框
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            alert("功能尚未实现...");
        });
    });


    // 关闭模态框
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });


    // 模态框提交按钮的事件
    $("#submit_task").click(function(){
        var product_id = select_success();
        var plan_number = parseInt($.trim($("#plan_number").val()));
        var batch_sn = $.trim($("#batch_sn").val());
        if(product_id === ""){
            alert("请选择产品种类");
            return false;
        }
        else if(isNaN(plan_number)){
            alert("计划生产数量必须是数字");
            return false;
        }
        else if(batch_sn === ""){
            alert("任务名称必须");
            return false;
        }
        else{
            var args = {
                "batch_sn": batch_sn,
                "product_id": product_id,
                "plan_number": plan_number
            };
            var text = $.trim($(".modal_outer .modal_title").text());
            if(text.indexOf("编辑") !== -1){
                args['type'] = "edit";
                var _id = $("#submit_task").attr("data-id");
                args['_id'] = _id;
            }
            else{
                args['type'] = "add";
            }
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("操作成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
    });

    // 选择器点击事件
    select_value = function($obj){
        var t_name = $.trim($obj.text());
        var t_id = $.trim($obj.attr("data-id"));
        var $current_value = $obj.parents(".my_input:first").find(".current_value");
        $current_value.text(t_name).attr("data-id", t_id);
    };

    /*删除任务*/
    $("#delete_task").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
            "ids": JSON.stringify(d)
        };
        var p = confirm("删除已开始的任务可能导致相关作业无法同步,你确定吗!");
        if(p){
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
        else{
            // ...
        }
    });

    /*全选事件*/
    $("#check_all").click(function(){
        var checked = $("#check_all:checked").length === 1? true: false;
        if(checked){
            $(".table_outer .select >input[type='checkbox']").prop("checked", true);
        }
        else{
            $(".table_outer .select >input[type='checkbox']").prop("checked", false);
        }
    });

    // 翻页事件
    PageHandler();

});