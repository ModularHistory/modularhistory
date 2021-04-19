from core.config.redis import REDIS_HOST
from core.config.secrets import SECRET_KEY

# https://channels.readthedocs.io/en/latest/
ASGI_APPLICATION = 'core.asgi.application'
WSGI_APPLICATION = 'core.wsgi.application'  # unused
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, 6379)],
            'symmetric_encryption_keys': [SECRET_KEY],
        },
    },
}
