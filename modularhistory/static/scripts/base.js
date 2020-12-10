const mobile_width = 660;

function initializeListeners(element = null) {
    let scope = element ? element : document;
    console.log(`Initializing listeners for ${scope}.`);
    $(scope).find('.display-source').unbind('click').on('click', function (event) {
        console.log('Displaying source.');
        let href = $(this).attr('href');
        let open_in_modal = false;
        let target_modal = null;
        if (open_in_modal) {
            target_modal = $(this).attr('data-target');
        }
        if (href.includes('.pdf')) {
            event.preventDefault();
            // TODO
            href = `/static/libraries/pdfjs/web/viewer.html?file=${href}`;
            if (open_in_modal) {
                /*
                    Evade XSS attacks by using $.find(target_modal) rather than
                    $(target_modal), as target_modal could be manipulated to
                    contain arbitrary JS.
                */
                $.find(target_modal).find('.modal-body').html(`
                    <div class="embed-responsive embed-responsive-210by297">
                        <iframe class="embed-responsive-item" src="${href}" allowfullscreen></iframe>
                    </div>
                `);
            } else {
                window.open(href, '_blank');
            }
            return false;  // prevent modal from popping up
        } else if (href.includes('.epub')) {
            console.log('Opening ePub');
        }
    });

    // Tooltips
    $(scope).tooltip({ selector: '[data-toggle="tooltip"]' });

    $(scope).on()

    $(scope).dblclick(function (event) {
        let selection = window.getSelection();
        let node = selection.getRangeAt(0).commonAncestorContainer;
        if (node.nodeType !== 1) {
            node = node.parentNode;
        }
        let html = $(node).html();
        if (!$(node).is('[title]')) {
            event.preventDefault();
            let word = selection && selection.toString();
            if (word) {
                console.log(`Requesting definitions for "${word}"...`);
                let pattern = `([ >";])${word}([\\.,;:&<])`;
                let request = {
                    "url": `/search/words/${word}`,
                    "crossDomain": false,
                    "async": true,
                    "method": "GET",
                };
                $.ajax(request).done(function (response) {
                    let definitions = response['definitions'];
                    if (definitions) {
                        let definitions_html = '<ol>'
                        definitions.forEach(function (item, index) {
                            definitions_html += `<li>${item['definition']}</li>`;
                        });
                        definitions_html += '</ol>';
                        let word_span = `<span title="${definitions_html}" data-toggle="tooltip" data-html="true" data-trigger="dblclick">${word}</span>`;
                        $(node).html(html.replaceAll(new RegExp(pattern, "g"), `$1${word_span}$2`));
                    } else {
                        console.log(`Failed to retrieve definitions for ${word}.`);
                    }
                });
            }
        }
    });

    // TODO: clean up
    // // enable annotations
    // $(scope).find('.detail').annotator().annotator('setupPlugins');
}

function setGetParam(key, value) {
    console.log(`Setting ${key} param to ${value}.`);
    if (history.pushState) {
        let params = new URLSearchParams(window.location.search);
        params.set(key, value);
        let newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + params.toString();
        console.log(newUrl);
        window.history.pushState({ path: newUrl }, '', newUrl);
    }
}

function lazyLoadImages(element = null) {
    let scope = element ? element : document;
    console.log(`Lazy-loading images in ${scope}.`);
    let lazyImages = [].slice.call(scope.querySelectorAll("img.lazy,.lazy-bg"));
    if ("IntersectionObserver" in window) {
        let lazyImageObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    let lazyElement = entry.target;
                    let url;
                    let hasLazyBg = lazyElement.classList.contains('lazy-bg');
                    let isImage = 'src' in lazyElement.dataset;
                    if (hasLazyBg) {
                        url = lazyElement.dataset.img;
                        if (!url) {
                            let key = lazyElement.parentElement.dataset.key;
                            console.log(`no URL could be retrieved for lazy-bg ${lazyElement.textContent} ${key}`);
                        }
                        lazyElement.classList.remove("lazy-bg");
                        lazyElement.style.backgroundImage = `url("${url}")`;
                    } else if (isImage) {
                        let lazyImage = lazyElement;
                        url = lazyImage.dataset.src;
                        if (!url) {
                            console.log(`no URL could be retrieved for ${lazyImage} ${lazyImage.textContent}`);
                        }
                        lazyImage.src = url;
                        // lazyElement.srcset = lazyElement.dataset.srcset;
                        lazyImage.classList.remove("lazy");
                        // lazyImageObserver.unobserve(lazyImage);
                    } else {
                        console.log('What is this?');
                        console.log(lazyElement.dataset);
                        console.log(lazyElement.parentElement);
                    }
                    lazyImageObserver.unobserve(lazyElement);
                }
            });
        }, {
            rootMargin: "0px 0px 999px 0px"
        });
        lazyImages.forEach(function (lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    } else {
        // Fall back to a more compatible method of lazy-loading images
        let active = false;
        const lazyLoad = function () {
            if (active === false) {
                active = true;
                setTimeout(function () {
                    lazyImages.forEach(function (lazyImage) {
                        let loadImage = (
                            (lazyImage.getBoundingClientRect().top <= window.innerHeight
                                && lazyImage.getBoundingClientRect().bottom >= 0)
                            && getComputedStyle(lazyImage).display !== "none"
                        );
                        if (loadImage) {
                            lazyImage.src = lazyImage.dataset.src;
                            lazyImage.srcset = lazyImage.dataset.srcset;
                            lazyImage.classList.remove("lazy");

                            lazyImages = lazyImages.filter(function (image) {
                                return image !== lazyImage;
                            });

                            if (lazyImages.length === 0) {
                                document.removeEventListener("scroll", lazyLoad);
                                window.removeEventListener("resize", lazyLoad);
                                window.removeEventListener("orientationchange", lazyLoad);
                            }
                        }
                    });
                    active = false;
                }, 200);
            }
        };
        document.addEventListener("scroll", lazyLoad);
        window.addEventListener("resize", lazyLoad);
        window.addEventListener("orientationchange", lazyLoad);
    }
}

// This function is used to track the user's position in the default "rows" viewing mode.
function scrollSpy() {
    let modules = [].slice.call(document.querySelectorAll(".result[data-key]"));
    if ("IntersectionObserver" in window) {
        let moduleObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    let module = entry.target;
                    let key = module.dataset.key;
                    setGetParam('key', key);
                }
            });
        }, {
            // when the top of the module is 60% from the bottom of the window
            rootMargin: "0px 0px -60% 0px"
        });
        modules.forEach(function (module) {
            moduleObserver.observe(module);
        });
    }
}

$(function () {
    console.log('base.js');

    let searchParams = new URLSearchParams(window.location.search);
    let hasDisplayOption = searchParams.has('display');
    let displayOption = (hasDisplayOption ? searchParams.get('display') : 'rows');
    if (displayOption === 'rows') {
        scrollSpy();
    }

    // any page
    initializeListeners();

    // lazy-load images
    lazyLoadImages();

    // SERP
    let serp_container_selector = '.serp-container';
    let serp_container = $(serp_container_selector).first();
    // If the page is a SERP
    if (serp_container[0]) {
        let display_option_selector = '.display-options .display-option';
        let searchParams = new URLSearchParams(window.location.search);
        $(display_option_selector).on('click', function () {
            let input = $(this).find('input');
            if (!input.is(':checked')) {
                $(`${display_option_selector} input:checked`).each(function () {
                    let previously_selected_option = $(this);
                    // TODO: Confirm this works as expected, and clean it up
                    previously_selected_option.prop('checked', false);
                    previously_selected_option.removeAttr('checked');
                    if (previously_selected_option.prop('checked')) {
                        // If we don't see this in the console,
                        // the behavior is probably correct even though
                        // the element inspector might show that the previously
                        // selected option still is checked.  : /
                        console.log('WTH');
                    }
                });
                // $(`${display_option_selector} input:checked`).prop('checked', false);
                console.log(`Selecting option: ${input.val()}`);
                input.prop('checked', true);
                let url = new URL(window.location.href);
                url.searchParams.set('display', input.val());
                window.location.href = url.href;
            }
        });
        let result_card_selector = '.results > .card';
        let result_selector = `${result_card_selector}, .results > .result`;
        let active_result = $(result_selector).first();
        if (active_result[0]) {
            if (searchParams.has('key')) {
                let key = searchParams.get('key');
                let active_result_selector = `[data-key=${key}]`;
                if ($(active_result_selector).length) {
                    active_result = $(active_result_selector).first();
                }
            } else {
                setGetParam('key', active_result.attr('data-key'));
            }

            // If not mobile, load 2pane for the first result
            if ($(window).width() > mobile_width) {
                active_result.addClass('active');
                if (!active_result.visible) {
                    active_result[0].scrollIntoView();
                }
                // Initial load of view-detail
                let detail_href = active_result.attr('data-href') + 'part';
                $('.view-detail').load(detail_href, function () {
                    initializeListeners(this);
                    lazyLoadImages(this);
                });
            }

            // Load view-detail when a card is clicked
            $(result_card_selector).on('click', function () {
                console.log('Result card was clicked; setting new active result.');
                $(`${result_selector}.active`).removeClass('active');
                $(this).addClass('active');
                let detail_href = $(this).attr('data-href') + 'part';
                let key = $(this).attr('data-key');
                $('.view-detail').load(detail_href, function () {
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
                        modal_body.find('iframe').each(function () {
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
                    initializeListeners(this);
                    lazyLoadImages(this);
                });
                setGetParam('key', key);
            });
        }

        // Enable slideout menu
        const toggle = document.getElementById('sliderToggle');
        const slider = document.getElementById('slider');
        function openSlider() {
            slider.classList.remove('closed');
            slider.classList.add('open');
            toggle.style.left = `${slider.offsetWidth - 5}px`;  // TODO: Use stylesheet rather than JS
        }
        function closeSlider() {
            slider.classList.remove('open');
            slider.classList.add('closed');
            toggle.style.left = '0';  // TODO: make this safer; use stylesheet rather than JS
        }
        // Toggle button
        toggle.addEventListener('click', function () {
            if (slider.classList.contains('closed')) {
                openSlider();
            } else if (slider.classList.contains('open')) {
                closeSlider();
            }
        });
    }

    // Enable hiding admin controls
    $('.hide-admin-controls').click(function (event) {
        // $('.edit-obj-button').hide();
        event.preventDefault();
        $('head').append(`<style>.edit-object-button {display: none}</style>`);
    });
});//ready