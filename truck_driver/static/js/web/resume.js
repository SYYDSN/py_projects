$(function(){
    // 随机查询2份简历
    let random_resume = function(){
        let cur_id = get_url_arg("id");
        if(cur_id !== undefined && cur_id.length >= 24){
            cur_id = cur_id.slice(0, 24);
            $.post("/web/random/resume", {"id": cur_id}, function (resp) {
                let json = JSON.parse(resp);
                console.log(json);
                let data = json['data'];
                let imgs = $(".random_image");
                for(let i=0;i<imgs.length;i++){
                    let img = $(imgs[i]);
                    img.empty();
                    let d = data[i];
                    if(d !== undefined){
                        let id = d['_id'];
                        let u = d['head_image'];
                        let html = `<a href="/web/company/resume?id=${id}">
                                        <img src="${u}">
                                    </a>`;
                        img.append(html);
                    }
                }
            });
        }
    };
    random_resume();

    // 换一批按钮事件
    $("#random").click(function(){
        random_resume();
    });

    // 导航锚点点击时间
    $(".block_02 .nav a").each(function(){
        let $this = $(this);
        $this.click(function(){
            console.log(1);
            $(".block_02 .nav span").not($this).removeClass("active");
            $this.prev().addClass("active");
        });
    });

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

// end!
});