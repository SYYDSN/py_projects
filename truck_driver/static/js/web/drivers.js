$(function(){
    /*
     使用jquery加载数据方式获取数据,等待数据返回时的省略号的动画
     在使用jinja2模板时,可以无视此函数(不会运行)
     */
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

    // bootstrap下拉选择菜单选择事件.
    $(".dropdown").each(function(){
        let down = $(this);
        let i = down.find(".fa");
        let show_area = down.find(".show_area");  // 下拉菜单选中的值的显示区域
        let options = down.find("ul > li > a");
        options.each(function(){
            let $this = $(this);
            $this.click(function(){
                if($this.hasClass("reset")){
                    // 清空选择
                    let text = $this.attr("data-text");
                    show_area.text(text).append(i).attr("data-val", $this.attr("data-val"));
                }
                else{
                    let text = $this.text();
                     show_area.html(text).append(i).attr("data-val", $this.attr("data-val"));
                }
            });
        });
    });

    // 清空搜索条件按钮事件
    $("#reset_condition").click(function(){
        $("#keywords").val("");
        $(".dropdown .reset").click();
    });

    // 搜索按钮事件
    $("#submit_search").click(function(){
        let args = {};
        let keywords = $.trim($("#keywords").val());
        args['keywords'] = keywords;  // 关键词
        let i_exp = $("#i_exp").attr("data-val");
        if(i_exp !== undefined && i_exp !== ""){
            args['i_exp'] = i_exp;  // 从业年限
        }
        let dl_class = $("#dl_class").attr("data-val");
        if(dl_class !== undefined && dl_class !== ""){
            args['dl_class'] = dl_class;  // 驾照级别
        }
        let salary = $("#salary").attr("data-val");
        if(salary !== undefined && salary !== ""){
            args['salary'] = salary;  // 期望待遇
        }
        let education = $("#education").attr("data-val");
        if(education !== undefined && education !== ""){
            args['education'] = education;  // 教育程度
        }
        let work_exp = $("#work_exp").attr("data-val");
        if(work_exp !== undefined && work_exp !== ""){
            args['work_exp'] = work_exp;  // 工作经验
        }
        let driver_status = $("#driver_status").attr("data-val");
        if(driver_status !== undefined && driver_status !== ""){
            args['driver_status'] = driver_status;  // 当前状态
        }
        let update_date = $("#update_date").attr("data-val");
        if(update_date !== undefined && update_date !== ""){
            args['update_date'] = update_date;  // 发布时间
        }
        let driving_exp = $("#driving_exp").attr("data-val");
        if(driving_exp !== undefined && driving_exp !== ""){
            args['driving_exp'] = work_exp;  // 驾龄
        }
        args['index'] = 1;
        let redirect_url = build_url(location.pathname, args);
        location.href = redirect_url;
    });

    // 从location.href获取参数.初始化相关的搜索区域的值
    (function(){
        let dict = get_url_arg_dict();
        console.log(dict);
        for(let id_str in dict){
            let val = dict[id_str];
            if(id_str === "keywords"){
                // 关键词参数
                if(val === ""){
                    // nothing...
                }
                else{
                    $("#keywords").val(val);
                }
            }
            else if(id_str === "index"){
                // 页码不处理
            }
            else{
                // 剩下的都是bootstrap的下拉选择框
                if(val === ""){
                    // nothing...
                }
                else{
                    let as = $("#" + id_str).next().find("li a");
                    for(let a of as){
                        let $a = $(a);
                        if($a.attr("data-val") === val){
                            $a.click();
                            break;
                        }
                    }
                }
            }
        }
    })();

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
                // 收藏成功.
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

// end !!!
});