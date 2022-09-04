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
    });

    // Tooltips
    $(scope).tooltip({ selector: '[data-toggle="tooltip"]' });

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
                console.log(`Requesting definitions for '${word}'...`);
                let pattern = `([ >";])${word}([\\.,;:&<])`;
                let request = {
                    'url': `/search/words/${word}`,
                    'crossDomain': false,
                    'async': true,
                    'method': 'GET',
                };
                $.ajax(request).done(function (response) {
                    let definitions = response['definitions'];
                    if (definitions) {
                        let definitions_html = '<ol>'
                        definitions.forEach(function (item, index) {
                            definitions_html += `<li>${item['definition']}</li>`;
                        });
                        definitions_html += '</ol>';
                        let word_span = `<span title='${definitions_html}' data-toggle='tooltip' data-html='true' data-trigger='dblclick'>${word}</span>`;
                        $(node).html(html.replaceAll(new RegExp(pattern, 'g'), `$1${word_span}$2`));
                    } else {
                        console.log(`Failed to retrieve definitions for ${word}.`);
                    }
                });
            }
        }
    });
}

function setGetParam(key, value) {
    console.log(`Setting ${key} param to ${value}.`);
    if (history.pushState) {
        let params = new URLSearchParams(window.location.search);
        params.set(key, value);
        let newUrl = window.location.protocol + '//' + window.location.host + window.location.pathname + '?' + params.toString();
        console.log(newUrl);
        window.history.pushState({ path: newUrl }, '', newUrl);
    }
}

function lazyLoadImages(element = null) {
    let scope = element ? element : document;
    console.log(`Lazy-loading images in ${scope}.`);
    let lazyImages = [].slice.call(scope.querySelectorAll('.lazy-bg'));
    if ('IntersectionObserver' in window) {
        let lazyImageObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    let lazyElement = entry.target;
                    let url;
                    let hasLazyBg = lazyElement.classList.contains('lazy-bg');
                    if (hasLazyBg) {
                        url = lazyElement.dataset.img;
                        if (!url) {
                            let key = lazyElement.parentElement.dataset.key;
                            console.log(`no URL could be retrieved for lazy-bg ${lazyElement.textContent} ${key}`);
                        }
                        lazyElement.classList.remove('lazy-bg');
                        lazyElement.style.backgroundImage = `url('${url}')`;
                    } else {
                        console.log(lazyElement.dataset);
                        console.log(lazyElement.parentElement);
                    }
                    lazyImageObserver.unobserve(lazyElement);
                }
            });
        }, {
            rootMargin: '0px 0px 999px 0px'
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
                            && getComputedStyle(lazyImage).display !== 'none'
                        );
                        if (loadImage) {
                            lazyImage.src = lazyImage.dataset.src;
                            lazyImage.srcset = lazyImage.dataset.srcset;
                            lazyImage.classList.remove('lazy');

                            lazyImages = lazyImages.filter(function (image) {
                                return image !== lazyImage;
                            });

                            if (lazyImages.length === 0) {
                                document.removeEventListener('scroll', lazyLoad);
                                window.removeEventListener('resize', lazyLoad);
                                window.removeEventListener('orientationchange', lazyLoad);
                            }
                        }
                    });
                    active = false;
                }, 200);
            }
        };
        document.addEventListener('scroll', lazyLoad);
        window.addEventListener('resize', lazyLoad);
        window.addEventListener('orientationchange', lazyLoad);
    }
}

// This function is used to track the user's position in the default 'rows' viewing mode.
function scrollSpy() {
    let modules = [].slice.call(document.querySelectorAll('.result[data-key]'));
    if ('IntersectionObserver' in window) {
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
            rootMargin: '0px 0px -60% 0px'
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

});//ready