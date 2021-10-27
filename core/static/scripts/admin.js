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
                $(this).parent().append(`
                    <div id="${id}" style="margin-left: 160px; padding-left: 10px;">
                    <small>${currentLength} characters (${remainingLength} remaining)</small>
                    </div>
                `);
                $(this).unbind('keyup').on('keyup', function (event) {
                    currentLength = $(this).val().length;
                    remainingLength = parseInt(maxLength) - currentLength;
                    $(`#${id}`).text(`${currentLength} characters (${remainingLength} remaining)`);
                });
            }
        });
    })(django.jQuery);
});