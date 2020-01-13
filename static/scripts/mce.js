function adjustMceHeight(iframe) {
    console.log('...');
    let initial_iframe_height = iframe.height();
    let content_height = iframe.contents().find('html').height() + 30;
    iframe.height(initial_iframe_height - (initial_iframe_height - content_height));
}

$(window).on('load', function() {
    $('.mce-branding,.mce-notification').hide();
    let label_width = $('.mce-container').prev().width();
    let form_width = $('.mce-container').closest('form').width();
    let new_mce_width = form_width - label_width;
    $('.mce-tinymce.mce-container.mce-panel').each(function() {
        $(this).css('margin-left', label_width + 'px').width(new_mce_width).height();
        // Adjust the text box height
        let iframe = $(this).find('iframe');
        adjustMceHeight(iframe);
        iframe.contents().find('#tinymce').on('input', (e) => {
            adjustMceHeight(iframe);
        });
    });
    // $('.add-row a').click(function() {
    //     let iframe = $( this ).closest('fieldset').find('iframe');
    //     // iframe.contents().find('body').replaceWith(
    //     //     `<body id="tinymce" class="mce-content-body " data-id="id_context" contenteditable="true"
    //     //      spellcheck="false" dir="ltr"><p><br data-mce-bogus="1"></p></body>`
    //     // );
    //     adjustMceHeight(iframe);
    // });
});