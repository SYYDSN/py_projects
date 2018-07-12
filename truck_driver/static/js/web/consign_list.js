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

    // 帮助图标点击事件
    $(".icon_desc").each(function(){
        let $this = $(this);
        $this.click(function(){
            $("#launch_tips").click();
        });
    });

    // 撤回委托事件.
    $(".delete_consign").each(function(){
        let $this = $(this);
        $this.click(function () {
            let l = confirm("你确实要撤回这项委托吗?撤回后你也可重新编辑提交本委托.");
            if(l){
                let cid = $this.attr("data-id");
                $.post("/web/consign/withdraw", {"cid": cid}, function(resp){
                    let json = JSON.parse(resp);
                    let status = json['message'];
                    if(status === "success"){
                        alert("撤回成功");
                        location.reload();
                    }
                    else{
                        alert(status);
                        return false;
                    }
                });
            }
            else{
                return false;
            }
        });
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