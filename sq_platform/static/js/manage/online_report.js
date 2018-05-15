$(function(){
    // 在线用户过滤器事件
    let filter_online = get_url_arg("filter_online");
    $(".filter_online").each(function(){
        let $this = $(this);
        let cur = $this.attr("data-filter");
        if(cur === filter_online){
            $this.click();
        }else{}
        $this.click(function(){
            let the_cur = $this.attr("data-filter");
            if(the_cur !== filter_online){
                location.href = `${location.pathname}?filter_online=${the_cur}`;
            }
        });
    });

// end !!!
});