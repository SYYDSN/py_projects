

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
      ['正面碰撞', 43.3, 85.8, 93.7],
      ['追尾碰撞', 86.4, 65.2, 82.5],
      ['侧面碰撞', 72.4, 53.9, 39.1],
      ['转弯碰撞', 72.4, 53.9, 39.1],
      ['超车碰撞', 72.4, 53.9, 39.1],
      ['会车碰撞', 72.4, 53.9, 39.1],
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
                text: "违章统计",
                subtext: ""
            },
  legend: {
  },
tooltip: {},
dataset: {
  source: [
      ['product', '同比', '当月', '环比'],
      ['酒后驾驶', 43.3, 85.8, 93.7],
      ['高速倒车', 86.4, 65.2, 82.5],
      ['违规停车', 72.4, 53.9, 39.1],
      ['闯红灯', 72.4, 53.9, 39.1],
      ['逆向行使', 72.4, 53.9, 39.1],
      ['超载超载', 72.4, 53.9, 39.1]
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