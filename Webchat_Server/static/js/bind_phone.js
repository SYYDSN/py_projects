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

// end!
});