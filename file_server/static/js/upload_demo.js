$(function(){
    // 点击选择按钮的事件
    $("#select_btn").click(function(){
        $("#select_image").click();
    });

    // 上传图片的input的change事件.
    $("#select_image").change(function(){
        try{
            var $this = $("#select_image");
            var file = $this[0].files[0];
            var reader = new FileReader();
            reader.readAsDataURL(file);
            var set_img = function(data){
                var img_obj = $("#view_image");
                img_obj.attr("src",data);
            };
            reader.onload = function(event){
                console.log(event);
                var img = event.target.result;
                set_img(img);
            };
        }
        catch(e){
            alert(e);
        }

    });

    // 上传图片模态框,提交按钮事件
    $("#upload_btn").click(function(){
        var url = "/images/obj/save/image_file";
        $.pop_alert("上传图片中...");
        $("#select_image").upload(url, function(json){
            $.close_alert();
            var resp = JSON.parse(json);
            var status = resp['message'];
            if(status === "success"){
                $(".json_div_inner").text(json);
            }
            else{
                $(".json_div_inner").text(status);
            }
        }, function(e){
            alert(e.toString());
            close_alert();
            return false;
        }, {"auth": "647a5253c1de4812baf1c64406e91396"});
    });


});