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

});