"""Auth-related settings, including social auth settings."""

from decouple import config

from core.environment import IS_PROD

AUTH_USER_MODEL = 'users.User'

# https://django-allauth.readthedocs.io/en/latest/configuration.html
SOCIALACCOUNT_QUERY_EMAIL = True

# https://dj-rest-auth.readthedocs.io/en/latest/configuration.html#configuration
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.api.serializers.UserSerializer',
}

# https://dj-rest-auth.readthedocs.io/en/latest/installation.html#json-web-token-jwt-support-optional
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'access-token'
JWT_AUTH_REFRESH_COOKIE = 'refresh-token'
JWT_COOKIE_SECURE = IS_PROD
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.api.serializers.UserSerializer'
}

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

# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#authentication-backends
AUTHENTICATION_BACKENDS = (
    # Necessary for Django admin login
    'django.contrib.auth.backends.ModelBackend',
    # allauth-specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Provider specific settings:
# https://django-allauth.readthedocs.io/en/latest/providers.html
SOCIALACCOUNT_PROVIDERS = {
    # https://django-allauth.readthedocs.io/en/latest/providers.html#discord
    'discord': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_DISCORD_CLIENT_ID', default=''),
            'key': config('SOCIAL_AUTH_DISCORD_KEY', default=''),
            'secret': config('SOCIAL_AUTH_DISCORD_SECRET', default=''),
        }
    },
    'github': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_GITHUB_CLIENT_ID', default=''),
            'secret': config('SOCIAL_AUTH_GITHUB_SECRET', default=''),
        },
        'SCOPE': ['user'],
        'VERIFIED_EMAIL': True,
    },
    'facebook': {
        # https://django-allauth.readthedocs.io/en/latest/providers.html#facebook
        'APP': {
            'key': config('SOCIAL_AUTH_FACEBOOK_KEY', default=''),
            'secret': config('SOCIAL_AUTH_FACEBOOK_SECRET', default=''),
        },
        'EXCHANGE_TOKEN': True,
        'SCOPE': ['email', 'public_profile'],
    },
    'google': {
        'APP': {
            'key': config('SOCIAL_AUTH_GOOGLE_KEY', default=''),
            'secret': config('SOCIAL_AUTH_GOOGLE_SECRET', default=''),
        },
        'SCOPE': ['profile', 'email'],
    },
    'twitter': {
        'APP': {
            'key': config('SOCIAL_AUTH_TWITTER_KEY', default=''),
            'secret': config('SOCIAL_AUTH_TWITTER_SECRET', default=''),
        }
    },
}
