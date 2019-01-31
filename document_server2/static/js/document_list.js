$(function () {
    /*上传成功事件*/
    var upload_success = function(resp){
        $(".file_path").text("");
        $(".modal_outer_progress").css("display", "none");
        $("#my_progress div").css("width", "0%");
        $("#my_progress .my_per").text("0%");
        $(".upload_line").css("display", "flex");
        $(".process_line").css("display", "none");

        console.log(resp);
        var json = JSON.parse(resp);
        var status = json['message'];
        if(status === "success"){
            alert("上传成功!");
        }
        else{
            alert(status);
        }
        location.reload();
    };

    /*上传失败事件*/
    var upload_error= function(resp){
        $(".file_path").text("");
        $(".modal_outer_progress").css("display", "none");
        $("#my_progress div").css("width", "0%");
        $("#my_progress .my_per").text("0%");
        $(".upload_line").css("display", "flex");
        $(".process_line").css("display", "none");

        console.log(resp);
        alert("上传失败");
    };

    /*上传进度处理函数*/
    var progress_cb = function(resp){
        console.log(resp);
        var val = `${resp}%`;
        $("#my_progress div").css("width", val);
        $("#my_progress .my_per").text(val);
        if(resp === 100){
            $(".upload_line").css("display", "none");
            $(".process_line").css("display", "flex");
        }else{}
    };

    // 弹出选择上传文件框
    $("#add_md").click(function(){
            $("#upload_file").click();

    });

    // 选择文件后,自动上传
    $("#upload_file").change(function(){
        $(".file_path").text($("#upload_file").val());
        upload();
    });

    /*上传函数*/
    var upload = function(){
        var $obj = $("#upload_file");
        let file_name = $obj.attr("name");
        if(file_name){
            // nothing...
        }
        else{
            file_name = "file"
        }
        let file_data = $obj[0].files[0];
        let file_series = $.trim($("#select_series .current_value").text());
        var opts = {
            headers: {"series":encodeURIComponent(file_series)},
            file_name: file_name,
            file_data: file_data,
            max_size: 900000,
            url: "/upload",
            success_cb: upload_success,
            progress_cb: progress_cb,
            error_cb: upload_error
        };
        $(".modal_outer_progress").css("display", "flex");
        $.upload(opts);
    };

    /*预览md文件*/
    $(".view_doc").each(function(){
        var $this = $(this);
        $this.click(function(){
            var _id = $this.attr("data-id");
            $.get("/read_file", {_id: _id}, function(resp){
                var json = JSON.parse(resp);
                var text = json['text'];
                var converter = new showdown.Converter();
                var html = converter.makeHtml(text);
                $("#modal_title").html(json['file_name']);
                $("#doc_html").html(html);
                $("#doc_modal").css("display", "flex");
            });
        });
    });

    /*预览pdf文件*/
    $(".view_pdf").each(function(){
        var $this = $(this);
        $this.click(function(){
            var _id = $this.attr("data-id");
            var url = `/download_file/${_id}`;
            PDFObject.embed(url, "#pdf_html");
            $("#pdf_modal").css("display", "flex");
        });
    });

    // 关闭模态框
    $(".close_modal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    // 选择上传文件类别
    $(".selected_series").each(function(){
        var $this = $(this);
        $this.click(function(){
            $("#select_series .current_value").text($this.text());
        });
    });

    // 跳转函数
    var redirect_to = function(arg_name, arg_value){
        var args = get_url_arg_dict();
        args[arg_name] = arg_value;
        var url = build_url(args);
        location.href = url;
    };

    // 分类按钮点击事件
    $(".series-btn").each(function(){
        var $this = $(this);
        $this.click(function(){
            var value = $.trim($(this).text());
            redirect_to("file_series", value);
        });
    });

    // 载入页面事件
    (function(){
        var args = get_url_arg_dict();
        var file_series = args['file_series'];
        if(file_series === undefined){
            // nothing...
        }
        else{
            $(".series-btn").each(function(){
                var $this = $(this);
                if(file_series === $.trim($this.text())){
                    $this.addClass("btn-primary");
                }
                else{
                    $this.removeClass("btn-primary");
                }
            });
        }
        var word = args['word'];
        if(word === undefined){
            // nothing...
        }
        else{
            $("#top_search_input").val(word);
        }
    })();

    // delete_doc
    $(".delete_doc").each(function(){
        var $this = $(this);
        $this.click(function(){
            var f_id = $.trim($this.attr("data-id"));
            var args = {"f_id": f_id};
            $.post("/remove_one", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }
                else{
                    alert(status);
                    return false;
                }
            });
        });
    });

    // 顶部导航Go点击事件
    $("#top_search_btn").click(function(){
        var value = $.trim($("#top_search_input").val());
            redirect_to("word", value);
    });

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