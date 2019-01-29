$(function () {
    /*弹出上传文件的窗口*/
    /*全选事件*/
    $("#check_all").click(function () {
        var checked = $("#check_all:checked").length === 1 ? true : false;
        if (checked) {
            $(".table_outer .select >input[type='checkbox']").prop("checked", true);
        }
        else {
            $(".table_outer .select >input[type='checkbox']").prop("checked", false);
        }
    });

    // 翻页事件
    PageHandler();
// end!
});