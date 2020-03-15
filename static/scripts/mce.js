// autoresize JS may no longer be necessary; now using the autoresize TinyMCE plugin

function adjustMceHeight(iframe) {
    let initial_iframe_height = iframe.height();
    let content_height = iframe.contents().find('html').height() + 30;
    iframe.height(initial_iframe_height - (initial_iframe_height - content_height));
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