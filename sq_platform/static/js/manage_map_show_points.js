/**
 * Created by walle on 17-8-17.展示海量的点
 */
$(function(){

    /*加载 PointSimplifier(海量点简化展示模块),模块名：ui/misc/PointSimplifier*/
    AMapUI.loadUI(['misc/PointSimplifier'], function(PointSimplifier){
        if(!PointSimplifier.supportCanvas){
            console.log("不支持Canvas");
        }
        else{
            console.log("支持Canvas");
            initPage(PointSimplifier);
        }
    });

    /*初始化组件*/
    function initPage(PointSimplifier){
        var pointSimplifierIns = new PointSimplifier({
            map: global_map,
            compareDataItem: function(a, b, aIndex, bIndex){
                //数据源中靠后的元素优先，index大的排到前面去
                return aIndex > bIndex ? -1 : 1;
            },
            getPosition: function(dataItem){
                //返回数据项的经纬度，AMap.LngLat实例或者经纬度数组
                return dataItem.position;
            },
            getHoverTitle: function(dataItem, idx){
                //返回数据项的Title信息，鼠标hover时显示
                return "No:" + idx + " 用户:"+ dataItem.name + " 坐标:"  + dataItem['position'][0] + "," + dataItem['position'][1];
            },
            renderOptions: {
                // 点的样式
                pointStyle: {
                    fillStyle: "blue"  // 蓝色填充
                }
            }
        });

        //随机创建一批点，仅作示意
        var data = createPoints(global_map.getCenter(), 10);

        //设置数据源，data需要是一个数组
        pointSimplifierIns.setData(data);

        //监听事件
        pointSimplifierIns.on('pointClick pointMouseover pointMouseout', function (e, record) {
            console.log(e.type, record);
        });
    }

    //仅作示意
    function createPoints(center, num) {
        var data = [];
        for (var i = 0, len = num; i < len; i++) {
            data.push({
                name: "user_" + i,
                position: [
                    center.getLng() + (Math.random() > 0.5 ? 1 : -1) * Math.random(),
                    center.getLat() + (Math.random() > 0.5 ? 1 : -1) * Math.random()
                ]
            });
        }
        return data;
    }
//end!
});
