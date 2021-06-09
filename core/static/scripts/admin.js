window.addEventListener("load", function() {
    (function($) { 
        // Add char counters.
        $(document).find('[type="text"]').each(function() {
            const maxLength = $(this).attr('maxlength');
            if (maxLength) {
                let currentLength = $(this).val().length;
                let remainingLength = parseInt(maxLength) - currentLength;
                const id = `${this.id}-count`;
                $(this).parent().append(`<span id="${id}">${currentLength} characters (${remainingLength} remaining)</span>`);
                $(this).unbind('keyup').on('keyup', function (event) {
                    currentLength = $(this).val().length;
                    remainingLength = parseInt(maxLength) - currentLength;
                    $(`#${id}`).text(`${currentLength} characters (${remainingLength} remaining)`);
                });
            }
        });
        if ($("textarea").length) {
            // Initialize Trumbowyg editors for HTML fields.
            $("textarea").trumbowyg({
                resetCss: true,
                autogrow: true,
                autogrowOnEnter: true,
                defaultLinkTarget: "_blank",
                removeformatPasted: true,
                btnsDef: {
                    image: {
                        dropdown: [
                            "upload",
                            "insertImage",
                            "base64",
                            "noembed"
                        ],
                        ico: "insertImage"
                    }
                },
                btns: [
                    ['viewHTML'],
                    ['undo', 'redo'], // Only supported in Blink browsers
                    ['formatting'],
                    ['strong', 'em', 'del'],
                    ['superscript', 'subscript'],
                    ['link'],
                    ['image'],
                    ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
                    ['unorderedList', 'orderedList'],
                    ['horizontalRule'],
                    ['removeformat'],
                    ['fullscreen']
                ],
                plugins: {},
                tagsToRemove: ['script', 'link']
            });
            $("textarea").find('img[data-src]').each(function () {
                $(this).attr('src', this.dataset.src);
            });
        }
    })(django.jQuery);
});