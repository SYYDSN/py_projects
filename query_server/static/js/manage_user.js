$(function(){
    /*填充用户信息到摩态框*/
    var fill_user_info = function(user_id){
        var tr = $("#" + user_id);
        var nick_name = $.trim(tr.find(".nick_name").text());
        var user_name = $.trim(tr.find(".user_name").text());
        $("#user_name").val(user_name);
        $("#nick_name").val(nick_name);
    };

    /*添加用户按钮*/
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
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
       else{
           var args = {
               "nick_name": nick_name,
               "user_name": user_name,
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

    /*弹出框提交按钮事件*/
    $("#submit").click(function(){
        var current_id = $.trim($("#modal_title").attr("data-current-id"));
        if(current_id === ""){
            // 添加角色
            add();
        }
        else{
            // 编辑角色
            edit();
        }
    });

});