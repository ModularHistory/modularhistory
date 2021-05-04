from elasticsearch_dsl import analyzer

html_field_analyzer = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "porter_stem"],
    char_filter=["html_strip"]
)

DEFAULT_INDEX_SETTINGS = {'number_of_shards': 1, 'number_of_replicas': 0}
