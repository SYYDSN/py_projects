$(function(){
    $(".kehu").hide();
    $("nav ul>li").hover(function(){
        $(this).find("ul").fadeIn();
    },function(){
        $(this).find("ul").fadeOut();
    })
    /*******************注册选项卡***************************/
    $(".banner-member ul li:first").addClass("activelogin");
    var $lis=$(".banner-member ul li");
    $lis.click(function(){
        $(this).addClass("activelogin").siblings().removeClass("activelogin");
        var index=$(this).index(".banner-member ul li");
        $(".banner-member-content div").eq(index).show().siblings().hide();
    });
    /*******************个人中心选项卡***************************/
    $(".person-right-one:not(:first)").hide();
    var $lis=$(".person-box-left ul li");
    $lis.click(function(){
        var index=$(this).index();
        $(".person-right-one").eq(index).show().siblings().hide();
    })
    $(".person-box-left li a").click(function(){
        $(this).addClass("person-active").parent().siblings().children("a").removeClass("person-active");
    })
    /*******************直播中心***************************/
    $(".live-my:not(:first)").hide();
    var $lis=$(".live-right-down ul li");
    $lis.click(function(){
        var index=$(this).index();
        $(".live-my").eq(index).show().siblings().hide();
    })
       $(".live-right-down ul li a").click(function(){
        $(this).addClass("live-active").parent().siblings().children("a").removeClass("live-active");
    })
    /*******************z专属服务选项卡***************************/
    $(".service-contents:not(:first)").hide();
    var $lis=$(".service-background ul li");
    $lis.mouseover(function(){
        var index=$(this).index(".service-background ul li");
        $(".service-contents").eq(index).show().siblings().hide();
    });
    $(".bg-ul ul li").mouseover(function(){
        var index=$(this).index();
        $(this).find("a").css("background","#18b0fb");
        $(this).siblings("li").find("a").css('background',"none");
        $(this).find("img").attr("src","../img/jifen2_"+(parseInt(index)+1)+".png");
        $(this).siblings("li").each(function(){
            var index=$(this).index();
            $(this).find("img").attr("src","../img/jifen_"+(parseInt(index)+1)+".png");
        });
        $(this).find("i").show().parent().parent().siblings().find("i").hide();
        $(this).find("a").css({"color":"#FFF","font-weight":"bold"}).parent().siblings("li").find("a").css({"color":"#666","font-weight":"100"});
    });
    $(".bg-ul ul li:first").trigger("mouseover");
    /*******************专属服务隔行换色***************************/
    $(".jinbi-huan p:odd").css("background","#beeaff");
    $(".jinbi-huan p:even").css("background","#eee");
    $(".jibi-table tbody tr:odd").css("background","#beeaff");
    $(".jibi-table tbody tr:even").css("background","#eee");
    /*******************悬浮窗***************************/
    var height=$(window).scrollTop();
    //var frameobject=$($(".load-foot")[0].contentWindow.document.body).find(".online-consultant");
    if(height<610){
        $(".contenter-fixed").css({position:"absolute",left:"80px",top:"720px"});
        $(".load-foot").css({position:"absolute",right:"0px",top:"690px"})
        $(".online-consultant").css({position:"absolute",right:"0px",top:"690px"});
    }else{
        $(".contenter-fixed").css({position:"fixed",left:"80px",top:"20px"});
        $(".load-foot").css({position:"fixed",right:"0px",top:"20px"});
        $(".online-consultant").css({position:"fixed",right:"0px",top:"40px"});
    }
    $(window).scroll(function(){
        var height=$(window).scrollTop();
        //var frameobject=$($(".load-foot")[0].contentWindow.document.body).find(".online-consultant");
        if(height<610){
            $(".contenter-fixed").css({position:"absolute",left:"80px",top:"720px"});
            $(".load-foot").css({position:"absolute",right:"0px",top:"700px"});
            $(".online-consultant").css({position:"absolute",right:"0px",top:"720px"});
        }else{
            $(".contenter-fixed").css({position:"fixed",left:"80px",top:"20px"});
            $(".load-foot").css({position:"fixed",right:"0px",top:"0px"});
            $(".online-consultant").css({position:"fixed",right:"0px",top:"20px"});
        }
    });
    /********************赞加一**************************/
    $(".addnum").click(function(){
        var value=$(this).siblings("span").html();
        $(this).siblings("span").html(parseInt(value)+1);
    })
    /********************获取当前引用页和当前页面的url**************************/
    var page=window.document.location.pathname;  //获得当前页面的url
    $(".referrer_page").val(document.referrer);     //获取当前的跳转前页面并赋值
    $(".user_page").val(page);                   //把这个值赋值给id=user_page的input
    //console.log( $(".referrer_page").val()+"    "+$(".user_page").val())

 /********************实时跟踪翻转**************************/
    var aLi = $('.mitchell-holland-leftdown  .fllow li');
    var aImg =  $('.mitchell-holland-leftdown  .fllow li a');
    var aSpan = $('.mitchell-holland-leftdown  .fllow li span');

    
    // var judge=1;
    var num=0;
    var judge=new Array();
    judge[0]=1;
    judge[1]=1;
    judge[2]=1;
    setInterval(function(){
        var obj=aLi.eq(num);
        if(judge[num]){
            obj.find("span").stop();
            obj.find("a").stop();
            var oldobj=obj;
            obj.find("a").css({zIndex:1}).animate({top:37,height:0},80,'',function(){
                $(this).hide();
                oldobj.find("span").css({zIndex:2,display:'inline'}).animate({
                    top:0,
                    height:53
                },250)
            });
        }else{
            obj.find("span").stop();
            obj.find("a").stop();
            var oldobj=obj;
            obj.find("span").css({zIndex:1}).animate({top:37,height:0},80,'',function(){
                $(this).hide();
                oldobj.find("a").css({zIndex:2,display:'inline'}).animate({
                    top:0,
                    height:53
                },250)
            })
        }
        judge[num]=judge[num]?0:1;
        num++;
        num=num>=3?0:num;
    },2000);

/********************客户跟单收益**************************/

    var aLi2 = $('.mitchell-leftTop-cont  .fllow li');
    var aImg2 =  $('.mitchell-leftTop-cont  .fllow li a');
    var aSpan2 = $('.mitchell-leftTop-cont  .fllow li span');
    // var judge=1;
    var num2=0;
    var judge2=new Array();
    judge2[0]=1;
    judge2[1]=1;
    judge2[2]=1;
    judge2[3]=1;
    setInterval(function(){
        var obj=aLi2.eq(num2);
        if(judge2[num2]){
            obj.find("span").stop();
            obj.find("a").stop();
            var oldobj=obj;
            obj.find("a").css({zIndex:1}).animate({top:37,height:0},80,'',function(){
                $(this).hide();
                oldobj.find("span").css({zIndex:2,display:'inline'}).animate({
                    top:0,
                    height:53
                },250)
            });
        }else{
            obj.find("span").stop();
            obj.find("a").stop();
            var oldobj=obj;
            obj.find("span").css({zIndex:1}).animate({top:37,height:0},80,'',function(){
                $(this).hide();
                oldobj.find("a").css({zIndex:2,display:'inline'}).animate({
                    top:0,
                    height:53
                },250)
            })
        }
        judge2[num2]=judge2[num2]?0:1;
        num2++;
        num2=num2>=4?0:num2;
    },2000);
    /************首页弹窗************/
    $(function(){
        $(".background-1").hide();
        function showdiv(){
            $(".background-1").show();
            $(".pop-up-box").show();
            $(".background-1").css({height:'100%',position:"fixed",top:"0px",zIndex:101});
            $(".pop-up-box").css({position: "fixed",background:"#FFF",top:($(window).height()-$(".pop-up-box").height())/2+'px',left:($(window).width()-$(".pop-up-box").width())/2+'px',zIndex:102});
        }
        $(".background-1,.close1").click(function(){
            $(".background-1").hide();
            $(".pop-up-box").hide();
        });
        $(".successful-profit h2 i,.aprofit-one h2 span,.iphone img,.contenter-fixed a img,.star-youxi2 img,.wechat-mid p,.wechat-foot h2,.wechat-mid1 dl,.chakan button,.live-join,.live-left-top p,.live-one,.live-one1,.live-one2").click(showdiv);
    });
    $(".mitchell-holland-right .star-youxi img").click(function(){
        $(".mitchell-holland-right .star-youxi").fadeOut();
    });
    $("#button0").click(function(){
        $(this).fadeOut();
    });
      /************登录************/
         $(function(){
        $(".background-1").hide();
        function showdiv1(){
            $(".background-1").show();
            $(".pop-up-box1").show();
            $(".background-1").css({height:'100%',position:"fixed",top:"0px",zIndex:101});
            $(".pop-up-box1").css({position: "fixed",background:"#FFF",top:($(window).height()-$(".pop-up-box1").height())/2+'px',left:($(window).width()-$(".pop-up-box1").width())/2+'px',zIndex:102});
        }
        $(".background-1,.close1").click(function(){
            $(".background-1").hide();
            $(".pop-up-box1").hide();
        });
        $(".live-login").click(showdiv1);
    });
    /************协议************/
    $(".background-1").hide();
    function showdiv(){
        $(".background-1").show();
        $(".xieyi").show();
        $(".background-1").css({height:'100%',position:"fixed",top:"0px",zIndex:101});
        $(".xieyi").css({position: "fixed",background:"#FFF",top:($(window).height()-$(".xieyi").height())/2+'px',left:($(window).width()-$(".xieyi").width())/2+'px',zIndex:102});
    }
    $(".background-1").click(function(){
        $(".background-1").hide();
        $(".xieyi").hide();
    });
    $(".yonghu").click(showdiv);
    $(".xieyi button").click(function(){
        $(".xieyi").hide();
        $(".background-1").hide();
    })
});
window.onload=function(){
    /************调整登录框************/
    var $banner=$("#imgbanner").find("img");
    var $login_div=$("#bannerConts");
    var $img=$(".banner-thinkchange img[src='../img/thinkchange.jpg']");
    function resizeLogin($obj1,$obj2){
        var h1=$obj1.height();
        $obj2.height(h1);
    }
    resizeLogin($banner,$login_div);
    $(window).resize(function(){
        resizeLogin($banner,$login_div);
    });
}






