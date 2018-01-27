/**
 * Created by walle on 17-8-17.跟踪运动轨迹
 */
$(function () {

    /*加载PathSimplifier组件*/
    AMapUI.load(['ui/misc/PathSimplifier'], function (PathSimplifier) {
        if (!PathSimplifier.supportCanvas) {
            console.log("不支持Canvas");
        }
        else {
            console.log("支持Canvas");
            init_track_paths(PathSimplifier);
        }
    });

    /*初始化函数*/
    function init_track_paths(PathSimplifier) {
        var pathSimplifierIns = new PathSimplifier({
            zIndex: 100,
            map: global_map,
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

        //这里构建两条简单的轨迹，仅作示例
        pathSimplifierIns.setData([{
            name: "轨迹1",
            path:[
                [100.340417, 27.376994],
                [101.426354, 27.827452],
                [103.392174, 28.208439],
                [103.905846, 28.232876]
            ]
        }]);

        //创建一个巡航器
        var navg0 = pathSimplifierIns.createPathNavigator(0, //关联第1条轨迹
            {
                loop: true, //循环播放
                speed: 100000
            });
        navg0.start();
    }

// end!
});