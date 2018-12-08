$(function(){
    /*清除模态框输入残留*/
    var clear_modal = function(){
        $(".modal_title").attr("data-current-id", "");
        $(".modal_mid .line input").val("");
    };

    /*关闭摩态框按钮*/
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    /*填充信息到生产线模态框*/
    var fill_line_info = function(id_str){
        console.log(id_str);
        var $tr = $("#" + id_str);
        var line_name = $.trim($tr.find(".line_name span").text());
        $(".modal_outer_line .line_name").val(line_name);
        $(".modal_outer_line .modal_title").attr("data-id", id_str);
    };

    /*填充信息到主控板模态框*/
    var fill_control_info = function(id_str, ip, line_id){
        $(".modal_outer_control ul li").each(function(){
            var temp = $.trim($(this).attr("data-id"));
            if(temp === line_id){
                $(this).click();
            }
        });
        $(".modal_outer_control .control_ip").val(ip);
        $(".modal_outer_control .submit_btn").attr("data-id", id_str);
    };

    /*填充信息到执行板模态框*/
    var fill_execute_info = function(c_id, ip, key){
        $(".modal_outer_execute ul li").each(function(){
            var temp = $.trim($(this).attr("data-id"));
            if(temp === c_id){
                $(this).click();
            }
        });
        $(".modal_outer_execute .execute_ip").val(ip).attr("data-key", key);
        $(".modal_outer_execute .submit_btn").attr("data-old-id", c_id);
    };

    /*弹出生产线模态框函数*/
    pop_modal_line = function($obj){
        clear_modal();
        var text = $.trim($obj.text());
        var title = "添加生产线";
        if(text === "编辑"){
            title = "编辑生产线";
            var _id = $obj.attr("data-id");
            fill_line_info(_id);
        }
        else{
            // nothing...
        }
        $(".modal_outer_line .modal_title").text(title);
        $(".modal_outer_line").css("display", "flex");
    };

    /*弹出主控板模态框*/
    $(".pop_modal_control, .edit_control").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添加主控板";
            if(text === "编辑"){
                title = "编辑主控板";
                var _id = $this.attr("data-id");
                var line_id = $this.attr("data-line-id");
                var ip = $.trim($this.parents(".control_item:first").find(".control_ip").text());
                fill_control_info(_id, ip, line_id);
            }
            else{
                // nothing...
            }
            $(".modal_outer_control .modal_title").text(title);
            $(".modal_outer_control").css("display", "flex");
        });
    });

    /*弹出控制板模态框*/
    $(".pop_modal_execute, .edit_execute").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添执行板";
            if(text === "编辑"){
                title = "编辑执行板";
                var control_id = $this.attr("data-id");
                var key = $this.attr("data-key");
                var ip = $.trim($this.parents(".execute_item:first").find(".execute_ip").text());
                fill_execute_info(control_id, ip, key);
            }
            else{
                // nothing...
            }
            $(".modal_outer_execute .modal_title").text(title);
            $(".modal_outer_execute").css("display", "flex");
        });
    });

    // 编辑生产线信息
    $(".edit_line").each(function(){
        var $this = $(this);
        var _id = $.trim($this.attr("data-id"));
        fill_line_info(_id);
    });

    /*弹出框提交按钮事件*/
    $(".submit_btn").each(function(){
        var $this = $(this);
        $this.click(function(){
            var args = {};
            var title = $.trim($this.parents(".modal_outer:first").find(".modal_title").text());
            var type = "line";
            var operate = title.indexOf("编辑") !== -1? "edit": "add";
            args['operate'] = operate;
            if(title.indexOf("主控") !== -1){
                // 主控板操作
                type = "control";
                var line_id = $.trim($(".modal_outer_control .current_value").attr("data-id"));
                args['line_id'] = line_id;
                if(operate === "edit"){
                    var c_id = $.trim($this.attr("data-id"));
                    args['_id'] = c_id;
                }
                else{
                    // nothing...
                }
                var control_ip = $.trim($(".modal_outer_control .control_ip").val());
                args['ip'] = control_ip;
                if(line_id === ""){
                    alert("生产线信息不能为空");
                    return false;
                }
                else if(control_ip === ""){
                    alert("主控板ip地址不能为空");
                    return false;
                }
                else{}
            }
            else if(title.indexOf("执行") !== -1){
                type = "execute";
                // 执行板操作
                args['key'] = $.trim($(".modal_outer_execute .execute_ip").attr("data-key"));
                var ip = $.trim($(".modal_outer_execute .execute_ip").val());
                args['ip'] = ip;
                var _id = $.trim($(".modal_outer_execute .current_value").attr("data-id"));
                args['_id'] = _id;
                if(operate === "edit"){
                    var old_id = $.trim($(".modal_outer_execute .submit_btn").attr("data-old-id"));
                    args['old_id'] = old_id;
                }
                else{
                    // nothing...
                }
                if(_id === ""){
                    alert("主控板信息不能为空");
                    return false;
                }
                else if(ip === ""){
                    alert("执行板ip地址不能为空");
                    return false;
                }
                else{}
            }
            else{
                // 生产线操作
                var _id = $.trim($(".modal_outer_line .modal_title").attr("data-id"));
                if(operate === "edit"){
                    args['_id'] = _id;
                }
                else{
                    // nothing...
                }
                var line_name = $.trim($(".modal_outer_line .line_name").val());
                if(line_name ===  ""){
                    alert("生产线名称必须");
                    return false;
                }
                else{
                    args['line_name'] = line_name;
                }
            }
            args['type'] = type;
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("操作成功");
                    location.reload();
                }
                else{
                    alert(status);
                    $(".close_medal").click();
                }
            });
        });
    });

    // 模态框的下拉选择菜单
    $(".my_input ul li").each(function(){
        var $this = $(this);
        $this.click(function(){
            var _id = $.trim($this.attr("data-id"));
            var text = $.trim($this.text());
            $this.parents(".my_input:first").find(".current_value").text(text).attr("data-id", _id);
        });
    });

    // 删除执行板
    $(".delete_execute").each(function(){
        var $this = $(this);
        $this.click(function(){
            var key = $.trim($this.attr("data-key"));
            var _id = $.trim($this.attr("data-id"));
            var args = {
                "type": "execute",
                "operate": "delete",
                "_id": _id,
                "key": key,
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }
                else{
                    alert(status);
                }
            });
        });
    });

    // 删除主控板
    $(".delete_control").each(function(){
        var $this = $(this);
        $this.click(function(){
            var _id = $.trim($this.attr("data-id"));
            var args = {
                "type": "control",
                "operate": "delete",
                "_id": _id
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }
                else{
                    alert(status);
                }
            });
        });
    });


    /*删除生产线*/
    $("#delete_line").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "line",
            "operate": "delete",
            "ids": JSON.stringify(d)
        }
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