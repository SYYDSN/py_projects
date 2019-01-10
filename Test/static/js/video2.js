var nav = navigator;

if (navigator.getUserMedia) {
    // 支持
} else {
    alert("不支持!");
}

var on_error = function(error){
    alert("出错");
    console.log(error);
};

var on_success = function(stream){
    var video = document.querySelector("#video");
    video.src = window.URL.createObjectURL(stream);
};

nav.getUserMedia({
    video: true,
    audio: true
}, on_success, on_error);