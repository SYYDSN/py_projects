// 基于准备好的dom，初始化echarts实例
let myChart = echarts.init(document.getElementById('myChart'));
// 绘制图表
myChart.setOption({
  title: {
       text: '健康状态',
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


//



setInterval(function(data){
    var dataAxis = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''];
    var data = [220, 182, 191, 234, 290, 330, 310, 123, 442, 321, 90, 149, 210, 122, 133, 334, 198, 123, 125, 220];
    var yMax = 500;
    var dataShadow = [];

for (var i = 0; i < data.length; i++) {
    dataShadow.push(yMax);
}
    let mylishi = echarts.init(document.getElementById('mylishi'));
mylishi.setOption({
    title: {
        text: '',
        subtext: '安全得分 12月第三周(17/12/31---18/1/7)'
    },
    xAxis: {
        dtype : 'category',
        data : ['1/1', '1/2', '1/3', '1/4', '1/5', '1/6', '1/7'],
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
            data: dataShadow,
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
            data: data
        }
    ]
});

},100)

// Enable data zoom when user click bar.
// 日期插件change事件
var change_date = function(obj){
    var $obj = $(obj);
    var my_id = $obj.attr("id");
        console.log(my_id);
        if(my_id === "form_date_end"){
            // 点击结束时间的时间选择器
            var begin = new Date($.trim($("#form_date").val()));
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
            var end = new Date($.trim($("#form_date_end").val()));
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

$('#form_date').datetimepicker({
    language:  'zh-CN',
    format: 'yyyy-mm-dd',
    weekStart: 1,
    todayBtn:  1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 3, //这里就设置了默认视图为年视图
    minView: 2, //设置最小视图为年视图
    forceParse: 0,
}).on('change',function(ev){
    change_date(this);
});
$('#form_date_end').datetimepicker({
    language:  'zh-CN',
    format: 'yyyy-mm-dd',
    weekStart: 1,
    todayBtn:  1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 3, //这里就设置了默认视图为年视图
    minView: 2, //设置最小视图为年视图
    forceParse: 0,
}).on('change',function(ev){
    change_date(this);
});



// 选项卡  切换操作
$('#xuka span').click( function() {
    $('#xuka span').removeClass('active-font');
    console.log($(this).index())
    $(this).addClass('active-font');

    if($(this).index() == 0){
        $('.tim').css('display','none');
        $('#dangri').css('display','block');
        $('#lishi').css('display','none');
        $('#shigu').css('display','none');
        $('#weizhang').css('display','none');
        $('#geren').css('display','none');
        $('#dibuec').css('display','block');

    }else if($(this).index() == 1){
        $('.tim').css('display','block');
        $('#dangri').css('display','none');
        $('#lishi').css('display','block');
        $('#shigu').css('display','none');
        $('#weizhang').css('display','none');
        $('#geren').css('display','none');
        $('#dibuec').css('display','block');

    }else if($(this).index() == 2){
        $('.tim').css('display','none');
        $('#dangri').css('display','none');
        $('#lishi').css('display','none');
        $('#shigu').css('display','block');
        $('#weizhang').css('display','none');
        $('#geren').css('display','none');
        $('#dibuec').css('display','none');

    }else if($(this).index() == 3){
        $('.tim').css('display','none');
        $('#dangri').css('display','none');
        $('#lishi').css('display','none');
        $('#shigu').css('display','none');
        $('#weizhang').css('display','block');
        $('#geren').css('display','none');
        $('#dibuec').css('display','none');

    }else if($(this).index() == 4){
        $('.tim').css('display','none');
        $('#dangri').css('display','none');
        $('#lishi').css('display','none');
        $('#shigu').css('display','none');
        $('#weizhang').css('display','none');
        $('#geren').css('display','block');
        $('#dibuec').css('display','none');

    }

   })