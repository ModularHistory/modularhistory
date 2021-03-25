"""Auth-related settings, including social auth settings."""

from decouple import config

from modularhistory.environment import IS_PROD

AUTH_USER_MODEL = 'users.User'

# https://django-allauth.readthedocs.io/en/latest/
# TODO

# https://dj-rest-auth.readthedocs.io/en/latest/configuration.html#configuration
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.users.api.serializers.UserSerializer',
}

# https://dj-rest-auth.readthedocs.io/en/latest/installation.html#json-web-token-jwt-support-optional
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'next-auth.session-token'
JWT_AUTH_REFRESH_COOKIE = 'next-auth.refresh-token'
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
