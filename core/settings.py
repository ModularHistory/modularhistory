"""
Django settings for modularhistory.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
from os.path import join

from decouple import config
from django.conf.locale.en import formats as en_formats
from easy_thumbnails.conf import Settings as ThumbnailSettings
from split_settings.tools import include

from core.environment import DOCKERIZED, ENVIRONMENT, IS_DEV, IS_PROD, TESTING

en_formats.DATETIME_FORMAT = 'Y-m-d H:i:s.u'

# https://docs.djangoproject.com/en/dev/ref/settings#s-debug
# DEBUG must be False in production (for security).
DEBUG = IS_DEV and not config('IS_CELERY', cast=bool, default=False)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use the BASE_URL setting to build absolute URLs when necessary.
BASE_URL = config('BASE_URL', default='http://localhost')

# --- URL MODIFICATION SETTINGS ---
# https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.common
# Do not prepend www to modularhistory.com.
# The Nginx reverse proxy chops off the "www." from incoming requests.
PREPEND_WWW = False
# When running in Docker, delegate slash appendage to the Nginx reverse proxy server.
APPEND_SLASH = not DOCKERIZED

# --- SECURITY SETTINGS ---
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# https://docs.djangoproject.com/en/dev/ref/settings#s-secure-ssl-redirect
SECURE_SSL_REDIRECT = False  # SSL redirect is handled by Nginx reverse proxy in prod.
# https://docs.djangoproject.com/en/dev/ref/settings#s-session-cookie-samesite
SESSION_COOKIE_SECURE = IS_PROD
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = 'Lax' if (IS_PROD or DOCKERIZED) else 'None'
# https://docs.djangoproject.com/en/dev/ref/settings#s-csrf-cookie-secure
CSRF_COOKIE_SECURE = IS_PROD
# https://docs.djangoproject.com/en/dev/ref/settings#s-secure-referrer-policy
# https://docs.djangoproject.com/en/dev/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'SAMEORIGIN'
# https://docs.djangoproject.com/en/dev/ref/settings#s-allowed-hosts
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

INSTALLED_APPS = [
    # ---------------------------------
    # Admin-related apps
    # ---------------------------------
    # Note: admin_tools and its modules must come before django.contrib.admin.
    'admin_tools',  # https://django-admin-tools.readthedocs.io/en/latest/configuration.html
    'admin_tools.menu',
    # 'admin_tools.theming',
    # 'admin_tools.dashboard',
    'admin_auto_filters',  # https://github.com/farhan0581/django-admin-autocomplete-filter
    'admin_honeypot',  # https://github.com/dmpayton/django-admin-honeypot
    'django_admin_env_notice',  # https://github.com/dizballanze/django-admin-env-notice
    'flat_json_widget',  # https://github.com/openwisp/django-flat-json-widget
    'massadmin',  # https://github.com/burke-software/django-mass-edit
    'rangefilter',  # https://github.com/silentsokolov/django-admin-rangefilter
    'tinymce',  # https://django-tinymce.readthedocs.io/en/latest/
    'trumbowyg',  # https://github.com/sandino/django-trumbowyg
    # ---------------------------------
    # Django core apps
    # ---------------------------------
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.forms',
    # ---------------------------------
    # API-related apps
    # ---------------------------------
    'corsheaders',  # https://github.com/adamchainz/django-cors-headers
    'django_filters',  # https://github.com/carltongibson/django-filter
    'graphene_django',  # https://github.com/graphql-python/graphene-django
    'rest_framework',  # https://github.com/encode/django-rest-framework
    # ---------------------------------
    # Auth-related apps
    # ---------------------------------
    # 'defender',  # https://github.com/jazzband/django-defender  # TODO
    'rest_framework.authtoken',  # https://github.com/iMerica/dj-rest-auth#quick-setup
    # Note: dj_rest_auth must be loaded after rest_framework.
    'dj_rest_auth',  # https://github.com/iMerica/dj-rest-auth
    # ---------------------------------
    # Model-related apps
    # ---------------------------------
    'autoslug',  # https://django-autoslug.readthedocs.io/en/latest/
    'image_cropping',  # https://github.com/jonasundderwolf/django-image-cropping
    'polymorphic',  # https://django-polymorphic.readthedocs.io/en/stable/
    'typedmodels',  # https://github.com/craigds/django-typed-models
    # ---------------------------------
    # Elasticsearch
    # ---------------------------------
    'django_elasticsearch_dsl',  # https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html
    # ---------------------------------
    # Debugging- and profiling-related apps
    # ---------------------------------
    'silk',  # https://github.com/jazzband/django-silk
    # ---------------------------------
    # Miscellaneous third-party apps
    # ---------------------------------
    'cachalot',  # https://django-cachalot.readthedocs.io/
    'channels',  # https://channels.readthedocs.io/en/latest/index.html
    'crispy_forms',  # https://django-crispy-forms.readthedocs.io/
    'dbbackup',  # https://django-dbbackup.readthedocs.io/en/latest/
    'django_celery_beat',  # https://github.com/celery/django-celery-beat
    'django_celery_results',  # https://github.com/celery/django-celery-results
    'django_extensions',  # https://github.com/django-extensions/django-extensions
    'django_select2',  # https://django-select2.readthedocs.io/en/latest/index.html
    'decouple',  # https://github.com/henriquebastos/python-decouple/
    'easy_thumbnails',  # https://github.com/jonasundderwolf/django-image-cropping
    'health_check',  # https://github.com/KristianOellegaard/django-health-check
    'health_check.contrib.psutil',  # disk and memory utilization; requires psutil
    'health_check.contrib.redis',
    'meta',  # https://django-meta.readthedocs.io/en/latest/
    'sass_processor',  # https://github.com/jrief/django-sass-processor
    'watchman',  # https://github.com/mwarkentin/django-watchman
    # ---------------------------------
    # In-project apps
    # ---------------------------------
    'apps.chat.apps.ChatConfig',
    'apps.collections.apps.CollectionsConfig',
    'apps.dates.apps.DatesConfig',
    'apps.donations.apps.DonationsConfig',
    'apps.entities.apps.EntitiesConfig',
    'apps.forums.apps.ForumsConfig',
    'apps.graph.apps.GraphConfig',
    'apps.interactions.apps.InteractionsConfig',
    'apps.search.apps.SearchConfig',
    'apps.images.apps.ImagesConfig',
    'apps.occurrences.apps.OccurrencesConfig',
    'apps.places.apps.LocationsConfig',
    'apps.propositions.apps.PropositionsConfig',
    'apps.quotes.apps.QuotesConfig',
    'apps.sources.apps.SourcesConfig',
    'apps.staticpages.apps.StaticPagesConfig',
    'apps.stories.apps.StoriesConfig',
    'apps.topics.apps.TopicsConfig',
    'apps.trees.apps.TreesConfig',
    'apps.users.apps.UsersConfig',
    'apps.verifications.apps.VerificationsConfig',
]

MIDDLEWARE = [
    # CORS middleware "should be placed as high as possible"
    'corsheaders.middleware.CorsMiddleware',
    # https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
    'django.middleware.security.SecurityMiddleware',
    # https://github.com/jazzband/django-silk
    'silk.middleware.SilkyMiddleware',
    # Update cache:
    # https://docs.djangoproject.com/en/dev/topics/cache/#order-of-middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    # Set the `site` attribute on the request, so request.site returns the current site:
    # 'django.contrib.sites.middleware.CurrentSiteMiddleware',
    # https://docs.djangoproject.com/en/dev/topics/http/sessions/
    'django.contrib.sessions.middleware.SessionMiddleware',
    # https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.common
    'django.middleware.common.CommonMiddleware',
    # Fetch from cache:
    # https://docs.djangoproject.com/en/dev/topics/cache/#order-of-middleware
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Add the `user` attribute to the request:
    # https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.contrib.auth.middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Protect against brute-force login:
    # https://github.com/jazzband/django-defender
    # 'defender.middleware.FailedLoginMiddleware',  # TODO
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Staticpage middleware (based on Django's Flatpage middleware):
    # https://docs.djangoproject.com/en/dev/ref/contrib/flatpages/#using-the-middleware
    'apps.staticpages.middleware.StaticPageFallbackMiddleware',
    # https://docs.djangoproject.com/en/dev/ref/contrib/redirects/
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    # Memory profiler
    # 'core.middleware.PymplerMiddleware',  # TODO
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core/templates')],
        # 'APP_DIRS': True,  # app_dirs must not be set when `loaders` is defined (in `OPTIONS`)
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                # https://github.com/dizballanze/django-admin-env-notice#quickstart
                'django_admin_env_notice.context_processors.from_settings',
            ],
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
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
                'content_types': 'core.templatetags.content_types',
                'global_elements': 'core.templatetags.global_elements',
                'media': 'core.templatetags.media',
                'modal': 'core.templatetags.modal',
                'model_urls': 'core.templatetags.model_urls',
                # https://stackoverflow.com/questions/41376480/django-template-exceptions-templatesyntaxerror-static-is-not-a-registered-tag
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
}

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
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

GRAPH_MODELS = {
    'app_labels': [
        'images',
        'places',
        'propositions',
        'quotes',
        'sources',
        'topics',
        'users',
    ],
    'group_models': True,
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Mega credentials
MEGA_USERNAME = config('MEGA_USERNAME', default=None)
MEGA_PASSWORD = config('MEGA_PASSWORD', default=None)

# Static files (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_URL = '/static/'
SHARED_STATICFILES_DIR = os.path.join(BASE_DIR, 'core/static')
STATICFILES_DIRS = (SHARED_STATICFILES_DIR,)
STATIC_ROOT = os.path.join(BASE_DIR, '_static')
SASS_PROCESSOR_ROOT = SHARED_STATICFILES_DIR

# Media files (images, etc. uploaded by users)
# https://docs.djangoproject.com/en/dev/topics/files/
MEDIA_ROOT = os.path.join(BASE_DIR, '_media')
MEDIA_URL = '/media/'

ARTIFACTS_URL = '/artifacts/'
ARTIFACTS_ROOT = os.path.join(BASE_DIR, '.artifacts')
ARTIFACTS_STORAGE = 'core.storage.LocalArtifactsStorage'

# https://django-dbbackup.readthedocs.io/en/master/
BACKUPS_DIR = os.path.join(BASE_DIR, '.backups')
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BACKUPS_DIR}

DB_INIT_DIR = os.path.join(BASE_DIR, '.init')
DB_INIT_FILENAME = 'init.sql'
DB_INIT_FILEPATH = os.path.join(DB_INIT_DIR, DB_INIT_FILENAME)

# https://github.com/jrief/django-sass-processor
SASS_PRECISION = 8

# https://docs.djangoproject.com/en/dev/topics/logging/
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
                'level': config('DJANGO_LOG_LEVEL', default='INFO'),
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

# https://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'
# https://django-crispy-forms.readthedocs.io/en/latest/crispy_tag_forms.html
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_CLASS_CONVERTERS: dict[str, str] = {}

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

# https://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = 1

CONFIG_DIR = join(BASE_DIR, 'config')

# https://github.com/sobolevn/django-split-settings
# Include all settings modules with names not beginning with an underscore.
include('config/[!_]*.py')
