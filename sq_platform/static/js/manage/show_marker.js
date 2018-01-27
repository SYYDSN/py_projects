/************高德地图的初始化，监听器，事件。请在这里定义*****************/
console.log("normal javascript begin load");
//console.log(global_datas)
// 函数字典，用于最小化全局污染。
func_dict = {};
function get_marker(arg_dict) {
    /*
    * 获取一个AMap.Marker的实例。
    * arg_dict为字典格式的参数。
    * marker.setMap(map);
    * */
    var obj = new AMap.Marker({
        position: arg_dict === undefined ? [121.504239, 31.239981] : arg_dict['position'],  // 经纬度
        title: arg_dict === undefined ? "name" : arg_dict['position'], // 名字
    });
    return obj;
}

test_hover = function(){alert();};

var datas = [];
let getOne = function(){
  var arr = [];
  var array = [];
  for(let i = 0; i< datas.length; i++){
    if(datas[i].real_name){
      arr.push(datas[i].real_name.substr(0,1))
    }
  }
  function dur () {

    for (var i = 0; i < arr.length ; i++) {
      let flag = true;
      for (var j = 0; j < array.length ; j++) {
        if(arr[i] == array[j]) {
          flag = false;
        }
      }
      if(array.length < 10){
        if(flag){
          array.push(arr[i]);
        }
      }
    }
  }
  dur();
  for ( let i = 0; i < array.length ; i++){
    let li = document.createElement("li");
    $(li).text(array[i]);
    $("#right_bar_handler_bottom ul").append(li);
  }
}

//datas = JSON.parse(window.localStorage.getItem("datas")).data_dict;
func_dict['get_marker'] = get_marker;  // 加入函数集
function init_map() {

    /*
    * 高德地图回调脚本的初始化函数，注意，这个函数不能写在jquery脚本的$(function(){......});中，
    * 那样会导致无法加载初始化函数。
    * 组件的异步初始化也应该在此函数中进行
    * */
    console.log("begin init amap...");
    // 初始化高德地图
    map = new AMap.Map('container', {
        resizeEnable: true,
        // viewMode: "3D",                 //开启3D视图,默认为关闭
        buildingAnimation: true,       //楼块出现是否带动画
        rotateEnable: true,    // 旋转开关
        // pitchEnable: true,     // 是否允许设置俯仰角
        expandZoomRange: true,//是否支持可以扩展最大缩放级别,和zooms属性配合使用.设置为true的时候，zooms的最大级别在PC上可以扩大到20级
        zooms: [1, 20],  // 地图缩放范围
        // pitch: 30,   // 俯仰角度
        // center: [121.165313,31.313883],    // 坐标位置
        center: [121.304239, 31.239981],    // 坐标位置
        // skyColor: "red",  // 天空颜色
        zoom: 11
    });
    /*给地图加载事件监听器*/
    AMap.event.addListener(map, 'zoomend', function () {
        // 缩放事件
        console.log(map.getZoom()); // 获取缩放级别
    });
    map.on("click", function (e) {
        // 点击事件。
        console.log(e.lnglat.lng, e.lnglat.lat); // 打印经度纬度
        console.log(e);
    });
    console.log("end init amap!");

    console.log("begin init AwesomeMarker...");

    function get_offset_for_nav() {
        /*
        * 获取因浏览器差异造成的便宜不同的数组。
        * */
        if(is_ff()){
            return new AMap.Pixel(63, -19);
        }
        else{
            return new AMap.Pixel(73, -23);
        }
    }

    // 初始化ui库
    initAMapUI();
    AMapUI.loadUI(['overlay/AwesomeMarker'], function (AwesomeMarker) {
        /*
        * 加载ui插件
        * */
        let get_awe_marker = function (arg_dict) {
            /*
            *有关ａｗｅ图标的细节，请参看http://fontawesome.io/examples/
            * 下举个例子：
            *卡车图标。
            * <i class='fa fa-truck fa-2x fa-flip-vertical' aria-hidden='true'></i>
            * ２倍大小的卡车图标向右。
            * fa-truck　　卡车图标名
            * fa-2x　　２倍尺寸，　fa-1g 原始大小
            * fa-flip-vertical　向右，默认是向左。
            * <i class='fa fa-truck fa-2x ' style='background:black;color:white' aria-hidden='true'></i>
            * ２倍大小的卡车图标，设置背景色为黑色，卡车为白色。
            * 利用fa-stack类，还可以实现图标的堆叠。
            * <span class="fa-stack fa-lg">
            *   <i class="fa fa-square-o fa-stack-2x"></i>
            *   <i class="fa fa-twitter fa-stack-1x"></i>
            * </span>
            * */
            let user_id = arg_dict === undefined ? "guest" : arg_dict['user_id'] ;
            let real_name = arg_dict === undefined ? "guest" : arg_dict['real_name'] ;
            let security_score = arg_dict === undefined ? 78 : arg_dict['security_score'] ;
            let time = arg_dict === undefined ? '' : arg_dict['time'] ;

            let icon_img = [
              "../../static/image/head_img/lan.png"
              // "../../static/image/head_img/hong.png",
            ];
            let icon_num = 0;
            let obj = new AMap.Marker({
                map: map,
                position: arg_dict === undefined ? [121.504239, 31.239981] : arg_dict['position'],
                icon: new AMap.Icon({
                  size: new AMap.Size(46, 64),  //图标大小
                  image: icon_img[icon_num]
                })
              });
              obj.on("mouseover",function() {
                var amap = $(".amap-icon");
                for(let i = 0; i< amap.length; i++){
                    $(amap[i]).on("mouseover",function () {
                       $(this).next().css("width",220);
                       $(this).next().children("ul").css("display","block");
                       $(this).next().children("img").css("display","block");
                       let tips_html = '<li><span>暂无预警信息</span></li>';
                       $(".alarm_tips").html(tips_html);
                       let imgSrc = $($(this).children("img")).attr("src");
                       if(imgSrc == "../../static/image/head_img/lan.png"){
                         $('.inner_left img').attr("src","../static/image/icon/anquan.png");
                         $(".inner_left img").attr("class","anquan_img");
                       }else{
                         $('.inner_left img').attr("src","../static/image/icon/alarm_big_circle.png");
                         $(".inner_left img").attr("class","alarm_img");
                       };
                    })
                    $(amap[i]).on("mouseout",function () {
                       $(this).next().css("width",0);
                       $(this).next().children("ul").css("display","none");
                       $(this).next().children("img").css("display","none");
                       let tips_html = '<li><span>沪宁高速路口有交通事故发生</span></li>'+'<li><span>心率偏高危险</span></li>'+'<li><span>前方有事故请绕道行驶，注意安全。</span></li>'+'<li><span>司机已长时间驾驶，注意休息。</span></li>';
                       $(".alarm_tips").html(tips_html);
                       $('.inner_left img').attr("src","../static/image/icon/alarm_big_circle.png");
                       $(".inner_left img").attr("class","alarm_img");
                    })
                }
              })
              var imgs = ["../../static/image/head_img/zMsb-fximeyv2774914.jpg","../../static/image/head_img/2015111093556890.jpg","../../static/image/head_img/2014092116375761ad6.jpg","../../static/image/head_img/16080904183524.jpg","../../static/image/head_img/16072910584233.jpg"];
            var num = parseInt(Math.random() * imgs.length);
            var content=[];
            content.push("<ul><li><span>姓名</span><span>"+arg_dict.real_name+"</span></li><li><span>部门</span><span>华新分拨公司</span></li><li><span>电话</span><span>"+arg_dict.phone_num+"</span></li></ul><img src="+ imgs[num] +">")
            // 图片图标，由于这个图片方向性太强，实用需要同时选择图标，比较复杂，稍后再处理。
            // track_content = "<img class='img' src='../static/image/icon/normal_truck.png'/>";
//            obj.setContent(track_content);   // 设置定义点样式。
            // 设置label，也就是自定义点的信息框体
            obj.setLabel({
                offset: new AMap.Pixel(-1, -2),  // 调整偏移量
                isCustom: true,
                content: content
            });
            obj.setMap(map);
            return obj;

        };

        func_dict['get_awe_marker'] = get_awe_marker;  // 加入函数集

        // 定义一个修改地图中心位置的函数。全局函数，不加入函数集
        let set_map_center = function (position){
            map.setCenter(position);
        };

        // 定义右侧边栏元素的头像的点击事件--点击头像调整地图坐标到中心位置。全局函数，不加入函数集
        to_map_center = function($obj){
            let position = $obj.parents(".item_main:first").attr("data-position").split(",");
            set_map_center(position);
        };
        // 定义一个追加右侧边栏元素的函数

        let add_right_side_bar_item = function(arg_dict){
            // 用户id
            let user_id = arg_dict['user_id'];
            // 用户头像
            let head_img_url = arg_dict['head_img_url'] === undefined ? "../static/image/head_img/default_01.png": arg_dict['head_img_url'];
            // 用户手机
            let phone_num = arg_dict['phone_num'] === undefined ? "1580080080": arg_dict['phone_num'];
            // 真实姓名
            let real_name = arg_dict['real_name'] === undefined ? phone_num: arg_dict['real_name'];
            // 当前位置
            let position = arg_dict['position'] === undefined ? [121.304239, 31.239981]: arg_dict['position'];
            // 车辆型号
            let car_model = arg_dict['car_model'] === undefined ? "9.6m": arg_dict['car_model'];
            // 驾驶时长
            let drive_time = arg_dict['drive_time'] === undefined ? "4h": arg_dict['drive_time'];
            // 行驶里程
            let mileage = arg_dict['mileage'] === undefined ? "3k+": arg_dict['mileage'];
            // 不良记录/跟安全有关的事件
            let event_count = arg_dict['event_count'] === undefined ? "0": arg_dict['event_count'];
            // 最后通信时间
            let time = arg_dict['time'] === undefined ? "未知": arg_dict['time'];
            // 版本信息
            let app_version = arg_dict['app_version'] === undefined ? "未知": arg_dict['app_version'];
            // 最后一个数据到现在的时间差，单位秒
            let time_delta =  arg_dict['time_delta'] === undefined ? 0: parseInt(arg_dict['time_delta']);
            // 计算颜色
            let name_color = "#408DBC";
            if(time_delta < 60 * 10){
                // pass
            }
            else if(time_delta < 60 * 60){
                name_color = color_normal_16;
            }
            else if(time_delta < 60 * 60 * 12){
                name_color = "#FFA500";
            }
            else{
                name_color = color_danger_16;
            }
            let html_str = `<li class="my_li" data-id="${user_id}">

                                <div class="item_main" data-position="${position}">
                                    <div class="left_side">
                                        <img title="最后通信时间:${time}\napp版本:${app_version}" onclick="to_map_center($(this))" class="side_bar_img" src="${head_img_url}">
                                    </div>
                                    <ul class="my_ul">
                                        <li class="my_li real_name my_flex">
                                            <span  style="color:${name_color}">${real_name}</span>
                                            <a target="_blank" href="show_track?phone_num=${phone_num}">
                                                <i title="查看轨迹" class="fa fa-dot-circle-o icon_mouse_leave" aria-hidden="true"></i>
                                            </a>
                                        </li>
                                        <li class="my_li my_flex"><span>车型:</span><span>${car_model}</span><span class="margin-right">时长:</span><span>${drive_time}</span></li>
                                        <li class="my_li my_flex"><span>里程:</span><span>${mileage}</span><span class="margin-right">记录:</span><span>${event_count}</span></li>
                                    </ul>
                                </div>
                                <div class="item_bottom">
                                    <!--<img class="side_bar_bottom_img" src="../static/image/icon/alarm_lamp.png">-->
                                    <svg style="margin-bottom:2px" class="xs_icon yujing_mian normal_status" aria-hidden="true"><use xlink:href="#icon-yujing_mian"></use></svg>
                                    <span class="current_message">当前路况良好</span>
                                </div>
                                <hr>
                            </li>`;

            $("#driver_list").append(html_str);
            lis = $("#driver_list>li");
        };

        func_dict['add_right_side_bar_item'] = add_right_side_bar_item;  // 加入函数集

    });
    console.log("end init AwesomeMarker...");

}  //  init_map()函数代码结束。

console.log("normal javascript end load");
/******************德地图的初始化，监听器，事件定义结束**************************/
/************************以下是jquery部分*************************************/
/*
* 注意，需要在高德地图初始化后加载的事件不要写在jquery代码中，因为jquery代码比高德地图的异步回调方法加载早。
* 加载顺序如下：
* 1.脚本中$(function(){......})之外的部分。
* 2.脚本中$(function(){......})之内的部分，也就是我们一般说的jquery代码/脚本部分。
* 3.脚本的回调函数，也就是脚本中callback=指向的那个回调函数，本例中 ，是指init_map这个函数。
* 请牢记次顺序，遇到使用时未赋值的异常，可以参考此顺序进行排查工作。
* */
$(function () {
    console.log("begin load jquery script");
    var set_window = function () {
        /*
         设置窗口高度,由于AdminLTE框架的影响，会导致高德地图无法铺满内部空间，所以需要在高德地图初始化窗口之前。
         调用此方法重设容器的大小，同时，此方法需要加载到window的onresize事件中，以便随时调整窗口大小。
         window.onresize = function(){set_window();};
         同时调整有侧边栏尺寸和位置。
         */
        var map_height = $(".content-wrapper").css("height");
        map_height = (parseInt(map_height.split("px")[0]) - 50) + "px";
        console.log("计算的窗口高度：" + map_height);
        if(document.getElementsByTagName("body")[0].offsetWidth <= 768){
          $("#right_side_bar").css("top", 100 + "px");
        }else{
          $("#right_side_bar").css("top", 50 + "px");
        }

        /*
        * 调整警示悬浮框的位置
        * */
        let left = $(".main-sidebar").width() + 10;
        $("#suspend_alarm_div").css("left", `${left}px`);
    };
    set_window();
    window.addEventListener('resize',function(){
      set_window();
    })  // 窗口大小变化时，重设高德地图容器的大小。
    $("#right_side_bar").click(function (e) {
        e.stopPropagation();
    })
    // 右侧边栏，点击手柄的滑动事件
    $("#right_side_bar_handler").click(function(e){
        let class_str = $("#right_side_bar").attr("class");
        if(class_str === undefined || class_str === ""){
            // 第一次
            $("#right_side_bar").addClass("bar_to_right");
            $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-left fa-flip-horizontal")
             $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-right fa-flip-horizontal")
        }
        else if(class_str === 'bar_to_right'){
            // 已经滑动到左边了。
             $("#right_side_bar").removeClass("bar_to_right");
             $("#right_side_bar").addClass("bar_to_left");
             $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-right fa-flip-horizontal")
             $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-left fa-flip-horizontal")
        }
        else if(class_str === 'bar_to_left'){
            // 已经滑动到右边了。
             $("#right_side_bar").removeClass("bar_to_left");
             $("#right_side_bar").addClass("bar_to_right");
             $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-left fa-flip-horizontal")
             $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-right fa-flip-horizontal")
        }
        else{
            console.log(class_str);
        }
        e.stopPropagation();
    });
    $("body").click(function(){
      $("#right_side_bar").removeClass("bar_to_left");
      $("#right_side_bar").addClass("bar_to_right");
      $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-left fa-flip-horizontal")
      $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-right fa-flip-horizontal")
    })

    $("form").submit(function () {
        alert("数据提交成功")
        return false;
    })
    function screenName(name){
    let key2 = $.trim($(name).val());
    $(name).val("");
    let lis = $("#driver_list>li");
    if(key2 != ""){
      for(let i=0;i<lis.length;i++){
        let li = lis[i];
        let name = $.trim($(li).find(".real_name span").text());
        if(name.indexOf(key2) !== -1){
          $(li).show();
          $(li).attr("test","bbb");
        }
        else{
          $(li).hide();
          $(li).removeAttr("test");
        }
      }
    }
  }

    $("#search").keyup(function(e){
      if(e.keyCode == 13){
        screenName(this);
        if($("#driver_box ul li[test='bbb']").length == 0){
          $("#driver_box .content").css("display","block");
        }else{
          $("#driver_box .content").css("display","none");
        }
      }
    })
    $("#btn").click(function(e){
      screenName("#search")
      if($("#driver_box ul li[test='bbb']").length == 0){
        $("#driver_box .content").css("display","block");
      }else{
        $("#driver_box .content").css("display","none");
      }
      e.stopPropagation();
    });
    $("#right_bar_handler i").click(function (e) {
        let lis = $("#driver_list>li");
        for (let i =0 ; i<lis.length ; i++){
            $("#driver_box .content").css("display","none");
            $(lis[i]).attr("test","bbb");
            $(lis[i]).show();
        }
      e.stopPropagation();
    })

    // 点击筛选司机
          $("#right_bar_handler_bottom").on('click','li',function (e) {
             $("#driver_box .content").css("display","none")
             var text = $(this).text();
             let driverLists = $("#driver_list>li");
             for(let i = 0; i< driverLists.length ; i++) {
                 var nameStr =  $(driverLists[i]).find(".real_name span").text();
                 if(nameStr.substring(0,1) === text) {
                    $(driverLists[i]).show()
                 }else {
                    $(driverLists[i]).hide()
                 }
             }
            e.stopPropagation();
          })

    /*************************jquery部分结束***************************************/
    console.log("end load jquery script");
//end!
   var len =  window.localStorage.getItem("len")
    $("#driver_list").height(len * 109);

  let right_side_bar = document.getElementById("right_side_bar");
  let right_side_bar_header = right_side_bar.children[1];
  let right_bar_handler = document.getElementById("right_bar_handler");
  let right_bar_handler_bottom = document.getElementById("right_bar_handler_bottom");
  let side_title = document.getElementById("side_title");
  let Hleng = right_side_bar.offsetHeight - right_side_bar_header.offsetHeight - right_bar_handler.offsetHeight - right_bar_handler_bottom.offsetHeight - side_title.offsetHeight;
  $("#driver_box").height(Hleng);

  var my_func = setInterval(function(){
    if(global_ws_finish){
      datas = global_members;
      getOne();
      clearInterval(my_func);
    }
    else{
      console.log("waiting for ws finish...");
    }
  }, 300);

});

