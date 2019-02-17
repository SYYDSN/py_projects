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
        minView: 0,  // 2不显示小时和分
        startView: 2,
        autoclose: true,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd hh:ii:ss",
    });

    // 根据用户选择的条件过滤信息
    var filter_info = function(){
        var args = get_url_arg_dict();
        // 胜场/负场
        var only_win = $(".only_win .current_value").attr("data-id");
        args['only_win'] = only_win;
        // 离场/持仓
        var case_type = $(".select_type .current_value").attr("data-id");
        args['case_type'] = case_type;
        // 选择老师
        var teacher_id = $(".select_teacher .current_value").attr("data-id");
        args['teacher_id'] = teacher_id;
        // 开始日期
        var begin = $.trim($("#trade_begin").val());
        args['begin'] = begin;
        // 结束日期
        var end = $.trim($("#trade_end").val());
        args['end'] = end;
        var kw = {};
        for(var k in args){
            var v = args[k];
            if(v === undefined || v === ""){
               // nothing...
            }
            else if(k === "page"){
                kw[k] = 1;
            }
            else{
                 kw[k] = v;
            }
        }
        var url = build_url(location.pathname, kw);
        console.log(url);
        location.href = url;
    };

    // 查询按钮点击事件
    $("#filter_info").click(function(){
        filter_info();
    });

    // 根据url参数重置所有选择器状态
    (function(){
        var kw = get_url_arg_dict();  // 生成url的参数字典
        // 胜场/负场
        var only_win = kw['only_win'];
        if(only_win !== undefined && only_win !== ""){
            var $values = $(".values li");
            $values.each(function(){
                var $li = $(this);
                var key = $.trim($li.attr("data-id"));
                if(key === only_win){
                    $(".only_win .current_value").attr("data-id", key).text($.trim($li.text()));
                }
            });
        }else{}
        // 离场/持仓
        var case_type = kw['case_type'];
        if(case_type !== undefined && case_type !== ""){
            var $types = $(".types li");
            $types.each(function(){
                var $li = $(this);
                var key = $.trim($li.attr("data-id"));
                if(key === case_type){
                    $(".select_type .current_value").attr("data-id", key).text($.trim($li.text()));
                }
            });
        }else{}
        // 选择老师
        var teacher_id = kw['teacher_id'];
        if(teacher_id !== undefined && teacher_id !== ""){
            var $ts = $(".teachers li");
            $ts.each(function(){
                var $li = $(this);
                var key = $.trim($li.attr("data-id"));
                if(key === teacher_id){
                    $(".select_teacher .current_value").attr("data-id", key).text($.trim($li.text()));
                }
            });
        }else{}
        // 开始日期
        var begin = kw['begin'];
        if(begin !== undefined && begin !== ""){
            $("#trade_begin").val(begin);
        }else{}
        // 结束日期
        var end = kw['end'];
        if(end !== undefined && end !== ""){
            $("#trade_end").val(end);
        }else{}
    })();

    // 下拉菜单li选择事件
    $(".dropdown > ul > li").each(function(){
        var $this = $(this);
        $this.click(function(){
            var text = $.trim($this.text());
            $this.parents(".dropdown").first().find(".current_value").text(text);
        });
    });

    // 清除模态框残留信息
    var clear_modal = function(){
        $(".modal_outer .current_value").text("").attr("data-id", "");
        $(".modal_outer .my_input input").val("");
        $("#submit_task").attr("data-id", "");
    };

    // 弹出编辑交易模态框
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var $tr = $this.parents("tr").first();
            $(".trade_modal_outer .modal_mid").attr("data-id", $.trim($this.attr("data-id")));
            $("#teacher").val( $.trim($tr.find(".teacher").text()));
            $("#direction").text( $.trim($tr.find(".direction").text()));
            $("#product").text( $.trim($tr.find(".product_name").text()));
            $("#enter_time").val( $.trim($tr.find(".enter_time").attr("data-val")));
            $("#enter_price").val( $.trim($tr.find(".enter_price").text()));
            $("#exit_time").val( $.trim($tr.find(".exit_time").attr("data-val")));
            $("#exit_price").val( $.trim($tr.find(".exit_price").text()));
            $(".trade_modal_outer").css("display", "flex");
        });
    });


    // 关闭模态框
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });


    // 模态框提交按钮的事件
    $("#submit_trade").click(function(){
        var _id = $.trim($(".trade_modal_outer .modal_mid").attr("data-id"));
        var product = $.trim($("#product").text());
        var direction = $.trim($("#direction").text());
        var teacher_name = $.trim($("#teacher").val());
        var enter_time = $.trim($("#enter_time").val());
        var enter_price = $.trim($("#enter_price").val());
        var exit_time = $.trim($("#exit_time").val());
        var exit_price = $.trim($("#exit_price").val());

        var args = {
            "type": "edit",
            "_id": _id,
            "teacher_name": teacher_name,
            "product": product,
            "direction": direction,
            "enter_time": enter_time,
            "enter_price": enter_price,
            "exit_time": exit_time,
            "exit_price": exit_price,
        };
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

    });

    // 选择器点击事件
    select_value = function($obj){
        var t_name = $.trim($obj.text());
        var t_id = $.trim($obj.attr("data-id"));
        var $current_value = $obj.parents(".my_input:first").find(".current_value");
        $current_value.text(t_name).attr("data-id", t_id);
    };

    /*反转交易*/
    $("#reverse_trade").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "reverse",
            "ids": JSON.stringify(d)
        };
        var p = confirm("反转交易方向可能会对关联的数据造成影响,你确定吗!");
        if(p){
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("反转成功");
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

    /*删除交易*/
    $("#delete_trade").click(function(){
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
        var p = confirm("删除交易可能会对关联的数据造成影响,你确定吗!");
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