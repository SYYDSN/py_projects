

    let mydata_img = echarts.init(document.getElementById('data_img'));
    mydata_img.setOption({
        title: {
                text: "事故统计",
                subtext: ""
            },
  legend: {},
tooltip: {},
dataset: {
  source: [
      ['product', '同比', '当月', '环比'],
      ['直行事故', 43.3, 85.8, 93.7],
      ['追尾事故', 86.4, 65.2, 82.5],
      ['会车事故', 72.4, 53.9, 39.1],
      ['超车事故', 72.4, 53.9, 39.1],
      ['停车事故', 72.4, 53.9, 39.1],
      ['弯道事故', 72.4, 53.9, 39.1],
      ['侧翻', 72.4, 53.9, 39.1],
      ['跌落', 72.4, 53.9, 39.1]
  ]
},
xAxis: {type: 'category'},
yAxis: {},
// Declare several bar series, each will be mapped
// to a column of dataset.source by default.
series: [
  {type: 'bar'},
  {type: 'bar'},
  {type: 'bar'}
]
});
let mydata_imgtwo = echarts.init(document.getElementById('data_imgtwo'));

    mydata_imgtwo.setOption({
        title: {
                text: "违章统计 top 6",
                subtext: ""
            },
  legend: {
  },
tooltip: {},
dataset: {
  source: [
      ['product', '同比', '当月', '环比'],
      ['酒驾', 3, 2, 1],
      ['超速', 43.3, 85.8, 93.7],
      ['高速倒车', 86.4, 65.2, 82.5],
      ['违规停车', 72.4, 53.9, 39.1],
      ['闯红灯', 72.4, 53.9, 39.1],
      ['逆向行使', 72.4, 53.9, 39.1],
      ['超载', 72.4, 53.9, 39.1]
  ]
},
xAxis: {type: 'category'},
yAxis: {},
// Declare several bar series, each will be mapped
// to a column of dataset.source by default.
series: [
  {type: 'bar'},
  {type: 'bar'},
  {type: 'bar'}
]
});
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
      name:'总计',
      type:'bar',
      barWidth: '60%',
      data:[10, 52, 200, 334, 390, 330, 220]
  }
]
});

// 全队安全得分
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

// 初始化日期插件
$("#date_picker").datetimepicker({
          language: "zh-CN",
          weekStart:1,  // 星期一作为一周的开始
          minView: 2,  // 不显示小时和分
          autoclose: true,  // 选定日期后立即关闭选择器
          format: "yyyy-mm-dd"
      }).on('change',function (ev) {
          change_date(this);
      });
  $("#date_picker_end").datetimepicker({
      language: "zh-CN",
      weekStart:1,  // 星期一作为一周的开始
      minView: 2,  // 不显示小时和分
      autoclose: true,  // 选定日期后立即关闭选择器
      format: "yyyy-mm-dd"
  }).on('change',function(ev){
      change_date(this);
  });