from elasticsearch_dsl import analyzer, tokenizer, char_filter

html_field_analyzer = analyzer(
    'html_strip',
    tokenizer='standard',
    filter=['lowercase', 'stop', 'porter_stem'],
    char_filter=['html_strip'],
)

instant_search_analyzer = analyzer(
    'custom',
    tokenizer=tokenizer('mono_bi_gram', 'ngram', min_gram=1, max_gram=2),
    filter=['lowercase', 'asciifolding'],
    char_filter=[char_filter('punctuation', 'pattern_replace', pattern=r'[^\w\s]', replacement='')]
)

DEFAULT_INDEX_SETTINGS = {
    'number_of_shards': 1,
    'number_of_replicas': 0,
}


def get_index_name_for_ct(ct_name: str):
    """Return the Elasticsearch index name for the given content type name."""
    return ct_name.split('.')[0]
