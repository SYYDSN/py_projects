$(function(){
    // 用户名输入框回车事件
    $("#user_name").keydown(function(event){
        let code = event.keyCode;
        if(code === 13){
            $("#user_password").focus();
        }
    });

    // 用户密码输入框回车事件
    $("#user_password").keydown(function(event){
        let code = event.keyCode;
        if(code === 13){
            $("#submit_login").focus();
        }
    });

    // 登陆按钮事件
    $("#submit_login").click(function(){
        let user_name = $.trim($("#user_name").val());
        let user_password = $.trim($("#user_password").val());
        if(user_name === ""){
            alert("用户名不能为空");
        }
        else if(user_password === ""){
            alert("密码不能为空");
        }
        else{
            let args = {
                "user_name": user_name,
                "user_password": $.md5(user_password)
            };
            $.post("/web/login", args, function(resp){
                let json = JSON.parse(resp);
                let mes = json['message'];
                if(mes === "success"){
                    // 登录成功,跳转
                    location.href = "/web/drivers?index=1"
                }
                else{
                    alert(mes);
                    return false;
                }
            });
        }
    });

// end !!!
});