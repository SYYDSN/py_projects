$(function(){
    // 打印
    $("#print_btn").click(function(){
        window.print();
    });

    // 导出pdf
    $("#export_btn").click(function(){
        var element = document.getElementById('main');
        html2pdf(element);
    });

// end !!!
});