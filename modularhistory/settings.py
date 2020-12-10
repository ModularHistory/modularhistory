"""
Django settings for modularhistory.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

import sentry_sdk
from decouple import config
from django.conf.locale.en import formats as en_formats
from easy_thumbnails.conf import Settings as ThumbnailSettings
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from modularhistory.constants.misc import PRODUCTION, Environments

ENABLE_ASGI: bool = False

# Environment
if os.getenv('ENVIRONMENT') == Environments.PROD:
    ENVIRONMENT = Environments.PROD
elif os.environ.get('GITHUB_WORKFLOW'):
    ENVIRONMENT = Environments.GITHUB_TEST
else:
    ENVIRONMENT = config('ENVIRONMENT', default=Environments.DEV)
logging.info(f'Environment: {ENVIRONMENT}')

IS_PROD = ENVIRONMENT == Environments.PROD
TESTING: bool = 'test' in sys.argv
VERSION = config('SHA', default='')

SERVER_LOCATION = 'unknown'  # TODO
GOOGLE_MAPS_API_KEY = 'undefined'  # TODO

ADMINS = (
    config(
        'ADMINS',
        cast=lambda admins: [
            tuple(entry.split(','))
            for entry in admins.replace(', ', ',').replace('; ', ';').split(';')
        ],
    )
    if config('ADMINS', default=None)
    else []
)

# Initialize the Sentry SDK for error reporting
SENTRY_DSN = config('SENTRY_DSN', default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        # https://docs.sentry.io/platforms/python/configuration/options/#dsn
        dsn=SENTRY_DSN,
        # https://docs.sentry.io/platforms/python/configuration/environments/
        environment=ENVIRONMENT,
        # https://docs.sentry.io/platforms/python/configuration/integrations/
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
        ],
        # https://docs.sentry.io/platforms/python/configuration/releases/
        release=f'modularhistory@{VERSION}',
        # Associate users to errors (using django.contrib.auth):
        # https://docs.sentry.io/platforms/python/configuration/options/#send-default-pii
        send_default_pii=True,
        # https://docs.sentry.io/platforms/python/performance/
        traces_sample_rate=0.5,
    )

    if ENABLE_ASGI:
        from modularhistory.asgi import application

        # https://docs.sentry.io/platforms/python/guides/asgi/
        application = SentryAsgiMiddleware(application)

en_formats.DATETIME_FORMAT = 'Y-m-d H:i:s.u'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# https://docs.djangoproject.com/en/3.0/ref/settings#s-debug
# DEBUG must be False in production (for security)
DEBUG = ENVIRONMENT == Environments.DEV

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secret-key
SECRET_KEY = config('SECRET_KEY')

# https://docs.djangoproject.com/en/3.1/ref/middleware/#module-django.middleware.common
PREPEND_WWW = False
APPEND_SLASH = True

# https://docs.djangoproject.com/en/3.1/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secure-ssl-redirect
SECURE_SSL_REDIRECT = False

# https://docs.djangoproject.com/en/3.0/ref/settings#s-session-cookie-samesite
SESSION_COOKIE_SECURE = IS_PROD

# https://docs.djangoproject.com/en/3.0/ref/settings#s-csrf-cookie-secure
CSRF_COOKIE_SECURE = IS_PROD

# https://docs.djangoproject.com/en/3.0/ref/settings#s-secure-referrer-policy
# https://docs.djangoproject.com/en/3.0/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = 'same-origin'

# https://docs.djangoproject.com/en/3.0/ref/settings#s-allowed-hosts
ALLOWED_HOSTS = (
    ['*']
    if ENVIRONMENT == Environments.DEV
    else config(
        'ALLOWED_HOSTS',
        default='localhost, 127.0.0.1',
        cast=lambda hosts: [string.strip() for string in hosts.split(',')],
    )
)

if ENABLE_ASGI:
    # https://channels.readthedocs.io/en/latest/
    ASGI_APPLICATION = 'modularhistory.asgi.application'
    # CHANNEL_LAYERS = {
    #     'default': {
    #         'BACKEND': 'channels_redis.core.RedisChannelLayer',
    #         'CONFIG': {
    #             'hosts': [('127.0.0.1', 6379)],
    #             'symmetric_encryption_keys': [SECRET_KEY],
    #         },
    #     },
    # }

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
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.forms',
    'admin_auto_filters',  # https://github.com/farhan0581/django-admin-autocomplete-filter  # noqa: E501
    'autoslug',  # https://django-autoslug.readthedocs.io/en/latest/
    'bootstrap_datepicker_plus',  # https://django-bootstrap-datepicker-plus.readthedocs.io/en/latest/  # noqa: E501
    # 'channels',  # https://channels.readthedocs.io/en/latest/index.html
    'concurrency',  # https://github.com/saxix/django-concurrency
    'crispy_forms',  # https://django-crispy-forms.readthedocs.io/
    'dbbackup',  # https://django-dbbackup.readthedocs.io/en/latest/
    'django_replicated',  # https://github.com/yandex/django_replicated
    'debug_toolbar',  # https://django-debug-toolbar.readthedocs.io/en/latest/
    'defender',  # https://github.com/jazzband/django-defender
    'django_q',  # https://django-q.readthedocs.io/en/latest/
    'django_select2',  # https://django-select2.readthedocs.io/en/latest/index.html
    'django_social_share',  # https://github.com/fcurella/django-social-share
    'decouple',  # https://github.com/henriquebastos/python-decouple/
    'easy_thumbnails',  # https://github.com/jonasundderwolf/django-image-cropping
    'extra_views',  # https://django-extra-views.readthedocs.io/en/latest/index.html
    'gm2m',  # https://django-gm2m.readthedocs.io/en/latest/
    # 'imagekit',  # https://github.com/matthewwithanm/django-imagekit
    'image_cropping',  # https://github.com/jonasundderwolf/django-image-cropping
    'lockdown',  # https://github.com/Dunedan/django-lockdown
    'massadmin',  # https://github.com/burke-software/django-mass-edit
    'martor',  # https://github.com/agusmakmun/django-markdown-editor
    'prettyjson',  # https://github.com/kevinmickey/django-prettyjson
    'pympler',  # https://pympler.readthedocs.io/en/latest/index.html
    'nested_admin',  # https://github.com/theatlantic/django-nested-admin
    'rest_framework',  # https://github.com/encode/django-rest-framework
    'sass_processor',  # https://github.com/jrief/django-sass-processor
    'social_django',  # https://python-social-auth.readthedocs.io/en/latest/configuration/django.html  # noqa: E501
    'tinymce',  # https://django-tinymce.readthedocs.io/en/latest/
    'typedmodels',  # https://github.com/craigds/django-typed-models
    'webpack_loader',  # https://github.com/owais/django-webpack-loader
    'apps.account.apps.AccountConfig',
    'apps.dates.apps.DatesConfig',
    'apps.entities.apps.EntitiesConfig',
    'apps.home.apps.HomeConfig',
    'apps.interactions.apps.InteractionsConfig',
    'apps.postulations.apps.PostulationsConfig',
    'apps.search.apps.SearchConfig',
    'apps.images.apps.ImagesConfig',
    'apps.occurrences.apps.OccurrencesConfig',
    'apps.places.apps.LocationsConfig',
    'apps.quotes.apps.QuotesConfig',
    'apps.sources.apps.SourcesConfig',
    'apps.staticpages.apps.StaticPagesConfig',
    'apps.topics.apps.TopicsConfig',
    'apps.verifications.apps.VerificationsConfig',
]

MIDDLEWARE = [
    # https://docs.djangoproject.com/en/3.1/ref/middleware/#module-django.middleware.security
    'django.middleware.security.SecurityMiddleware',
    # Update cache:
    # https://docs.djangoproject.com/en/3.1/topics/cache/#order-of-middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    # Set the `site` attribute on the request, so request.site returns the current site:
    # 'django.contrib.sites.middleware.CurrentSiteMiddleware',
    # https://docs.djangoproject.com/en/3.1/topics/http/sessions/
    'django.contrib.sessions.middleware.SessionMiddleware',
    # https://docs.djangoproject.com/en/3.1/ref/middleware/#module-django.middleware.common
    'django.middleware.common.CommonMiddleware',
    # Fetch from cache:
    # https://docs.djangoproject.com/en/3.1/topics/cache/#order-of-middleware
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Add the `user` attribute to the request:
    # https://docs.djangoproject.com/en/3.1/ref/middleware/#module-django.contrib.auth.middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Protect against brute-force login:
    # https://github.com/jazzband/django-defender
    'defender.middleware.FailedLoginMiddleware',
    # https://django-debug-toolbar.readthedocs.io/en/latest/
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    # Staticpage middleware (based on Django's Flatpage middleware):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/flatpages/#using-the-middleware
    'apps.staticpages.middleware.StaticPageFallbackMiddleware',
    # https://docs.djangoproject.com/en/3.1/ref/contrib/redirects/
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    # Memory profiler
    'modularhistory.middleware.PymplerMiddleware',
]

ROOT_URLCONF = 'modularhistory.urls'

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
                (
                    'django.template.loaders.cached.Loader',
                    [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                        # https://django-admin-tools.readthedocs.io/en/latest/configuration.html
                        'admin_tools.template_loaders.Loader',
                    ],
                ),
            ],
            'libraries': {
                # https://stackoverflow.com/questions/41376480/django-template-exceptions-templatesyntaxerror-static-is-not-a-registered-tag
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'modularhistory.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
if ENVIRONMENT == Environments.GITHUB_TEST:
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
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': config('POSTGRES_HOST', default='localhost'),
            'NAME': config('POSTGRES_DB', default='modularhistory'),
            'USER': config('POSTGRES_USER', default='postgres'),
            'PASSWORD': config('POSTGRES_PASSWORD', default='postgres'),
        }
        # 'mongo': {
        #     'ENGINE' : 'django_mongodb_engine',
        #     'NAME' : 'default'
        # }
    }

# https://django-dbbackup.readthedocs.io/en/master/
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, '.backups/')}

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
    # Get the user's email address, if it wasn't automatically obtained
    'account.social_auth.get_user_email',
    # Make up a username for this person.
    # Append a random string at the end if there's any collision.
    'social_core.pipeline.user.get_username',
    # Associate the current details with a user account having a similar email address.
    # Note: Default settings would disable this.
    'social_core.pipeline.social_auth.associate_by_email',
    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',
    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',
    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
    # Get the user's profile picture
    'account.social_auth.get_user_avatar',
)
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_LOGIN_ERROR_URL = '/account/settings'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
# Fields to populate `search_fields` in admin to search for related users
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email']
# Permissions to request
SOCIAL_AUTH_SCOPE = ['email']
# Twitter auth settings
SOCIAL_AUTH_TWITTER_KEY = config('SOCIAL_AUTH_TWITTER_KEY', default='')
SOCIAL_AUTH_TWITTER_SECRET = config('SOCIAL_AUTH_TWITTER_SECRET', default='')
SOCIAL_AUTH_TWITTER_SCOPE = SOCIAL_AUTH_SCOPE
# Facebook auth settings
SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_SCOPE = SOCIAL_AUTH_SCOPE
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id, name, email'}
# GitHub auth settings
SOCIAL_AUTH_GITHUB_KEY = config('SOCIAL_AUTH_GITHUB_KEY', default='')
SOCIAL_AUTH_GITHUB_SECRET = config('SOCIAL_AUTH_GITHUB_SECRET', default='')
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']
# Google auth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH_SECRET', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email']

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

# Mega credentials
MEGA_USERNAME = config('MEGA_USERNAME', default=None)
MEGA_PASSWORD = config('MEGA_PASSWORD', default=None)

# Static files (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
SHARED_STATICFILES_DIR = os.path.join(BASE_DIR, 'modularhistory/static')
STATICFILES_DIRS = (SHARED_STATICFILES_DIR,)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
SASS_PROCESSOR_ROOT = SHARED_STATICFILES_DIR

# Media files (images, etc. uploaded by users)
# https://docs.djangoproject.com/en/3.1/topics/files/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

ARTIFACTS_URL = '/artifacts/'
ARTIFACTS_ROOT = os.path.join(BASE_DIR, '.artifacts')
ARTIFACTS_STORAGE = 'modularhistory.storage.LocalArtifactsStorage'

X_FRAME_OPTIONS = 'SAMEORIGIN'

# https://github.com/jrief/django-sass-processor
SASS_PRECISION = 8

# https://docs.djangoproject.com/en/3.1/topics/logging/
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False,
            },
        },
    }

# https://django-tinymce.readthedocs.io/en/latest/usage.html
# TODO: https://django-tinymce.readthedocs.io/en/latest/installation.html#prerequisites
TINYMCE_JS_URL = 'https://cloud.tinymce.com/stable/tinymce.min.js'
TINYMCE_JS_ROOT = 'https://cloud.tinymce.com/stable/'
TINYMCE_DEFAULT_CONFIG = {
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea.tinymce',
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
    'contextmenu': (
        'formats | blockquote | highlight smallcaps | link media image '
        'charmap hr | code | pastetext'
    ),
    'menubar': True,
    'statusbar': True,
    'branding': False,
    'setup': (
        '''
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
    '''
    ),
}
TINYMCE_SPELLCHECKER = True

# https://github.com/jonasundderwolf/django-image-cropping
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + ThumbnailSettings.THUMBNAIL_PROCESSORS

# https://pypi.org/project/django-bootstrap-datepicker-plus/
BOOTSTRAP4 = {'include_jquery': False}

# https://github.com/cdrx/django-admin-menu
ADMIN_LOGO = 'logo_head_white.png'

# https://django-admin-tools.readthedocs.io/en/latest/customization.html
ADMIN_TOOLS_MENU = 'admin.admin_menu.AdminMenu'
ADMIN_TOOLS_THEMING_CSS = 'styles/admin.css'

# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_CLASS_CONVERTERS: Dict[str, str] = {}

MENU_ITEMS = [
    # ['Occurrences', 'occurrences'],
    # ['People', 'entities'],
    # ['Quotes', 'quotes'],
    ['About', 'about'],
]

ENABLE_PATREON = True

SETTINGS_EXPORT = [
    # 'Environment',  # TODO: Can't be exported as a class/enum
    'ENVIRONMENT',
    'MENU_ITEMS',
    'ENABLE_PATREON',
]

# https://docs.djangoproject.com/en/3.1/ref/settings#s-internal-ips
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#configuring-internal-ips
INTERNAL_IPS = ['127.0.0.1']

# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_COLLAPSED': True,
    'SHOW_TOOLBAR_CALLBACK': 'config.debug_toolbar.show_toolbar',
}
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
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
]

RAPIDAPI_KEY = config('RAPIDAPI_KEY', default='')

# https://docs.djangoproject.com/en/3.0/ref/contrib/sites/
SITE_ID = 1

# https://docs.djangoproject.com/en/3.0/topics/email/
# https://docs.djangoproject.com/en/3.0/ref/settings#s-email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
try:
    EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
except Exception as error:
    logging.error(f'{error}')
    EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True

# Caching settings
use_dummy_cache_in_dev_environment = config('USE_DUMMY_CACHE', cast=bool, default=False)
Cache = Dict[str, Any]
CACHES: Dict[str, Cache]

REDIS_HOST = None
if ENVIRONMENT in (Environments.DEV, Environments.GITHUB_TEST):
    REDIS_HOST = 'localhost'
else:
    REDIS_HOST = 'redis'
REDIS_BASE_URL = f'redis://{REDIS_HOST}:6379'

# https://github.com/jazzband/django-redis
if ENVIRONMENT == Environments.DEV and use_dummy_cache_in_dev_environment:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
elif REDIS_HOST:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'{REDIS_BASE_URL}/0',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        }
    }
    # https://github.com/jazzband/django-redis
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

# https://django-q.readthedocs.io/en/latest/configure.html
Q_CLUSTER = {
    'cpu_affinity': 1,
    'label': 'Django Q',
    'redis': f'{REDIS_BASE_URL}/0',
}

# https://github.com/jazzband/django-defender
DEFENDER_REDIS_URL = f'{REDIS_BASE_URL}/0'
if IS_PROD:
    DEFENDER_BEHIND_REVERSE_PROXY = True

VUE_FRONTEND_DIR = os.path.join(BASE_DIR, 'client')

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'vue/',  # must end with slash
        'STATS_FILE': os.path.join(VUE_FRONTEND_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}

DISABLE_CHECKS = config('DISABLE_CHECKS', default=False, cast=bool)

if ENVIRONMENT == Environments.DEV and not DISABLE_CHECKS:
    from config import checks  # noqa: F401
