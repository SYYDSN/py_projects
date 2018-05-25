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
        let subtext = '';
        let now = new Date();
        let month = now.getMonth() + 1;
        let year = now.getFullYear();
        let day_list = [];
        let count_list = [];
        for(let day in the_data){
            day_list.push(parseInt(day));
            count_list.push(parseInt(the_data[day]));
        }
        console.log(day_list)
        console.log(count_list)
        let option = {
            title: {
                text: `${year}年${month}月`,
            },
            grid: {
                top: 80,
            },
            xAxis: {
                type: 'category',
                data: day_list
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    data: count_list,
                    type:"line"
                }
            ]
        };
        return option;
    };

    // 查看月活用户图
    $("#btn_01").click(function(){
        $.post("/online_report", function(resp){
            let data = JSON.parse(resp);
            let opt = line_option(data);
            let charts = echarts.init($("#myModal1 .modal-body")[0]);
            charts.setOption(opt);
        });
    });

// end !!!
});