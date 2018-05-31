$(function(){
    // 点击显示文件路径的input的事件.
    $("#file_path").click(function(){
        $("#up_file").click();
    });

    // file类型的input在加载完文件时的事件.
    $("#up_file").change(function(){
        let val = $(this).val();
        $("#file_path").val(val);
    });
    
    // 上传文件按钮点击事件.
    $("#upload_btn").click(function(){
        let url = `http://${location.host}/manage/upload_file`;
        upload("case_file", $("#up_file"), url);
    });
    
// end!
});
