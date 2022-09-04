from decouple import config

# https://docs.djangoproject.com/en/dev/ref/settings#s-secret-key
SECRET_KEY = config('SECRET_KEY', default='f67EPexT9Tmwnt71kcGPk')
