$(function(){

    // 上传文件按钮
    $("#upload_image").click(function(){
        let file = document.getElementById("my_file").files[0];
        console.log(file);
        if(file){
            form = new FormData();
            form.append("image", file);
            let request = new XMLHttpRequest();
            let callback = function(){
                if(request.readyState === 4){  // 4的意思是读取服务器响应结束
                    let code = request.status;
                    if (code === 200){
                        let response = JSON.parse(request.response);  // 返回的响应
                        if (response['message'] === "success"){
                            alert("success");
                            location.reload();
                        }
                        else{
                            alert(response['message']);
                        }
                    }
                    else{

                        alert(`服务器响应错误,错误代码:${code}`);
                    }
                }
            };
            request.onreadystatechange = callback;  // 设置回调函数
            request.open("post", "/upload_image");   // 打开链接
            request.send(form);                      // 发送数据
        }
    });

// end!
});