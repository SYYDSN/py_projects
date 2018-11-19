$(function(){
    /*填充用户信息到摩态框*/
    var fill_user_info = function(user_id){
        var tr = $("#" + user_id);
        $("#modal_title").attr("data-current-id", user_id);
        var nick_name = $.trim(tr.find(".nick_name").text());
        var user_name = $.trim(tr.find(".user_name").text());
        $("#user_name").val(user_name);
        $("#nick_name").val(nick_name);
        var role_id = $.trim(tr.find(".role").attr("data-id"));
        var role_name = $.trim(tr.find(".role").text());
        $(".current_role").text(role_name).attr("data-role-id", role_id);
        var status = $.trim(tr.find(".status").attr("data-status"));
        $(".my_status .status_value").each(function(){
            var $this = $(this);
            if($.trim($this.attr("data-value")) === status){
                $this.addClass("select_status");
            }
            else{
                $this.removeClass("select_status");
            }
        });
    };

    /*清除模态框输入残留*/
    var clear_modal = function(){
        $("#modal_title").attr("data-current-id", "");
        $(".modal_mid .line input").val("");
    };

    /*添加用户按钮*/
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添加用户";
            if(text === "编辑"){
                title = "编辑用户";
                var _id = $this.attr("data-id");
                fill_user_info(_id);
            }
            else{
                // nothing...
            }
            $("#modal_title").text(title);
            $(".modal_outer").css("display", "flex");
        });
    });

    /*关闭摩态框按钮*/
    $("#close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    /*添加角色*/
    var add = function(){
       var nick_name = $.trim($("#nick_name").val());
       var user_name = $.trim($("#user_name").val());
       var pw1 = $.trim($("#u_password1").val());
       var pw2 = $.trim($("#u_password2").val());
       var role_id = $.trim($(".current_role").attr("data-role-id"));

       if(nick_name === ""){
           alert("姓名不能为空");
           return false;
       }
       else if(user_name === ""){
           alert("账户不能为空");
           return false;
       }
       else if(pw1 === "" || pw2 === ""){
           alert("密码必须");
           return false;
       }
       else if(pw1 !== pw2){
           alert("两次输入的密码必须一致");
           return false;
       }
       else if(role_id === ""){
           alert("工作组不能为空!");
           return false;
       }
       else{
           var args = {
               "nick_name": nick_name,
               "user_name": user_name,
               "role_id": role_id,
               "status": parseInt($.trim($(".select_status").attr("data-value"))),
               "password": $.md5(pw1),
               "type": "add"
           };
           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['message'];
               if(status === "success"){
                   alert("添加成功!");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       }
    };

    /*编辑用户事件*/
    var edit = function(c_id){
        var nick_name = $.trim($("#nick_name").val());
       var user_name = $.trim($("#user_name").val());
       var pw1 = $.trim($("#u_password1").val());
       var pw2 = $.trim($("#u_password2").val());
       var role_id = $.trim($(".current_role").attr("data-role-id"));

       if(nick_name === ""){
           alert("姓名不能为空");
           return false;
       }
       else if(user_name === ""){
           alert("账户不能为空");
           return false;
       }
       else if(pw1 !== pw2){
           alert("两次输入的密码必须一致");
           return false;
       }
       else if(role_id === ""){
           alert("工作组不能为空!");
           return false;
       }
       else{
           var args = {
               "_id": c_id,
               "nick_name": nick_name,
               "user_name": user_name,
               "role_id": role_id,
               "status": parseInt($.trim($(".select_status").attr("data-value"))),
               "type": "edit"
           };
           if(pw1 === ""){
               // 置空表示不修改密码
           }
           else{
               args['password'] = $.md5(pw1);
           }

           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['message'];
               if(status === "success"){
                   alert("修改成功!");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       }
    };

    /*弹出框提交按钮事件*/
    $("#submit").click(function(){
        var current_id = $.trim($("#modal_title").attr("data-current-id"));
        if(current_id === ""){
            // 添加角色
            add();
        }
        else{
            // 编辑角色
            edit(current_id);
        }
    });

    /*模态框选择角色事件*/
    $(".select_role").each(function(){
        var $this = $(this);
        $this.click(function(){
            var role_id = $this.attr("data-id");
            var role_name = $.trim($this.text());
            $(".current_role").attr("data-role-id", role_id).text(role_name);
        });
    });

    /*模态框选择用户状态事件*/
    $(".status_value").each(function(){
        var $this = $(this);
        $this.click(function(){
            $(".status_value").not($this).removeClass("select_status");
            $this.addClass("select_status");
        });
    });

    /*删除用户*/
    $("#delete_user").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
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

});