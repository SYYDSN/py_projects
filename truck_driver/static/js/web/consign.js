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

    // 日期选择器初始化函数
    (function () {
        /* 初始化日期函数,
        注意，如果你使用bootstrap,input就必须加上form-control类，否则左右选择的小箭头不显示
        * 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/index.htm
        * id_str参数是日期input的id/class
        */
        $(`#entry_date`).datetimepicker({
            language: "zh-CN",
            weekStart: 1,  // 星期一作为一周的开始
            minView: 2,  // 不显示小时和分
            autoclose: true,  // 选定日期后立即关闭选择器
            format: "yyyy-mm-dd"
        }).on("show", function (ev) {
            // 当选择器显示时被触发.示范,无实际意义.
            console.log(ev);
            console.log("选择器面板被打开");
        }).on("hide", function (ev) {
            // 当选择器隐藏时被触发 示范,无实际意义
            console.log(ev);
            console.log("选择器面板被隐藏");
        }).on("changeDate", function (ev) {
            // 当日期被改变时被触发
            console.log(ev);
            console.log("选择器日期被改变");
        });
    })();

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

    // 提交委托事件
    let submit_consign = function(){
        let args = {};
        /*先搜集基本要求*/
        let industry_experience = parseInt($("#i_exp").attr("data-val"));             // 从业年限
        let dl_license_class = $("#dl_class").attr("data-val");                       // 驾照最低等级要求
        let work_place = $("#work_place").attr("data-val");                           // 工作地
        let work_exp = parseInt($("#work_exp").attr("data-val"));                     // 工作经验
        let education = parseInt($("#education").attr("data-val"));                   // 最低学历
        let salary_range = $("#salary").attr("data-val");                             // 待遇范围
        let count = parseInt($.trim($("#count").val()));                              // 招聘人数
        let entry_date = $.trim($("#entry_date").val());                              // 入职日期
        let driving_exp = parseInt($.trim($("#driving_exp").attr("data-val")));       // 驾龄
        if(!isNaN(industry_experience)){
            args['industry_experience'] = industry_experience;
        }
        if(dl_license_class !== ""){
            args['dl_license_class'] = dl_license_class;
        }
        if(work_place !== ""){
            args['work_place'] = work_place;
        }
        if(!isNaN(work_exp)){
            args['work_exp'] = work_exp;
        }
        if(!isNaN(education)){
            args['education'] = education;
        }
        if(salary_range !== ""){
            args['salary_range'] = salary_range;
        }
        if(!isNaN(count)){
            args['count'] = count;
        }
        let pattern = /^20[1-9][1-9]-[0-1]?[0-9]-[0-3]?[0-9]$/;
        if(pattern.test(entry_date)){
            args['entry_date'] = entry_date;
        }
        if(!isNaN(driving_exp)){
            args['driving_exp'] = driving_exp;
        }
        /*取福利待遇*/
        let children = $(".welfare input[type='checkbox']:checked");
        let welfare = [];
        for(let child of children){
            let $child = $(child);
            welfare.push($child.next().text());
        }
        welfare = welfare.join(",");
        args['welfare'] = welfare;
        /*取岗位职责*/
        let job_duty = $.trim($("#job_duty").val());
        args['job_duty'] = job_duty;
        console.log(job_duty);
        /*备注*/
        let desc = $("#desc").val();
        args['desc'] = desc;
        console.log(desc);
        if(args['job_duty'] !== ""){
            // 先检查是新建委托还是编辑委托?
            let consign_id = $("#consign_id").text();
            let type = "add";
            if(typeof(consign_id) === "string" && consign_id.length === 24){
                args['_id'] = consign_id;
                type = "update";
            }
            args['type'] = type;
            $.post("/web/add_consign", args, function(resp){
                let json = JSON.parse(resp);
                let status = json['message'];
                if(status === "success"){
                    alert("委托成功");
                    location.href = "/web/consign_list";
                }
                else{
                    alert(status);
                    return false;
                }
            });
        }
        else{
            alert("岗位职责不能为空");
            return false;
        }
    };

    // 立即委托按钮事件
    $("#submit").click(function(){
        submit_consign();
    });

// end!
});