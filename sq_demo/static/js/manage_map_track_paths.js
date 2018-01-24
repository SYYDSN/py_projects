/**
 * Created by walle on 17-8-17.跟踪运动轨迹
 */
$(function () {

    /*加载PathSimplifier组件*/
    my_pathSimplifierIns = null;
    AMapUI.load(['ui/misc/PathSimplifier', 'lib/$', 'lib/utils'], function (PathSimplifier, $, utils) {
        if (!PathSimplifier.supportCanvas) {
            console.log("不支持Canvas");
        }
        else {
            console.log("支持Canvas");
            my_pathSimplifierIns = new PathSimplifier({
                zIndex: 100,
                map: map,
                getPath: function (pathData, pathIndex) {
                    //返回轨迹数据中的节点坐标信息
                    return pathData.path;
                },
                getHoverTitle: function (pathData, pathIndex, pointIndex) {
                    //返回鼠标悬停时显示的信息
                    if (pointIndex >= 0) {
                        //鼠标悬停在某个轨迹节点上
                        return pathData.name + '，点:' + pointIndex + '/' + pathData.path.length;
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
            // console.log(my_pathSimplifierIns);
        }

        var defaultRenderOptions = {
            pathNavigatorStyle: {
                width: 16,
                height: 16,
                autoRotate: true,
                lineJoin: 'round',
                content: 'defaultPathNavigator',
                fillStyle: '#087EC4',
                strokeStyle: '#116394', //'#eeeeee',
                lineWidth: 1,
                pathLinePassedStyle: {
                    lineWidth: 2,
                    strokeStyle: 'rgba(8, 126, 196, 1)',
                    borderWidth: 1,
                    borderStyle: '#eeeeee',
                    dirArrowStyle: false
                }
            }
        };

        var customContainer = document.getElementById('container');
        function createKeyNavigatorStyleGui(target){
            var keyNavigatorStyleGui = new dat.GUI({
                width: 260,
                autoPlace: false
            });
            var keyNavigatorStyleParams = utils.extend({}, defaultRenderOptions[target]);
            // 形状类型
            keyNavigatorStyleGui

        }


    });




    // 设置轨迹数组
    function set_track_list(obj, data_name, data_list){
        obj.setData([{
            name:data_name,
            path: data_list
        }]);
    }

    // 批量设置轨迹数组
    function batch_set_and_run(obj, data_list, speed){
        // obj = my_pathSimplifierIns；直接传入此参数即可。
        // data_list 如下面示范的字典的数组，存放的是轨迹数据。
        // speed 播放速度 10000
        // data_list = [{"name": name_01, "path": [pos_1, pos_2..pos_n]}...]
        // obj.setData([{
        //     name:data_name,
        //     path: data_list
        // }]);
        obj.setData(data_list);
        var l = data_list.length;
        for(var i = 0; i < l; i++){
            var navigator = obj.createPathNavigator(i, {loop: true, speed: speed});
            navigator.start();
        }
    }

    /*初始化函数*/
    function init_track_paths(obj, speed) {
        //创建一个巡航器
        var navg0 = obj.createPathNavigator(0, //关联第1条轨迹

            {
                loop: true, //循环播放
                speed: speed  // 播放速度 10000
            });
        navg0.start();
    }

   // 以下为自由调用函数,用于获取数据并加载。测试用
   track_info_test = function (user_id){
        $.post("/manage/track_info", {"user_id": user_id}, function(data){
            var data = JSON.parse(data);
            var all_data = data['data'];  // 批量数据
            var result_list = new Array();  // 容器
            for(var i=0, l=all_data.length; i<l; i++){
                var data_list = all_data[i];
                console.log(data_list);
                var temp = {"name": "user_" + (i + 1), "path": data_list};
                result_list.push(temp);
            }
            batch_set_and_run(my_pathSimplifierIns, result_list, 1000);
        });
   };
   setTimeout(function(){track_info_test("ok");},2000);

   // 以下为自由调用函数,用于获取数据并加载。
   track_info = function (user_id){
        $.post("/manage/track_info", {"user_id": user_id}, function(data){
            var data = JSON.parse(data);
            var data_name = "张三的轨迹";
            var data_raw = data['data'];
            var data_list = new Array();
            for(var i=data_raw.length-1; i>=0;i--){
                // console.log(data_raw[i]);
                data_list.push(data_raw[i]['coordinates']);
            }
            // console.log(data_list);
            set_track_list(my_pathSimplifierIns, data_name, data_list);
            init_track_paths(my_pathSimplifierIns, 10000);
        });
   };

// end!
});