"""Auth-related settings, including social auth settings."""

AUTH_USER_MODEL = 'account.User'
LOGIN_URL = 'account/login'
LOGOUT_URL = 'account/logout'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

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
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
