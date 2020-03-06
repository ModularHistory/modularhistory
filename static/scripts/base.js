function initializeListeners() {
    $('.display-source').click(function(event) {
        // event.preventDefault();
        let href = $( this ).attr('href');
        let target_modal = $( this ).attr('data-target');
        if (href.includes('.pdf')) {
            $(target_modal).find('.modal-body').html(`
                <div class="embed-responsive embed-responsive-210by297">
                    <iframe class="embed-responsive-item" src="/static/pdfjs/web/viewer.html?file=${href}" allowfullscreen></iframe>
                </div>
            `);
        } else if (href.includes('.epub')) {
            console.log('Attempting to load ePub.');
            let book = ePub(href);
            $(target_modal).find('.modal-body').html(`
                <div class="embed-responsive embed-responsive-210by297" id="document-viewer">
                </div>
            `);
            let rendition = book.renderTo('document-viewer');
            rendition.display();
        }
    });
}

function setGetParam(key, value) {
    if (history.pushState) {
        let params = new URLSearchParams(window.location.search);
        params.set(key, value);
        let newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + params.toString();
        console.log(newUrl);
        window.history.pushState({path:newUrl},'', newUrl);
    }
}

$(function() {
    // let vertical_offset = $('.results .card').first().offset().top;
    // console.log(vertical_offset);
    // $('.view-detail').css('top', vertical_offset).css('visibility', 'visible');
    let result_card_selector = '.results .card';
    let searchParams = new URLSearchParams(window.location.search);
    let active_card = $(result_card_selector).first();
    if (active_card[0]) {
        if (searchParams.has('key')) {
            let key = searchParams.get('key');
            let active_card_selector = `[data-key=${key}]`;
            if ($(active_card_selector).length) {
                active_card = $(active_card_selector).first();
            }
        } else {
            setGetParam('key', active_card.attr('data-key'));
        }
        active_card.addClass('active');
        if (!active_card.visible) {
            active_card[0].scrollIntoView();
        }

        // Initial load of view-detail
        let detail_href = active_card.attr('data-href') + 'part';
        $('.view-detail').load(detail_href, function() {
            initializeListeners();
        });
        // Listener to load view-detail when a card is clicked
        $(result_card_selector).click(function() {
            $(`${result_card_selector}.active`).removeClass('active');
            $( this ).addClass('active');
            let detail_href = $( this ).attr('data-href') + 'part';
            let key = $( this ).attr('data-key');
            $('.view-detail').load(detail_href, function() {
                initializeListeners();
            });
            setGetParam('key', key);
        });
    }

    $('.hide-admin-controls').click(function(event) {
        // $('.edit-object-button').hide();
        event.preventDefault();
        $('head').append(`<style>.edit-object-button {display: none}</style>`);
    });

    // $('.mdb-select').materialSelect();
});//ready