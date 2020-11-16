// autoresize JS may no longer be necessary; now using the autoresize TinyMCE plugin

function adjustMceHeight(iframe) {
    let content_height = iframe.contents().find('html').height() + 30;
    let initial_iframe_height = iframe.height();
    let new_iframe_height = initial_iframe_height - (initial_iframe_height - content_height);
    iframe.height(new_iframe_height);
    return new_iframe_height;
}

$(window).on('load', function() {
    $('.mce-branding,.mce-notification').hide();
    $('.mce-tinymce.mce-container.mce-panel').not('[data-inline-type="tabular"] *').each(function() {
        let iframe = $(this).find('iframe');
        iframe.contents().find('head').append(`
            <noscript>
                <link rel="stylesheet" href="/static/styles/mce.css" type="text/css" />
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" />
            </noscript>
        `);
        // Include MCE styles
        $.when($.get("/static/styles/mce.css")).done(function(response) {
            iframe.contents().find('style').append(`<style>${response}</style>`);
        });
        // Include Bootstrap styles
        $.when($.get("https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css")).done(function(response) {
            iframe.contents().find('head.style').append(`${response}`);
        });
        iframe.contents().find('#tinymce').on('input change keyup', (e) => {
            adjustMceHeight(iframe);
        });
        let form_row = $(this).parent().parent('.form-row');
        form_row.prepend('<div class="label"></div>');
        let label_wrapper = form_row.find('.label');
        form_row.find('label').appendTo(label_wrapper);
        iframe.contents().find('img.lazy').each(function() {
            $(this).attr('src', this.dataset.src);
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