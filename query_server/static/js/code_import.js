$(function(){
    /*上传成功和失败事件*/
    var upload_success = function(resp){
        console.log(resp);
    };

    var upload_error= function(resp){
        console.log(resp);
    };

    /*上传*/
     $("#open_file").click(function(){
        $("#upload_file").upload(location.pathname, upload_success, upload_error, {"upload-file": "1"});

    });

});