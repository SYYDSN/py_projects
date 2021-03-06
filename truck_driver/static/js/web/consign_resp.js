$(function(){
    // 顶部 nav-tabs的点击事件
    $(".nav_top .nav > li > a").each(function(){
        let $this = $(this);
        $this.click(function(){
            location.href = $this.attr("data-url");
        });
    });

    // 顶部 nav-tabs的页面ready事件
    (function(){
        let cur_path = location.pathname;
        let lis = $(".nav_top .nav > li");
        for(let li of lis){
            let $li = $(li);
            if($li.find("a").attr("data-url") === cur_path){
                $li.addClass("active");
            }
            else{
                 $li.removeClass("active");
            }
        }
    })();

    // 页码区域的翻页事件
    $(".page_area a").click(function(){
        let args = get_url_arg_dict();
        args['index'] = $(this).attr("data-page");
        let redirect_url = build_url(location.pathname, args);
        location.href = redirect_url;
    });

// end!
});