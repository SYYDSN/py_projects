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

    // 团队成员图片的hover事件
    $(".content_05 .img_item").each(function(){
        var $this = $(this);
        var name = $this.attr("data-name");
        $this.hover(function(){
            console.log(name + "鼠标进入");
            var img = $this.find(".img_div");
            var text = $this.find(".text_div");
            img.fadeOut(0, "swing", function(){
                text.fadeTo(0, 1);
                console.log(name + "显示介绍");
            });
        },function(){
            console.log(name + "鼠标离开");
            var img = $this.find(".img_div");
            var text = $this.find(".text_div");
            text.fadeOut(0, "swing", function(){
                img.fadeTo(0, 1);
                console.log(name + "显示图片");
            });
        });
    });

//end !
});