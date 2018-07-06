$(function(){
    // 收藏事件
    $(".favorite").click(function(){
        let $this = $(this);
        let resume_id = $this.attr("data-id");
        console.log(resume_id);
        $.post("/web/favorite/add", {"id": resume_id}, function(resp){
            let json = JSON.parse(resp);
            let mes = json['message'];
            if(mes === "success"){
                // 收藏成功.
                $this.hide().next().show();
            }
            else{
                alert(mes);
                return false;
            }
        });
    });

     // 反收藏事件
    $(".un_favorite").click(function(){
        let $this = $(this);
        let resume_id = $this.attr("data-id");
        console.log(resume_id);
        $.post("/web/favorite/remove", {"id": resume_id}, function(resp){
            let json = JSON.parse(resp);
            let mes = json['message'];
            if(mes === "success"){
                // 反收藏成功.
                $this.hide().prev().show();
            }
            else{
                alert(mes);
                return false;
            }
        });
    });

    // 更多信息事件
    $(".more_info").click(function(){
        let $this = $(this);
        let resume_id = $this.attr("data-id");
        let u = `/web/company/resume?id=${resume_id}`;
        window.open(u);
    });

    // 页码区域的翻页事件
    $(".page_area a").click(function(){
        let args = get_url_arg_dict();
        args['index'] = $(this).attr("data-page");
        let redirect_url = build_url(location.pathname, args);
        location.href = redirect_url;
    });

    // 一键全选事件
    $("#select_all").change(function(){
        let all = $(".select input[type='radio']");
        let status = $("#select_all").prop("checked");
        if(status){
            all.prop("checked", true);
        }
        else{
            // nothing...
        }
    });

    // 一键取消事件
    $("#un_select_all").change(function(){
        let all = $(".select input[type='radio']");
        let status = $("#un_select_all").prop("checked");
        if(status){
            all.prop("checked", false);
        }
        else{
            // nothing...
        }
    });

    // 批量从收藏夹移除事件
    $("#batch_remove").click(function(){
        let all = $(".select input[type='radio']:checked");
        let ids = [];
        for(let t of all){
            let temp = $(t);
            ids.push(temp.attr("data-id"));
        }
        if(ids.length > 0){
            let c = confirm(`你确定要从收藏夹移除这${ids.length}条简历吗?`);
            if(c){
                $.post("/web/favorite/batch_remove", {"ids": ids.join(",")}, function(resp){
                    let json = JSON.parse(resp);
                    let mes = json['message'];
                    if(mes === "success"){
                        // 批量反收藏成功.
                        location.reload();
                    }
                    else{
                        alert(mes);
                        return false;
                    }
                });
            }
        }
    });

// end !
});