$(function(){
    console.log(chart);

    // 生成一个线图
    draw = function(type, title, subtext, x, y){
        // $obj warp容器
        var option = {
            title:{
                text: title,
                subtext: subtext
            },
            grid:{
                top: 60,
                left: 50,
                bottom: 30
            },
            color: ["#437ab7"],
            xAxis: {
                type: 'category',
                data: x
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                data: y,
                type: type
            }]
        };
        var chart_div = $("<div class='chart_div'></div>");
        $(".chart_wrap").append(chart_div);
        let charts = echarts.init(chart_div[0]);
        charts.setOption(option);
    };

    /*绘制所有产品的图标
    2018-11-25日，原有的分产品的线图取消．代之的是：
    １.按照周切分的胜率柱状图
    2.按照周切分的收益率柱状图
    3 .按照周切分的收益率线图
    */
    var dx = [];
    var d1 = [];  // 每周胜率柱状图
    var d2 = [];  // 每周净赢利柱状图
    var d3 = [];  // 累计每手盈利线图
    var raw_profit = 0;  // 原始每手净盈利
    for(var x of chart){
        var week = x['_id'];  // 周
        dx.push(week);
        var v1 = x['win_per'] * 100;  // 胜率
        d1.push(v1);
        var v2 = x['avg_profit'];  // 每单每手净盈利
        d2.push(v2);
        var v3 = raw_profit + v2;  // 每单每手累计净盈利
        raw_profit = v3;
        d3.push(Math.floor(v3));
        // d3.push(Math.floor(v3 / 100));
    }
    console.log(d3);
    draw("bar", "周胜率统计", "单位: %", dx, d1);
    draw("bar", "周平均盈利", "单位: 美元/手", dx, d2);
    draw("line", "每手累计盈利", "单位: 美元/手", dx, d3);
    // draw("line", "周收益率", "单位: %", dx, d3);


    // 切换 数据统计/当前持仓和历史交易 的按钮的时间
    $(".crunchy-tabList li").each(function(){
        var $this = $(this);
        $this.click(function(){
            $(".crunchy-tabList li").not($this).removeClass("on");
            $this.addClass("on");
            if($this.hasClass("chart_li")){
                $(".wrap:not(.chart_wrap)").hide(0);
                $(".chart_wrap").show(0);
            }
            else if($this.hasClass("hold_li")){
                $(".wrap:not(.hold_wrap)").hide(0);
                $(".hold_wrap").show(0);
            }
            else{
                $(".wrap:not(.crunchy-wrap)").hide(0);
                $(".crunchy-wrap").show(0)
            }
        });
    });
    $("#hold_page").click();  // 默认先显示持仓页面

    // 跟踪老师事件
    $("#follow_btn").click(function(){
        var t_id = get_url_arg("t_id");
        // alert(user_follow)
        // alert(t_id)
        // alert(user_follow.indexOf(t_id))
        var args = {"t_id": t_id};
        if(user_follow.length == 0){
            // 以前没有关注过老师
            args['type'] = "follow";
        }
        else if(user_follow.length != 0 && user_follow.indexOf(t_id) == -1){
             // 以前有关注过老师
            var f = confirm("会替换掉以前关注的老师并消耗额外积分，确认吗");
            if(f){
                args['type'] = "follow";
            }
            else{
                return false;
            }
        }
         else if(user_follow.length != 0 && user_follow.indexOf(t_id) != -1){
            // 相同的老师，再次关注等于取消关注
            var f = confirm("取消关注此老师，确认吗");
            if(f){
                args['type'] = "un_follow";
            }
            else{
                return false;
            }
        }else{
            console.log("未知的情况");
            return false;
        }
        $.post("/user/follow_teacher", args, function(resp){
            var json = JSON.parse(resp);
            var status = json['message'];
            if(status == "success"){
                alert("操作成功");
                location.reload();
            }
            else{
                alert(status);
            }
        });
    });


// end!
});


