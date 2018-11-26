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
            var args = {"key": key, "type": "import"};
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert(`成功导入${json['inserted']}条数据`);
                    location.reload();
                }
                else{
                    alert(status);
                }
            });
        });
    });

    /*删除导入文件和记录*/
    $("#delete_import").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
            "ids": JSON.stringify(d)
        };
        var p = confirm("这将删除导入的文件删除!");
        if(p){
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
        else{
            // ...
        }
    });

    /*全选事件*/
    $("#check_all").click(function(){
        var checked = $("#check_all:checked").length === 1? true: false;
        if(checked){
            $(".table_outer .select >input[type='checkbox']").prop("checked", true);
        }
        else{
            $(".table_outer .select >input[type='checkbox']").prop("checked", false);
        }
    });

});