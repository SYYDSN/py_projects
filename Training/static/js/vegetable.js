$(function(){
    // 点击导航图片的效果
    $(".nav_item").click(function(){
        let url = $(this).find("img").attr("src");
        let title = $(this).find("img").attr("data-title");
        let desc = $(this).find("img").attr("data-desc");
        $("#current_img").attr("src", url);
        $("#current_title").text(title);
        $("#current_desc").text(desc);
    });

    // 页码区域的翻页事件
    $(".page_area a").click(function(){
        let args = get_url_arg_dict();
        args['index'] = $(this).attr("data-page");
        let redirect_url = build_url(location.pathname, args);
        location.href = redirect_url;
    });

// end!
});