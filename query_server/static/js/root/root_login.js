$(function(){
    // 提交登录事件
    $("#sub_btn").click(function(){
        var user_name = $.trim($("#user_name").val());
        var password = $.trim($("#password").val());

        if(user_name === ""){
            alert("用户名不能为空!");
            return false;
        }
        else if(password === ""){
            alert("密码不能为空!");
            return false;
        }
        else{
            var args = {
                "user_name": user_name,
                "password": $.md5(password)
            };
            var url = "/root/login";
            $.pop_alert("正在登录,请稍后...");
            $.post(url, args, function(resp){
                $.close_alert();
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    var u = "/root/common/manage_user";
                    location.href = u;
                }
                else{
                    alert(status);
                }
            });
        }
    });

    // 密码输入框回车事件.
    $("#password").keydown(function(event){
        var key = event.keyCode;
        if(key === 13){
            var user_name = $.trim($("#user_name").val());
            var password = $.trim($("#password").val());
            if(user_name !== "" && password !== ""){
                $("#sub_btn").click();
            }
            else{
                // nothing...
            }
        }
        else{
            // nothing...
        }
    });

});