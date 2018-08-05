$(function(){
    // 发送短信事件
    $("#send_sms").click(function(){
        var phone = $.trim($("#phone").val());
        if(validate_phone(phone)){
            var args = {"phone": phone};
            $.post("/user/sms/send", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status == "success"){
                    alert("短信已发送");
                }
                else{
                    alert(status);
                }
            });
        }
        else{
            alert("错误的手机号码: " + phone);
            return false;
        }
    });

    // 提交短信验证
    $("#submit").click(function(){
        var phone = $.trim($("#phone").val());
        if(validate_phone(phone)  || phone != ""){
            var code = $.trim($("#code").val());
            if(isNaN(code)){
                alert("验证码填写错误");
            }
            else{
                var args = {"phone": phone, "code": code};
                $.post("/user/sms/check", args, function(resp){
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    if(status == "success"){
                        alert("绑定成功");
                        location.href = "/user/html/user.html";
                    }
                    else{
                        alert(status);
                    }
                });
            }
        }
        else{
            alert("错误的手机号码: " + phone);
            return false;
        }
    });

    // 载入页面时检查用户是否已绑定过手机？
    (function(){
        var my_phone = $.trim($("#my_phone").text());
        console.log(my_phone)
        console.log(isNaN(my_phone))
        if(isNaN(my_phone) || my_phone == ""){
            // nothing....
        }
        else{
            // alert(my_phone);
            alert("你已绑定过手机，无需再次绑定");
            location.href = "/user/html/user.html";
        }
    })();

// end!
});