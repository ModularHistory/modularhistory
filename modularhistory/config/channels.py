from modularhistory.config.secrets import SECRET_KEY
from modularhistory.config.redis import REDIS_HOST

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
