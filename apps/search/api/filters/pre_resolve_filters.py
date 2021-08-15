from typing import Callable

SORT_BY_PARAM = 'ordering'

# list of filters that's applied to every module
PRE_RESOLVE_FILTERS: list[Callable] = [
    # random ordering filter could be applied as a hack to disable caching search queries via cachalot
    # assuming caching of random queries is disabled
    # see: https://django-cachalot.readthedocs.io/en/latest/quickstart.html#cachalot-cache-random
    # lambda queryset: queryset.order_by('?'),
]

# list of filters per module
PER_MODULE_PRE_RESOLVE_FILTERS: dict[str, list[Callable]] = {
    # disabled for now because apparently it's redundant when serialized relations are cached
    # Occurrence: [Occurrence.objects.prefetch_search_relatives]
}


class PreResolveFilterBackend:
    """
    Filter that's applied for resolving modules from search results per module
    """

    def filter_queryset(self, request, queryset, view, model):
        for pre_resolve_filter in PRE_RESOLVE_FILTERS:
            queryset = pre_resolve_filter(queryset)

        if model in PER_MODULE_PRE_RESOLVE_FILTERS:
            for pre_resolve_filter in PER_MODULE_PRE_RESOLVE_FILTERS[model]:
                queryset = pre_resolve_filter(queryset)
        return queryset
