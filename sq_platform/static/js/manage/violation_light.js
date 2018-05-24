$(function(){
    // 初始化日期选择器
    $("#begin_date, #end_date").datetimepicker({
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
        let title_row_height = $(".title_row").height();
        let middle_zone_height = $(".middle_zone").height();
        if((main_zone_height - title_row_height - middle_zone_height) > 10){
            let w_h = $("html").height();
            let b_t = $(".middle_zone").offset().top + $(".middle_zone").height();
            let h = w_h - b_t;
            let x = parseInt($(".table_col").css("height").split("px")[0]);
            $(".table_col").css("height", x + h - 5);
        }else{}
    };

    $(window).resize(function(){resize();});
    resize();

    // 事件注销,只保留直接修改关联司机的功能
    // // 修改按钮事件
    // $("#show_table .my_btn_group .edit").each(function(){
    //     let item = $(this);
    //     item.click(function(){
    //         let $this = $(this);
    //         let vio_id = $this.attr("data-id");
    //         let tr = $(`#${vio_id}`);
    //         let span = tr.find(".span");
    //         let select = tr.find(".select");
    //         let span_show = span.hasClass("show");
    //         console.log(span_show);
    //         if(span_show){
    //             // 处于正常状态
    //             $this.text("放弃");
    //         }
    //         else{
    //             $this.text("修改");
    //         }
    //         span.toggleClass("show").toggleClass("hide");
    //         select.toggleClass("show").toggleClass("hide");
    //     });
    // });
    //
    // // 保存按钮事件
    // $("#show_table .my_btn_group .save").each(function(){
    //     let item = $(this);
    //     item.click(function(){
    //         let $this = $(this);
    //         let vio_id = $this.attr("data-id");
    //         let tr = $(`#${vio_id}`);
    //         let span = tr.find(".span");
    //         let select = tr.find(".select");
    //         let span_show = span.hasClass("show");
    //         if(!span_show){
    //             let user_id = select.val();
    //             if(user_id !== ""){
    //                 // 修改违章的所有人
    //                 let args = {
    //                   "vio_id": vio_id,
    //                   "user_id": user_id,
    //                   "the_type": "update_user_id"
    //                 };
    //                 $.post("violation", args, function(resp){
    //                     span.text(select.find("option:selected").text());
    //                 });
    //             span.toggleClass("show").toggleClass("hide");
    //             select.toggleClass("show").toggleClass("hide");
    //             }else{}
    //         }
    //         else{
    //             // 非编辑状态,pass
    //         }
    //     });
    // });

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
        let driver = $.trim($("#select_driver").val());
        if(driver !== ""){
            args['user_id'] = driver;
        }else{}
        let plate_number = $.trim($("#select_car").val());
        if(plate_number !== ""){
            args['plate_number'] = plate_number;
        }else{}
        let check_01 = $("#check_processed").prop("checked");   // 已处理
        let check_02 = $("#check_unprocessed").prop("checked");   // 未处理
        if(check_01 && check_02){
            // nothing....
        }
        else{
            if(check_01){
                // 已处理
                args['vio_status'] = 3;
            }
            else if(check_02){
                args['vio_status'] = 1;   // 已处理
            }
        }
        let url = "violation?";
        url += $.param(args);
        console.log("url = " + url);
        location.href = url;
    });

    // 清空筛选条件
    $("#clear_condition").click(function(){
        $("#check_processed,#check_unprocessed").prop("checked", true);
        $("#begin_date,#end_date,#select_city,#select_car,#select_driver").val("");
    });

    // let prev_relevant_user = null;   // 在修改违章关联的事件发生前,保存之前的违章相关司机,以便修改失败的时候回溯.
    // 改变违章记录归属司机的selected事件.
    $(".change_user_id").each(function(){
        let select = $(this);
        // select.mousedown(function(){
        //     // 把改变之前的违章关联司机的id写入全局变量
        //     prev_relevant_user = select.parents("tr:first").attr("data-uid");
        // });
        select.change(function(){
            let tr = select.parents("tr:first");
            let vio_id = tr.attr("id");
            let prev_user_id = tr.attr("data-uid");
            let new_user_id = select.val();
            let new_driver = driver_dict[new_user_id];
            let emp_num = new_driver === undefined? "": new_driver['employee_number'];
            // 发送修改违章关联司机的请求
            let u = "/manage/violation";
            let args = {
                "the_type": "update_user_id",
                "vio_id": vio_id,
                "user_id": new_user_id
            };
            if(vio_id.length === 24 && new_user_id.length === 24){
                $.post(u, args, function(resp){
                    let json = JSON.parse(resp);
                    if(json['message'] === "success"){
                        let id_str = "#" + vio_id;
                        $(`${id_str} .employee_number`).text(emp_num);
                        $(`${id_str}`).attr("data-uid", new_user_id);
                    }
                    else{
                        alert(json['message']);
                        select.val(prev_user_id);
                        return false;
                    }
                });
            }else{
                console.log(`错误的id长度,vio_id:${vio_id}, new_user_id:${new_user_id}`);
                select.val(prev_user_id);
                return false;
            }


        });
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
                    else if (k === "user_id") {
                        $("#select_driver").val(v);
                    }
                    else if (k === "city") {
                        $("#select_city").val(v);
                    }
                    else if (k === "plate_number") {
                        $("#select_car").val(v);
                    }
                    else if (k === "vio_status") {
                         $("#check_processed, #check_unprocessed").removeProp("checked");
                        if(v === "3"){
                            $("#check_processed").prop("checked", true);
                        }
                        else if (v === "1"){
                            $("#check_unprocessed").prop("checked", true);
                        }
                        else{
                             $("#check_processed, #check_unprocessed").prop("checked", true);
                        }
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