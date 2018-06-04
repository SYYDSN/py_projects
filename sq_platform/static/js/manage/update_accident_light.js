$(function(){
    // 选择事故状态的checkbox
    $(".accident_status").each(function(){
        let $this = $(this);
        $this.click(function(){
            let status = $this.prop("checked");
            if(status){
                $(".accident_status").not(this).prop("checked", false);
            }
            else{}
        });
    });

    // 初始化富文本编辑器
    const E = window.wangEditor;
    let desc_obj = new E("#accident_content");
    desc_obj.customConfig.debug = true;
    desc_obj.customConfig.uploadImgMaxSize = 3 * 1024 * 1024;
    desc_obj.customConfig.uploadImgMaxLength = 1;
    desc_obj.customConfig.uploadImgShowBase64 = true;
    desc_obj.customConfig.uploadImgServers = "/manage/upload_file";
    desc_obj.create();

    // 提交事故事件
    $("#submit_accident").click(function(){
        let a_name = $.trim($("#accident_title").val()); // 事故名称
        let a_type = $.trim($("#accident_type").val()); // 事故类型
        let a_code = $.trim($("#accident_code").val()); // 事故编号
        let a_driver = $.trim($("#accident_driver").val()); // 涉及司机
        let a_truck = $.trim($("#accident_truck").val()); // 事故车辆
        let a_address = $.trim($("#accident_address").val()); // 事故地址
        let a_time = $.trim($("#accident_time").val()); // 事故日期
        let a_city = $.trim($("#accident_city").val()); // 事故城市
        let a_loss = $.trim($("#accident_loss").val()); // 事故损失
        let a_level = $.trim($("#accident_level").val()); // 严重程度
        let a_status = $("#check_processed").prop("checked")? 1: 0;  // 是否已处理
        let a_comment = $.trim($("#accident_comment").text()); // 备注
        let content = desc_obj.txt.html();
        let args = {
            "title": a_name,
            "type": a_type,
            "code": a_code,
            "driver_name": a_driver,
            "plate_number": a_truck,
            "address": a_address,
            "time": a_time,
            "city": a_city,
            "loss": a_loss,
            "level": a_level,
            "status": a_status,
            "comment": a_comment,
            "content": content
        };
        let url = "/manage/update_accident";
        $.post(url, args, function(resp){
            let json = JSON.parse(resp);
            console.log(json);
        });
    });

    // 初始化日期选择器
    $("#accident_time").datetimepicker({
        language: "zh-CN",
        weekStart:1,  // 星期一作为一周的开始
        minView: 0,  // 显示小时和分
        startView: 2,
        autoclose: true,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd hh:ii:ss",
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