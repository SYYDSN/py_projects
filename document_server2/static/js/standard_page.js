$(function(){
    // 调整高度
    function resize(){
        var height = $(window).height();
        console.log(height);
        $(".middle_outer,.side_left,.side_right").css("min-height", height - 90);
    }
    resize();

    $(window).resize(function(){
        resize();
    });

    /*
    * 一级导航栏,收起别人的子导航,展开自己的子导航的函数
    * */
    var click_nav = function($dom){
        // $dom是nav类的jquery对象
        var sub = $dom.next();
        $(".plus_sign").removeClass("fa-minus-square");
        $(".plus_sign").addClass("fa-plus-square");
        var sub_navs = $(".left_nav .sub_nav");
        if(sub_navs.length === 1){
            sub.slideDown();
        }
        else{
            $(".left_nav .sub_nav").not(sub).slideUp(300, 'swing', function(){
                var icon = $dom.find(".plus_sign");
                icon.removeClass('fa-plus-square');
                icon.addClass('fa-minus-square');
                sub.slideDown();
            });
        }
    };

    /*
    * 一级导航栏点击事件,
    * */
    $(".left_nav .nav").each(function(){
        var $this = $(this);
        $this.click(function(){
            click_nav($this);
        });
    });

    /*
    * 二级导航栏当前页匹配效果,会在当前页匹配的导航按钮的左侧加一个蓝色
    * */
    (function(){
        var path = location.pathname;
        var navs = $(".left_nav .nav_name");
        navs.each(function(){
            var $this = $(this);
            var temp = $this.attr("href");
            if(temp === path){
                $this.addClass("active_nav_inner");
                var nav = $this.parents(".sub_nav:first").prev();
                click_nav(nav);
            }
            else{
                $this.removeClass("active_nav_inner");
            }
        });
    })();

    // 弹出修改密码模态框
    $("#change_pw").click(function(){
        $(".modal_outer_pw").css("display", "flex");
    });

    // 关闭修改密码模态框
    $("#modal_outer_pw").click(function(){
        $(".modal_outer_pw input").val("");
        $(".modal_outer_pw").css("display", "none");
    });

    // 提交修改密码请求.
    $("#submit_change_pw").click(function(){
        var _id = $.trim($(this).attr("data-id"));
        var pw_old = $.trim($("#u_password_old").val());
        var pw_n1 = $.trim($("#u_password_new1").val());
        var pw_n2 = $.trim($("#u_password_new2").val());
        if(pw_n1 !== pw_n2){
            alert("两次输入的新密码必须相同!");
            return false;
        }
        else{
            var args = {
                "_id": _id,
                "type": "change_pw",
                "pw_old": $.md5(pw_old),
                "pw_n1": $.md5(pw_n1),
                "pw_n2": $.md5(pw_n2)
            };
            $.post("/self_info", args, function(resp){
                var json = JSON.parse(resp);
                console.log(json);
                var status = json['message'];
                if(status === "success"){
                    alert("修改密码成功,请重新登录");
                    location.href = "/login";
                }
                else{
                    alert(status);
                }
            });
        }
    });

    // 弹出修改昵称模态框
    $("#change_nick").click(function(){
        $(".modal_outer_nick").css("display", "flex");
    });

    // 关闭修改昵称模态框
    $("#modal_outer_nick").click(function(){
        $(".modal_outer_nick input").val("");
        $(".modal_outer_nick").css("display", "none");
    });

    // 提交修改昵称请求.
    $("#submit_change_nick").click(function(){
        var _id = $.trim($(this).attr("data-id"));
        var nick_name = $.trim($("#nick_name_new").val());
        var args = {
            "_id": _id,
            "type": "change_nick",
            "nick_name": nick_name
        };
        $.post("/self_info", args, function(resp){
            var json = JSON.parse(resp);
            console.log(json);
            var status = json['message'];
            if(status === "success"){
                alert("修改昵称成功");
                location.reload();
            }
            else{
                alert(status);
            }
        });
    });

});