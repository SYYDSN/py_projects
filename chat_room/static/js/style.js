// JavaScript Document

$(document).ready(function(){
    //图片轮播slider插件
    $('#demo01').flexslider({animation: "slide",direction:"horizontal",easing:"swing",slideshowSpeed: 30000});//slideshowSpeed是动画间隔时间

	/*头部qq交谈hover*/
	/*
    $("#header_list_qq").hover(function(){
        $(this).find(".qq_menu").show();
    },function(){
        $(this).find(".qq_menu").hide();
    });
    */

    /*高度*/
    $("#container").height($(window).height()-65-20);//整体内容部分高度设定
    $("#container_left ul li").height(parseInt(($("#container").height()-20) / 8));//左侧每个li的高度
    $("#video_div").height(parseInt($("#container").height() - 35 - 20) * 0.7 ) ; //直播室的高度
    $("#scroll_img").height(parseInt($("#container").height() - 35 - 20) * 0.3 ) ; //图片滚动高度
    $(".container_center .scroll_img img").height($("#scroll_img").height());
    $("#chat").height($("#container").height() - 35 - 170-20); //聊天窗口的高度aaaa
    $("#ChatLog").height($("#chat").height() - 20-20); //聊天窗口的高度



    /*窗口变化*/
    $(window).resize(function(){
        /*高度*/
        $("#container").height($(window).height()-65-20);//整体内容部分高度设定
        $("#container_left ul li").height(parseInt(($("#container").height()-20)/ 8));//左侧每个li的高度
        $("#video_div").height(parseInt($("#container").height() - 35 - 20) * 0.7 ) ; //直播室的高度
        $("#scroll_img").height(parseInt($("#container").height() - 35 - 20) * 0.3 ) ; //图片滚动高度
        $(".container_center .scroll_img img").height($("#scroll_img").height());
        $("#chat").height($("#container").height() - 35 - 170-20); //聊天窗口的高度
        $("#ChatLog").height($("#chat").height() - 20-20); //聊天窗口的高度
    });
    //聊天窗口滚动条插件
    $("#ChatLog").niceScroll({
        cursorcolor:"#F0F0F0",
        cursoropacitymax:0.7,
        touchbehavior:false,
        cursorwidth:"5px",
        cursorborder:"0",
        cursorborderradius:"5px"
    });
    //滚动条默认在最底端
    $('#ChatLog').scrollTop( $('#ChatLog')[0].scrollHeight );

    //弹出qq
    /*
    $(".qq_click").click(function(){
       $(this).attr("href","tencent://message/?Menu=yes&amp;uin=800056892&amp;Service=58&amp;SigT=A7F6FEA02730C988C270F5F626B096E510856BB1E738634E78FF172DDB6D36C3CF62BD4DC74388DE139438CB2C8B90BEE416E24BEDD12E8CBAB468C2620A21952E8DDE7CA07AA3EADC834187969E7EA2C297E9CDD6578CB41203AAE5463AB8B912CE9969B6E504612030FF1A4DA0ADB68F47207C1170481B&amp;SigU=30E5D5233A443AB23D54BBDE85B364CDFC362CA5D9D7C90E3A3A2D388873303315A1ADBEA3609EA74C4F8BF8B514F0F4A0781E4460F0544AA9675BF83D5B3F38609BD83CBBCBDD6E");
    });
    */
    //注册弹窗
    $(".register").click(function(){
        $("#pop_register").show();
    });
    $("#pop_register").find(".close").click(function(){
        $("#pop_register").hide();
    });

    //点击账号登录
    $("#dl").click(function(){
       $("#pop_register").hide();
       $("#pop_login").show();
    });
    //点击账号注册
    $("#zc").click(function(){
        $("#pop_register").show();
        $("#pop_login").hide();
    });

    //登录弹窗
    $("#login").click(function(){
        $("#pop_login").show();
    });
    $("#pop_login").find(".close").click(function(){
        $("#pop_login").hide();
    });

    //课程安排弹窗
    $("#course").click(function(){
       $("#pop_course").show();
    });
    $("#pop_course").find(".close").click(function(){
        $("#pop_course").hide();
    });

    //左侧部分鼠标hover效果
    function lihover(dli,dd){
        $(dli).hover(function(){
            $(this).find("img").attr("src","../static/images/lm_"+dd+"_h.png");
            $(this).find("p").css({color:"#ff0"});
        },function(){
            $(this).find("img").attr("src","../static/images/lm_"+dd+".png");
            $(this).find("p").css({color:"#fff"});
        })
    };
    lihover("#container_left ul li:nth-child(1)",1);
    lihover("#container_left ul li:nth-child(2)",2);
    lihover("#container_left ul li:nth-child(3)",3);
    lihover("#container_left ul li:nth-child(4)",4);
    lihover("#container_left ul li:nth-child(5)",5);
    lihover("#container_left ul li:nth-child(6)",6);
    lihover("#container_left ul li:nth-child(7)",7);
    lihover("#container_left ul li:nth-child(8)",8);


    //添加表情
    function add_face(){
        var bq=$("#send_bq");
        $("#qq_face").remove();
        strface = '<div class="qqface" id="qq_face" style=""> '+ '<table border="0" cellspacing="0" cellpadding="0">' + '<tr>';
        for(i=1;i<=100;i++){
            strface += '<td><img src="../static/images/face/'+i+'.gif" /></td>';
            if( i % 15 == 0 ){ strface += '<tr></tr>'}
        }
        strface += '</tr></table></div>';
        bq.append(strface);
        $("#qq_face").css("display","none");
    }
    add_face();

    //--添加弹出qq表情--

    $("#send_bq").bind("click",function(event) {
        if ($("#qq_face:visible").size() == 0) {
            $("#qq_face").css("display", "block");
        }
        else {
            $("#qq_face").css("display", "none");
        }
    });


    //十分钟之后弹出弹窗
    $("#afterpop").find(".close").click(function(){
        $("#afterpop").hide();
    });


    //财经日历弹窗
    $("#cjrl").click(function(){
        $("#pop_cjrl").show();
    });
    $(".close").click(function(){
        $("#pop_cjrl").hide();
    })

});


	