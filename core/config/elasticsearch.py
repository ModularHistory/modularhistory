from os.path import join

from decouple import config

from core.environment import DOCKERIZED

ELASTIC_PASSWORD = config('ELASTIC_PASSWORD', default='')
ELASTIC_CERTS_DIR = config(
    'ELASTIC_CERTS_DIR', default='/usr/share/elasticsearch/config/certificates'
)

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200' if DOCKERIZED else 'localhost:9200',
        'http_auth': f'elastic:{ELASTIC_PASSWORD}',
        'use_ssl': True,
        'ssl_assert_hostname': False,
        'ca_certs': join(ELASTIC_CERTS_DIR, 'ca/ca.crt'),
        'verify_certs': True,
        'timeout': 60,
        'retry_on_timeout': True,
        'max_retries': 2,
    }
}

# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-auto-refresh
ELASTICSEARCH_DSL_AUTO_REFRESH = False

# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-signal-processor
ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'core.signals.CelerySignalProcessor'

# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-parallel
ELASTICSEARCH_DSL_PARALLEL = config('USE_PARALLEL_INDEX_BUILDING', cast=bool, default=True)
