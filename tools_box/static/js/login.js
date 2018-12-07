/**
 * Created by walle on 2017/1/28.
 */
$(function () {
    $(".content-r form input[type='password']").attr("test","aaa");
    var flag = true;
    $(".content-r form i").click(function(){
        if(flag){
            $(".content-r form input[type='password']").css("display",'none');
            $(".content-r>input").css("display","block");
            $(".content-r>input").attr("test","aaa");
            $(".content-r form input[type='password']").removeAttr("test");
            $(".content-r>input").val($(".content-r form input[type='password']").val());
            $(this).attr("class","iconfont icon-dengluzhuce-yanjingmimabukekan");
            flag = false;
        }else {
            $(".content-r form input[type='password']").css("display",'block');
            $(".content-r>input").css("display","none");
            $(".content-r>input").removeAttr("test");
            $(".content-r form input[type='password']").attr("test","aaa");
            $(".content-r form input[type='password']").val($(".content-r>input").val());
            $(this).attr("class","iconfont icon-dengluzhuce-yanjingmimakekan");
            flag = true;
        }
    })
    // 提交前检查表单
    function check_form() {
        if ($.trim($("#user_name").val()) == "") {
            $(".name_error").html("用户名不能为空");
            $("#submit_btn").removeAttr("disabled");
            return false;
        }
        else if ($(".user_password[test='aaa']").val() == 0 || $(".user_password[test='aaa']").val().length < 6) {
            $(".name_error").html("");
            $(".password_error").html("密码长度至少6位");
            $("#submit_btn").removeAttr("disabled");
            return false;
        }
        else {
            return true;
        }
    }

     $("#user_name").on('blur', function () {
        if($(this).val().trim() === ""){
            $(".name_error").html("用户名不能为空");
        }else{
            $(".name_error").html("");
        }
    })
    $('.user_password').on('blur', function () {
        if($(".user_password[test='aaa']").val() < 6){
            $(".password_error").html("密码长度至少6位");
        }else{
            $(".password_error").html("");
        }
    })
    // 绑定按钮
    // $("#phone,#password,#sms_code").keydown(function(){return false;});
    bind_enter_event($("#user_name"), $(".user_password"));
    bind_enter_event($(".user_password"), $("#submit_btn"));

    // 打开页面时清除表单的值
    // $("#handler_name,#handler_password").val("");


    // 提交事件
    $("#submit_btn").removeAttr("disabled");
    $("#submit_btn").click(function () {
        if($(".user_password[test='aaa']").val().trim().length >= 6){
            $(".password_error").html("");
        }else{
          $(".password_error").html("密码长度至少6位");
        }
        if (check_form()) {
            var user_name = $.trim($("#user_name").val());
            var user_password = $.md5($(".user_password[test='aaa']").val().trim());
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
            $.post("/manage/login", args, function (data) {
                 $("#submit_btn").removeAttr("disabled");
                 var data = JSON.parse(data);
                if (data['message'] != 'success') {

                    $(".password_error").html(data['message']);
//                    location.reload();
                }
                else {
                    // 登录成功
                    $("#handler_name,#handler_password").val("");
                    location.href = "/manage/index";
                }
            });
        }
    });


    //end!
});
