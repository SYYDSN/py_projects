$(function(){
    // 点击选择按钮的事件
    $("#select_btn").click(function(){
        $("#select_image").click();
    });

    let progress = function(per){
        // 处理上传进度
        console.log(`per is ${per}`);
        $("#my_progress>.progress-bar").attr("style", `width: ${per}%;`).attr("aria-valuenow", `${per}`);
        if(per > 52){
            $(".my_per").css("color", "#fff");
        }
        else{
            $(".my_per").css("color", "#ff7d7f");
        }
        $(".my_per").text(`${per}%`);
    };

    // 上传图片按钮事件
    $("#select_image").change(function(){
        let ul = $(".json_div_inner:first");
        ul.empty();
        let files = this.files;
        for(let f of files){
            ul.append(`<li id="${f.name}"><span>${f.name}</span></li>`);
        }
    });
    let call_back = function(){
        $("#upload_btn, #select_btn").attr("disabled", false).removeClass("disabled");
        alert("操作结束!");
    };

    // 上传图片模态框,提交按钮事件
    $("#upload_btn").click(function(){
            let $obj = $("#select_image");
            let files = $obj[0].files;
            let opts = {
                "url": "/file/save",
                "files": files,
                "success_cb": call_back,
                "error_cb": call_back,
                "progress_cb": progress
            };
            $("#upload_btn, #select_btn").attr("disabled", true).addClass("disabled");
            $.batch_upload(opts);
        });


});