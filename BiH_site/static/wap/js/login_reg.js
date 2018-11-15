var validate_phone = function (phone) {
    /*
     * 检查手机号码是否合法?合法返回真,
     * */
    var myreg = /^(((1[3-9][0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
    if (myreg.test(phone)) {
        return true;
    }
    else {
        return false;
    }
};


$("#v_container").click(function () {
    // 注册框点击发送短信按钮事件.
    var phone = $.trim($("#iphone").val());
    if (validate_phone(phone)) {
        var url = "/sms/get";
        var args = {"phone": phone, "csrf_token": $("#csrf_token").val()};
        $.post(url, args, function (resp) {
            var resp = JSON.parse(resp);
            var status = resp['message'];
            if (status === "success") {
                alert("短信已发送,请注意查收.");
                return true;

            }
            else {
                alert(status);
                return false;
            }
        });

        var clock = '';
        var nums = 60;
        var col = "#bbb";
        var v_container = document.getElementById("v_container");

        function sendCode() {
            v_container.disabled = true; //将按钮置为不可点击
            v_container.style.background = col; //将按钮置为不可点击
            v_container.value = nums + '秒后可重新获取';
            clock = setInterval(doLoop, 1000); //一秒执行一次
        }

        function doLoop() {
            nums--;
            if (nums > 0) {
                v_container.value = nums + '秒后可重新获取';
            } else {
                clearInterval(clock); //清除js定时器
                v_container.disabled = false;
                v_container.style.background = ""
                v_container.value = '点击发送验证码';
                nums = 60; //重置时间
            }
        }

        sendCode()


    }
    else {
        var str = `手机号码不正确!`;
        alert(str);

        return false;
    }
});

$("#code_input").keydown(function(event){
    // 注册框的短信输入框回车事件
    var code = event.keyCode;
    if(code === 13){
        $("#su_mit").click();
    }
});

$("#su_mit").click(function () {
    /*提交注册信息的函数*/
    var phone = $.trim($("#iphone").val());
    var password = $.trim($("#password").val());
    // var password2 = $.trim($("#password2").val());
    var code = $.trim($("#code_input").val());
    if (phone === "") {

        alert("手机号码不能为空");
        $("#iphone").css({border: "1px solid red"})
        return false;
    }
    else if (!validate_phone(phone)) {
        alert("手机号码不正确");
        $("#iphone").css({border: "1px solid red"})
        return false;

    }
    // else if (password === "" || password !== password2) {
    //     alert("密码不能为空且两次输入的密码必须一致");
    //     $("#password").css({border: "1px solid red"})
    //     $("#password2").css({border: "1px solid red"})
    //     return false;
    // }
    else if (code === "") {
        alert("短信验证码不能为空");
        $("#code_input").css({border: "1px solid red"})
        return false;
    }
    else if (code.length !== 4) {
        alert("短信验证码是4位数字");
        $("#code_input").css({border: "1px solid red"})
        return false;
    }
    else {
        // $("#iphone").css({border:""})
        // $("#password").css({border:""})
        // $("#password2").css({border:""})
        // $("#code_input").css({border:""})
        password = $.md5(password);
        var args = {
            "phone": phone,
            "password": password,
            "code": code,
            "csrf_token": $("#csrf_token").val()
        };
        var url = "/register";
        $.post(url, args, function (resp) {
            var json = JSON.parse(resp);
            var status = json['message'];
            if (status === "success") {
                alert("注册成功!");
                //location.reload();
                location.href="login.html"
                // if(location.href="index_web.html"){
                //     alert(1)
                // }
            }
            else {
                alert(status);
                return false;
            }
        });
    }
});


$("#password3").keydown(function(event){
    // 登录页面,密码输入框回车事件.
    var code = event.keyCode;
    if(code === 13){
        $("#su_mit2").click();
    }
});


$("#su_mit2").click(function () {
    var phone = $.trim($("#iphone2").val());
    var password = $.trim($("#password3").val());
    if (phone === "") {
        alert("账户不能为空!");
        $("#iphone2").css({border: "1px solid red"})
        return false;

    } else if (password === "") {
        alert("密码不能为空!");

        $("#password3").css({border: "1px solid red"})
        return false;
    } else {
        var url = "/login";
        var args = {
            "phone": phone,
            "password": $.md5(password),
            "csrf_token": $("#csrf_token").val()
        };
        $.post(url, args, function (resp) {
            var json = JSON.parse(resp);
            var status = json['message'];
            if (status === "success") {
                console.log("登录成功");
                /*执行登录成功后的函数*/
                //location.reload();
                location.href="index_web.html"

                //判断用户有没有注册和登录成功
                var user_val=iphone.substr(iphone.length-4)+'用户'

                var users=document.getElementById("user")

                users.innerHTML=user_val+'用户'//插入用户的4位数尾号+用户
                if(users.innerHTML == user_val+'用户') {//判断标签里的值和获取的值是否相等
                    alert(1)
                    $("#login").css({display: "none"})//隐藏登录按钮
                    $("#reg").css({display: "none"})//隐藏注册按钮
                    users.style.display="block"//显示用户按钮
                }else {
                    $("#login").css({display: "block"})
                    $("#reg").css({display: "block"})
                    users.style.display="none"
                }
            }
            else {
                alert(status);
                return false;
            }
        });
    }
});





// $(".tiaozhuan").click(function () {
//     //var user = "曹志"
//     location.href = "index_web.html"
//     // var users=document.getElementById("user")
//     // var user_val='曹志'
//     // users.innerHTML=user_val
//
// })
// //判断用户有没有注册和登录成功
// var iphone='18816931927'
// alert(iphone.substr(iphone.length-4)+'用户');
// alert(iphone.substring(1,3));//输出88
//
// var users=document.getElementById("user")
// //console.log(users)
// var user_val='1927'
// users.innerHTML=user_val+'用户'
// //console.log($("#user").innerHTML)
// //var users_value=user_val+'用户'
//
//
// if(users.innerHTML == user_val+'用户') {
//     alert(1)
//     $("#login").css({display: "none"})
//     $("#reg").css({display: "none"})
//     users.style.display="block"
// }else {
//     $("#login").css({display: "block"})
//     $("#reg").css({display: "block"})
//     users.style.display="none"
// }
