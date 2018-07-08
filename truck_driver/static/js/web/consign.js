$(function(){
    // 日期选择器初始化函数
    (function () {
        /* 初始化日期函数,
        注意，如果你使用bootstrap,input就必须加上form-control类，否则左右选择的小箭头不显示
        * 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/index.htm
        * id_str参数是日期input的id/class
        */
        $(`#entry_date`).datetimepicker({
            language: "zh-CN",
            weekStart: 1,  // 星期一作为一周的开始
            minView: 2,  // 不显示小时和分
            autoclose: true,  // 选定日期后立即关闭选择器
            format: "yyyy-mm-dd"
        }).on("show", function (ev) {
            // 当选择器显示时被触发.示范,无实际意义.
            console.log(ev);
            console.log("选择器面板被打开");
        }).on("hide", function (ev) {
            // 当选择器隐藏时被触发 示范,无实际意义
            console.log(ev);
            console.log("选择器面板被隐藏");
        }).on("changeDate", function (ev) {
            // 当日期被改变时被触发
            console.log(ev);
            console.log("选择器日期被改变");
        });
    })();

// end!
});