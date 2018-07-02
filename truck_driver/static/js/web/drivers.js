$(function(){
    // 省略号的动画
    let ellipsis = setInterval(function(){
        let visible = $("#ellipsis:visible");
        if(visible.length === 0){
            clearInterval(ellipsis);
        }
        else{
            let l = visible.text();
            if(l.length < 6){
                l += ".";
            }
            else{
                l = ".";
            }
            visible.text(l);
        }
    }, 1000);

    // 调整页底的位置
    function reset_bottom(){
        let top_obj = $(".page_top");
        let middle_obj = $(".page_middle");
        let bottom_obj = $(".page_bottom");
        let b_t = bottom_obj.position().top;
        let b_h = bottom_obj.height();
        let doc_h = $("body").height();
        let real_h = b_h + b_t;
        console.log(real_h);
        console.log(doc_h);
        if(doc_h < real_h){
            let new_h = doc_h - b_h - top_obj.height() - 10;
            console.log(`new height is ${new_h}`);
            middle_obj.css("height", new_h);
        }
    }
    reset_bottom();

// end !!!
});