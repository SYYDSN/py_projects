$(function(){
    // 子页面切换函数
    $(".change_sub_page .page").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".change_sub_page .active_page").removeClass("active_page");
            $this.addClass("active_page");
            let s = $this.attr("id");
            if(s === "prev_chart"){
                $(".date_row").show();
                init_prev_chart();
            }
            else if(s === "today_chart"){
                init_today_chart();
            }
            else{
                $(".date_row").hide();
            }
            s = "." + s;
            $(".sub_page").not(s).addClass("hide_page");
            $(s).removeClass("hide_page");
            $(".page").not($this).removeClass("active_page");
            $this.addClass("active_page");
        });
    });

    // 初始化日期插件函数
    function init_date(step){
        let min_v = 2;
        let start_v = 2;
        let format = "yyyy-mm-dd";
        let begin = `2018-01-01`;
        if(step === "day"){
            min_v = 2;
            start_v = 2;
            format = "yyyy-mm-dd";
            begin = `2017-01-01`;
        }
        else if(step === "month"){
            min_v = 3;
            start_v = 3;
            format = "yyyy-mm";
            begin = `2017-01`;
        }
        else if(step === "year"){
            min_v = 4;
            start_v = 4;
            format = "yyyy";
            begin = `2017`;
        }
        else{}
        $('#select_date').datetimepicker('remove');
        $("#select_date").datetimepicker({
            language: "zh-CN",
            startDate: begin,
            weekStart:1,  // 星期一作为一周的开始
            startView: start_v,  // 开始视图
            minView: min_v,  // 最小视图
            autoclose: true,  // 选定日期后立即关闭选择器
            format: format
        });
    }

    // 启动时,初始化页面,包括时间选择器.
    (function(){
        // 初始化时间选择器
        let date = get_url_arg("date");
        let step = get_url_arg("step");
        step = step?step:"month";
        let now = new Date();
        let y = now.getFullYear();
        let m = now.getMonth() + 1;
        let d = now.getDate();
        let str = `${y}-${m}`;
        if(step === "month"){
            init_date(step);
        }
        else if(step === "day"){
            str = `${y}-${m}-${d}`;
            $(".select_interval[data-val='day']").click();
        }
        else if(step === "year"){
            str = `${y}`;
            $(".select_interval[data-val='year']").click();
        }
        else{}
        if(date){
            $('#select_date').val(date);
        }
        // 初始化 子页面选择器
        let page = get_url_arg("page");
        if(page){
            let s = "#" + page;
            $(s).click();
        }
        else{
            $("#today_chart").click();
        }
    })();

    // 选择时间粒度的按钮
    $(".select_interval").each(function(){
        let $this = $(this);
        $this.click(function(){
            $(".select_interval").not(this).removeClass("select_interval_action");
            $this.addClass("select_interval_action");
            init_date($this.attr("data-val"));
        });
    });

    // 跳转按钮事件.
    $("#redirect_btn").click(function(){
        let args = {};
        // 开始收集跳转参数
        let date = $("#select_date").val();
        let step = $(".select_interval_action").attr("data-val");
        args['date'] = date;
        args['step'] = step;
        console.log(args);
        let url = `${location.pathname}?`;
        for(let k in args){
            url += `${k}=${args[k]}&`;
        }
        url = url.endsWith("&")?url.slice(0, -1): url;
        url = url.endsWith("?")?url.slice(0, -1): url;
        console.log(url);
        location.href = url;
    });

    function init_today_chart(){
        // 初始化今日报表
        setTimeout(function(){
            // 绘制安全评估
        let myyb = echarts.init(document.getElementById('myyb'));
        myyb.setOption({
            backgroundColor: "#ffffff",
            color: ["#ccc", "#ccc", "#67E0E3"],
            series: [{
                name: '安全指标',
                type: 'gauge',
                detail: {
                    formatter: '{value}分',
                    color: '#37a2da',
                    fontSize:18
                },
                axisLine: {
                    show: true,
                    lineStyle: {
                        width: 30,
                        shadowBlur: 0,
                        color: [
                            [0.3, '#fd666d'],
                            [0.7, '#37a2da'],
                            [1, '#3BE4E4']
                        ]
                    }
                },
                data: [{
                    value: 50 + parseInt((Math.random() * 100) / 2),
                    name: '',
                }]

            }]
        });
        let myChart = echarts.init(document.getElementById('myChart'));
        // 绘制生理状态图表
        myChart.setOption({
            title: {
                // text: '健康状态',
                textStyle:{
                    color: '#A0A0A0',
                    fontSize:12
                }
            },
            tooltip: {
                trigger: 'axis',
                backgroundColor:'rgba(255,255,255,0.8)',
                extraCssText: 'box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);',
                textStyle:{
                    color:'#666',
                },
            },

            grid: {

                containLabel: true
            },
            xAxis: [{
                type: 'category',
                data: ['1时', '2时', '3时', '4时', '5时', '6时', '7时','8时','9时', '10时', '11时', '12时', '13时', '14时', '15时','16时','17时', '18时', '19时', '20时', '21时', '22时', '23时','24时'],
                boundaryGap: false, //坐标轴两边留白
                alignWithLabel:true,
                splitLine: {
                    show: false,
                    lineStyle: {
                        color: ['#D4DFF5']
                    }
                },
                axisTick: {
                    show: true,
                    inside:true
                },
                axisLine: {
                    lineStyle: {
                        color: '#666'
                    }
                },
            }, ],
            yAxis: {
                type: 'value',
                boundaryGap: true,
                offset:'50',
                axisLabel: {
                    textStyle: {
                        color: '#666',
                        fontStyle: 'normal',
                    }
                },
                axisLine: {
                    show: false
                },
                axisTick: {
                    color:'#dadfea',
                    inside:true
                },
                axisLabel:{
                    inside:true,
                    z:10
                },
                splitLine: {
                    show: true,
                    lineStyle:{
                        type:'dashed'
                    },
                    zlevel:9999999
                }
            },
            series: [{
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 16,
                data: ['1200', '1400', '1008', '1411', '1026', '1288', '1300','1400','1200', '1400', '1008', '1411', '1026', '1288', '1300','1400','1200', '1400', '1008', '1411', '1026', '1288', '1300','1400'],
                areaStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(
                            0, 0, 0, 1, [{
                                offset: 0,
                                color: '#DCDFFF'
                            },
                                {
                                    offset: 1,
                                    color: '#F8F8FD'
                                }
                            ]
                        )
                    }
                },
                itemStyle: {
                    opacity: 0
                },
                lineStyle: {
                    normal: {
                        color: 'transparent'
                    }
                },
                emphasis: {
                    itemStyle: {
                        color: '#87d857',
                        borderColor: '#fff',
                        borderWidth: 11,
                        borderType: 'solid',
                        opacity: 1
                    },
                }
            }]
        });
        // 当日报表,不良驾驶行为
        let myxw = echarts.init(document.getElementById('myxw'));
        myxw.setOption({
            title:{
                subtext: '不良驾驶行为',
                textStyle:{
                    color:'#ccc'
                }
            },
            color: ['#3398DB'],
            tooltip : {
                trigger: 'axis',
                axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                    type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis : [
                {
                    type : 'category',
                    data : ['疲劳驾驶', '看手机', '打手机', '急加速', '急转弯', '急刹车', '超速'],
                    axisTick: {
                        alignWithLabel: true
                    }
                }
            ],
            yAxis : [
                {
                    type : 'value'
                }
            ],
            series : [
                {
                    name:'直接访问',
                    type:'bar',
                    barWidth: '60%',
                    data:[10, 52, 200, 334, 390, 330, 220]
                }
            ]
        });
        }, 300);
    }

    function init_prev_chart(){
        // 初始化历史报表
        setTimeout(function(){
            let mylishi = echarts.init(document.getElementById('mylishi'));
            mylishi.setOption({
                title: {
                    text: '',
                    subtext: '安全得分 12月第三周(17/12/31---18/1/7)'
                },
                xAxis: {
                    dtype : 'category',
                    data : ['1/1', '1/2', '1/3', '1/4', '1/5'],
                    axisTick: {
                        alignWithLabel: true
                    }

                },
                yAxis: {
                    axisLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    axisLabel: {
                        textStyle: {
                            color: '#999'
                        }
                    }
                },
                dataZoom: [
                    {
                        type: 'inside'
                    }
                ],
                series: [
                    { // For shadow
                        type: 'bar',
                        itemStyle: {
                            normal: {color: 'rgba(0,0,0,0.05)'}
                        },
                        barGap:'-100%',
                        barCategoryGap:'40%',
                        data: ['周一', '周二', '周三', '周四', '周五'],
                        animation: false
                    },
                    {
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: new echarts.graphic.LinearGradient(
                                    0, 0, 0, 1,
                                    [
                                        {offset: 0, color: '#83bff6'},
                                        {offset: 0.5, color: '#188df0'},
                                        {offset: 1, color: '#188df0'}
                                    ]
                                )
                            },
                            emphasis: {
                                color: new echarts.graphic.LinearGradient(
                                    0, 0, 0, 1,
                                    [
                                        {offset: 0, color: '#2378f7'},
                                        {offset: 0.7, color: '#2378f7'},
                                        {offset: 1, color: '#83bff6'}
                                    ]
                                )
                            }
                        },
                        data: [89, 87, 76, 73, 83]
                    }
                ]
            });

            // 历史报表,不良驾驶行为
            let prev_myxw = echarts.init(document.getElementById('prev_myxw'));
            prev_myxw.setOption({
                title:{
                    subtext: '不良驾驶行为',
                    textStyle:{
                        color:'#ccc'
                    }
                },
                color: ['#3398DB'],
                tooltip : {
                    trigger: 'axis',
                    axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                        type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis : [
                    {
                        type : 'category',
                        data : ['疲劳驾驶', '看手机', '打手机', '急加速', '急转弯', '急刹车', '超速'],
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                yAxis : [
                    {
                        type : 'value'
                    }
                ],
                series : [
                    {
                        name:'直接访问',
                        type:'bar',
                        barWidth: '60%',
                        data:[10, 52, 200, 334, 390, 330, 220]
                    }
                ]
            });
        }, 300);
        // 初始化历史报表的安全评估

    }













// end !!!
});