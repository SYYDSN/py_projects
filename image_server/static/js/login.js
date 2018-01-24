/**
 * Created by walle on 2017/1/28.
 */
$(function () {

    // 提交前检查表单
    function check_form() {
        if ($.trim($("#user_name").val()) == "") {
            alert("用户名错误");
            $("#submit_btn").removeAttr("disabled");
            return false;
        }
        else if ($.trim($("#user_password").val()) == 0 || $.trim($("#user_password").val()).length < 6) {
            alert("密码至少6位");
            $("#submit_btn").removeAttr("disabled");
            return false;
        }
        else {
            return true;
        }
    }

    // 绑定按钮
    // $("#phone,#password,#sms_code").keydown(function(){return false;});
    bind_enter_event($("#user_name"), $("#user_password"));
    bind_enter_event($("#user_password"), $("#submit_btn"));

    // 打开页面时清除表单的值
    // $("#handler_name,#handler_password").val("");


    // 提交事件
    $("#submit_btn").removeAttr("disabled");
    $("#submit_btn").click(function () {
        if (check_form()) {
            var user_name = $.trim($("#user_name").val());
            var user_password = $.md5($.trim($("#user_password").val()));
            // var referrer = document.referrer;
            var args = {
                "user_name": user_name, "user_password": user_password
            };
            $("#submit_btn").prop("disabled","disabled");
            setTimeout(function(){
                var prop = $("#submit_btn").prop("disabled");
                if(prop){
                    console.log("yes");
                    $("#submit_btn").removeProp("disabled");
                }
            }, 1200);
            $.post("/login", args, function (data) {
                 $("#submit_btn").removeAttr("disabled");
                 var data = JSON.parse(data);
                if (data['message'] != 'success') {
                    alert(data['message']);
                    location.reload();
                }
                else {
                    // 登录成功
                    $("#handler_name,#handler_password").val("");
                    location.href = "/upload_image";
                }
            });
        }
    });


    //end!
});
