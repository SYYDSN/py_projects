/*
* 轨迹跟踪
* */
$(function () {
    //内部函数开始
    set_window = function () {
        // 设置窗口高度
        var map_height = $(".content-wrapper").css("height");
        map_height = (parseInt(map_height.split("px")[0]) - 50) + "px";
        console.log("计算的窗口高度：" + map_height);
    };
    set_window();

    /*初始化高德地图*/
    map = new AMap.Map('container', {
        resizeEnable: true,
        zoom: 12
    });

    window.onresize = function () {
        set_window();
    };

    // 全局变量
    let track_time_list = [];  // 轨迹索引的时序，用于确认轨迹点的时间。
    //加载PathSimplifier，loadUI的路径参数为模块名中 'ui/' 之后的部分
    AMapUI.load(['ui/misc/PathSimplifier'], function (PathSimplifier) {

        if (!PathSimplifier.supportCanvas) {
            alert('当前环境不支持 Canvas！');
            return;
        }

        //启动页面
        initPage(PathSimplifier);
    });

    function initPage(PathSimplifier) {
        //创建组件实例
        pathSimplifierIns = new PathSimplifier({
            zIndex: 100,
            map: map, //所属的地图实例
            getPath: function (pathData, pathIndex) {
                //返回轨迹数据中的节点坐标信息，[AMap.LngLat, AMap.LngLat...] 或者 [[lng|number,lat|number],...]
                return pathData.path;
            },
            getHoverTitle: function (pathData, pathIndex, pointIndex) {
                //返回鼠标悬停时显示的信息
                if (pointIndex >= 0) {
                    //鼠标悬停在某个轨迹节点上
                    let cur_time = track_time_list[pointIndex].split(".")[0];
                    return `第${pointIndex}/${pathData.path.length}节点。时间:${cur_time}`;
                }
                //鼠标悬停在节点之间的连线上
                return pathData.name + '，点数量' + pathData.path.length;
            },
            renderOptions: {
                //轨迹线的样式
                pathLineStyle: {
                    strokeStyle: 'red',
                    lineWidth: 6,
                    dirArrowStyle: true
                }
            }
        });
        setTimeout(function () {
            query_track_info();
        }, 800);
    }

    // 查询数据
    query_track_info = function () {
        var args = {
            "phone_num": phone_num,
            "begin_date": track_begin_date,
            "end_date": track_end_date
        };
        $.post("/manage/track_info", args, function (raw_data) {
            let data = JSON.parse(raw_data);
            if (data['message'] === "success") {
                let data_set = data['data'];
                let data_list = data_set['track_list'];
                let total_mileage = data_set['total_mileage'];
                let total_time = data_set['total_time'];
                let length = data_list.length;
                if (length === 0) {
                    $(".cue_info").css("opacity",1);
                    setTimeout(function(){
                      $(".cue_info").css("opacity",0);
                    },3000)
                }
                else {
                    let path_list = [];
                    let time_list = [];
                    console.log(data_list[0]);
                    console.log(data_list[-1]);
                    for (let i = 0; i < length; i++) {
                        let raw = data_list[i];
                        path_list.push(raw['loc']);
                        time_list.push(raw['time']);
                    }
                    console.log(path_list.length);
                    track_time_list = time_list;  // 给时序点数组赋值。
                    pathSimplifierIns.setData([{
                        name: '轨迹0',
                        path: path_list
                    }]);
                    // 计算回放速度

                    let nav_speed = 10;
                    //创建一个巡航器
                    var navg0 = pathSimplifierIns.createPathNavigator(0, //关联第1条轨迹
                        {
                            loop: true, //循环播放
                            speed: nav_speed
                        });

                    navg0.start();
                }
            }
            else {
                alert(data['message']);
            }
        })
    };
    function getNowFormatDate() {
        let date = new Date();
        let seperator1 = "-";
        let seperator2 = ":";
        let month = date.getMonth() + 1;
        let strDate = date.getDate();
        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate
                + " " + date.getHours() + seperator2 + date.getMinutes()
                + seperator2 + date.getSeconds();
        return currentdate;
    }

    var Max = getNowFormatDate().split(" ")[0];
    let date = new Date();
    let year = date.getFullYear();
    let month = date.getMonth()+ 1;
    let day = date.getDate();
    var begin_date = 0;
    var end_date = 0;

   if(location.search.split("?")[1]){
     if(location.search.split("?")[1].split("&")[1]){
       $("#start").val(location.search.split("?")[1].split("&")[1].split("=")[1]);
       $("#end").val(location.search.split("?")[1].split("&")[2].split("=")[1]);
     }else{
       $("#start").val(year+"-"+month+"-"+day);
       $("#end").val(year+"-"+month+"-"+day);
     }
   }else{
     $("#start").val(year+"-"+month+"-"+day);
     $("#end").val(year+"-"+month+"-"+day);
   }

  // 日期插件
        var start = {
            format: 'YYYY-MM-DD',
            multiPane:true,
            onClose:false,
            minDate: '2014-06-16', //设定最小日期为当前日期
            maxDate: Max, //最大日期
            okfun: function(obj){
                end.minDate = obj.val; //开始日选好后，重置结束日的最小日期
                endDates();
                begin_date = obj.val;
            },
        };
        var end = {
            format: 'YYYY-MM-DD',
            minDate: $.nowDate({DD:0}), //设定最小日期为当前日期
            maxDate: Max, //最大日期
            multiPane:true,
            onClose:false,
            okfun: function(obj){
                start.maxDate = obj.val; //将结束日的初始值设定为开始日的最大日期
                end_date = obj.val;
            },
        };

        //这里是日期联动的关键
        function endDates() {
            //将结束日期的事件改成 false 即可
            end.trigger = false;
            $("#end").jeDate(end);
        }

        $('#start').jeDate(start);
        $('#end').jeDate(end);
        begin_date = $("#start").val();
        end_date = $("#end").val();
        var datas = JSON.parse(window.localStorage.getItem("datas")).data_dict;

        for(let i = 0; i < datas.length; i++){
            if(location.search.split("?")[1] != undefined){
              var search = location.search === "?" || location.search.split("?")[1].split("=")[1];
            }
            var option = document.createElement('option');
            if(search == datas[i].phone_num){
                $(option).attr("selected",true)
            }
            $(option).text(datas[i].real_name);
            $(option).val(datas[i].phone_num);
            $("#driverList").append(option)
        }
        if(location.search.split("?")[1]){
          var options = $("#driverList option");
          var options_search = location.search.split("?")[1].split("=")[1].split("&")[0];
          for(let j=0; j<options.length; j++){
            if(options_search === $(options[j]).attr("value")){
              $(options[j]).attr("selected",true);
            }
          }
        }

        var phone = $("#driverList").val();
        if(phone != ""){
            $("#right_box_sun input").attr("disabled",false)
        }else{
             $("#driverList").change(function () {
                $("#right_box_sun input").attr("disabled",false)
            })
        }
        $("#right_box_go").on('click', function () {
           var phone = $("#driverList").val();
           if(begin_date.length === 0 || end_date.length === 0){
                alert("日期不能为空");
           }else {
                var href =  location.origin + '' + location.pathname + "?" + "phone_num=" + phone + "&" +"begin_date=" + begin_date + " 0:0:0&" + "end_date=" + end_date+" 23:59:59";
                location.href = href;
           }
        })


        function getBtnWidth(){
          if(document.getElementsByTagName("body")[0].offsetWidth <= 768){
            $("#right_box").css("top","-85px");
            let flag = true;
            $("#right_box_btn").click(function(){
              if(flag){
                $("#right_box").css("top","100px");
                flag = false;
              }else{
                $("#right_box").css("top","-85px");
                flag = true;
              }
            })
          }else{
            $("#right_box").css("top","-135px");
            let flag = true;
            $("#right_box_btn").click(function(){
              if(flag){
                $("#right_box").css("top","50px");
                flag = false;
              }else{
                $("#right_box").css("top","-135px");
                flag = true;
              }
            })
          }
        }
        getBtnWidth();
        window.onresize = function(){
          getBtnWidth();
        }
// end !
})




