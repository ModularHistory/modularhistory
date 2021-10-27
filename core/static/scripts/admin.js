window.addEventListener("load", function() {
    (function($) { 
        // Add char counters.
        $(document).find('[type="text"]').each(function() {
            const maxLength = $(this).attr('maxlength');
            if (maxLength) {
                const width = `${maxLength/2}em`;
                const labelWidth = $(this).prev('label').outerWidth();
                const maxWidth = `${($(this).parent().innerWidth() - labelWidth) * 0.9}`;
                $(this).css('width', `${width}`).css('max-width', `${maxWidth}`);
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
        // Initialize Trumbowyg editors for HTML fields.
        $("textarea[trumbowyg]").trumbowyg({
            resetCss: true,
            autogrow: true,
            autogrowOnEnter: true,
            defaultLinkTarget: "_blank",
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
                ['formatting'],
                ['strong', 'em', 'underline', 'del'],
                ['superscript', 'subscript'],
                ['removeformat'],
                ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
                ['unorderedList', 'orderedList'],
                ['horizontalRule'],
                ['table'],
                ['link'],
                ['image'],
                ['undo', 'redo'], // Only supported in Blink browsers
                ['fullscreen']
            ],
            plugins: {},
            tagsToRemove: ['script', 'link']
        });
    })(django.jQuery);
});