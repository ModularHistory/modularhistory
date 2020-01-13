function initializeListeners() {
    $('.display-source').click(function(event) {
        // event.preventDefault();
        let href = $( this ).attr('href');
        console.log(href);
        let target_modal = $( this ).attr('data-target');
        console.log(target_modal);
        $(target_modal).find('.modal-body').html(`
            <div class="embed-responsive embed-responsive-210by297">
                <iframe class="embed-responsive-item" src="/static/pdfjs/web/viewer.html?file=${href}" allowfullscreen></iframe>
            </div>
        `);
        // $(target_modal).modal('show');
        console.log('Loaded source modal');
    });
}

$(function() {
    // let vertical_offset = $('.results .card').first().offset().top;
    // console.log(vertical_offset);
    // $('.view-detail').css('top', vertical_offset).css('visibility', 'visible');
    let result_card_selector = '.results .card';

    $(result_card_selector).first().addClass('active');

    initializeListeners();

    $(result_card_selector).click(function() {
        $(`${result_card_selector}.active`).removeClass('active');
        $( this ).addClass('active');
        let detail_href = $( this ).attr('data-href') + 'part';
        console.log(detail_href);
        $('.view-detail').load(detail_href, function() {
            initializeListeners();
        });
    });

    $('.hide-admin-controls').click(function(event) {
        // $('.edit-object-button').hide();
        event.preventDefault();
        $('head').append(`<style>.edit-object-button {display: none}</style>`);
    });

    // $('.mdb-select').materialSelect();
});//ready