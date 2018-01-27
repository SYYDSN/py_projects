$(function () {

    //加载PointSimplifier，loadUI的路径参数为模块名中 'ui/' 之后的部分
    AMapUI.loadUI(['misc/PointSimplifier'], function (PointSimplifier) {

        if (!PointSimplifier.supportCanvas) {
            alert('当前环境不支持 Canvas！');
            return false;
        }

        console.log('当前环境支持 Canvas！');
        //启动页面
        initPage(PointSimplifier);
    });

    // 初始化页面的函数
    function initPage(PointSimplifier) {
        //创建组件实例
        pointSimplifierIns = new PointSimplifier({
            map: map, //关联的map
            compareDataItem: function (a, b, aIndex, bIndex) {
                //数据源中靠后的元素优先，index大的排到前面去
                return aIndex > bIndex ? -1 : 1;
            },
            getPosition: function (dataItem) {
                //返回数据项的经纬度，AMap.LngLat实例或者经纬度数组
                return dataItem.position;
            },
            getHoverTitle: function (dataItem, idx) {
                //返回数据项的Title信息，鼠标hover时显示
                return '序号: ' + idx;
            },
            renderConstructor: PointSimplifier.Render.Canvas.GroupStyleRender,
            renderOptions: {
                //点的样式
                "drawQuadTree": false,
                "drawPositionPoint": false,
                "drawShadowPoint": false,
                "disableHardcoreWhenPointsNumBelow": 0,
                "pointStyle": {
                    "content": "circle",
                    "width": 6,
                    "height": 6,
                    "fillStyle": "#1f77b4",
                    "lineWidth": 1,
                    "strokeStyle": null
                },
                "topNAreaStyle": {
                    "autoGlobalAlphaAlpha": true,
                    "content": "rect",
                    "fillStyle": "#e25c5d",
                    "lineWidth": 1,
                    "strokeStyle": null
                },
                "pointHardcoreStyle": {
                    "content": "none",
                    "width": 5,
                    "height": 5,
                    "lineWidth": 1,
                    "fillStyle": null,
                    "strokeStyle": null
                },
                "pointPositionStyle": {
                    "content": "circle",
                    "width": 2,
                    "height": 2,
                    "lineWidth": 1,
                    "strokeStyle": null,
                    "fillStyle": "#cc0000"
                },
                "pointHoverStyle": {
                    "width": 10,
                    "height": 10,
                    "content": "circle",
                    "fillStyle": null,
                    "lineWidth": 2,
                    "strokeStyle": "#ffa500"
                },
                "shadowPointStyle": {
                    "fillStyle": "rgba(0,0,0,0.2)",
                    "content": "circle",
                    "width": 6,
                    "height": 6,
                    "lineWidth": 1,
                    "strokeStyle": null
                },
                getGroupId: function (item, idx) {
                    console.log(item);
                    console.log(idx);
                    return 1;
                    // return Math.round(Math.random());
                },
                groupStyleOptions: function (gid) {
                    console.log(gid);
                    return {
                        pointStyle: {
                            fillStyle: colors[gid % colors.length]
                        }
                    };
                }
            }

        });

        function startAnim(){
            var renderOptions = pointSimplifierIns.getRenderOptions();
            var pointStyle = renderOptions.pointStyle;
            var size = pointStyle.width;
            range = [2, 10];
            step = size < range[1] ? 1: -1;

            function anim(){
                size += step;
                pointStyle.width = pointStyle.height = size;
                pointSimplifierIns.render();
                if(size >= range[1]){
                    step = -1;
                }
                else if(size <= range[0]){
                    step = 1;
                }
                // setTimeout(anim, 100);
            }
            anim();
        }


        //监听事件
        pointSimplifierIns.on('pointClick pointMouseover pointMouseout', function (e, record) {
            console.log(e.type, record);
        });

        demo_data = createPoints(map.getCenter(), 100);
    colors = [
        "#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00",
        "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707",
        "#651067", "#329262", "#5574a6", "#3b3eac"
    ];
    pointSimplifierIns.setData(demo_data);
    startAnim();
    }

    //仅作示意
    function createPoints(center, num) {
        var data = [];
        for (var i = 0, len = num; i < len; i++) {
            data.push({
                position: [
                    center.getLng() + (Math.random() > 0.5 ? 1 : -1) * Math.random(),
                    center.getLat() + (Math.random() > 0.5 ? 1 : -1) * Math.random()
                ]
            });
        }
        return data;
    }



// end !
});