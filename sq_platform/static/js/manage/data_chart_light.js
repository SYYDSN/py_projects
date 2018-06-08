$(function(){
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

    let mydata_img = echarts.init(document.getElementById('data_img'));
    mydata_img.setOption({
        title: {
            text: "事故统计",
            subtext: ""
        },
        grid:{
            tooltip:{
                formatter: function (params){
                    console.log(params);
                    let name = params.seriesName;
                    let index = params.seriesIndex + 1;
                    let count = params.data[index];
                    let str = `${name}${count}起${params.name}`;
                    return str;
                }
            }
        },
        legend: {},
        tooltip: {},
        dataset: {
            source: chart_data['acc']
        },
        xAxis: {type: 'category'},
        yAxis: {type: 'value'},
        series: [
            {type: 'bar'},
            {type: 'bar'},
            {type: 'bar'}
        ]
    });
    let mydata_imgtwo = echarts.init(document.getElementById('data_imgtwo'));

    mydata_imgtwo.setOption({
        title: {
            text: "违章统计",
            subtext: ""
        },
        grid:{
            tooltip:{
                formatter: function (params){
                    console.log(params);
                    let name = params.seriesName;
                    let index = params.seriesIndex + 1;
                    let count = params.data[index];
                    let str = `${name}${count}起${params.name}`;
                    return str;
                }
            }
        },
        legend: {},
        tooltip: {},
        dataset: {
            source: chart_data['vio']
        },
        xAxis: {type: 'category'},
        yAxis: {type: 'value'},
        series: [
            {type: 'bar'},
            {type: 'bar'},
            {type: 'bar'}
        ]
    });

// 日期插件change事件
    var change_date = function(obj){
        var $obj = $(obj);
        var my_id = $obj.attr("id");
        console.log(my_id);
        if(my_id === "date_picker_end"){
            // 点击结束时间的时间选择器
            var begin = new Date($.trim($("#date_picker").val()));
            var end = new Date($.trim($obj.val()));
            var delta = end - begin;
            console.log(end, begin);
            console.log($.trim($obj.val()));
            console.log(delta);
            if(typeof(delta) === "number" && delta < 0){
                alert("结束时间不能早于开始时间！");
                $obj.val("");
                return false;
            }
        }
        else{
            // 点击开始时间的时间选择器
            var end = new Date($.trim($("#date_picker_end").val()));
            var begin = new Date($.trim($obj.val()));
            var delta = end - begin;
            console.log(end, begin);
            console.log($.trim($obj.val()));
            console.log(delta);
            if(typeof(delta) === "number" && delta < 0){
                alert("结束时间不能早于开始时间！");
                $obj.val("");
                return false;
            }

        }
    };

    // 初始化日期插件函数
    function init_date(step){
        let min_v = 2;
        let start_v = 2;
        let format = "yyyy-mm-dd";
        if(step === "day"){
            min_v = 2;
            start_v = 2;
            format = "yyyy-mm-dd";
        }
        else if(step === "month"){
            min_v = 3;
            start_v = 3;
            format = "yyyy-mm";
        }
        else if(step === "year"){
            min_v = 4;
            start_v = 4;
            format = "yyyy";
        }
        else{}
        $('#select_date').datetimepicker('remove');
        $("#select_date").datetimepicker({
            language: "zh-CN",
            weekStart:1,  // 星期一作为一周的开始
            startView: start_v,  // 开始视图
            minView: min_v,  // 最小视图
            autoclose: true,  // 选定日期后立即关闭选择器
            format: format
        });
    }

    // 启动时,初始化时间选择器.
    (function(){
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
        $('#select_date').val(str);

    })();

    // 安全得分
    let pieChart = echarts.init(document.getElementById('pie'));
    var labelTop = {//上层样式
        normal : {
            color :'#5CF9DC',
            label : {
                show : true,
                position : 'center',
                formatter : '{b}',
                textStyle: {
                    baseline : 'bottom',
                    fontSize:18
                }
            },
            labelLine : {
                show : false
            }
        }
    };
    var labelFromatter = {//环内样式
        normal : {//默认样式
            label : {//标签
                formatter : function (a,b,c){return 100 - c + '%'},
                // labelLine.length：30,  //线长，从外边缘起计算，可为负值
                textStyle: {//标签文本样式
                    color:'black',
                    align :'center',
                    baseline : 'top'//垂直对其方式
                }
            }
        },
    };
    var labelBottom = {//底层样式
        normal : {
            color: '#cdcdcd',
            label : {
                show : true,
                position : 'center',
                fontSize:22
            },
            labelLine : {
                show : false
            }
        },
        emphasis: {//悬浮式样式
            // color: 'rgba( 0,0,0,0)'
        }
    };
    var radius = [105,122];// 半径[内半径，外半径]
    pieChart.setOption({
        animation:false,
        tooltip : {         // 提示框. Can be overwrited by series or data
            trigger: 'axis',
            //show: true,   //default true
            showDelay: 0,
            hideDelay: 50,
            transitionDuration:0,
            borderRadius : 8,
            borderWidth: 1,
            padding: 10,    // [5, 10, 15, 20]
        },
        series : [
            {
                type : 'pie',
                center : ['50%', '50%'],//圆心坐标（div中的%比例）
                radius : radius,//半径
                x: '0%', // for
                itemStyle : labelTop,//graphStyleA,//图形样式 // 当查到的数据不存在（并非为0），此属性隐藏
                data : [
                    {name:parseInt(50+50*Math.random())+'分', value:79,itemStyle : labelTop},
                    {name:'安全得分', value:21, itemStyle : labelBottom}
                ]
            }
        ]
    });


// 生理状态汇总
    let summary_img = echarts.init(document.getElementById('summary_img'));
    summary_img.setOption({
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            data:['优20次','差5次']
        },
        series: [
            {
                name:'访问来源',
                type:'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: false,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '30',
                            fontWeight: 'bold'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {
                        value:20,
                        name:'优20次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#4EB3FF'}
                        }
                    },
                    {
                        value:5,
                        name:'差5次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#FF5D6B'}
                        }
                    }
                ]
            }
        ]
    });
// 汇总 图表2
    let summary_img_two = echarts.init(document.getElementById('summary_img_two'));
    summary_img_two.setOption({
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            x: 'left',
            data:['优20次','差5次']
        },
        series: [
            {
                name:'访问来源',
                type:'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: false,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '30',
                            fontWeight: 'bold'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {
                        value:20,
                        name:'优20次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#4EB3FF'}
                        }
                    },
                    {
                        value:5,
                        name:'差5次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#FF5D6B'}
                        }
                    }
                ]
            }
        ]
    });
// 汇总 图表3
    let summary_img_three = echarts.init(document.getElementById('summary_img_three'));
    summary_img_three.setOption({
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
        },
        legend: {//图标 辅助类提示
            orient: 'vertical',//视图块的 排列
            x: 'left',
            data:['优20次','差5次']
        },
        series: [ //主体柱子
            {
                name:'访问来源',
                type:'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: false,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '30',
                            fontWeight: 'bold'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {
                        value:20,
                        name:'优20次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#4EB3FF'}
                        }
                    },
                    {
                        value:5,
                        name:'差5次',
                        fontSize:'12',
                        itemStyle:{
                            normal:{color:'#FF5D6B'}
                        }
                    }
                ]
            }
        ]
    });

// 不良驾驶行为
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
                type : 'shadow'        // 默认为猜猜猜直线，可选为：'line' | 'shadow'
            }
        },
        legend: {
            // orient: 'vertical',
            itemWidth: 10,
            itemHeight: 10,
            itemGap: 10,
            x: 'right'
        },
        dataset: {
            source: [
                ['疲劳驾驶', 43.3, 85.8, 93.7],
                ['看手机', 86.4, 65.2, 82.5],
                ['打手机', 72.4, 53.9, 39.1],
                ['急加速', 72.4, 53.9, 39.1],
                ['急转弯', 72.4, 53.9, 39.1],
                ['急刹车', 72.4, 53.9, 39.1],
                ['超速', 72.4, 53.9, 39.1]
            ]
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
                name:'同比',
                type:'bar',
                barWidth: '10',
                itemStyle:{
                    normal:{color:'#ACB0FF'}
                }
            },
            {
                name:'当月',
                type:'bar',
                barWidth: '10',
                itemStyle:{
                    normal:{color:'#95E8FE'}
                }
            },
            {
                name:'环比',
                type:'bar',
                barWidth: '10',
                itemStyle:{
                    normal:{color:'#FFC572'}
                }
            }
        ]
    });




// end!
});
