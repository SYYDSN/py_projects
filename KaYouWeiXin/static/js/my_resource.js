$(function(){
    (function(){
        // 启动时,调试底部页码区域位置,让他们正哈哈哦保持在底部.
        var $bottom = $(".bottom");
        var b_t = $bottom.offset().top;
        var b_h = $bottom.height();
        var w_h = $(window).height();
        console.log(b_t);
        console.log(b_h);
        console.log(w_h);
        var $middle = $(".middle");
        var m_t = $middle.offset().top;
        var d = w_h - b_h - m_t - 40;
        console.log(d);
        $middle.css("min-height", d);
    })();

    // 关键词查询函数
    $("#submit_search").click(function(){
        var text = $.trim($("#search_keyword").val());
        search_user(text);
    });

    // 关键词清除函数
    $("#refresh_search").click(function(){
        $("#search_keyword").val("");
        var text = $.trim($("#search_keyword").val());
        search_user(text);
    });

    // 根据关键词决定显示哪些名单?
    var search_user = function(nick_name){
        var lines = $(".user_list>.line");
        if(nick_name == ""){
            lines.show();
        }
        else {
            for(var line of lines){
                if($(line).attr("data-nick-name").indexOf(nick_name) != -1){
                    $(line).show();
                }
                else{
                    $(line).hide();
                }
            }
        }
    };

    // 返回按钮
    $("#return_btn").click(function(){
        var referrer = location.referrer;
        if(referrer == undefined){
            referrer = "/wx/html/help_job.html?s_id=" + user['_id'];
        }
        location.href = referrer;
    });

// end !!!
});