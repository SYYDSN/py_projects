$(function(){
    let get_key = function(){
        /*
        * 获取url的path的最后一段,这用于判断处于哪个页面?也是区别不同的图表页面的根本依据
        * summary  总览
        * 横坐标 老师 纵坐标 成功率
        * teacher 以老师分组,每个老师一个图表.
        * 横坐标 产品 纵坐标 成功率
        * product 以产品分组 每个产品一个图表
        * 横坐标 老师 纵坐标 成功率
        * */
        return location.pathname.split("/").reverse()[0]
    };
    const key = get_key();  // 图表的分组依据,也就是get_key函数的返回值.

    let bar_option = function(name, x, y, z){
        /*
        *柱状图的配置项
        * */
        let subtext = '';
        let l = x.length;
        for(let i=0; i<l; i++){
            subtext += `${x[i]}: ${z[i]}单,  `;
        }

        let option = {
            title: {
                text: name,
                subtext: subtext
            },
            xAxis: {
                type: 'category',
                data: x
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                itemStyle: {
                    normal: {
                        color: function (params) {
                            let index = params['dataIndex'];
                            let count = z[index];
                            if(count <= 10){
                                return "grey";
                            }
                            else{
                                return "red";
                            }
                        }
                    },
                },
                label: {
                    normal: {
                        show: true,
                        position: "top",
                        formatter: function(params){
                            console.log(params);  // 继续
                            return "100";
                        }
                    }
                },
                data: y,
                type: 'bar'
            }]
        };
        return option;
    };

    let create_chart = function(raw_dict){
        /*
        * 创建可以直接用于echarts的数据.主要有x轴数据和y轴数据组成.
        * raw_dict: 从后台取回的原始数据{老师名1: {产品名1: [喊单记录1, ...]}, 产品名2: [喊单记录1, ...], ....}
        * return:
        * */
        let container = $("#chart_zone");
        if(key === "teacher"){
            /*以老师为分组依据*/
            for(let teacher_name in raw_dict){
                let all_product = raw_dict[teacher_name];
                let x_data = [];  // x轴数据
                let y_data = [];  // y轴数据
                let z_data = [];  // 数据总数
                for(let product_name in all_product){
                    let per = (all_product[product_name]['per'] * 100).toFixed(1);
                    y_data.push(per);
                    z_data.push(all_product[product_name]['count']);
                    x_data.push(product_name);
                }
                let opt = bar_option(teacher_name, x_data, y_data, z_data);
                let chart_div = $("<div class='chart_div'></div>");
                container.append(chart_div);
                draw_chart(chart_div[0], opt);
            }
        }
    };

    let draw_chart = function(dom_obj, opt){
        /*
        * 绘制图标的函数
        * param dom_obj: 一个javascript的dom对象.
        * param opt:  echarts的配置字典
        * */
        let charts = echarts.init(dom_obj);
        charts.setOption(opt);
    };

    let query_data = function(begin_str, end_str){
        /*
        * 向服务器查询老师的喊单信息的汇总数据.
        * */
        let url = `/teacher_charts/${key}`;
        let args = {"begin": begin_str, "end": end_str};
        $.post(url, args, function(resp){
            let json = JSON.parse(resp);
            let data = json['data'];   // 老师的喊单信息的汇总数据
            create_chart(data);  // 处理数据并绘制本页面所有的图表
        });
    };

    query_data();
});