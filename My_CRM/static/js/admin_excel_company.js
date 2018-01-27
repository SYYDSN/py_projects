/**
 * Created by walle on 17-2-8.
 */
$(function () {

    // 修改公司操作excel权限的函数
    $(".c_id").each(function(){
        let item = $(this);
        item.change(function(){
            let $this = $(this);
            let status = $this.prop("checked")?1:0;
            let sn = parseInt($this.attr("data-id"));
            let args = {"sn": sn, "status_code": status, "the_type": "set_status"};
            $.post("/company/excel", args, function(data){
                console.log(data);
                if(data['message'] === "success"){
                    $this.prop("checked", status === 1?true:false);
                }
                else{
                    alert(data['message']);
                }
            });
        });
    });

    // 默认日期
    const default_date = new Date();
    const current_year = default_date.getFullYear();
    const current_month = default_date.getMonth() + 1;
    const current_day = default_date.getDate();
    const current_hour = default_date.getHours();
    const current_minute = default_date.getMinutes();
    console.log(current_year, current_month, current_day, current_hour, current_minute);

    // 获取一个月的最后一天数值
    let get_last_day = function(month){
        /*注意这个月不是ｊｓ哪个需要＋１的月，而是实际上的月份*/
        return new Date(current_year, month, 0).getDate();
    };

    // 填充一月内天
    fill_day = function($obj, month){
        /*$obj待填充的目标，一般是ｓｅｌｅｃｔ标签,month是月份*/
        let days = get_last_day(month);
        let olds = $obj.children().length;
        let select = parseInt($obj.val());
        if( olds === days){
            //nothing...
        }
        else{
            $obj.empty();
            let html = "";
            for(let i=1;i<=days;i++){
                html += `<option value="${i}">${i}</option>`;
            }
            $obj.append(html);
            if(select <= days){
                $obj.val(select);
            }
        }
    };
    fill_day($(".begin .day"), 1);
    fill_day($(".end .day"), 1);

    // 设置默认起止时间
    let set_default = function(){
        $(".begin .year").val(current_year);
        $(".begin .month").val(current_month);
        $(".begin .day").val(current_day);
        $(".begin .hour").val(0);
        $(".begin .minute").val(0);
        $(".end .year").val(current_year);
        $(".end .month").val(current_month);
        $(".end .day").val(current_day);
        $(".end .hour").val(current_hour);
        $(".end .minute").val(current_minute);
    };
    set_default();

    // 选择月份事件。
    $(".month").each(function(){
        let $this = $(this);
        $this.change(function(){
            let $this = $(this);
            let month = $this.val();
            let day_select = $this.next(".day:first");
            fill_day(day_select, month);
        });
    });

    // 添加
    add_excel = function () {
        $("#myModalLabel").text("生成excel文件");
        $("#pop_modal").click();
        var members = $("#sn,#url,#url_name,#company_sn,#channel_sn,#pattern_sn,#platform_sn");
        members.val('');
    };


    // 保存
    $("#save_url").click(function () {
        let b_year = $(".begin .year:first").val();
        let b_month = $(".begin .month:first").val();
        let b_day = $(".begin .day:first").val();
        let b_hour = $(".begin .hour:first").val();
        let b_minute = $(".begin .minute:first").val();
        let begin = `${b_year}-${b_month}-${b_day} ${b_hour}:${b_minute}:00`;
        let e_year = $(".end .year:first").val();
        let e_month = $(".end .month:first").val();
        let e_day = $(".end .day:first").val();
        let e_hour = $(".end .hour:first").val();
        let e_minute = $(".end .minute:first").val();
        let end = `${e_year}-${e_month}-${e_day} ${e_hour}:${e_minute}:59`;
        console.log(begin, end);
        $.post("/company/excel",{"begin": begin, "end": end, "the_type": "export"}, function(json){
            if(json['message'] === "success"){
                alert("生成成功");
                location.reload();
            }
            else{
                alert(json['message']);
            }
        });
    });

    // 删除
    delete_excel = function($obj){
        var file_name = $.trim($obj.attr("data-id"));
        var r = confirm("你确实向删除此excel吗？");
        if (r) {
            var args = {"the_type": "delete", "file_name": file_name};
            $.post("/company/excel", args, function (data) {
                if (data['message'] == "success") {
                    alert("删除成功");
                    location.reload();
                }
                else {
                    alert(data["message"]);
                }
            });
        } else {}
    };


    //end !
});