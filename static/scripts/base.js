const mobile_width = 660;

function initializeListeners() {
    $('.display-source').click(function(event) {
        event.preventDefault();
        let href = $( this ).attr('href');
        let open_in_modal = false;
        let target_modal = null;
        if (open_in_modal) {
            target_modal = $( this ).attr('data-target');
        }
        if (href.includes('.pdf')) {
            href = `/static/libraries/pdfjs/web/viewer.html?file=${href}`;
            if (open_in_modal) {
                $(target_modal).find('.modal-body').html(`
                    <div class="embed-responsive embed-responsive-210by297">
                        <iframe class="embed-responsive-item" src="${href}" allowfullscreen></iframe>
                    </div>
                `);
            } else {
                window.open(href, '_blank');
            }
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
        return false;  // prevent modal from popping up
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
    console.log('base.js');

    // any page
    initializeListeners();

    // SERP
    let result_card_selector = '.results .card';
    let searchParams = new URLSearchParams(window.location.search);
    let active_card = $(result_card_selector).first();
    // If the page is a SERP
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

        // If not mobile, load 2pane for the first result
        if ($(window).width() > mobile_width) {
            active_card.addClass('active');
            if (!active_card.visible) {
                active_card[0].scrollIntoView();
            }
            // Initial load of view-detail
            let detail_href = active_card.attr('data-href') + 'part';
            $('.view-detail').load(detail_href, function() {
                initializeListeners();
            });
        }

        // Load view-detail when a card is clicked
        $(result_card_selector).click(function() {
            $(`${result_card_selector}.active`).removeClass('active');
            $( this ).addClass('active');
            let detail_href = $( this ).attr('data-href') + 'part';
            let key = $( this ).attr('data-key');
            $('.view-detail').load(detail_href, function() {
                if ($(window).width() <= mobile_width) {
                    console.log('Mobile width detected.');
                    let content = $(this).html();
                    let modal = $('#modal');
                    let modal_body = modal.find('.modal-body');
                    modal_body.html(content).addClass('view-detail');
                    let iframe;
                    let iframe_width;
                    let iframe_height;
                    let aspect_ratio;
                    modal_body.find('iframe').each(function() {
                        iframe = $(this);
                        iframe_width = iframe.attr('width');
                        iframe_height = iframe.attr('height');
                        let calculated_width = iframe.width();
                        if (iframe_width && iframe_height && iframe_width > calculated_width) {
                            console.log('iframe may need to be resized');
                            aspect_ratio = iframe_width / iframe_height;
                            // TODO
                        }
                    });
                    modal.modal();
                }
                initializeListeners();
            });
            setGetParam('key', key);
        });
        // Enable slideout menu
        const toggler = document.getElementById('sliderToggle');
        const slider = document.getElementById('slider');
        function openSlider() {
            slider.classList.remove('closed');
            slider.classList.add('open');
            toggler.style.left = `${slider.offsetWidth - 5}px`;  // TODO: Use stylesheet rather than JS
        }
        function closeSlider() {
            slider.classList.remove('open');
            slider.classList.add('closed');
            toggler.style.left = '0';  // TODO: make this safer; use stylesheet rather than JS
        }
        // Toggle button
        toggler.addEventListener('click', function() {
            if (slider.classList.contains('closed')) {
                openSlider();
            } else if (slider.classList.contains('open')) {
                closeSlider();
            }
        });
    }

    // Enable hiding admin controls
    $('.hide-admin-controls').click(function(event) {
        // $('.edit-object-button').hide();
        event.preventDefault();
        $('head').append(`<style>.edit-object-button {display: none}</style>`);
    });
});//ready