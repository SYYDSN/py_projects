$(function(){
    /*上传成功和失败事件*/
    var upload_success = function(resp){
        console.log(resp);
        var json = JSON.parse(resp);
        var status = json['message'];
        if(status === "success"){
            location.reload();
        }
        else{
            alert(status);
        }
    };

    var upload_error= function(resp){
        console.log(resp);
    };

    /*上传*/
     $("#open_file").click(function(){
        $("#upload_file").upload(location.pathname, upload_success, upload_error, {"upload-file": "1"});
    });

   /*导入数据*/
   $(".import_btn").each(function(){
       var $this = $(this);
       $this.click(function(){
           var key = $.trim($this.attr("data-id"));
           var args = {"key": key};
           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['status'];
               if(status === "success"){
                   alert("导入成功");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       });
   });

});