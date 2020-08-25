"""
Django settings for modularhistory.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys
from enum import Enum

import sentry_sdk
from decouple import config
from django.conf.locale.en import formats as en_formats
from easy_thumbnails.conf import Settings as ThumbnailSettings
from mega import Mega
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration


class Environment(str, Enum):
    PROD = 'prod'
    DEV = 'dev'
    GITHUB_TEST = 'test'


IS_GCP = bool(os.getenv('GAE_APPLICATION', None))
IS_PROD = IS_GCP and os.getenv('GAE_ENV', '').startswith('standard')
USE_PROD_DB = config('USE_PROD_DB', default=IS_PROD, cast=bool)
TESTING = 'test' in sys.argv
ENVIRONMENT = (Environment.PROD if IS_PROD
               else Environment.GITHUB_TEST if os.environ.get('GITHUB_WORKFLOW')
               else Environment.DEV)

ADMINS = config(
    'ADMINS',
    cast=lambda value: [
        tuple(name_and_email.split(','))
        for name_and_email in value.replace(', ', ',').replace('; ', ';').split(';')
    ]
) if config('ADMINS', default=None) else []

# Initialize the Sentry SDK for error reporting.
if ENVIRONMENT != Environment.DEV:
    integrations = [DjangoIntegration()]
    # If not in Google Cloud, add the Celery integration.
    if not IS_GCP:
        integrations.append(CeleryIntegration())
    sentry_sdk.init(
        dsn="https://eff106fa1aeb493d8220b83e802bb9de@o431037.ingest.sentry.io/5380835",
        environment=ENVIRONMENT.value,
        integrations=integrations,
        # Associate users to errors (using django.contrib.auth) by sending PII data
        send_default_pii=True
    )

en_formats.DATETIME_FORMAT = 'Y-m-d H:i:s.u'

# Build paths inside the project like this:
# os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secret-key
SECRET_KEY = config('SECRET_KEY')

# DEBUG must be False in production (for security)
# https://docs.djangoproject.com/en/3.0/ref/settings#s-debug
DEBUG = (ENVIRONMENT != Environment.PROD) if ENVIRONMENT else config('DEBUG', default=True, cast=bool)

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secure-ssl-redirect
SECURE_SSL_REDIRECT = not DEBUG

# https://docs.djangoproject.com/en/3.0/ref/settings#s-session-cookie-samesite
SESSION_COOKIE_SECURE = not DEBUG

# https://docs.djangoproject.com/en/3.0/ref/settings#s-csrf-cookie-secure
CSRF_COOKIE_SECURE = not DEBUG

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secure-referrer-policy
# https://docs.djangoproject.com/en/3.0/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = 'same-origin'

# https://docs.djangoproject.com/en/3.0/ref/settings#s-allowed-hosts
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost, 127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# https://docs.djangoproject.com/en/3.0/ref/settings#s-internal-ips
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configuring-internal-ips
INTERNAL_IPS = ['127.0.0.1']

# Application definition

INSTALLED_APPS = [
    # admin_menu come before django.contrib.admin; see https://github.com/cdrx/django-admin-menu
    # 'admin_menu',  # This breaks mass_edit; TODO: test locally and fix it
    # admin_tools and its modules must come before django.contrib.admin
    'admin_tools',  # https://django-admin-tools.readthedocs.io/en/latest/configuration.html
    'admin_tools.menu',
    # 'admin_tools.theming',
    # 'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.forms',
    # 'django.contrib.gis',  # https://docs.djangoproject.com/en/3.0/ref/contrib/gis/
    'admin_auto_filters',  # https://github.com/farhan0581/django-admin-autocomplete-filter
    'bootstrap_datepicker_plus',  # https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/
    'crispy_forms',  # https://django-crispy-forms.readthedocs.io/
    'dbbackup',  # https://django-dbbackup.readthedocs.io/en/latest/
    'django_celery_beat',  # https://github.com/celery/django-celery-beat
    'django_celery_results',  # https://github.com/celery/django-celery-results
    'django_nose',  # https://github.com/jazzband/django-nose
    'django_replicated',  # https://github.com/yandex/django_replicated
    'debug_toolbar',  # https://django-debug-toolbar.readthedocs.io/en/latest/
    'django_select2',  # https://django-select2.readthedocs.io/en/latest/index.html
    'decouple',
    'easy_thumbnails',  # https://github.com/jonasundderwolf/django-image-cropping
    'extra_views',  # https://django-extra-views.readthedocs.io/en/latest/index.html
    # TODO: https://django-file-picker.readthedocs.io/en/latest/index.html
    # 'file_picker',
    # 'file_picker.uploads',  # file and image Django app
    # 'file_picker.wymeditor',  # optional WYMeditor plugin
    # 'sorl.thumbnail',  # required
    'gm2m',  # https://django-gm2m.readthedocs.io/en/latest/
    'image_cropping',  # https://github.com/jonasundderwolf/django-image-cropping
    'imagekit',  # https://github.com/matthewwithanm/django-imagekit
    'massadmin',  # https://github.com/burke-software/django-mass-edit
    # 'menu',  # https://github.com/jazzband/django-simple-menu
    'pympler',  # https://pympler.readthedocs.io/en/latest/index.html
    'nested_admin',  # https://github.com/theatlantic/django-nested-admin
    'polymorphic',  # https://django-polymorphic.readthedocs.io/en/stable/
    'rest_framework',  # https://github.com/encode/django-rest-framework
    'sass_processor',  # https://github.com/jrief/django-sass-processor
    'social_django',  # https://python-social-auth.readthedocs.io/en/latest/configuration/django.html
    'tinymce',  # https://django-tinymce.readthedocs.io/en/latest/
    'typedmodels',  # https://github.com/craigds/django-typed-models
    'account.apps.AccountConfig',
    'entities.apps.EntitiesConfig',
    'home.apps.HomeConfig',
    'markup.apps.MarkupConfig',
    'search.apps.SearchConfig',
    'images.apps.ImagesConfig',
    'occurrences.apps.OccurrencesConfig',
    'places.apps.LocationsConfig',
    'quotes.apps.QuotesConfig',
    'sources.apps.SourcesConfig',
    'topics.apps.TopicsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#enabling-middleware
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # # https://github.com/yandex/django_replicated
    # 'django_replicated.middleware.ReplicationMiddleware',  # breaks user sessions

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
]

ROOT_URLCONF = 'history.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'APP_DIRS': True,  # app_dirs must not be set when `loaders` is defined (in `OPTIONS`)
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django_settings_export.settings_export',
            ],
            # https://docs.djangoproject.com/en/3.0/ref/templates/api/#loader-types
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    # https://django-admin-tools.readthedocs.io/en/latest/configuration.html
                    'admin_tools.template_loaders.Loader',
                ]),
            ],
            'libraries': {
                # https://stackoverflow.com/questions/41376480/django-template-exceptions-templatesyntaxerror-static-is-not-a-registered-tag
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'history.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    # '--cover-package=foo,bar',  # which apps to measure coverage for
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if ENVIRONMENT == Environment.PROD:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'HOST': config('DB_HOST'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
        }
    }
elif ENVIRONMENT == Environment.GITHUB_TEST:
    DATABASES = {
        'default': {
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': 5432,
            'ENGINE': 'django.db.backends.postgresql',
        }
    }
elif ENVIRONMENT == Environment.DEV and USE_PROD_DB:
    DATABASES = {
        'default': {
            'NAME': config('PROD_DB_NAME'),
            'USER': config('PROD_DB_USER'),
            'PASSWORD': config('PROD_DB_PASSWORD'),
            'HOST': config('PROD_DB_HOST'),
            'PORT': config('PROD_DB_PORT'),
            'ENGINE': 'django.db.backends.postgresql',
        }
    }
    print(f'WARNING: Using production database!  Tread carefully!')
else:
    DATABASES = {
        'default': {
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'ENGINE': 'django.db.backends.postgresql',
        },
        'slave': {
            'NAME': 'slave',
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'ENGINE': 'django.db.backends.postgresql',
        },
        'backup': {
            'NAME': 'backup',
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'ENGINE': 'django.db.backends.postgresql',
        }
    }

# TODO: Fix this so it doesn't break user sessions
# # https://github.com/yandex/django_replicated
# from django_replicated.settings import *
# REPLICATED_DATABASE_SLAVES = ['slave']
# DATABASE_ROUTERS = ['django_replicated.router.ReplicationRouter']
# REPLICATED_DATABASE_DOWNTIME = 30
# REPLICATED_VIEWS_OVERRIDES = {
#     '/admin/*': 'master',
#     '/history/*': 'master',  # TODO: probably should use slave eventually
#     # 'api-store-event': 'slave',
#     # 'app.views.do_something': 'master',
#     # '/users/': 'slave',
# }

# https://django-dbbackup.readthedocs.io/en/latest/installation.html
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': config('DBBACKUP_STORAGE_LOCATION', default=None)}

AUTH_USER_MODEL = 'account.User'
LOGIN_URL = 'account/login'
LOGOUT_URL = 'account/logout'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html
SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_USER_FIELDS = ['email', 'username']
# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html#authentication-backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
# https://python-social-auth.readthedocs.io/en/latest/pipeline.html
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social UID from whatever service we're authing thru. The UID is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verify that the current auth process is valid within the current project.
    # This is where emails and domains whitelists are applied (if defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Check if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person. Append a random string at the end if there's any collision.
    'social_core.pipeline.user.get_username',

    # Associate the current social details with another user account with a similar email address.
    'social_core.pipeline.social_auth.associate_by_email',  # Note: Default settings would disable this.

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',

    'history.social_auth.get_user_avatar',
)
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_LOGIN_ERROR_URL = '/account/settings'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
# Fields to populate `search_fields` in admin to search for related users
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email']

SOCIAL_AUTH_TWITTER_KEY = config('SOCIAL_AUTH_TWITTER_KEY', default='')
SOCIAL_AUTH_TWITTER_SECRET = config('SOCIAL_AUTH_TWITTER_SECRET', default='')

SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id, name, email'}

SOCIAL_AUTH_GITHUB_KEY = config('SOCIAL_AUTH_GITHUB_KEY', default='')
SOCIAL_AUTH_GITHUB_SECRET = config('SOCIAL_AUTH_GITHUB_SECRET', default='')

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='')
# SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']

# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Google Cloud Storage bucket names
# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
GS_MEDIA_BUCKET_NAME = 'modularhistory-media'
GS_STATIC_BUCKET_NAME = 'modularhistory-static'
GS_LOCATION = 'media'  # Bucket subdirectory in which to store files. (Defaults to the bucket root.)

MEGA_USERNAME = config('MEGA_USERNAME', default=None)
MEGA_PASSWORD = config('MEGA_PASSWORD', default=None)
mega = None
if IS_PROD and MEGA_USERNAME and MEGA_PASSWORD:
    mega = Mega()

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'static')
if IS_PROD:
    STATICFILES_STORAGE = 'history.storage.GoogleCloudStaticFileStorage'

# Media files (images, etc. uploaded by users)
MEDIA_URL = f'https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/media/' if IS_PROD else '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if IS_PROD:
    DEFAULT_FILE_STORAGE = 'history.storage.GoogleCloudMediaFileStorage'
    GS_BUCKET_NAME = GS_MEDIA_BUCKET_NAME

X_FRAME_OPTIONS = 'SAMEORIGIN'

# https://github.com/jrief/django-sass-processor
SASS_PRECISION = 8

# https://django-tinymce.readthedocs.io/en/latest/usage.html
TINYMCE_JS_URL = 'https://cloud.tinymce.com/stable/tinymce.min.js'
TINYMCE_JS_ROOT = 'https://cloud.tinymce.com/stable/'
TINYMCE_DEFAULT_CONFIG = {
    # 'height': 100,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': (
        'autolink, autoresize, autosave, blockquote, '
        # 'casechange, '  # Premium
        'charmap, code, contextmenu, emoticons, '
        # 'formatpainter, '  # Premium
        'fullscreen, hr, image, link, lists, media, paste, preview, '
        'searchreplace, spellchecker, textcolor, visualblocks, visualchars, wordcount'
    ),
    'toolbar1': (
        'bold italic | blockquote '
        # 'formatpainter | '
        'alignleft aligncenter alignright alignjustify | indent outdent | '
        'bullist numlist | visualblocks visualchars | '
        # 'charmap hr '
        'nonbreaking anchor | image media link | code | smallcaps highlight | '
        'spellchecker preview | undo redo'
    ),
    'contextmenu': ('formats | blockquote | highlight smallcaps | link media image '
                    'charmap hr | code | pastetext'),
    'menubar': True,
    'statusbar': True,
    'branding': False,
    'setup': ('''
        function (editor) {
            editor.addMenuItem('highlight', {
                text: 'Highlight text',
                icon: false,
                onclick : function() {
                    editor.focus();
                    let content = editor.selection.getContent();
                    if (content.length) {
                        content = content.replace("<mark>", "").replace("</mark>", "");
                        editor.selection.setContent("<mark>" + editor.selection.getContent() + '</mark>');
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
                        editor.selection.setContent(opening_tag + editor.selection.getContent() + closing_tag);
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
                        editor.selection.setContent("<mark>" + editor.selection.getContent() + '</mark>');
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
                        editor.selection.setContent(opening_tag + editor.selection.getContent() + closing_tag);
                    }
                }
            });
        }
    ''')
}
TINYMCE_SPELLCHECKER = True

# https://github.com/jonasundderwolf/django-image-cropping
THUMBNAIL_PROCESSORS = ('image_cropping.thumbnail_processors.crop_corners',) + ThumbnailSettings.THUMBNAIL_PROCESSORS

# https://pypi.org/project/django-bootstrap-datepicker-plus/
BOOTSTRAP4 = {'include_jquery': False}

# https://github.com/cdrx/django-admin-menu
ADMIN_LOGO = 'logo_head_white.png'

# https://django-admin-tools.readthedocs.io/en/latest/customization.html
ADMIN_TOOLS_MENU = 'history.admin_menu.AdminMenu'
ADMIN_TOOLS_THEMING_CSS = 'styles/admin.css'

# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_CLASS_CONVERTERS = {
    # 'textinput': "textinput inputtext"
}

# https://django-select2.readthedocs.io/en/latest/django_select2.html#module-django_select2.conf
# SELECT2_CSS = ''

MENU_ITEMS = [
    ['Occurrences', 'occurrences'],
    ['People', 'entities'],
    # ['Places', 'places'],
    ['Quotes', 'quotes'],
    # ['Sources', 'sources'],
    # ['Topics', 'topics'],
]

ENABLE_PATREON = True

SETTINGS_EXPORT = [
    'MENU_ITEMS',
    'ENABLE_PATREON'
]

# TODO: show debug toolbar in prod if desired
# def show_debug_toolbar(request) -> bool:
#     return DEBUG
#
#
# # https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': 'history.settings.show_debug_toolbar'
# }

# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-panels
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'pympler.panels.MemoryPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    # 'debug_toolbar.panels.logging.LoggingPanel',
    # 'debug_toolbar.panels.redirects.RedirectsPanel',
    # 'debug_toolbar.panels.profiling.ProfilingPanel',
    # 'debug_toolbar.panels.settings.SettingsPanel',
    # 'debug_toolbar.panels.versions.VersionsPanel',
]

X_RAPIDAPI_HOST = config('X_RAPIDAPI_HOST', default=None)
X_RAPIDAPI_KEY = config('X_RAPIDAPI_KEY', default=None)

# https://docs.djangoproject.com/en/3.0/ref/contrib/sites/
SITE_ID = 1

# https://docs.djangoproject.com/en/3.0/topics/email/
# https://docs.djangoproject.com/en/3.0/ref/settings#s-email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True

# Celery settings
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'amqp://localhost'

# CELERY_BROKER_URL = 'amqp://guest:**@localhost:5672'
# CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672'

# TODO
# CELERY_CACHE_BACKEND = 'default'
if ENVIRONMENT == Environment.DEV:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache',
        }
    }

# Google Cloud settings
GC_PROJECT = config('GC_PROJECT', default=None)
GC_QUEUE = config('GC_QUEUE', default=None)
GC_REGION = config('GC_REGION', default=None)
