$(function(){
    // 初始化富文本编辑器
    const E = window.wangEditor;
    let desc_obj = new E("#accident_description");
    desc_obj.create();

    // 初始化日期选择器
    $("#accident_time").datetimepicker({
        language: "zh-CN",
        weekStart:1,  // 星期一作为一周的开始
        minView: 2,  // 不显示小时和分
        startView: 2,
        autoclose: false,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd",
    }).on("show", function(ev){
        // 当选择器显示时被触发
        console.log(ev);
        console.log("选择器面板被打开");
    }).on("changeDate", function(ev){
        // 当日期被改变时被触发
        console.log(ev);
        console.log("选择器日期被改变");
    }).on("hide", function(ev){
        // 当日期被隐藏时被触发
        console.log(ev);
        console.log("选择器日期被隐藏");
    });

    var resize = function(){
        // 重新计算中间表格的高度
        console.log(1);

        let main_zone_height = $("#main_zone").height();
        let first_height = $(".first_row").height();
        let second_height = $(".second_row").height();
        if((main_zone_height - first_height - second_height) > 10){
            let w_h = $("html").height();
            let b_t = $(".second_row").offset().top + $(".second_row").height();
            let h = w_h - b_t;
            let table_col = $(".second_row>.my_col:eq(0)");
            let x = parseInt(table_col.css("height").split("px")[0]);
            table_col.css("height", x + h - 35);
        }else{}
    };

    $(window).resize(function(){resize();});
    resize();

    // 修改按钮事件


    // 确定跳转按钮事件
    $("#redirect_btn").click(function(){
        let args = {};
        let begin_date_str = get_picker_date($("#begin_date"));
        let end_date_str = get_picker_date($("#end_date"));
        console.log(begin_date_str, end_date_str);
        if(begin_date_str !== null && end_date_str !== null){
            let begin_date = new Date(begin_date_str);
            let end_date = new Date(end_date_str);
            if(end_date < begin_date){
                // 检查时间的合法性
                pop_tip_div("结束时间不能早于开始时间");
                return false;
            }
            else{
                // pass
            }
        }else{}
        if(begin_date_str !== null){
            args["begin_date"] = begin_date_str + " 00:00:00";
        }
        if(end_date_str !== null){
            args["end_date"] = end_date_str + " 23:59:59";
        }
        let city = $.trim($("#select_city").val());
        if(city !== ""){
            args['city'] = city;
        }else{}
        let driver_name = $.trim($("#select_driver").val());
        if(driver_name !== ""){
            args['driver_name'] = driver_name;
        }else{}
        let plate_number = $.trim($("#select_car").val());
        if(plate_number !== ""){
            args['plate_number'] = plate_number;
        }else{}

        let url = "accident?";
        url += $.param(args);
        console.log("url = " + url);
        location.href = url;
    });

    // 清空筛选条件
    $("#clear_condition").click(function(){
        $("#begin_date,#end_date,#select_city,#select_car,#select_driver").val("");
    });


    function init_input(arg_url) {
        // 从url分析参数,进行初始化工作
        let url = typeof(arg_url) === "undefined" ? location.href : arg_url;
        if (url.indexOf("?") !== -1) {
            let arg_str = url.split("?")[1];
            arg_str = decodeURIComponent(arg_str);
            console.log(arg_str);
            let a_list = arg_str.split("&");
            for (var item of a_list) {
                if (item.indexOf("=") !== -1) {
                    let temp = item.split("=");
                    let k = temp[0];
                    let v = temp[1];
                    if (k === "begin_date") {
                        $("#begin_date").val(v.split(" ")[0]);
                    }
                    else if (k === "end_date") {
                        $("#end_date").val(v.split(" ")[0]);
                    }
                    else if (k === "driver_name") {
                        $("#select_driver").val(v);
                    }
                    else if (k === "city") {
                        $("#select_city").val(v);
                    }
                    else if (k === "plate_number") {
                        $("#select_car").val(v);
                    }

                } else {}
            }
        }
        else {
            // pass
        }
    }
    init_input();  // 根据url参数初始化input状态

// end!
});