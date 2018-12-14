$(function(){
    var time_out = null;
    var show_mes = function(obj){
        /*
        * 显示警告消息
        * params obj: 一个jquery对象, 是显示消息的div
        * */
        if(time_out){
            clearTimeout(time_out);
        }else{}
        obj.fadeTo(400, 1, function(){
            time_out = setTimeout(function(){
                obj.fadeTo(800, 0);
            }, 3000);
        });
    };

    // 提交登录事件
    $("#sub_btn").click(function(){
        var user_name = $.trim($("#user_name").val());
        var password = $.trim($("#password").val());

        if(user_name === ""){
            show_mes($("#name_error"));
            return false;
        }
        else if(password === ""){
            show_mes($("#pwd_error"));
            return false;
        }
        else{
            var args = {
                "user_name": user_name,
                "password": $.md5(password)
            };
            var url = "/manage/login";
            $.post(url, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    var r = document.referrer;
                    var u = r === ""? "/manage/trade_history": r;
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