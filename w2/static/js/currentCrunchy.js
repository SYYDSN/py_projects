$(function(){
    console.log(chart);

    // 生成一个线图
    line = function($obj, data){
        // $obj warp容器
        // data数据
        var x = [];
        var y = [];
        var d = data['data'];
        var l = d.length;
        var p_name = data['product'];
        var count = 0;
        var sub = [];
        for(var i=0; i<l; i++){
            var temp = d[i];
            count += temp['all_count'];
            x.push(temp['week']);
            y.push(temp['win_per']);
            if(i == 0 || i == (l - 1)){
                sub.push(temp['week']);
            }
        }
        sub.reverse();
        var option = {
            title:{
                text: p_name,
                subtext: `${sub.join("-")} 共计 ${count}单`
            },
            xAxis: {
                type: 'category',
                data: x
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                data: y,
                type: 'line'
            }]
        };
        var chart_div = $("<div class='chart_div'></div>");
        $obj.append(chart_div);
        let charts = echarts.init(chart_div[0]);
        charts.setOption(option);
    };

    // 绘制所有产品的图标
    for(var x of chart){
        line($(".chart_wrap"), x);
    }

    // 切换 数据统计/当前持仓和历史交易 的按钮的时间
    $(".crunchy-tabList li").each(function(){
        var $this = $(this);
        $this.click(function(){
            $(".crunchy-tabList li").not($this).removeClass("on");
            $this.addClass("on")
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


