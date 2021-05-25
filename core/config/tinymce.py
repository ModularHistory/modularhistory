"""Settings for TinyMCE."""

# https://django-tinymce.readthedocs.io/en/latest/usage.html
# TODO: https://django-tinymce.readthedocs.io/en/latest/installation.html#prerequisites
TINYMCE_JS_URL = 'https://cloud.tinymce.com/stable/tinymce.min.js'
TINYMCE_JS_ROOT = 'https://cloud.tinymce.com/stable/'
TINYMCE_COMPRESSOR = False
TINYMCE_SPELLCHECKER = True
TINYMCE_DEFAULT_CONFIG = {
    'width': '100%',
    'max_height': 1000,
    'extended_valid_elements': 'module[data-id|data-type],proposition[data-id],citation[data-id]',
    'custom_elements': 'module,~proposition,~citation',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea.tinymce',
    'theme': 'modern',
    'plugins': (
        'autolink, autoresize, autosave, blockquote, '
        'charmap, code, contextmenu, emoticons, '
        'fullscreen, hr, image, link, lists, media, paste, preview, '
        'searchreplace, spellchecker, textcolor, visualblocks, visualchars, wordcount'
    ),
    'autoresize_bottom_margin': 1,
    'toolbar1': (
        'bold italic | blockquote | indent outdent | bullist numlist | '
        'visualblocks visualchars | charmap | code | spellchecker preview'
    ),
    'contextmenu': (
        'formats | blockquote | highlight smallcaps | link media image '
        'charmap hr | code | pastetext'
    ),
    'menubar': True,
    'statusbar': True,
    'branding': False,
    # fmt: off
    # After upgrading to v5, add `.ui.registry` before `.addMenuItem` and `addButton`
    'setup': ' '.join(('''
        function (editor) {
            editor.addMenuItem('highlight', {
                text: 'Highlight text',
                icon: false,
                onclick : function() {
                    editor.focus();
                    let content = editor.selection.getContent();
                    if (content.length) {
                        content = content.replace("<mark>", "").replace("</mark>", "");
                        editor.selection.setContent(
                            "<mark>" + editor.selection.getContent() + '</mark>'
                        );
                    }
                }
            });
            editor.addMenuItem('smallcaps', {
                text: 'Small caps',
                icon: false,
                onclick : function() {
                    editor.focus();
                    let content = editor.selection.getContent();
                    if (content.length) {
                        let opening_tag = '<span style="font-variant: small-caps">';
                        let closing_tag = '</span>';
                        content = content.replace(opening_tag, '').replace(closing_tag, '');
                        editor.selection.setContent(
                            opening_tag + editor.selection.getContent() + closing_tag
                        );
                    }
                }
            });
            editor.addButton('highlight', {
                text: 'Highlight text',
                icon: false,
                onclick : function() {
                    editor.focus();
                    let content = editor.selection.getContent();
                    if (content.length) {
                        content = content.replace("<mark>", "").replace("</mark>", "");
                        editor.selection.setContent(
                            "<mark>" + editor.selection.getContent() + '</mark>'
                        );
                    }
                }
            });
            editor.addButton('smallcaps', {
                text: 'Small caps',
                icon: false,
                onclick : function() {
                    editor.focus();
                    let content = editor.selection.getContent();
                    if (content.length) {
                        let opening_tag = '<span style="font-variant: small-caps">';
                        let closing_tag = '</span>';
                        content = content.replace(opening_tag, '').replace(closing_tag, '');
                        editor.selection.setContent(
                            opening_tag + editor.selection.getContent() + closing_tag
                        );
                    }
                }
            });
        }
    ''').split()),
    # fmt: on
}
TINYMCE_EXTRA_MEDIA = {
    'css': {
        'all': ['/static/styles/mce.css'],
    },
    'js': ['/static/scripts/mce.js'],
}
