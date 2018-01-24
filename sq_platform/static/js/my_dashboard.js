/*
自定义的仪表板插件
1.需要jquery的支持.
2.需要引入jquery.AshAlom.gaugeMeter-2.0.0.min.js
*/

// 一个生成仪表盘的函数
let create_dashboard = function(id_str, init_dict){
    /*
    id_str: 字符串类型,一个元素的id,这个元素将被初始化成一个仪表盘.
    init_dict: 初始化仪表盘时用到的字典.
    下面是该仪表盘插件的一些可用参数，这些参数也可以在HTML DOM元素的data标签中使用。
    参数 	         默认值 	        可用值 	                        描述
    data-percent 	0 	        任何0-100之间的正整数 	  仪表盘的当前数值，必填参数
    data-used 	    0 	        任何正整数 	            该参数用于覆盖data-percent设置的数值。例如：你要显示512GB的内存被使用了“25%”，那么这里要指定为128，在data-total参数中指定512
    data-total 	   100 	        任何正整数 	            该参数用于覆盖data-percent设置的数值。例如：你要显示512GB的内存被使用了“25%”，那么data-used要指定为128，在data-total参数中指定512
    data-text 	   null 	    字符串 	              它会替换仪表盘中间显示的data-percent数值
    data-prepend   null 	    字符串（最大2 bytes） 	   在百分比数量之前添加的文本
    data-append    null 	    字符串（最大2 bytes） 	   在百分比数量之后添加的文本，例如添加“%”
    data-size 	   100 	        任何正整数 	            仪表盘的宽度和高度，单位像素
    data-width 	    3 	        任何正整数 	            仪表盘圆形进度条的厚度
    data-style 	   Full 	    Full, Semi 或 Arch 	   是显示整圆，半圆还是arched-circle
    data-color 	 #2C94E0 	    十六进制颜色或RGBA颜色  	  仪表盘圆形进度条的前景色。如果设置了data-theme属性，该属性会被覆盖
    data-back 	RGBA(0,0,0,.06) 十六进制颜色或RGBA颜色 	  仪表盘圆形进度条的背景色。
    data-theme 	Red-Gold-Green 	Green-Gold-Red          仪表盘圆形进度条的颜色渐变主题
                                Green-Red
                                Red-Green
                                DarkBlue-LightBlue
                                LightBlue-DarkBlue
                                DarkRed-LightRed
                                LightRed-DarkRed
                                DarkGreen-LightGreen
                                LightGreen-DarkGreen
                                DarkGold-LightGold
                                LightGold-DarkGold
                                White
                                Black   
                                Red-Gold-Green
    
        
    data-animate_gauge_colors 	0 	    布尔值0或1 	    如果该参数设置为可用，仪表盘圆形进度条的前景色将会根据data-theme中的渐变来在不同的圆形位置显示不同的颜色。该参数会覆盖data-color设置的值
    data-animate_text_colors 	0 	    布尔值0或1 	    如果该参数设置为可用，仪表盘圆形进度条的文本色将会根据data-theme中的渐变来在不同的圆形位置显示不同的颜色。该参数会覆盖data-color设置的值
    data-label 	                null 	字符串 	     显示在百分比数值下面的文本
    data-label_color 	        Black 	十六进制颜色或RGBA颜色或HTML颜色名字（如red） 	添加的文本的颜色
    data-stripe 	            0 	    任何正整数 	    以直线或条纹来显示仪表盘圆形进度条。如果给出的值大于0，圆形进度条从直线变为条纹，值为条纹的厚度
    */
    // 原型标靶
    $(`#${id_str}`).remove();
    var g = $(`<div class='GaugeMeter' id='${id_str}'></div>`);
    $("#dash_board_outer").append(g);
    g.attr(init_dict).gaugeMeter();
};
let head = document.getElementsByTagName("head");
let style = document.createElement('style');
style.innerHTML = `.GaugeMeter{
    Position:        Relative;
    Text-Align:      Center;
    Overflow:        Hidden;
    Cursor:          Default;
  }
   
  .GaugeMeter SPAN,
  .GaugeMeter B{
    Margin:          0 23%;
    Width:           5%;
    Position:        Absolute;
    Text-align:      Center;
    Display:         Inline-Block;
    Color:           RGBa(0,0,0,.8);
    Font-Weight:     100;
    Font-Family:     "Open Sans", Arial;
    Overflow:        Hidden;
    White-Space:     NoWrap;
    Text-Overflow:   Ellipsis;
  }
  .GaugeMeter[data-style="Semi"] B{
    Margin:          0 10%;
    Width:           80%;
  }
   
  .GaugeMeter S,
  .GaugeMeter U{
    Text-Decoration: None;
    Font-Size:       .49em;
    Opacity:         .5;
  }
   
  .GaugeMeter B{
    Color:           Black;
    Font-Weight:     300;
    Opacity:         .8;
  }  `;
