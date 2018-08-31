$(function(){
    var clock_01 = $("#clock_01").FlipClock({
        language: "chinese",
        clockFace: 'TwentyFourHourClock',
        showSeconds: true
    });

    var width = 300;
    var height = 300;
    var svg = d3.select("#clock_02").append("svg").attr("width", width).attr("height", height);

    var react_height = 25;


//end !!!
});