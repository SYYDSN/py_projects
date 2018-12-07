$(function(){
    var flag = true;

    var timerId = null;
    var falg = true;
    $(".form span").on('click',function(){
        if(falg){
          var num = 60;
          falg = false;
          INTERVAL();
          timerId = window.setInterval(INTERVAL,1000)
          function INTERVAL(){
            $(".form span").html((num--) + "秒后可再次发送验证码");
            if(num < 0){
              falg = true;
              clearInterval(timerId);
              $(".form span").html("获取验证码");
            }
          }
        }
      })
    $(".content-r .form i").click(function() {
        if(flag){
            $(".content-r .form input[type='password']").css("display",'none');
            $(".content-r>input").css("display","block");
            $(".content-r>input").val($(".content-r .form input[type='password']").val());
            $(this).attr("class","iconfont icon-dengluzhuce-yanjingmimabukekan");
            flag = false;
        }else {
            $(".content-r .form input[type='password']").css("display",'block');
            $(".content-r>input").css("display","none");
            $(".content-r .form input[type='password']").val($(".content-r>input").val());
            $(this).attr("class","iconfont icon-dengluzhuce-yanjingmimakekan");
            flag = true;
        }
    })
    $("#submit_btn").click(function () {
        var phone_num = $("#phone_num").val().trim();
        var sms_code = $(".sms").val().trim();
        var user_password = $(".password").val().trim();
        $("#phone_num").val("");
        $(".sms").val("");
        $(".password").val("");
        if(validate_phone(phone_num)){
                var args = {
                    phone_num : phone_num,
                    sms_code : sms_code,
                    user_password : user_password
                }
                $.post("/manage/register",args, function (data) {
                    console.log(JSON.parse(data))
                })
        }else {
            alert("手机号码格式不正确")
        }


    })
})