"""Auth-related settings, including social auth settings."""

from datetime import timedelta

from decouple import config

from modularhistory.config.secrets import SECRET_KEY
from modularhistory.environment import IS_PROD

AUTH_USER_MODEL = 'users.User'

# https://django-allauth.readthedocs.io/en/latest/
# TODO

# https://dj-rest-auth.readthedocs.io/en/latest/installation.html#json-web-token-jwt-support-optional
REST_USE_JWT = True
# TODO
JWT_AUTH_COOKIE = 'my-app-auth'
JWT_AUTH_REFRESH_COOKIE = 'my-refresh-token'
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.api.serializers.UserSerializer'
}

# https://dj-rest-auth.readthedocs.io/en/latest/configuration.html#configuration
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.api.serializers.UserSerializer',
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

# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
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

AUTHENTICATION_BACKENDS = (
    # Necessary for Django admin login
    'django.contrib.auth.backends.ModelBackend',
    # allauth-specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Provider specific settings:
# https://django-allauth.readthedocs.io/en/latest/providers.html
# TODO: For each OAuth based provider, either add a ``SocialApp``
# (``socialaccount`` app) containing the required client
# credentials, or list them here:
SOCIALACCOUNT_PROVIDERS = {
    # https://django-allauth.readthedocs.io/en/latest/providers.html#discord
    'discord': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_DISCORD_CLIENT_ID', default=''),
            'key': config('SOCIAL_AUTH_DISCORD_PUBLIC_KEY', default=''),
            'secret': config('SOCIAL_AUTH_DISCORD_SECRET', default=''),
        }
    },
    'github': {
        'APP': {
            'client_id': '123',
            'key': config('SOCIAL_AUTH_GITHUB_KEY', default=''),
            'secret': config('SOCIAL_AUTH_GITHUB_SECRET', default=''),
        }
    },
    'facebook': {
        'APP': {
            'client_id': '123',
            'key': config('SOCIAL_AUTH_FACEBOOK_KEY', default=''),
            'secret': config('SOCIAL_AUTH_FACEBOOK_SECRET', default=''),
        }
    },
    'google': {
        'APP': {
            'client_id': '123',
            'key': config('SOCIAL_AUTH_GOOGLE_OAUTH_KEY', default=''),
            'secret': config('SOCIAL_AUTH_GOOGLE_OAUTH_SECRET', default=''),
        }
    },
    'twitter': {
        'APP': {
            'client_id': '123',
            'key': config('SOCIAL_AUTH_TWITTER_KEY', default=''),
            'secret': config('SOCIAL_AUTH_TWITTER_SECRET', default=''),
        }
    },
}
