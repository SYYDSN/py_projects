$(function(){
/*时期jquery插件，用于选择日期和时间
*依赖jquery.datetimepicker.full.min.js和jquery.datetimepicker.min.css
* */
    $('#my_datetime_picker_div>.begin_picker').periodpicker({
        norange: true, // use only one value
        cells: [1, 1], // show only one month

        resizeButton: false, // deny resize picker
        fullsizeButton: false,
        fullsizeOnDblClick: false,

        timepicker: true, // use timepicker
        timepickerOptions: {
            hours: true,
            minutes: true,
            seconds: false,
            ampm: true
        }
    });


// end！
});