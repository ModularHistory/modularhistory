// autoresize JS may no longer be necessary; now using the autoresize TinyMCE plugin

function adjustMceHeight(iframe) {
    let initial_iframe_height = iframe.height();
    let content_height = iframe.contents().find('html').height() + 30;
    console.log(`>>> content_height: ${content_height}`);
    let new_iframe_height = initial_iframe_height - (initial_iframe_height - content_height);
    console.log(`>>> new_iframe_height: ${new_iframe_height}`);
    // iframe.closest('.mce-wrapper').height(new_iframe_height);
    iframe.height(new_iframe_height);
    return new_iframe_height;
}

$(window).on('load', function() {
    console.log('mce.js');
    $('.mce-branding,.mce-notification').hide();
    $('.mce-tinymce.mce-container.mce-panel').not('[data-inline-type="tabular"] *').each(function() {
        let iframe = $(this).find('iframe');
        iframe.contents().find('head').append(`
            <noscript>
                <link rel="stylesheet" href="/static/styles/mce.css" type="text/css" />
            </noscript>
        `);
        $.when($.get("/static/styles/mce.css")).done(function(response) {
            iframe.contents().find('head').append(`
                <style>${response}</style>
            `);
        });
        iframe.contents().find('#tinymce').on('input change keyup', (e) => {
            adjustMceHeight(iframe);
        });
        let form_row = $(this).parent().parent('.form-row');
        form_row.prepend('<div class="label"></div>');
        let label_wrapper = form_row.find('.label');
        form_row.find('label').appendTo(label_wrapper);
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