from elasticsearch_dsl import analyzer

html_field_analyzer = analyzer(
    'html_strip',
    tokenizer='standard',
    filter=['lowercase', 'stop', 'porter_stem'],
    char_filter=['html_strip'],
)

DEFAULT_INDEX_SETTINGS = {'number_of_shards': 1, 'number_of_replicas': 0}


def get_index_name_for_ct(ct_name: str):
    """Return the Elasticsearch index name for the given content type name."""
    app_label, _model = ct_name.split('.')
    return app_label
