$(function () {
    /*脚本全局变量，非js的全局变量*/
    var point_size = 14;  // 点的大小


    function set_point_size(l) {
        if (l < 10) {
            point_size = 20;
        }
        else if (10 <= l < 50) {
            point_size = 18;
        }
        else if (50 <= l < 100) {
            point_size = 16;
        }
        else if (100 <= l < 200) {
            point_size = 14;
        }
        else {
            point_size = 12;
        }
    }


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
    initPage = function (PointSimplifier) {
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
                console.log(dataItem);
                console.log(idx);
                console.log(dataItem['user_phone']);
                return 'phone: ' + dataItem['user_phone'] + "<br>" + "upload: " + dataItem['time'].split(".")[0];
            },
            renderConstructor: PointSimplifier.Render.Canvas.GroupStyleRender,
            renderOptions: {
                //点的样式
                "pointStyle": {
                    "fillStyle": "#1f77b4"
                },
                getGroupId: function (item, index) {
                    console.log(item);
                    console.log(index);
                    return index;  //
                },
                groupStyleOptions: function (code_num) {
                    /*根据status_code获取样式*/
                    var style = get_point_style(code_num);
                    // var style = get_img_point(code_num);
                    console.log("样式");
                    console.log(style);
                    return style;
                }
            }

        });

        // 自定义图片点的样式
        get_img_point = function (status_code) {
            var style = {pointStyle: {"content":
                "http://127.0.0.1:5000/static/image/icon/normal_truck.png"}};
            return style;
        };

        // 加载数据
        get_data_ajax();

        //监听事件
        pointSimplifierIns.on('pointClick pointMouseover pointMouseout', function (e, record) {
            console.log(e.type, record);
        });
    };

    // 定义一个获取自定义点样式的函数
    get_point_style = function (status_code) {
        /*
        * status_code必须是一个int参数，这是高德地图的硬性规定。
        * 实际上，这个参数是后台用来定义安全级别的，同时也对样式做了却别。
        * 返回的是一个字典类型的对象。符合renderOptions的要求。
        * */
        var styles =
            [
                {"fillStyle": "#1f77b4"},
                {"fillStyle": "#dc3912"},
                {"fillStyle": "#e67300"},
                {"fillStyle": "#8b0707"},
                {"fillStyle": "#6633cc"},
                {"fillStyle": "#aaaa11"},
                {"fillStyle": "#316395"},
                {"fillStyle": "#994499"},
                {"fillStyle": "#66aa00"},
                {"fillStyle": "#0099c6"},
                {"fillStyle": "#109618"},
                {"fillStyle": "#ff9900"},
                {"fillStyle": "#dc3912"},
                {"fillStyle": "#3366cc"}
            ];
        var style = styles[status_code];
        style['width'] = point_size;
        style['height'] = point_size;
        style = {"pointStyle": style};
        return style;
    };

    // ajax方式获取数据，仅在测试使用，正式要使用web-socket
    get_data_ajax = function (){
        $.post("/manage/test_last_position", function (data) {
            var data = JSON.parse(data);
            // 设置点的大小
            set_point_size(data.length);
            console.log(data);
            var result = [];
            var l = data.length;
            for (var i = 0; i < l; i++) {
                var raw_temp = data[i];
                var temp = {
                    "user_id": raw_temp['user_id'], "position": raw_temp['loc'],
                    "time": raw_temp['time'], "user_phone": raw_temp['user_phone']
                };
                console.log("打印用户:" + temp['user_phone'], temp['position']);
                result.push(temp);
            }
            pointSimplifierIns.setData(result);  // 加载数据
        });
    };



// end !
});