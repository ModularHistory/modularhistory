from django.urls import reverse

from apps.admin.list_filters import ManyToManyAutocompleteFilter
from apps.topics.models.topic import Topic


class TopicFilter(ManyToManyAutocompleteFilter):
    """Reusable filter for models with topic tags."""

    title = 'tags'
    field_name = 'tags'
    _parameter_name = 'tags__pk__exact'
    m2m_cls = Topic

    def get_autocomplete_url(self, *args, **kwargs):
        """Return the URL used for topic autocompletion."""
        return reverse('admin:tag_search')
