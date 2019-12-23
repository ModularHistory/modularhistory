$(function() {

    // set up the date-time picker gui
    $('#id_date_of_birth').datetimepicker({
    	mask:'9999-19-39',
    	timepicker: false,
    	format: 'Y-m-d',
        allowBlank: true,
    });//datetimepicker

});//ready
