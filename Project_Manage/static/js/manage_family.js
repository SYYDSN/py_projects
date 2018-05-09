$(function(){
    // 注销登录
    $("#login_out").click(function(){
        $.post("/login_out", function(){
            location.href = "/login";
        });
    });


// end!!!
});