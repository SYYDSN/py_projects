$(function(){
    // 点击清除警告框
    $("input").focus(function(){$(this).removeClass("warning")});

    $("#password").keyup(function(event){
        console.log(event);
        if(event.keyCode === 13){
             $("#btn_login").click();
        }
    });

    // 登录
    $("#btn_login").click(function(){
        try{
            var phone = $.trim($("#phone").val());
            var password = $.trim($("#password").val());
            if(phone.length < 4){
                $.alert("账户错误", function(){$("#phone").addClass("warning")});
            }
            else if(password == ""){
                $.alert("密码不能为空", function(){$("#password").addClass("warning")});
            }
            else{
                var args = {"phone": phone, "password": password};
                var ref = undefined;
                try{
                    ref = get_url_arg("ref");
                }catch(e){
                    console.log(e)
                }
                if(ref != undefined){
                    args['ref'] = ref;
                }
                $.post("/teacher/login.html", args, function(resp){
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if(status != "success"){
                        $.alert(status, function(){return false;});
                    }
                    else{
                        var ref = resp['ref'];

                        location.href = ref == undefined? "/teacher/process_case.html": ref;
                        // location.href = ref == undefined? "/teacher/html/positions.html": ref;
                    }
                });
            }
        }
        catch(e){
            var error = `登录时发生错误 ${e}`;
            console.log(error);
            var kw = {
                "phone": $.trim($("#phone").val()),
                "password": $.trim($("#password").val())
            };
            var now = new Date();
            var error_time = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}.${now.getMilliseconds()}`;
            var args = {
                "args": JSON.stringify(kw),
                "url": "/teacher/login.html",
                "ajax_error_count": 1,
                "error": error,
                "error_time": error_time
            };
            $.post("/teacher/log", args, function(r){
                // 发送出错消息
                try{
                    var a = JSON.parse(r);
                    console.log(a);
                }
                catch(e){
                    console.log(r);
                }
            });
        }
    });
// end !!!
});