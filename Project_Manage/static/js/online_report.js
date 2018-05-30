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

    let line_option = function (the_data) {
        /*
        *线图的配置项
        * */
        let weeks = ["日", "一", "二", "三", "四", "五", "六"];
        let month = the_data['month'];
        let year = the_data['year'];
        let day_list = [];
        let count_list = [];
        let user_count = the_data['user_count'];
        let month_count = 0;
        let max_active = 0;
        for(let data of the_data['data']){
            day_list.push(parseInt(data.day));
            let today_count = parseInt(data.count);
            max_active = max_active < today_count?today_count: max_active;
            count_list.push(today_count);
            month_count += today_count;
        }
        console.log(day_list);
        console.log(count_list);
        let option = {
            title: {
                //text:"月活用户分布图",
                subtext: `${year}年${month}月,共计:${user_count}人,${month_count}次/天`
            },
            tooltip: {
                triggerOn: 'mousemove',
                formatter: function (params) {
                    console.log(params['data']);
                    console.log(params);
                    let cur_day = params.dataIndex + 1;
                    let the_day = new Date(`${year}-${month}-${cur_day}`);
                    let week = the_day.getDay();
                    let str = `${month}月${cur_day}日 星期${weeks[week]} 活跃:${params.data}人`;
                    return str;
                }
            },
            grid: {
                top: 80,
            },
            xAxis: {
                type: 'category',
                data: day_list
            },
            yAxis: {
                type: 'value',
                max: max_active < 40?40: max_active
            },
            series: [
                {
                    data: count_list,
                    type:"line",
                    smooth: true
                }
            ]
        };
        return option;
    };

    // 查看月活用户图的函数
    let can_query = true;
    month_active_chart = function($obj){
        if(can_query){
            $(".my_outer").show();
            can_query = false;
            let y = $obj.attr("data-year");
            let m = $obj.attr("data-month");
            init_modal_nav(y, m);  //调整模态框标题栏
            let args = {"year": y, "month": m};
            $.post("/online_report", args, function(resp){
                $(".my_outer").hide();
                can_query = true;
                let data = JSON.parse(resp);
                let opt = line_option(data);
                let obj = echarts.init($("#month_active_chart")[0]);
                obj.resize({"width":900, "height":400});
                obj.setOption(opt);
            });
        }
        else{
            // nothing...
        }
    };

    // 初始化月活图的标题导航栏
    function init_modal_nav(y, m){
        // y指的是月份,m指的是年份
        let now = new Date();
        let n_y = now.getFullYear();
        let n_m = now.getMonth() + 1;
        if(isNaN(y)){
            y = n_y;
        }
        if(isNaN(m)){
            m = n_m;
        }
        y = parseInt(y);
        m = parseInt(m);
        let now_date = new Date(`${n_y}-${n_m}-01`);
        let cur_date = new Date(`${y}-${m}-01`);
        let next_date = new Date(`${y}-${m}-01`);
        next_date.setMonth(next_date.getMonth() + 1);
        next_date = next_date > now_date? now_date: next_date;
        let prev_date = new Date(`${y}-${m}-01`);
        prev_date.setMonth(prev_date.getMonth() - 1);
        prev_date = prev_date < now_date? prev_date: now_date;
        console.log(`now_date: ${now_date.toLocaleString()}`);
        console.log(`cur_date: ${cur_date.toLocaleString()}`);
        console.log(`next_date: ${next_date.toLocaleString()}`);
        console.log(`prev_date: ${prev_date.toLocaleString()}`);
        let html = `
            <i data-year="${prev_date.getFullYear()}" data-month="${prev_date.getMonth() + 1}" class="fa fa-step-backward fa-2x modal_nav_item" onclick="month_active_chart($(this))" ></i>
            <button onclick="month_active_chart($(this))" class="modal_nav_item active_nav_item" data-month="${m}" data-year="${y}">${y}年${m}月活跃用户</button>
            <i data-year="${next_date.getFullYear()}" data-month="${next_date.getMonth() + 1}" class="fa fa-step-forward fa-2x modal_nav_item" onclick="month_active_chart($(this))" ></i>
            `;

        $("#my_modal_nav").html(html);
    }
// end !!!
});