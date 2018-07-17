$(function(){
    // 六边形hover事件
    $(".text,.text_2").each(function(){
        var $this = $(this);
        $this.hover(function(){
            $this.css("color", "#8cb4e0").prev().attr("src","image/blue_border.png");
        },function(){
        $this.css("color", "#434343").prev().attr("src","image/red_border.png");
    });
    });

//end !
});