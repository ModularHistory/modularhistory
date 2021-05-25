from core.environment import DOCKERIZED

ELASTICSEARCH_DSL = {
    'default': {'hosts': 'elasticsearch:9200' if DOCKERIZED else 'localhost:9200'},
}
