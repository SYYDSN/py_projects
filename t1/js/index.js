$(function(){
    // 六边形hover事件
    $(".text,.text_2").each(function(){
        var $this = $(this);
        $this.hover(function(){
            $this.css("color", "#8cb4e0");
            $this.prev().prev().hide(0).next(".b_02:first").show(0);
            console.log($this.html());
            console.log($this.prev(".b_01:first")[0]);
        },function(){
        $this.css("color", "#434343").prev(".b_02").hide(0).prev(".b_01").show(0);
    });
    });

//end !
});