$(function () {
    const ids = [
        "59cda964ad01be237680e29d",
        "5ab0ae831315e00e3cb61db8",
        "5aaf2f3ee39a7b6f4b6ce26f"

    ];
    const names = ['栾新军',  '童小平', '刘江鹏'];
    const id_name_map = {
        "59cda964ad01be237680e29d": "栾新军",
        "5ab0ae831315e00e3cb61db8": "童小平",
        "5aaf2f3ee39a7b6f4b6ce26f": "刘江鹏"
    };

    // 初始化柱状图
    let get_opt1 = function () {

        let setting = {
            title: {text: "事件汇总"},
            tooltip: {
                trigger: 'axis',
                axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                    type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            legend: {
                data: ['超速', '急加速', '急减速']
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [
                {
                    type: 'category',
                    data: names
                }
            ],
            yAxis: [
                {
                    type: 'value'
                }
            ],
            series: [
                {
                    name: '超速',
                    type: 'bar',
                    data: [1, 1, 1]
                },
                {
                    name: '急加速',
                    type: 'bar',
                    data: [2, 1, 0]
                },
                {
                    name: '急减速',
                    type: 'bar',
                    data: [0, 0, 0]
                }
            ]
        };
        return setting;
    };
    echarts.init($("#my_chart_01")[0]).setOption(get_opt1());

});