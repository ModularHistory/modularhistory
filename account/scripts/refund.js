$(function(context) {
    return function() {
        if ($('.item input[type="checkbox"]').length == $('.item input[type="checkbox"]:disabled').length) {
            $( '#return-instructions' ).html('None of these items are eligible to be returned.<br /><small>If you have questions, please read our <a href="">return policy</a> and feel free to <a href="/contact/">contact us</a>.</small>');
            $( 'textarea[name="reason"]' ).hide();
        }
        $('.item input[type="checkbox"]').on('change', function () {
            var ids = '';
            if ($( '.item input[type="checkbox"]:checked' ).length > 0) {
                $( '#process-return-btn' ).css('display', 'inline-block');
                $( '.item input[type="checkbox"]:checked' ).each(function() {
                    var item_id = $( this ).closest('tr').data('id');
                    ids = ids + item_id + ',';
                });
                ids = ids.substring(0, ids.length - 1);
                $.get("/api/orders/"+sale_id+"/refund_estimate?items="+ids, function(data, status) {
                    $( '#expected-refund' ).text('$'+data);
                });
            } else {
                $( '#expected-refund' ).text('$0.00');
                $( '#process-return-btn' ).css('display', 'none');
            }
        });
    }
}(DMP_CONTEXT.get()))
