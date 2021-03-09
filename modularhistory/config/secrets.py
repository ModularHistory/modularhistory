
from decouple import config

# https://docs.djangoproject.com/en/3.1/ref/settings#s-secret-key
SECRET_KEY = config('SECRET_KEY', default='f67EPexT9Tmwnt71kcGPk')
