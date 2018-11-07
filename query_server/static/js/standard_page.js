$(function(){
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

});