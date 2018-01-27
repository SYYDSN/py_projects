$(function() {
    function getState(state_num) {
        // 获取情绪,睡眠图标的函数
        if (state_num <= 60) {
            return '../static/image/head_img/cha.png';
        } else if (state_num <= 80) {
            return '../static/image/head_img/liang.png';
        } else if (state_num <= 100) {
            return '../static/image/head_img/you.png';
        }
    }

    // 直方图
    let bad_drive_column = function (data) {
        // 不良驾驶初始化函数
        let acce = typeof(data['sum_cnt_rapi_acce']) === 'undefined' ? data['cnt_rapi_acce'] : data['sum_cnt_rapi_acce'];
        let turn = typeof(data['sum_cnt_shar_turn']) === 'undefined' ? data['cnt_shar_turn'] : data['sum_cnt_shar_turn'];
        let brak = typeof(data['sum_cnt_sudd_brak']) === 'undefined' ? data['cnt_sudd_brak'] : data['sum_cnt_sudd_brak'];
        var myBadCenter = echarts.init(document.getElementById("bad-drive-center"));
        var badOption = {
            color: ['#3398DB'],
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: ['急加速', '急转弯', '急刹车', '超速', '疲劳驾驶'],
                    axisTick: {
                        alignWithLabel: true
                    }
                }
            ],
            yAxis: [
                {
                    name: '(次)',
                    min: 0,
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '事件次数',
                    type: 'bar',
                    barWidth: '60%',
                    data: [
                        acce, turn, brak, 0, 0]
                }
            ]
        };
        myBadCenter.setOption(badOption);

        var bad_drive_html = '<li><i></i><span>急加速事件次数</span><span>' + acce
            + '</span></li>' +
            '<li><i></i><span>急转弯事件次数 </span><span>' + turn + '</span></li>' +
            '<li><i></i><span>急刹车事件次数</span><span>' + brak + '</span></li>' +
            '<li><i></i><span>超速事件次数</span><span>' + 0
            + '</span></li>' +
            '<li><i></i><span>疲劳驾驶事件次数</span><span>0</span></li>';
        $(".bad-drive-data ul").html(bad_drive_html);
    };
    let bad_headle_column = function (data) {
        // 不良操作行为函数
        var myHeadCenter = echarts.init(document.getElementById("bad-headle-center"));
        var HeadOption = {
            color: ['#3398DB'],
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: ['看手机', '打手机'],
                    axisTick: {
                        alignWithLabel: true
                    }
                }
            ],
            yAxis: [
                {
                    name: '(次)',
                    min: 0,
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '事件次数',
                    type: 'bar',
                    barWidth: '50',
                    data: [data[0], data[1]]
                }
            ]
        };
        myHeadCenter.setOption(HeadOption);
    };

    function repair_date_format(a_str) {
        // 修正日期的格式
        let temp = a_str.split("-");
        let y = temp[0];
        let m = temp[1];
        let d = temp[2];
        m = m.length < 2 ? "0" + m : m;
        d = d.length < 2 ? "0" + d : d;
        let format = y + "-" + m + "-" + d;
        return format;
    }
    show_report = function(arg){
    // 选择日期后的按钮事件
    let str = $.trim($("#text").val());
    str =repair_date_format(str);
    if(typeof(arg) !== "undefined"){
        str = arg
    }
    var data = current_reports[str];
    console.log(data);
    if(typeof(data) === "undefined"){
        //pass
    }
    else{
        data['rank'] = current_user_archive['rank'];
        init_chart(data);
    }
};


   // 日期高亮事件
    function height_show(){
        $(".layui-laydate-content td[lay-ymd^='2017']").each(function() {
            var $this = $(this);
            var cur = $.trim($this.attr("lay-ymd"));
            cur = repair_date_format(cur);
            console.log(cur);
            if(typeof(current_reports[cur])!="undefined"){
                $this.removeClass("laydate-disabled").addClass("layui-this");
            }
            else{
                $this.addClass("laydate-disabled").removeClass("layui-this");
            }
        });
    }
    $("#text").mouseup(function(){
        height_show();
    });


function init_chart (data){
    /*
    初始化各种仪表显示
    *
    * */

    // 填充不良驾驶数据
    bad_drive_column(data);
    // 填充不良操作数据
    bad_headle_column([
        typeof(data['sum_look_phone']) === "undefined" ?data['look_phone']:data['sum_look_phone'],
        typeof(data['sum_call_phone']) === "undefined" ?data['call_phone']:data['sum_call_phone']
    ]);

    //  情绪和睡眠
    var emotion_status_state = getState(typeof(data['avg_emotion_status'])==='undefined'?data['emotion_status']:data['avg_emotion_status']);
    var life_habits_state = getState(typeof(data['avg_life_habits'])==='undefined'?data['life_habits']:data['avg_life_habits']);

    // 情绪和睡眠的html
    var phy_img_html = `<li class="col-lg-4 col-md-4 col-sm-6 col-xs-12"><div><img src="${emotion_status_state}" alt=""></div><p>情绪状态</p></li>
        <li class="col-lg-4 col-md-4 col-sm-6 col-xs-12"><div><img src="${life_habits_state}" alt=""></div><p>睡眠质量</p></li>
        <li class="col-lg-4 col-md-4 col-sm-6 col-xs-12"><div><img src="../static/image/head_img/you.png" alt=""></div><p>健康状态</p></li>`;
    $(".phy-img ul").html(phy_img_html);

    // 原型标靶
    $("#GaugeMeter_1").remove();
    var g = $("<div class='GaugeMeter' id='GaugeMeter_1'></div>");
    $("#safe_title").after(g);
    g.attr({
            "data-percent": data['scr_synt'],
            "data-size": "300",
            "data-label_color": "#ccc",
            "data-label": "综合指数",
            "data-color" : "#21b3f9",
            "data-back" : "#96e4ff" ,
            "data-width" : "20",
            "data-label_color": "#565656"
      }).gaugeMeter();
    // u填充五角星
    var wjx = null;

    if( data['scr_synt']>=0 && data['scr_synt'] <= 60){
        wjx = '★☆☆☆☆';
        $($(".itsec ul li span")[1]).text(wjx);
    }else if(data['scr_synt'] > 60 && data['scr_synt'] <= 70){
        wjx = '★★☆☆☆';
        $($(".itsec ul li span")[1]).text(wjx);
    }else if(data['scr_synt'] > 70 && data['scr_synt'] <= 80){
        wjx = '★★★☆☆';
        $($(".itsec ul li span")[1]).text(wjx);
    }else if(data['scr_synt'] > 80 && data['scr_synt'] <= 90){
        wjx = '★★★★☆';
        $($(".itsec ul li span")[1]).text(wjx);
    }else if(data['scr_synt'] > 90 && data['scr_synt'] < 100){
        wjx = '★★★★★';
        $($(".itsec ul li span")[1]).text(wjx);
    }
    var safe_html = '<li><i></i><span>安全等级</span><span>'+ wjx +'</span></li>' +
        '<li><i></i><span>安全排名</span><span>'+ data['rank'] +'</span></li>';
    $(".safe ul").html(safe_html);
    // 五角星下方的平均时速
    var drive_data_html = '<li><p>平均时速</p><h2>'+ data['avg_speed'] +'公里/小时</h2></li>';
    $(".drive-data ul").html(drive_data_html);
    // 填充总里程和时长的进度条.
    let t_mile = parseInt(typeof(data['total_mileage'])==='undefined'?data['sum_mile']:data['total_mileage']);
    let t_time = parseInt(typeof(data['driving_hours_sum'])==='undefined'?(data['sum_time']/60):data['driving_hours_sum']);
    var driver_course_html = '<p>行驶公里：<span>'+
        t_mile
        +'</span></p><div id="course-container"></div>';
    $(".driver-course").html(driver_course_html);
    var driver_speed_html = '<p>行驶时长：<span>'+
        t_time
        +'</span></p><div id="speed-container"></div>';
    $(".driver-speed").html(driver_speed_html);
    // 里程进度条
    $('#course-container').jQMeter({
        goal:'$2,0000',
        raised:'$'+ t_mile +'',
        orientation:'horizontal',
        width: '90%',
        height:'53px',
        barColor: '#fd9732',
        bgColor : "#eff0f0",
        displayTotal : false,
        animationSpeed : '5000'
    });
    // 时长进度条
    $('#speed-container').jQMeter({
        goal:'$1,000',
        raised:'$'+ t_time +'',
        orientation:'horizontal',
        width: '90%',
        height:'53px',
        barColor: '#fd9732',
        bgColor : "#eff0f0",
        displayTotal : false,
        animationSpeed : '5000'
    });
};

init_base_info = function(data) {

   /*第一次加载页面时的初始化基础信息*/

   // 年龄
   var age = data.age || 30;
   // 驾龄
   var driving_experience = data.driving_experience || 12;
   // 紧急联系人
   var emergency_contact = data.emergency_contact || data.leader_name;
   // 性别
   var gender = data.gender || "男";
   // 公司名称
   var prev_dept = data.prev_dept || "华新分拨公司";
   // 手机制造商
   var manufacturer = data.manufacturer || 'vivo';
   // 手机型号
   var model = data.model || 'y53';
   // 车牌号
   var plate_number = data.plate_number || "沪A12345";
   // 车辆类型
   var car_type = data.car_type || '重型箱式货车';
   // 车辆型号
   var car_model = data.car_model || "一汽解放J6";
   // 车架号
   var vin_id = data.vin_id || 'D544S2';
   // 发动机号
   var engine_id = data.engine_id || 'AZ544Q';
   // 注册地
   var register_city = data.register_city || "上海市";
   // 注册日期
   var register_date = data.register_date || "2017/5/5";
   // 发证日期
   var issued_date = data.issued_date || "2017/5/5";
   // 安全指数
   var scr_synt = data.scr_synt || 0;
   // 急加速
   var cnt_rapi_acce = data.cnt_rapi_acce || 39;
   // 急转弯
   var cnt_shar_turn = data.cnt_shar_turn || 24;
   // 急刹车
   var cnt_sudd_brak = data.cnt_sudd_brak || 23;
   // 超速
   var cnt_over_sped = data.cnt_over_sped || 0;
   // 驾驶总里程
   var total_mileage = Math.ceil(data.total_mileage) || 0;
   // 驾驶总时长
   var driving_hours_sum = data.driving_hours_sum || 0;
   // 平均速度
   var speed_avg = data.speed_avg || 0;
   // 国家
   var country = data.country || "中国";
   // 省份
   var province = data.province || "上海";
   // 头像
   var head_img_url = "/" + data.head_img_url || "../../static/image/head_img/2015111093556890.jpg";
   //排名
   var rank = data.rank || 1;
   //姓名
   var real_name = data.real_name || data.user_name;
   //电话
   var data_phone_num = data.phone_num || 17923566679;
   //所属部门
   var dept_name = data.dept_name || "测试团队A组";
   //部门领导
   var leader_name = data.leader_name || "奕新军";
   //公司名称
   var company_name = data.company_name || "华新分拨公司";
   //职务
   var post_name = data.post_name || "测试团队司机";

    var info_html = '<div class="img">' +
                                '<span><i>第</i><i>'+ rank +'</i><i>名</i></span>'+
                                '<img src='+head_img_url+'  alt="">' +
                            '</div>' +
                            '<div class="detail-info">' +
                            '<ul class="clearfix">' +
      '<li>'+ real_name +'</li>' +
      '<li>'+ age +'</li>' +
      '<li><i class="iconfont icon-yujing"></i>当前路况良好</li>' +
      '<li>驾龄 : '+ driving_experience +'</li>' +
      '<li>紧急联系人 : '+ emergency_contact +'</li>' +
      '<li>性别 : '+ gender +'</li>' +
      '<li>'+ country + province +'</li>' +
      '<li>手机号码 : '+ data_phone_num +'</li>' +
      '<li>紧急联系人号码 : '+ 17923566679 +'</li>' +
      '<li>职务：'+ post_name +'</li>'+
      '<li>所属部门：'+ dept_name +'</li>'+
      '<li>部门领导：'+ leader_name +'</li>'+
      '<li>上级部门：'+ prev_dept +'</li>'+
      '<li>公司名称：'+ company_name +'</li>'+
      '</ul>'+
                           ' </div>';
    $("#info").append(info_html);
};

     function init_right_bar (data) {
        // 右侧选择用户的导航条
        for (let i = 0; i < data.length; i++) {
            var head_img_url = "/" + data[i].head_img_url || "../../static/image/head_img/default_01.png";
            var real_name = data[i].real_name || data[i].user_name;
            var li = document.createElement("li");
            var img = document.createElement("img");
            var span = document.createElement("span");
            $(span).text(real_name);
            $(img).attr("src", head_img_url);
            $(img).attr("class", "hidden-md hidden-sm hidden-xs");
            $(li).append(img);
            $(li).append(span);
            $(li).attr({id: data[i]._id});
            $(".driver-list-right ul").append(li);
        }
        // 底部右侧返回按钮
        $(".driver-btn button").click(function () {
            history.go(-1);
        });

        $(".driver-list-right ul").on('click', 'li', function () {
            var user_id = $(this).attr("id");
            location.href = location.origin + '/' + location.pathname.split('/')[1] + "/employee_detail?user_id=" + user_id;
        });
    };
    // 日期选择部分

    var text = document.getElementById("text");
    var text1 = document.getElementById("text1");
    var text2 = document.getElementById("text2");
    var btn = $(".date-btn input");
    var date = new Date();
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var max = year +'-'+month+'-'+day;
    var month_len = Math.ceil(day / 7);
    $("#text").val(year+"-"+month+"-"+day);
    for(let i = 1; i <= month_len; i++){
      console.log(i)
      var li = document.createElement("li");
      $(li).html(i + "周");
      $(".month-body ul").append(li);
    }
    function getDay(month,year) {
      if(month === 1 || month === 3 || month === 5 || month === 7 || month === 8 || month === 10 || month === 12){
        return 31;
      }else if(month === 4 || month === 6 || month === 9 || month === 11){
        return 30;
      }else if(month === 2 && (year/4).toString().split(".")[1]){
        return 28;
      }else{
        return 29;
      }
    }
  console.log(day);
  $(".month").click(function(e){
    e.stopPropagation();
  })
  $("#year").html(year + "年");
    $("#month").html(month + "月");
    var year_num = year;
    var month_num = month;
    $($(".month-header").children()[0]).click(function(e){
        year_num -= 1;
        $("#year").html(year_num + "年");
        e.stopPropagation()
    })
    $($(".month-header").children()[1]).click(function(e){
      $(".month-body ul").html("");
      month_num -= 1;
      $("#month").html(month_num + "月");
      let day_num = getDay(month_num,year_num);
      let month_len = Math.ceil(day_num / 7);
      for(let i = 1; i <= month_len; i++){
        let li = document.createElement("li");
        $(li).html(i + "周");
        $(".month-body ul").append(li);
      }
      $(".month-body").on("click","li",function(){
        let text = $(this).text();
        if(text.substr(0, text.length - 1) * 7 > day_num){
          let start = day_num-(6 - (text.substr(0, text.length - 1) * 7 - day_num));
          let end = day_num;
          if(start == end){
            $("#text3").val(year_num+"-"+month_num+"-"+start);
          }else{
            $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
          }
        }else{
          let start = text.substr(0, text.length - 1) * 7 - 6;
          let end = text.substr(0, text.length - 1) * 7;
          if(start == end){
            $("#text3").val(year_num+"-"+month_num+"-"+start);
          }else{
            $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
          }
        }
      })
      e.stopPropagation()
    })
    $($(".month-header").children()[3]).click(function(e){
      $(".month-body ul").html("");
      if(month_num >= month){
        let day_num = day;
        let month_len = Math.ceil(day_num / 7);
        for(let i = 1; i <= month_len; i++){
          let li = document.createElement("li");
          $(li).html(i + "周");
          $(".month-body ul").append(li);
        };
        $(".month-body").on("click","li",function(){
          let text = $(this).text();
          if(text.substr(0, text.length - 1) * 7 > day_num){
            let start = day_num-(6 - (text.substr(0, text.length - 1) * 7 - day_num));
            let end = day_num;
            if(start == end){
              $("#text3").val(year_num+"-"+month_num+"-"+start);
            }else{
              $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
            }
          }else{
            let start = text.substr(0, text.length - 1) * 7 - 6;
            let end = text.substr(0, text.length - 1) * 7;
            if(start == end){
              $("#text3").val(year_num+"-"+month_num+"-"+start);
            }else{
              $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
            }
          }
        });
        return false;
      }
      else{
        month_num += 1;
        $("#month").html(month_num + "月");
        if(month_num == month){
          let day_num = day;
          let month_len = Math.ceil(day_num / 7);
          for(let i = 1; i <= month_len; i++){
            let li = document.createElement("li");
            $(li).html(i + "周");
            $(".month-body ul").append(li);
          }
          $(".month-body").on("click","li",function(){
            let text = $(this).text();
            if(text.substr(0, text.length - 1) * 7 > day_num){
              let start = day_num-(6 - (text.substr(0, text.length - 1) * 7 - day_num));
              let end = day_num;
              if(start == end){
                $("#text3").val(year_num+"-"+month_num+"-"+start);
              }else{
                $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
              }
            }else{
              let start = text.substr(0, text.length - 1) * 7 - 6;
              let end = text.substr(0, text.length - 1) * 7;
              if(start == end){
                $("#text3").val(year_num+"-"+month_num+"-"+start);
              }else{
                $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
              }
            }
          })
        }else{
          let day_num = getDay(month_num,year_num);
          let month_len = Math.ceil(day_num / 7);
          for(let i = 1; i <= month_len; i++){
            let li = document.createElement("li");
            $(li).html(i + "周");
            $(".month-body ul").append(li);
          }
          $(".month-body").on("click","li",function(){
            let text = $(this).text();
            if(text.substr(0, text.length - 1) * 7 > day_num){
              let start = day_num-(6 - (text.substr(0, text.length - 1) * 7 - day_num));
              let end = day_num;
              if(start == end){
                $("#text3").val(year_num+"-"+month_num+"-"+start);
              }else{
                $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
              }
            }else{
              let start = text.substr(0, text.length - 1) * 7 - 6;
              let end = text.substr(0, text.length - 1) * 7;
              if(start == end){
                $("#text3").val(year_num+"-"+month_num+"-"+start);
              }else{
                $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
              }
            }
          })
        }
      }
      e.stopPropagation()
    })
    $($(".month-header").children()[4]).click(function(e){
        if(year_num >=  year){
          return false;
        }else{
          year_num += 1;
          $("#year").html(year_num + "年");
        }
      e.stopPropagation()
    })
  $(".month-body").on("click","li",function(){
    let text = $(this).text();
    if(text.substr(0, text.length - 1) * 7 > day){
      let start = day-(6 - (text.substr(0, text.length - 1) * 7 - day));
      let end = day;
      if(start == end){
        $("#text3").val(year_num+"-"+month_num+"-"+start);
      }else{
        $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
      }
    }else{
      let start = text.substr(0, text.length - 1) * 7 - 6;
      let end = text.substr(0, text.length - 1) * 7;
      if(start == end){
        $("#text3").val(year_num+"-"+month_num+"-"+start);
      }else{
        $("#text3").val(year_num+"-"+month_num+" "+start+"~"+end);
      }
    }
  })
  laydate.render({
        elem: '#text',
        type: 'date',
        max: max
    });

    $("#select").change(function(){
      $(text).val("");
      $(text1).val("");
      $(text2).val("");
      $(text3).val("");
      let val = $(this).val();
      if(val == "月"){
        $(text).css("display","none");
        $(text2).css("display","none");
        $(text1).css("display","block");
        $(text3).css("display","none");
        laydate.render({
          elem: '#text1',
          type: 'month',
          max: month
        });
        btn.on("click",function(){
          if($("#text1").val()){
            console.log($("#text1").val());
          }
        })
      }else if(val == "年"){
        $(text).css("display","none");
        $(text2).css("display","block");
        $(text1).css("display","none");
        $(text3).css("display","none");
        laydate.render({
          elem: '#text2',
          type: 'year',
          max: year.toString()
        });
        btn.on("click",function(){
          if($("#text2").val()){
            console.log($("#text2").val());
          }
        })
      }else if(val == "天"){
        $(text).css("display","block");
        $(text2).css("display","none");
        $(text1).css("display","none");
        $(text3).css("display","none");
        laydate.render({
          elem: '#text',
          type: 'date',
          max: max
        });
        btn.on("click",function(){
          if($("#text").val()){
            console.log($("#text").val());
          }
        })
      }else if(val == "周"){
        $(text).css("display","none");
        $(text2).css("display","none");
        $(text1).css("display","none");
        $(text3).css("display","block");
        $(text3).click(function(e){
          $(".month").css({opacity:1,top:"34px"});
          e.stopPropagation();
        })
      }
    });
    $("body").click(function(){
      $(".month").css({opacity:0,top:"54px"});
    });

    let user_id = location.href.split("?")[1].split("=")[1];  // 用户id
    let datas = JSON.parse(window.localStorage.getItem("data")).data;  // 从会话取的所有用户的档案list
    console.log(datas);
    current_user_archive = null;  // 当前用户档案
    for (let i = 0; i < datas.length; i++) {
        // 给用户档案赋值
        let temp = datas[i];
        if (temp["_id"] === user_id) {
            current_user_archive = temp;
            break;
        }
    }
    current_reports = {};    // 当前用户安全报告,按天切分.
    if(current_user_archive !== null){
        // 给用户报告赋值
        var temp_reports = current_user_archive['reports'];
        for (var i = 0; i < temp_reports.length; i++) {
            let temp = temp_reports[i];
            let k = temp['report_time'].split(" ")[0];
            current_reports[k] = temp;
        }
    }

    // 启动页面时初始化基本信息
    init_base_info(current_user_archive);   // 加载基本信息
    init_right_bar(datas);  // 加载右侧边栏
    init_chart(current_user_archive);  // 初始化各种图表
// end
});