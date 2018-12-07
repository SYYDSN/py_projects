$(function () {
    // 饼图


    // 柱状图
    let histogram_column = function (data) {
        var myHistogram = echarts.init(document.getElementById("histogram"));
        var histogram = {
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
                  data : ['急加速', '急转弯', '急刹车', '超速', '使用手机', '疲劳驾驶'],
                  axisTick: {
                    alignWithLabel: true
                  }
                }
              ],
              yAxis : [
                {
                  min : 0,
                  type : 'value'
                }
              ],
              series : [
                {
                  name:'发生次数',
                  type:'bar',
                  barWidth: '60%',
                  data:[data[0], data[1], data[2], data[3], data[4], data[5]]
                }
              ]
            };
        myHistogram.setOption(histogram);
    }


    // 折线图
    var mylineChart = echarts.init(document.getElementById("line_chart"));
    var lineChart = {
      xAxis: {
        type: 'category',
        splitLine: {show: false},
        data: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月','十月','十一月','十二月']
      },
      yAxis: {
        type: 'value',
        min : 0,
        max : 40
      },
      series : [
        {
          type: 'line',
          data: [2,11,5,24,20,9,9,9,23,20,11,12],
          symbolSize: 11,
          lineStyle : {
            normal :{
                color : "#ff881d"
            }
          },
          areaStyle : {
            normal : {
              color :{
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0, color: '#ff881d' // 0% 处的颜色
                }, {
                  offset: 1, color: 'white' // 100% 处的颜色
                }],
                globalCoord: false // 缺省为 false
              }
            }
          }
        },
      ]
    };
    mylineChart.setOption(lineChart);

    // 饼图
    let Pie_column = function (data) {
         var myPie = echarts.init(document.getElementById("pie"));
        var Pie = {
          tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
          },
          color : ['#53d3ff','#7cc58e', '#e9dd55', '#ff7fa8', '#a989de'],
          series: [
            {
              name:'事件所占比重',
              type:'pie',
              radius: ['50%', '70%'],
              avoidLabelOverlap: false,
              label: {
                normal: {
                  show: false,
                  position: 'center'
                },
                emphasis: {
                  show: false,
                  textStyle: {
                    fontSize: '12',
                    fontWeight: 'normal',
                  }
                }
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              data:[
                {value:data[0], name:'打手机事件所占比重'},
                {value:data[1], name:'超速事件所占比重'},
                {value:data[2], name:'急刹车事件所占比重 '},
                {value:data[3], name:'急转弯事件所占比重 '},
                {value:data[4], name:'急加速事件所占比重  '}
              ]
            }
          ]
        };
        myPie.setOption(Pie);
    }

    $.post("/manage/report_page", function(data){
        var data = JSON.parse(data);
        console.log(data)
        histogram_column([data.data.cnt_rapi_acce, data.data.cnt_shar_turn, data.data.cnt_sudd_brak, 0, 0, 0]);
        Pie_column([0, 0, data.data.cnt_sudd_brak, data.data.cnt_shar_turn, data.data.cnt_rapi_acce]);
        var report_html = '<li><h5>'+ data.data.total_mileage +'km</h5>行驶总里程</li>'+
                   ' <li><h5>'+ data.data.total_time +'h</h5>行驶总时长</li>'+
                    '<li><h5>'+ data.data.member_count +'人</h5>参与总人数</li>'+
                    '<li><h5>0次</h5>事故出现总次数</li>';
        $(".report-data ul").append(report_html);

        var histogram_html ='<li><i></i><span>急加速事件次数 </span><span>'+ data.data.cnt_rapi_acce +'</span></li>' +
                            '<li><i></i><span>急转弯事件次数 </span><span>'+ data.data.cnt_shar_turn +'</span></li>' +
                            '<li><i></i><span>急刹车事件次数 </span><span>'+ data.data.cnt_sudd_brak +'</span></li>' +
                            '<li><i></i><span>超速事件次数 </span><span>0</span></li>' +
                            '<li><i></i><span>使用手机事件次数 </span><span>0</span></li>' +
                            '<li><i></i><span>疲劳驾驶事件次数 </span><span>0</span></li>';
        $(".histogram-list ul").append(histogram_html);
        var scr_synt = parseInt(data.data.scr_synt);
        var wjx = null;
        if(scr_synt<= 0 && scr_synt <= 60){
             wjx = '★☆☆☆☆';
        }else if(scr_synt > 60 && scr_synt <= 70){
             wjx = '★★☆☆☆';
        }else if(scr_synt > 70 && scr_synt <= 80){
             wjx = '★★★☆☆';
        }else if(scr_synt > 80 && scr_synt <= 90){
            wjx = '★★★★☆';
        }else if(scr_synt > 90 && scr_synt < 100){
            wjx = '★★★★★';
        }

        var Pbar_html = '<li><i></i><span>安全等级</span><span>'+ wjx +'</span></li>' +
                        '<li><i></i><span>安全排名</span><span>1</span></li>' +
                        '<li><i></i><span>驾驶总里程</span><span>'+ data.data.total_mileage +'</span></li>' +
                        '<li><i></i><span>平均时速</span><span>69</span></li>' +
                        '<li><i></i><span>驾驶总时长</span><span>'+ data.data.total_time +'</span></li>';
         $(".Pbar ul").append(Pbar_html);

        let pie_num = data.data.cnt_rapi_acce + data.data.cnt_shar_turn + data.data.cnt_sudd_brak;
        // 急加速事件所占比重
        let cnt_rapi_acce = ((data.data.cnt_rapi_acce / pie_num) * 100).toFixed(2);
        // 急转弯事件所占比重
        let cnt_shar_turn = ((data.data.cnt_shar_turn / pie_num) * 100).toFixed(2);
        // 急刹车事件所占比重
        let cnt_sudd_brak = ((data.data.cnt_sudd_brak / pie_num) * 100).toFixed(2)
        var pie_html = '<li><span></span><span>使用手机事件所占比重</span><span>0%</span></li>' +
                       '<li><span></span><span>超速事件所占比重</span><span>0%</span></li>' +
                       '<li><span></span><span>急刹车事件所占比重 </span><span>'+ cnt_sudd_brak +'%</span></li>' +
                       '<li><span></span><span>急转弯事件所占比重</span><span>'+ cnt_shar_turn +'%</span></li>' +
                       '<li><span></span><span>急加速事件所占比重</span><span>'+ cnt_rapi_acce +'%</span></li>';
        $(".pie-list ul").append(pie_html);

        $(document).ready(function(){
              $(".GaugeMeter").gaugeMeter();
        });
        $("#GaugeMeter_1").attr({
              "data-percent": parseInt(data.data.scr_synt) ,
              "data-size": "200",
              "data-label_color": "#ccc",
              "data-label": "安全指数",
              "data-color" : "#21b3f9",
              "data-back" : "#96e4ff" ,
              "data-width" : "15",
              "data-label_color": "#565656"
        })
    });

});

