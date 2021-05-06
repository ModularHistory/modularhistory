from elasticsearch_dsl import analyzer
from core.constants.content_types import get_ct_id

html_field_analyzer = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "porter_stem"],
    char_filter=["html_strip"]
)

DEFAULT_INDEX_SETTINGS = {'number_of_shards': 1, 'number_of_replicas': 0}


def get_index_name_for_ct(ct_name: str):
    """Return the Elasticsearch index name for the given content type name."""
    return get_ct_id(ct_name).app_label