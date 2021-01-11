"""
Settings for Martor.

https://github.com/agusmakmun/django-markdown-editor
"""

MARTOR_THEME = 'bootstrap'
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',  # to enable/disable emoji icons.
    'imgur': 'true',  # to enable/disable imgur/custom uploader.
    'mention': 'false',  # to enable/disable mention
    'jquery': 'true',  # to include/revoke jquery (require for admin default django)
    'living': 'false',  # to enable/disable live updates in preview
    'spellcheck': 'false',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',  # to enable/disable hljs highlighting in preview
}
MARTOR_TOOLBAR_BUTTONS = [
    'bold',
    'italic',
    'horizontal',
    'heading',
    'pre-code',
    'blockquote',
    'unordered-list',
    'ordered-list',
    'link',
    'image-link',
    'image-upload',
    'emoji',
    'direct-mention',
    'toggle-maximize',
    'help',
]
MARTOR_ENABLE_LABEL = True  # default is False
MARTOR_IMGUR_CLIENT_ID = config('IMGUR_CLIENT_ID')
MARTOR_IMGUR_API_KEY = config('IMGUR_CLIENT_SECRET')
# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',
    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',  # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',  # to parse markdown mention
    'martor.extensions.emoji',  # to parse markdown emoji
    'martor.extensions.mdx_video',  # to parse embed/iframe video
    'martor.extensions.escape_html',  # to handle the XSS vulnerabilities
]
# Markdown extension configs:
# MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}
# Markdown urls:
MARTOR_UPLOAD_URL = '/martor/uploader/'  # default
MARTOR_SEARCH_USERS_URL = '/martor/search-user/'  # default
# Markdown extensions:
# webfx emojis: 'https://www.webfx.com/tools/emoji-cheat-sheet/graphics/emojis/'
# Default from GitHub:
MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://github.githubassets.com/images/icons/emoji/'
MARTOR_MARKDOWN_BASE_MENTION_URL = 'https://modularhistory.com/author/'
# If you need to use your own themed "bootstrap" or "semantic ui" dependency
# replace the values with the file in your static files dir
MARTOR_ALTERNATIVE_JS_FILE_THEME = "semantic-themed/semantic.min.js"  # default None
MARTOR_ALTERNATIVE_CSS_FILE_THEME = "semantic-themed/semantic.min.css"  # default None
MARTOR_ALTERNATIVE_JQUERY_JS_FILE = "jquery/dist/jquery.min.js"  # default None
