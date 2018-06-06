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
            "driver_id": a_driver,
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
        let a_id = get_url_arg("a_id");
        if(a_id){
            args['_id'] = a_id;
        }
        let url = "/manage/update_accident";
        $.post(url, args, function(resp){
            let json = JSON.parse(resp);
            if(a_id && json['message'] === "success"){
                alert("编辑成功");
                location.href = "/manage/accident";
            }
            else if(json['message'] === "success"){
                alert("提交成功");
            }
            else{
                alert(json['message']);
                return false;
            }
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

// end!
});