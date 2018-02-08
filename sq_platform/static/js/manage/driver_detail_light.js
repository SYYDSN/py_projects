$(function() {
    let normal_color = "#a1a1a1";
    let good_color = "#87aafb";
    let bad_color = "#f8b767";
    let cur_user_id = get_url_arg("user_id"); // 待查询用户的id
    $("#cur_user_id").text(cur_user_id);  // 给隐藏元素赋值,用于传递变量
    let popover_conf= false; // 部门信息和车辆信息的弹出框配置是否配置过?

    // 显示loading动画
    show_loading_animation = function(){
        let html = `<div style="font-size:1.4rem;padding-right:1.0em"><img style="width:1.5em;height:1.5em;margin-right:1em" src="../static/image/icon/gif3.gif">正在努力查询中,请稍后...</div>`;
        pop_tip_div_plus("show", html);
    };

    // 关闭loading动画
    close_loading_animation = function(){
        pop_tip_div_plus("hide");
    };



    function set_window() {
        /*计算并重设右侧边栏高度*/
        $("#right_bar").css("height", $(".main_row").height());
    }

    window.onresize = function() {
        // 修改窗口大小事件
        set_window();
    };

    //popover信息弹出框的配置
    function init_popover_conf(arg_dict,$obj){

        let id = $obj.attr("id");
        let key_list = ["公司名称", "职务", "所属部门", "部门领导", "上级部门"];
        let title = "部门信息";
        let left = "40%";
        let outer = $("#my_table_outer_dept");
        let arrow = $("#popover_info_dept .arrow");
        if(id === "truck_info_img"){
            key_list = ["车辆号牌", "车辆类型", "车辆型号", "车架号码", "发动机号", "注册地区", "注册日期", "发证日期"];
            title = "车辆信息";
            left = "70%";
            outer = $("#my_table_outer_truck");
            arrow = $("#popover_info_truck .arrow");
        }else{}

        let l = key_list.length;
        let max_l = Math.ceil(l / 5) * 5;
        let data_group = [];
        // 以5个为一组,截断索引,用于添加多个table
        let index_temp = [];
        for(let i=0;i<max_l;i++){

            index_temp.push(typeof(key_list[i])==="undefined"?"":key_list[i]);
            if(i % 5 === 4){
                data_group.push(index_temp);
                index_temp = [];
            }
        }

        // 填充
        let html = '';
        for(let i=0;i<data_group.length;i++){
            let data = data_group[i];
            let temp = `<table class="table my_table">
                                            <tr>
                                                <th>${data[0]}</th>
                                                <th>${data[1]}</th>
                                                <th>${data[2]}</th>
                                                <th>${data[3]}</th>
                                                <th>${data[4]}</th>
                                            </tr>
                                            <tr>
                                                <td>${data[0]===""?"":arg_dict[data[0]]}</td>
                                                <td>${data[1]===""?"":arg_dict[data[1]]}</td>
                                                <td>${data[2]===""?"":arg_dict[data[2]]}</td>
                                                <td>${data[3]===""?"":arg_dict[data[3]]}</td>
                                                <td>${data[4]===""?"":arg_dict[data[4]]}</td>
                                            </tr>
                                                            
                                          </table>`;
            html += temp;
        }
        outer.append(html);
        arrow.css("left", left);
    }
    // 两个大图标的hover时的popover事件
    $("#dept_info_img, #truck_info_img").each(function(){
        let $this = $(this);
        let pop = $("#popover_info_truck");
        if($.trim($this.attr("id")) === "dept_info_img"){
            pop = $("#popover_info_dept");
        }else{}
        $this.hover(function(){
            pop.show();
        },function(){
            pop.hide();
        });
    });


    // 右侧用户头像导航栏点击跳转事件.
    redirect_driver_detail = function($obj) {
        let user_id = $.trim($obj.attr("data-id"));
        location.href = "/manage/driver_detail?user_id=" + user_id;
    };

    fill_right_bar(redirect_driver_detail);  // 初始化右侧边栏

    // 获取司机信息并填充页面中部的部分,启动页面时调用
    let get_driver_detail = function(args) {
        if(typeof(args) === "undefined"){
            console.log("user_id is " + cur_user_id);
            args = { 'user_id': cur_user_id };
        }else{}
        if (args['user_id'] === null) {
            // pass
        } else {
            console.log("开始向服务器查询安全报告....");
            show_loading_animation(); // 开启查询动画
            $.post(`${server}/manage/driver_detail`, args, function(json) {
                close_loading_animation(); // 关闭查询动画
                let resp = JSON.parse(json);
                if (resp['message'] !== "success") {
                    alert(resp['message']);
                } else {
                    let data = resp['data'];
                    console.log(data);
                    // 无论有没有获取到安全报告,都可以整理部门信息和车辆信息.
                    // 整理部门信息和车辆信息
                    if(!popover_conf){
                        let dept_dict = {};
                        dept_dict["公司名称"] = typeof(data['company_name'])==="undefined"?"":data['company_name'];
                        dept_dict["职务"] = typeof(data['post_name'])==="undefined"?"":data['post_name'];
                        dept_dict["所属部门"] = typeof(data['dept_name'])==="undefined"?"":data['dept_name'];
                        dept_dict["部门领导"] = typeof(data['leader_name'])==="undefined"?"":data['leader_name'];
                        dept_dict["上级部门"] = typeof(data['prev_dept'])==="undefined"?"":data['prev_dept'];
                        init_popover_conf(dept_dict, $("#dept_info_img"));

                        let truck_dict = {};
                        let license_data = data['car_licenses'];  // 取行车证信息.
                        /*car_licenses一定是一个数组对象.一定有.但为了防止特殊意外,仍然要进行防错处理*/
                        license_data = typeof(license_data)==="undefined"?[]:license_data;
                        if(license_data.length > 0){
                            license_data = license_data[0];  // 取第一个值为准
                            truck_dict["车辆号牌"] = typeof(license_data['plate_number'])==="undefined"?"":license_data['plate_number'];
                            truck_dict["车辆类型"] = typeof(license_data['car_type'])==="undefined"?"":license_data['car_type'];
                            truck_dict["车辆型号"] = typeof(license_data['car_model'])==="undefined"?"":license_data['car_model'];
                            truck_dict["车架号码"] = typeof(license_data['vin_id'])==="undefined"?"":license_data['vin_id'];
                            truck_dict["发动机号"] = typeof(license_data['engine_id'])==="undefined"?"":license_data['engine_id'];
                            truck_dict["注册地区"] = typeof(license_data['register_city'])==="undefined"?"":license_data['register_city'];
                            truck_dict["注册日期"] = typeof(license_data['register_date'])==="undefined"?"":license_data['prev_dept'];
                            truck_dict["发证日期"] = typeof(license_data['issued_date'])==="undefined"?"":license_data['issued_date'];
                        }
                        else{
                            // 虚拟车辆信息用于测试
                            truck_dict["车辆号牌"] = "沪A0012E";
                            truck_dict["车辆类型"] = "重型货车";
                            truck_dict["车辆型号"] = "东风140";
                            truck_dict["车架号码"] = "ddsk3432ak230212a";
                            truck_dict["发动机号"] = "AS39801";
                            truck_dict["注册地区"] = "上海";
                            truck_dict["注册日期"] = "2010-12-12";
                            truck_dict["发证日期"] = "2014-9-1";
                        }
                        init_popover_conf(truck_dict, $("#truck_info_img"));

                    }else{}
                    // 整理车辆信息
                    if(popover_conf){
                        let license_data = data['car_licenses'];
                        license_data = typeof(license_data)==="undefined"?[]:license_data;
                        let temp = [];
                        temp.push(typeof(license_data['plate_number'])==="undefined"?"":license_data['plate_number']);
                        temp.push(typeof(license_data['car_type'])==="undefined"?"":license_data['car_type']);
                        temp.push(typeof(license_data['car_model'])==="undefined"?"":license_data['car_model']);
                        temp.push(typeof(license_data['vin_id'])==="undefined"?"":license_data['vin_id']);
                        temp.push(typeof(license_data['engine_id'])==="undefined"?"":license_data['engine_id']);
                    }else{}

                    if(typeof(data['drive_score']) === "undefined" ){
                        // 没有获取对应的安全报告.
                        let ms = typeof(args['date'])==="undefined"?"用户暂无安全报告记录": `没有查询到${args["date"]}的安全报告`;
                        pop_tip_div(ms);
                    }
                    else{
                        // 查询到安全报告了,要进行页面的填充工作
                        let now = new Date();
                        let report_datetime = data['report_datetime'];  // 报告时间
                        /*
                        * 排班数据,排版是一个数组的数组,元素是一个二元数组,上班和持续时间.
                        * 比如一个scheduling对象可能看起来是这样的:
                        * scheduling = [["09:00", 9]];
                        * 表示这个排版只有一个时间段,就是从早9点到晚六点(9点+9个小时)
                        * scheduling = [["09:00", 3], ["13:00",5]]
                        * 表示这个排版有2个时间段,一个时间段是上午9点到12点(+3小时),一个时间段是下午1点到6点(13:00+5个小时)
                        * */
                        let scheduling = data['scheduling'];
                        scheduling = typeof(scheduling)==="undefined"?[["09:00", 9]]:scheduling;
                        /* 由于数据字典的key的名称和元素的id约定的是一致的,所以这里有一个简化的方法来给dom赋值*/
                        let keys = Object.keys(data);
                        let l = keys.length;
                        for (let i = 0; i < l; i++) {
                            let key = keys[i];
                            let value = data[key];
                            if (key === "password") {
                                // pass 密码忽略
                            }
                            else if(key === "bad_drive_action"){
                                // 处理不良驾驶行为的数据.
                                init_bad_action_chart(value);
                            }
                            else if (key === "health") {
                                // 拆分健康相关数据
                                let mood_dict = value['mood']['value']; // 情绪字典
                                let heart_rate_dict = value['heart_rate']['value']; // 心跳字典
                                let sleep_time = value['sleep_time']['value']; // 休息小时数

                                // 处理心跳数据
                                let heart_rate_data = []; // 初始化折线图的心跳数据容器
                                let heart_rate_index = Object.keys(heart_rate_dict); // 初始化折线图的心跳索引容器
                                heart_rate_index.sort(compare_hour_and_minute_str); // 排序
                                let l_1 = heart_rate_index.length;
                                for(let i=0;i<l_1;i++){
                                    let key = heart_rate_index[i];
                                    let val = heart_rate_dict[key];
                                    heart_rate_data.push(val);
                                }

                                init_heart_chart(heart_rate_index, heart_rate_data, report_datetime, scheduling); // 初始化心跳折线图和表格

                                // 处理情绪数据
                                let mood_data = []; // 初始化折线图的情绪数据容器
                                let mood_index_raw = Object.keys(mood_dict);
                                mood_index_raw.sort(compare_hour_and_minute_str);
                                let mood_index = []; // 初始化折线图的情绪索引容器
                                let l_2 = mood_index_raw.length;
                                for(let i=0;i<l_2;i++){
                                    let key = mood_index_raw[i];
                                    let val = mood_dict[key];
                                    mood_index.push(key);
                                    mood_data.push(val);
                                }
                                init_mood_chart_scatter(mood_index, mood_data, report_datetime, scheduling);  // 可视化情绪数据

                                // 开始处理睡眠数据
                                let sleep_time2 = sleep_time < 7 ? "差" : (sleep_time < 8 ? "良" : "优");
                                $("#sleep_time").text(sleep_time + "小时");
                                $("#sleep_time2").text(sleep_time2);
                            } else if (key === "driving_hours_sum") {
                                $("#progress_02").css("width", "54%").text(float_to_string(value)); // 驾驶总时长
                            } else if (key === "total_mileage") {
                                $("#progress_01").css("width", "67%").text(parseFloat(value).toFixed(1) + "公里"); // 总里程
                            } else if (key === "drive_score") {
                                init_security_score(value); // 初始化安全得分/驾驶得分
                            } else if (key === "head_img_url") {
                                $(`#${key}`).attr("src", `../${value}`); // 头像
                            } else {
                                $(`#${key}`).text(value);
                            }
                        }
                        // 原始输出里面没有平均速度.
                        let total_mileage = data['total_mileage'];
                        let driving_hours_sum = data['driving_hours_sum'];
                        let avg_speed = ((isNaN(total_mileage) ? 0 : parseFloat(total_mileage)) / parseFloat(driving_hours_sum)).toFixed(1);
                        $("#avg_speed").text(avg_speed); // 平均时速赋值
                        // 调整日期选择器的值为安全报告的生成日期
                        change_datepicker_val(data['report_datetime']);
                    }
                }
            set_window();
            });
        }
    };
    get_driver_detail();

    // 初始化安全得分仪表盘
    init_security_score = function(score) {
        $("#GaugeMeter_1").remove();
        var g = $("<div class='GaugeMeter' id='GaugeMeter_1'></div>");
        $("#dash_board_outer").append(g);
        g.attr({
            "data-percent": score,
            "data-size": 300,
            "data-label": "综合指数",
            "data-color": "#7C8FF3",
            "data-back": "#96e4ff",
            "data-width": "20",
            "data-label-color": "#565656"
        }).gaugeMeter();
    };

    // 初始心跳化折线图表
    init_heart_chart = function(index, data, report_datetime, scheduling_list) {
        // 根据排班信息,预处理数据
        let new_data = [];  // 经过排班处理的心跳数据
        let now = new Date();
        let year = now.getFullYear();
        let month = now.getMonth() + 1;
        let day = now.getDate();
        let index_begin = 999;   // 索引的取值范围开始
        let index_end = 0;   // 索引的取值范围结束
        for(let scheduling of scheduling_list){
            /*
            javascript的Date构造器接受一下五种格式.注意前两种参数是字符串,后面的3种参数是数字格式
            new Date("month dd,yyyy hh:mm:ss");
            new Date("month dd,yyyy");
            new Date(yyyy,mth,dd,hh,mm,ss);
            new Date(yyyy,mth,dd);
            new Date(ms);
            * */
            let begin_hour_str = `${month} ${day},${year} ${scheduling[0]}:00`;
            let begin_hour = new Date(begin_hour_str);  // 本段排班的开始时间,date对象.
            let duration = parseFloat(scheduling[1]);       // 本段排版持续时长,单位小时
            let begin_time = begin_hour.getTime();          // 本段排班开始时间,转成毫秒是为了方便计算.
            let end_time = begin_time + duration * 3600000; // 本段排班结束时间,转成毫秒是为了方便计算.
            // 看看是不是当天?不能显示还未发生的事情
            if(is_today(report_datetime)){
                let cur_time = new Date();
                cur_time = cur_time.getTime();
                if(cur_time < end_time){
                    end_time = cur_time;
                }
                else{
                    // pass
                }
            }else{}
            // 注意这里没考虑跨天的问题..
            for(let i=0;i<data.length;i++){
                let cur_time = (new Date(`${month} ${day},${year} ${index[i]}:00`)).getTime();
                if(begin_time <= cur_time && cur_time <= end_time){
                    new_data.push([index[i], data[i]]);
                    if(i > index_end){
                        index_end = i;
                    }
                    if(i < index_begin){
                        index_begin = i;
                    }
                }
            }
        }
        // 截取索引
        let new_index = index.slice(index_begin, (index_end + 3)>(index.length-1)?(index.length-1):(index_end + 3));

        let option = {
            tooltip: {
                trigger: 'axis',
                position: function(pt) {
                    return [pt[0], '10%'];
                }
            },
            title: {
                left: 'center',
                text: '24小时心率折线图',
            },
            toolbox: {
                feature: {
                    dataZoom: {
                        yAxisIndex: 'none'
                    },
                    restore: {},
                    saveAsImage: {}
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: new_index
            },
            yAxis: {
                type: 'value',
                min: 30,
                boundaryGap: [0, '100%'],
                splitLine: {
                    show: false    // 不显示分割线
                }
            },
            series: [{
                name: '心率',
                type: 'line',
                // symbol: "rect",  // 标记点形状
                showSymbol: false, // 不显示拐点,设置为false时,上面的symbol选项就无效了.
                smooth: true, // 平滑折线
                data: new_data, // 数据,数组,或者数组的数组
                itemStyle: {
                    normal: {
                        lineStyle: {
                            color: "#7C8FF3", // 折线颜色
                        }
                    }
                },
                areaStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                            offset: 0,
                            color: "#7C8FF3"
                        }, {
                            offset: 1,
                            color: 'white'
                        }])
                    }
                },
                markLine: { // 水平/垂直的标志线
                    symbol:['none', 'none'],  // 标志线两端无形状

                    data:[
                        {
                            name: '心率下限标志线',
                            yAxis: 60,                  // 一根平行x轴的标志线
                            lineStyle: { // 标志线的样式
                                normal: { // 一般样式
                                    color: bad_color, // 线颜色
                                    width: 0.5, // 线宽度
                                    type: "solid" // 线类型
                                }
                            },
                            label:{
                                normal:{
                                    formatter:function(){return "心率下限";}
                                }
                            }
                        },
                        {
                            name: '心率上限标志线',
                            yAxis: 100,                  // 一根平行x轴的标志线
                            lineStyle: { // 标志线的样式
                                normal: { // 一般样式
                                    color: bad_color, // 线颜色
                                    width: 0.5, // 线宽度
                                    type: "solid" // 线类型
                                }
                            },
                            label:{
                                normal:{
                                    formatter:function(){return "心率上限";}
                                }
                            }
                        }
                    ]
                }
            }]
        };

        var charts = echarts.init(document.getElementById("heart_rate_chart"));
        charts.setOption(option);
        // 填充心跳数据表格
        let table = $("#heart_rate_table");
        let heart_rate_max = 0;
        let heart_rate_min = 999;
        let sum_val = 0;
        let html_0 = '<tr>';
        let html_1 = '<tr>';
        let html_2 = '<tr>';
        let html_3 = '<tr>';
        let html_4 = '<tr>';
        let html_5 = '<tr>';
        let html = [];
        html.push(html_0);
        html.push(html_1);
        html.push(html_2);
        html.push(html_3);
        html.push(html_4);
        html.push(html_5);
        let date_str = report_datetime;
        if(typeof(date_str) === "undefined"){
            let date = new Date();
            let day = date.getDate();
            date.setDate(day - 1);
            date_str = (date.getMonth() + 1) + "月" + date.getDate() + "日";
        }else{
            date_str = date_str.replace("-","年").replace("-","月") + "日";
        }

        for (let i = 0; i < index.length; i++) {
            let cur = data[i];
            let key = index[i];
            if (cur > heart_rate_max) {
                heart_rate_max = cur;
            }
            if (cur < heart_rate_min) {
                heart_rate_min = cur;
            }
            sum_val += cur;
            let time_str = key.replace(":", "时") + "分";
            let cur_color = cur > 90 ? bad_color : (cur < 70 ? normal_color : good_color);
            let cur_html = `<td style="color:${cur_color};font-size:1.4rem;">
                                <!--<span class="date_str">${date_str}</span>-->
                                <span class="time_str">${time_str}</span>
                                <span class="heart_rate">${(i >= index_begin && i <= index_end)?cur:" "}次/分</span>
                           </td>`;
            let temp = html[i % 6];
            temp += cur_html;
            html[i % 6] = temp;
        }
        let html_str = '';
        for (let i = 0; i < html.length; i++) {
            let temp = html[i];
            temp += "</tr>";
            html_str += temp;
        }
        table.empty().append(html_str);
        let avg_heart_rate = Math.round(sum_val / index.length);
        let avg_heart_rate2 = (avg_heart_rate >= 60 && avg_heart_rate <= 100) ? "好" : "注意";
        $("#avg_heart_rate").text(avg_heart_rate).css("color", (avg_heart_rate < 70 || avg_heart_rate > 90) ? bad_color : good_color);
        $("#avg_heart_rate2").text(avg_heart_rate2).css("color", (avg_heart_rate2 === "注意") ? bad_color : good_color);
        $("#heart_rate_max").text(heart_rate_max).css("color", (heart_rate_max < 70 || heart_rate_max > 90) ? bad_color : good_color);
        $("#heart_rate_min").text(heart_rate_min).css("color", (heart_rate_min < 70 || heart_rate_min > 90) ? bad_color : good_color);
    };

    // 初始情绪化折线图表1,目前处于弃用状态,已被热力图替代.2018-01-04
    init_mood_chart = function(index, data) {
        // 先计算平均值,提前计算的原因是接下来的并接要用计算情绪的函数.
        let sum_val = 0;
        let index_l = index.length;
        for (let i = 0; i < index_l; i++) {
            let cur = data[i];
            sum_val += cur;
        }
        let avg_mood = Math.round(sum_val / index_l);
        function mood(num){
            // 根据情绪值判断情绪状态,和平均值相差大于15可以认为是出现了情绪的波动.
            let delta = parseInt(num) - avg_mood;
            let mood = '平稳';
            if(delta <= -15){
                mood = "低落"
            }
            else if(delta >= 15){
                mood = "焦躁"
            }
            else{
                // pass
            }
            return mood;
        }
        // 图的配置
        let option = {
            grid:{
                top:"5%",
                left:"12%",
                right:"0%",
                bottom:60
            },
            title: {
                show:false
            },
            toolbox: {
                show:false
            },
            tooltip: {
                trigger: 'axis',
                position: function(pt) {
                    return [pt[0], '10%'];
                },
                formatter: function (param) {
                    return mood(param[0]['data']);
                }
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                axisLine:{
                    show:true,
                    lineStyle:{
                        color:"#666666"
                    }
                },
                data: index
            },
            yAxis: {
                axisLine:{
                    show:true,
                    lineStyle:{
                        color:"#ddd"
                    }
                },
                axisLabel:{
                    formatter: function(){    // 不显示刻度的值
                        return "";
                    }
                },
                axisTick:{
                    show:false
                },
                splitLine: {
                    show: false    // 不显示分割线
                }
            },
            series: [{
                name: '情绪',
                type: 'line',
                // symbol: "rect",  // 标记点形状
                showSymbol: false, // 不显示拐点,设置为false时,上面的symbol选项就无效了.
                smooth: true, // 平滑折线
                data: data, // 数据,数组,或者数组的数组
                itemStyle: {
                    normal: {
                        lineStyle: {
                            color: "#7C8FF3", // 折线颜色
                        }
                    }
                },
                areaStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                            offset: 0,
                            color: "#7C8FF3"
                        }, {
                            offset: 1,
                            color: 'white'
                        }])
                    }
                },
                markLine: { // 水平/垂直的标志线
                    silent:true,
                    symbol:['none', 'none'],  // 标志线两端无形状
                    label:{
                        normal:{
                            show:false    // 不显示标志线的标签
                        }
                    },
                    data:[
                        {
                            name: '',
                            yAxis: avg_mood,                  // 一根平行x轴的标志线
                            lineStyle: { // 标志线的样式
                                normal: { // 一般样式
                                    color: good_color, // 线颜色
                                    width: 0.5, // 线宽度
                                    type: "solid" // 线类型
                                }
                            }
                        }
                    ]
                }
            }]
        };

        var charts = echarts.init(document.getElementById("mood_chart"));
        charts.setOption(option);
        // 填充情绪数据表格
        let table = $("#mood_table");
        let mood_max = 0;
        let mood_min = 999;
        let html = '';

        // 循环拼接html
        for (let i = 0; i < index_l; i++) {
            if(i % 12 === 0){
                html += "<tr>";
            }
            let cur = data[i];
            let key = index[i];
            if (cur > mood_max) {
                mood_max = cur;
            }
            if (cur < mood_min) {
                mood_min = cur;
            }

            cur = mood(cur);
            let cur_color = cur != "平稳" ? bad_color : normal_color;
            let cur_html = `<td class="mood_item" style="color:${cur_color}">
                                <span class="time">${key.split(":")[0]}时</span>
                                <span class="status">${cur}</span>
                           </td>`;
            html += cur_html;
            if(i % 12 === 11){
                html += "</tr>";
            }
        }
        table.empty().append(html);
        // $("#avg_heart_rate").text(avg_heart_rate).css("color", (avg_heart_rate < 70 || avg_heart_rate > 90) ? bad_color : good_color);
        // $("#avg_heart_rate2").text(avg_heart_rate2).css("color", (avg_heart_rate2 === "注意") ? bad_color : good_color);
        // $("#heart_rate_max").text(heart_rate_max).css("color", (heart_rate_max < 70 || heart_rate_max > 90) ? bad_color : good_color);
        // $("#heart_rate_min").text(heart_rate_min).css("color", (heart_rate_min < 70 || heart_rate_min > 90) ? bad_color : good_color);
    };

    // 初始化情绪热力图,高总的方案,目前使用的情绪方案
    init_mood_chart_scatter = function(index, data, report_datetime, scheduling_list) {
        /* 先计算平均值,提前计算的原因是接下来的并接要用计算情绪的函数.
        index是x轴数据.
        data是y轴数据.
        report_datetime是数据的日期.
        scheduling_list 是排班
         */
        let sum_val = 0;
        let index_l = index.length;
        for (let i = 0; i < index_l; i++) {
            let cur = data[i];
            sum_val += cur;
        }
        let avg_mood = Math.round(sum_val / index_l);
        let threshold = 10;   // 判断情欲是否平稳的阈值
        let size = 25;        // 圆形标记点的尺寸
        function mood(num){
            // 根据情绪值判断情绪状态,和平均值相差大于15可以认为是出现了情绪的波动.
            let delta = Math.abs(parseInt(num) - avg_mood);
            let mood = '平稳';
            if(delta >= threshold){
                mood = "焦躁"
            }
            else{
                // pass
            }
            return mood;
        }

        let data_01_good = [],data_01_bad = [], data_02_good = [], data_02_bad = [];
        let can_show_index = [];  // 可以被显示的元素的索引,用于匹配循环拼接html的元素
        let now = new Date();
        let year = now.getFullYear();
        let month = now.getMonth() + 1;
        let day = now.getDate();

        for(let scheduling of scheduling_list){
            /*
            javascript的Date构造器接受一下五种格式.注意前两种参数是字符串,后面的3种参数是数字格式
            new Date("month dd,yyyy hh:mm:ss");
            new Date("month dd,yyyy");
            new Date(yyyy,mth,dd,hh,mm,ss);
            new Date(yyyy,mth,dd);
            new Date(ms);
            * */
            let begin_hour_str = `${month} ${day},${year} ${scheduling[0]}:00`;
            let begin_hour = new Date(begin_hour_str);  // 本段排班的开始时间,date对象.
            let duration = parseFloat(scheduling[1]);       // 本段排版持续时长,单位小时
            let begin_time = begin_hour.getTime();          // 本段排班开始时间,转成毫秒是为了方便计算.
            let end_time = begin_time + duration * 3600000; // 本段排班结束时间,转成毫秒是为了方便计算.
            // 看看是不是当天?不能显示还未发生的事情
            if(is_today(report_datetime)){
                let cur_time = new Date();
                cur_time = cur_time.getTime();
                if(cur_time < end_time){
                    end_time = cur_time;
                }
                else{
                    // pass
                }
            }else{}
            // 注意这里没考虑跨天的问题..
            for(let i=0;i<data.length;i++){
                let cur_time = (new Date(`${month} ${day},${year} ${index[i]}:00`)).getTime();
                if(begin_time <= cur_time && cur_time <= end_time){
                    if(i in can_show_index){
                        // nothing...
                    }
                    else{
                        can_show_index.push(i);
                    }
                    let temp = [i % 12, 1, data[i]];
                    let abs = Math.abs(parseInt(temp[2]) - avg_mood);
                    if(i < 12){
                        if(abs >= threshold){
                            data_01_bad.push(temp);
                        }else{
                            data_01_good.push(temp);
                        }
                    }else{
                        if(abs >= threshold){
                            data_02_bad.push(temp);
                        }else{
                            data_02_good.push(temp);
                        }
                    }
                }
            }

        }

        let bad_item_style = {
                        shadowBlur: 10,
                        shadowColor: 'rgba(120, 36, 50, 0.5)',
                        shadowOffsetY: 5,
                        color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [{
                            offset: 0,
                            color: 'rgb(251, 118, 123)'
                        }, {
                            offset: 1,
                            color: 'rgb(204, 46, 72)'
                        }])
                    };
        let good_item_style = {
                shadowBlur: 10,
                shadowColor: 'rgba(25, 100, 150, 0.5)',
                shadowOffsetY: 5,
                color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [{
                    offset: 0,
                    color: 'rgb(129, 227, 238)'
                }, {
                    offset: 1,
                    color: 'rgb(25, 183, 207)'
                }])
            };

        let option = {
            grid: [{
                x: '0%',
                y: '0%',
                left:"4%",
                height: '38%'
            }, {
                x: '0%',
                y2: '0%',
                left:"4%",
                height: '38%',
                bottom:20
            }],
            tooltip: {
                formatter: function(params, ticket, callback){
                    /*第一个参数 params 是 formatter 需要的数据集
                    * 第二个参数 ticket 是异步回调标识
                    * 第三个参数 callback 是异步回调
                    * 详细用法请参考 http://echarts.baidu.com/option.html#tooltip.formatter
                    * */
                    return mood(params.data[2]);
                }
            },
            xAxis: [{
                gridIndex: 0,
                nameTextStyle:{
                    fontSize:10
                },
                data:index.slice(0, 12)
            }, {
                gridIndex: 1,
                nameTextStyle:{
                    fontSize:10
                },
                data:index.slice(12)
            }],
            yAxis:[{
                gridIndex: 0,
                show:false,
                min: 0,
                max:2
            }, {
                gridIndex: 1,
                show:false,
                min: 0,
                max: 2
            }],
            series: [{
                type: 'scatter',
                xAxisIndex: 0,   // 通过xAxisIndex和yAxisIndex可以确认绘制在哪一个子图表中
                yAxisIndex: 0,
                /*自定义图标的方法,注意开头是image://格式*,svg格式暂时没有成功*/
                symbol:`image:///static/image/manage/icon_buxiao.png`,
                symbolSize: size,
                itemStyle: {
                    normal:{
                        color:"#f8b767"
                    }
                    // normal: bad_item_style
                },
                data: data_01_bad
            },
                {
                name: 'AM',
                type: 'scatter',
                xAxisIndex: 0,
                yAxisIndex: 0,
                /*自定义图标的方法,注意开头是image://格式*,svg格式暂时没有成功*/
                symbol:`image:///static/image/manage/icon_xiao.png`,
                symbolSize: size,
                itemStyle: {
                    normal:{
                        color:"#18CD3B"
                    }
                    // normal: good_item_style
                },
                data: data_01_good
            }, {
                name: 'PM',
                type: 'scatter',
                xAxisIndex: 1,
                yAxisIndex: 1,
                /*自定义图标的方法,注意开头是image://格式*,svg格式暂时没有成功*/
                symbol:`image:///static/image/manage/icon_buxiao.png`,
                symbolSize: size,
                itemStyle: {
                    normal:{
                        color:"#18CD3B"
                    }
                    // normal: good_item_style
                },
                data: data_02_bad
            }, {
                type: 'scatter',
                xAxisIndex: 1,
                yAxisIndex: 1,
                /*自定义图标的方法,注意开头是image://格式*,svg格式暂时没有成功*/
                symbol:`image:///static/image/manage/icon_xiao.png`,
                symbolSize: size,
                itemStyle: {
                    normal:{
                        color:"#f8b767"
                    }
                    // normal: bad_item_style
                },
                data: data_02_good
            }]
        };

        let charts = echarts.init(document.getElementById("mood_chart"));
        charts.setOption(option);
        // 填充情绪数据表格
        let table = $("#mood_table");
        let mood_max = 0;
        let mood_min = 999;
        let html = '';

        // 循环拼接html
        for (let i = 0; i < index_l; i++) {
            if(i % 12 === 0){
                html += "<tr>";
            }
            let cur = data[i];
            let key = index[i];
            if (cur > mood_max) {
                mood_max = cur;
            }
            if (cur < mood_min) {
                mood_min = cur;
            }
            if(can_show_index.indexOf(i) !== -1){
                cur = mood(cur);
            }
            else{
                cur = "";
            }
            let cur_color = (cur != "" && cur != "平稳") ? bad_color : normal_color;
            let cur_html = `<td class="mood_item" style="color:${cur_color}">
                                <span class="time">${key.split(":")[0]}时</span>
                                <span class="status">${cur}</span>
                           </td>`;
            html += cur_html;
            if(i % 12 === 11){
                html += "</tr>";
            }
        }
        table.empty().append(html);

    };

    // 初始化不良行为柱装图
    init_bad_action_chart = function(data_list) {
        /*需要先拆分数据,data_list是数组格式的*/

        // 映射字典,目前,急左转和急右转都是急转.两个映射字典是因为字段格式从空格改为下划线,用于兼容.
        let key_name_dict_1 = {
            'speeding drive': '超速行驶',
            'speeding left turn': '急转',
            'speeding right turn': '急转',
            'calling drive': '打电话',
            'quickly accelerate': "急加速",
            'quickly decelerate': "急减速",
            'fatigue drive': '疲劳驾驶',
            'play phone drive': '玩手机',
            'quick lane': '急变道'
        };
        let key_name_dict_2 = {
            'speeding_drive': '超速行驶',
            'speeding_left_turn': '急转',
            'speeding_right_turn': '急转',
            'calling_drive': '打电话',
            'quickly_accelerate': "急加速",
            'quickly_decelerate': "急减速",
            'fatigue_drive': '疲劳驾驶',
            'play_phone_drive': '玩手机',
            'quick_lane': '急变道'
        };
        let l = data_list.length;
        if (l === 0){
            // pass
        }
        else{
            let dict = {};   // 存放事件和计数的字典容器
            // 真实的柱装图排序
            let keys = ["疲劳驾驶", "打电话", "玩手机", "超速行驶", "急加速", "急减速", "急转", "急变道"];
            let d_k = keys.length;
            // 初始化一数据字典的键,值全部至0,用于计数
            for(let i=0;i<d_k;i++){
                let key = keys[i];
                dict[key] = 0;
            }
            let max_count = 0;
            // 轮询事件数组,对不同的事件进行分别计数.
            for(let i=0;i<l;i++){
                let item = data_list[i];
                let key = item['type'];
                let name = key_name_dict_1[key];
                name = typeof(name) === "undefined"?key_name_dict_2[key]: name;
                if(typeof(name) !== "undefined"){
                    let count = dict[name];
                    if(typeof(count) === "undefined"){
                        // 新的类型.
                        count = 1;
                    }
                    else{
                        count = parseInt(count) + 1;
                    }
                    dict[name] = count;
                    if(count > max_count){
                        max_count = count;
                    }
                }
            }
            let index = Object.keys(dict);
            let data = new Array();
            let l2 = index.length;
            for(let i=0;i<l2;i++){
                data.push(dict[index[i]]);
            }

            let option2 = {
                itemStyle:{
                    normal:{
                        color:new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                            offset: 0,
                            color: "#7C8FF3"
                        }, {
                            offset: 1,
                            color: '#9DAAF3'
                        }])
                    }
                },
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
                        data : index,
                        axisTick: {
                            alignWithLabel: true
                        }
                    }
                ],
                yAxis : [
                    {
                        type : 'value',
                        interval:1,
                        max: max_count < 3? 3: max_count + 2
                    }
                ],
                series : [
                    {
                        name:'统计',
                        type:'bar',
                        barWidth: '60%',
                        data:data
                    }
                ]
            };

            let charts = echarts.init(document.getElementById("bad_action_chart"));
            charts.setOption(option2);
        }
    };

    // 初始化日期选择器
    (function (last_date_str) {
        // 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/
        // 参数last_date_str是最后一个可用的日期
        $("#date_picker").datetimepicker({
            language: "zh-CN",
            weekStart:1,  // 星期一作为一周的开始
            minView: 2,  // 不显示小时和分
            autoclose: true,  // 选定日期后理解关闭选择器
            format: "yyyy-mm-dd"
        }).on("show", function(ev){
            // 当选择器显示时被触发.示范,无实际意义.
            console.log(ev);
            console.log("选择器面板被打开");
        }).on("hide", function(ev){
            // 当选择器隐藏时被触发 示范,无实际意义
            console.log(ev);
            console.log("选择器面板被隐藏");
        }).on("changeDate", function(ev){
            // 当日期被改变时被触发
            console.log(ev);
            console.log("选择器日期被改变");
            let selected_date = ev.date;
            let the_str = `${selected_date.getFullYear()}-${selected_date.getMonth() + 1}-${selected_date.getDate()}`;
            console.log(the_str);
            $("#date_picker_submit_btn").click();  // 触发查询司机安全报告
        });
    })();

    // 日期选择器提交按钮的事件
    $("#date_picker_submit_btn").click(function(){
        let date_str = $.trim($("#date_picker").val());
        let user_id = $.trim($("#cur_user_id").text());
        let date_list = date_str.split("-");
        let year = date_list[0];
        /*防止浏览器之间的差异,这里必须做手动转换,以保证时间字符串格式的一致性*/
        let month = String(date_list[1]).length < 1? "0" + date_list[1]:date_list[1];
        let day = String(date_list[2]).length < 1? "0" + date_list[2]:date_list[2];
        let date = `${year}-${month}-${day}`;
        let arg_dict = {"user_id": user_id, 'date': date};
        get_driver_detail(arg_dict);

    });

    // 改变日期选择器的日期为最后一次成功获取数据的日期
    change_datepicker_val = function(date_str){
        $("#date_picker").val(date_str);
    };

    // end!
});
