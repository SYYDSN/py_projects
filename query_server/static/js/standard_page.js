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
        $(".left_nav .sub_nav").not(sub).slideUp(300, 'swing', function(){
            var icon = $dom.find(".plus_sign");
            icon.removeClass('fa-plus-square');
            icon.addClass('fa-minus-square');
            sub.slideDown();
        });
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

});