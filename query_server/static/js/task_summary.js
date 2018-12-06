$(function(){
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
            var $this = $(this);
            var text = $.trim($this.text());
            var title = "新增生产任务";
            clear_modal();   // 清除模态框残留信息
            if(text.indexOf("编辑") !== -1){
                title = "编辑生产任务";
                var id_str = $.trim($this.attr("data-id"));
                fill_info(id_str);   // 填充信息
            }
            else{}
            $(".modal_title").text(title);
            $(".modal_outer").css("display", "flex");
        });
    });


    // 关闭模态框
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    // 是否四级联动选择框就绪? 就绪返回产品id,不就绪返回空字符串
    var select_success = function(){
        var product_id = "";
        var product_name = $.trim($("#select_product_name .current_value").text());
        var specification = $.trim($("#select_specification .current_value").text());
        var net_contents = $.trim($("#select_net_contents .current_value").text());
        var package_ratio  = $.trim($("#select_package_ratio .current_value").text());
        if(product_name === "" || specification === "" || net_contents === "" || package_ratio === ""){
            console.log("还未选择正确的产品信息!");
        }
        else {
            product_id = $.trim($("#select_package_ratio .current_value").attr("data-id"));
        }
        return product_id;
    };

    // 填充任务信息到模态框
    var fill_info = function(id_str){
        id_str = id_str.startsWith("#")? id_str: "#" + id_str;
        var $tr = $(id_str);
        var task_name = $.trim($tr.find(".task_name").text());
        var product_id  = $.trim($tr.find(".product_info").attr("data-id"));
        var p = $.trim($tr.find(".product_info").text()).split(" ");
        var product_name = p[0];
        var specification = p[1];
        var net_contents = p[2];
        var package_ratio = p[3];
        var plan_number = $.trim($tr.find(".plan_number").text());
        $("#task_name").val(task_name);
        $("#select_product_name .current_value").text(product_name).attr("data-id", product_id);
        $("#select_specification .current_value").text(specification).attr("data-id", product_id);
        $("#select_net_contents .current_value").text(net_contents).attr("data-id", product_id);
        $("#select_package_ratio .current_value").text(package_ratio).attr("data-id", product_id);
        $("#plan_number").val(plan_number);
        var _id = id_str.replace("#","");
        $("#submit_task").attr("data-id", _id);
    };

    // 模态框提交按钮的事件
    $("#submit_task").click(function(){
        var product_id = select_success();
        var plan_number = parseInt($.trim($("#plan_number").val()));
        var task_name = $.trim($("#task_name").val());
        if(product_id === ""){
            alert("请选择产品种类");
            return false;
        }
        else if(isNaN(plan_number)){
            alert("计划生产数量必须是数字");
            return false;
        }
        else if(task_name === ""){
            alert("任务名称必须");
            return false;
        }
        else{
            var args = {
                "task_name": task_name,
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


    // 点击未填充的产品规格选择器的事件
    $("#select_specification .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var product_name = $.trim($("#select_product_name .current_value").text());
            var args = {
                "type": "selector",
                "product_name": product_name
            };
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 点击未填充的产品净含量选择器的事件
    $("#select_net_contents .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 点击未填充的产品包装比例选择器的事件
    $("#select_package_ratio .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var text = $.trim(current_div.prev().find(".current_value").text());
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "net_contents": text, "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 选择器点击事件
    select_value = function($obj){
        var text = $.trim($obj.text());
        var $current_value = $obj.parents(".my_input:first").find(".current_value");
        $current_value.text(text);
        var a_id = $obj.attr("data-id");
        if(a_id !== undefined && a_id !== ""){
            $current_value.attr("data-id", $.trim(a_id));
        }else{
            // nothing...
        }
        $obj.parents(".select_div:first").next().find(".current_value").text("");
        var $ul = $obj.parents("ul:first");
        if($.trim($ul.attr("data-type")) === "product_name"){
            var $next_ul = $("ul[data-type='specification']");
            var args = {"product_name": text, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else if($.trim($ul.attr("data-type")) === "specification"){
            var $next_ul = $("[data-type='net_contents']");
            var product_name = $.trim($("#select_product_name .current_value").text());
            var args = {
                "specification": text,
                "product_name": product_name,
                "type": "selector"
            };
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else if($.trim($ul.attr("data-type")) === "net_contents"){
            var $next_ul = $("[data-type='package_ratio']");
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "net_contents": text, "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else{
            // nothing...
        }
    };

    // 开始任务按钮点击事件
    $(".start_task").each(function(){
        var $this = $(this);
        $this.click(function(){
            var task_id = $.trim($this.attr("data-id"));
            var args = {
                "type": "start_task",
                "_id": task_id
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    alert("任务已下发!");
                    location.reload();
                }
            });
        });
    });

    // 停止任务按钮点击事件
    $(".stop_task").each(function(){
        var $this = $(this);
        $this.click(function(){
            var task_id = $.trim($this.attr("data-id"));
            var args = {
                "type": "stop_task",
                "_id": task_id
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    alert("任务已关闭!");
                    location.reload();
                }
            });
        });
    });

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


});