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

// end !!!
});