"""
Django settings for modularhistory.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import sys
from datetime import timedelta
from os.path import join
from typing import Any, Dict

from decouple import config
from django.conf.locale.en import formats as en_formats
from easy_thumbnails.conf import Settings as ThumbnailSettings
from split_settings.tools import include

from modularhistory.constants.environments import Environments
from modularhistory.environment import DOCKERIZED, ENVIRONMENT, IS_DEV, IS_PROD

en_formats.DATETIME_FORMAT = 'Y-m-d H:i:s.u'

TESTING: bool = 'test' in sys.argv

# https://docs.djangoproject.com/en/3.1/ref/settings#s-debug
# DEBUG must be False in production (for security)
DEBUG = IS_DEV

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# https://docs.djangoproject.com/en/3.1/ref/settings#s-secret-key
SECRET_KEY = config('SECRET_KEY', default='f67EPexT9Tmwnt71kcGPk')

# --- URL MODIFICATION SETTINGS ---
# Do not prepend `www.` to `modularhistory.com`; in production,
# the Nginx reverse proxy chops off the `www.` from all incoming requests.
# https://docs.djangoproject.com/en/3.1/ref/middleware/#module-django.middleware.common
PREPEND_WWW = False
APPEND_SLASH = True

# --- SECURITY SETTINGS ---
# https://docs.djangoproject.com/en/3.1/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# https://docs.djangoproject.com/en/3.1/ref/settings#s-secure-ssl-redirect
SECURE_SSL_REDIRECT = False  # SSL redirect is handled by Nginx reverse proxy in prod.
# https://docs.djangoproject.com/en/3.1/ref/settings#s-session-cookie-samesite
SESSION_COOKIE_SECURE = IS_PROD
# https://docs.djangoproject.com/en/3.1/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = 'Lax' if IS_PROD else 'None'
# https://docs.djangoproject.com/en/3.1/ref/settings#s-csrf-cookie-secure
CSRF_COOKIE_SECURE = IS_PROD
# https://docs.djangoproject.com/en/3.1/ref/settings#s-secure-referrer-policy
# https://docs.djangoproject.com/en/3.1/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'SAMEORIGIN'
# https://docs.djangoproject.com/en/3.1/ref/settings#s-allowed-hosts
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost, 127.0.0.1, 0.0.0.0, django',
    cast=lambda hosts: [string.strip() for string in hosts.split(',')],
)

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

REDIS_HOST = 'redis' if DOCKERIZED else 'localhost'
REDIS_PORT = '6379'
REDIS_BASE_URL = REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

# https://channels.readthedocs.io/en/latest/
ASGI_APPLICATION = 'modularhistory.asgi.application'
WSGI_APPLICATION = 'modularhistory.wsgi.application'  # unused
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, 6379)],
            'symmetric_encryption_keys': [SECRET_KEY],
        },
    },
}

INSTALLED_APPS = [
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
    'channels',  # https://channels.readthedocs.io/en/latest/index.html
    'concurrency',  # https://github.com/saxix/django-concurrency
    'corsheaders',  # https://github.com/adamchainz/django-cors-headers
    'crispy_forms',  # https://django-crispy-forms.readthedocs.io/
    'dbbackup',  # https://django-dbbackup.readthedocs.io/en/latest/
    'django_celery_beat',  # https://github.com/celery/django-celery-beat
    'django_celery_results',  # https://github.com/celery/django-celery-results
    'django_replicated',  # https://github.com/yandex/django_replicated
    'debug_toolbar',  # https://django-debug-toolbar.readthedocs.io/en/latest/
    # 'defender',  # https://github.com/jazzband/django-defender  # TODO
    'django_select2',  # https://django-select2.readthedocs.io/en/latest/index.html
    'django_social_share',  # https://github.com/fcurella/django-social-share
    'decouple',  # https://github.com/henriquebastos/python-decouple/
    'easy_thumbnails',  # https://github.com/jonasundderwolf/django-image-cropping
    'extra_views',  # https://django-extra-views.readthedocs.io/en/latest/index.html
    'gm2m',  # https://django-gm2m.readthedocs.io/en/latest/
    'health_check',  # https://github.com/KristianOellegaard/django-health-check
    'health_check.contrib.migrations',
    'health_check.contrib.psutil',  # disk and memory utilization; requires psutil
    'health_check.contrib.redis',
    'image_cropping',  # https://github.com/jonasundderwolf/django-image-cropping
    'lockdown',  # https://github.com/Dunedan/django-lockdown
    'massadmin',  # https://github.com/burke-software/django-mass-edit
    'martor',  # https://github.com/agusmakmun/django-markdown-editor
    'meta',  # https://django-meta.readthedocs.io/en/latest/
    # 'menu',
    'prettyjson',  # https://github.com/kevinmickey/django-prettyjson
    'pympler',  # https://pympler.readthedocs.io/en/latest/index.html
    'nested_admin',  # https://github.com/theatlantic/django-nested-admin
    'rest_framework',  # https://github.com/encode/django-rest-framework
    'sass_processor',  # https://github.com/jrief/django-sass-processor
    'tinymce',  # https://django-tinymce.readthedocs.io/en/latest/
    'typedmodels',  # https://github.com/craigds/django-typed-models
    'watchman',  # https://github.com/mwarkentin/django-watchman
    'webpack_loader',  # https://github.com/owais/django-webpack-loader
    'apps.account.apps.AccountConfig',
    'apps.chat.apps.ChatConfig',
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
    # CORS middleware "should be placed as high as possible"
    'corsheaders.middleware.CorsMiddleware',
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
    # 'defender.middleware.FailedLoginMiddleware',  # TODO
    # https://django-debug-toolbar.readthedocs.io/en/latest/
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Staticpage middleware (based on Django's Flatpage middleware):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/flatpages/#using-the-middleware
    'apps.staticpages.middleware.StaticPageFallbackMiddleware',
    # https://docs.djangoproject.com/en/3.1/ref/contrib/redirects/
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    # Memory profiler
    # 'modularhistory.middleware.PymplerMiddleware',  # TODO
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
                'django_settings_export.settings_export',
            ],
            # https://docs.djangoproject.com/en/3.1/ref/templates/api/#loader-types
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
                'content_types': 'modularhistory.templatetags.content_types',
                'global_elements': 'modularhistory.templatetags.global_elements',
                'media': 'modularhistory.templatetags.media',
                'modal': 'modularhistory.templatetags.modal',
                'model_urls': 'modularhistory.templatetags.model_urls',
                # https://stackoverflow.com/questions/41376480/django-template-exceptions-templatesyntaxerror-static-is-not-a-registered-tag
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'modularhistory.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    # Whatever value is set for AUTH_HEADER_TYPES must be reflected in React’s headers.
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}
JWT_COOKIE_NAME = 'jwt_token'
JWT_COOKIE_SAMESITE = 'Strict' if IS_PROD else 'None'
JWT_COOKIE_SECURE = IS_PROD

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': config('POSTGRES_HOST', default='localhost'),
        'NAME': config('POSTGRES_DB', default='modularhistory'),
        'USER': config('POSTGRES_USER', default='postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='postgres'),
        'PORT': 5432,
    },
}

# TODO: https://github.com/nesdis/djongo
ENABLE_MONGO = False
if ENABLE_MONGO:
    DATABASES['mongo'] = {
        'ENGINE': 'djongo',
        'NAME': 'default',
        'CLIENT': {
            'host': 'your-db-host',
        },
    }

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Mega credentials
MEGA_USERNAME = config('MEGA_USERNAME', default=None)
MEGA_PASSWORD = config('MEGA_PASSWORD', default=None)
MEGA_DEV_USERNAME = config('MEGA_DEV_USERNAME', default=MEGA_USERNAME)
MEGA_DEV_PASSWORD = config('MEGA_DEV_PASSWORD', default=MEGA_PASSWORD)

# Static files (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
SHARED_STATICFILES_DIR = os.path.join(BASE_DIR, 'modularhistory/static')
STATICFILES_DIRS = (SHARED_STATICFILES_DIR,)
STATIC_ROOT = os.path.join(BASE_DIR, '.static')
SASS_PROCESSOR_ROOT = SHARED_STATICFILES_DIR

# Media files (images, etc. uploaded by users)
# https://docs.djangoproject.com/en/3.1/topics/files/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

ARTIFACTS_URL = '/artifacts/'
ARTIFACTS_ROOT = os.path.join(BASE_DIR, '.artifacts')
ARTIFACTS_STORAGE = 'modularhistory.storage.LocalArtifactsStorage'

# https://django-dbbackup.readthedocs.io/en/master/
BACKUPS_DIR = os.path.join(BASE_DIR, '.backups')
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BACKUPS_DIR}

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

# https://github.com/jonasundderwolf/django-image-cropping
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + ThumbnailSettings.THUMBNAIL_PROCESSORS
# https://github.com/jonasundderwolf/django-image-cropping#custom-jquery
IMAGE_CROPPING_JQUERY_URL = None

# https://pypi.org/project/django-bootstrap-datepicker-plus/
BOOTSTRAP4 = {'include_jquery': False}

# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_CLASS_CONVERTERS: Dict[str, str] = {}

MENU_ITEMS = [
    ['Occurrences', '/occurrences/'],
    ['Quotes', '/quotes/'],
    ['Entities', '/entities/'],
]

ENABLE_PATREON = False

SETTINGS_EXPORT = [
    # 'Environment',  # TODO: Can't be exported as a class/enum
    'ENVIRONMENT',
    'MENU_ITEMS',
    'ENABLE_PATREON',
]

RAPIDAPI_KEY = config('X_RAPIDAPI_KEY', default='')

# https://docs.djangoproject.com/en/3.1/ref/contrib/sites/
SITE_ID = 1

# Caching settings
use_dummy_cache = config('DUMMY_CACHE', cast=bool, default=False)
Cache = Dict[str, Any]
CACHES: Dict[str, Cache]

# https://github.com/jazzband/django-redis
if IS_DEV and use_dummy_cache:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
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
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# https://github.com/jazzband/django-defender
USE_DEFENDER = False  # TODO
if USE_DEFENDER:
    DEFENDER_REDIS_URL = f'{REDIS_BASE_URL}/0'
    if IS_PROD or DOCKERIZED:
        # https://github.com/jazzband/django-defender#customizing-django-defender
        DEFENDER_BEHIND_REVERSE_PROXY = True

# https://docs.celeryproject.org/en/stable/django/
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_BROKER_URL = f'{REDIS_BASE_URL}/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html#django-celery-results-using-the-django-orm-cache-as-a-result-backend
CELERY_RESULT_BACKEND = 'django-cache'
CELERY_CACHE_BACKEND = 'default'

CONFIG_DIR = join(BASE_DIR, '.config')

# https://github.com/sobolevn/django-split-settings
# Include all settings modules with names not beginning with an underscore.
include('config/[!_]*.py')
