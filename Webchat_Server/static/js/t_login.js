$(function(){
    // 点击清除警告框
    $("input").focus(function(){$(this).removeClass("warning")});

    $("#password").keyup(function(event){
        console.log(event);
        if(event.keyCode == 13 && validate_phone($.trim($("#phone").val())) && $.trim($("#password").val()) != ""){
             $("#btn_login").click();
        }
    });

    // 登录
    $("#btn_login").click(function(){
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
            var ref = get_url_arg("ref");
            if(ref != undefined){
                args['ref'] = ref
            }
            $.post("/teacher/login.html", args, function(resp){
                var resp = JSON.parse(resp);
                var status = resp['message'];
                if(status != "success"){
                    $.alert(status, function(){return false;});
                }
                else{
                    var ref = resp['ref'];

                    // location.href = ref == undefined? "/teacher/process_case.html": ref;
                    location.href = ref == undefined? "/teacher/html/positions.html": ref;
                }
            });
        }
    });
// end !!!
});