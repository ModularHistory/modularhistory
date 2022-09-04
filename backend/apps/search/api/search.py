import logging
from itertools import chain
from typing import TYPE_CHECKING, Optional, Sequence, Union

from elasticsearch_dsl import Search as DSLSearch

from apps.search.documents.entity import EntityDocument
from apps.search.documents.image import ImageDocument
from apps.search.documents.occurrence import OccurrenceDocument
from apps.search.documents.proposition import PropositionDocument
from apps.search.documents.quote import QuoteDocument
from apps.search.documents.source import SourceDocument

if TYPE_CHECKING:
    from apps.search.models.searchable_model import SearchableModel


SEARCHABLE_DOCUMENTS = {
    OccurrenceDocument.get_index_name(): OccurrenceDocument,
    PropositionDocument.get_index_name(): PropositionDocument,
    SourceDocument.get_index_name(): SourceDocument,
    EntityDocument.get_index_name(): EntityDocument,
    QuoteDocument.get_index_name(): QuoteDocument,
    ImageDocument.get_index_name(): ImageDocument,
}


class Search(DSLSearch):
    results_count: int
    results_by_id: Optional[dict]

    def to_queryset(self, view) -> tuple[Union[Sequence['SearchableModel'], chain], int]:
        """Resolve results from ElasticSearch to Django model instances."""
        response = self

        # Do not query again if the es result is already cached
        if not hasattr(self, '_response'):
            # We only need the meta fields with the models ids
            response = self.source(excludes=['*']).extra(track_scores=True)
            response = response.execute()

        self.results_count = int(response.hits.total.value)
        self._response = response

        logging.info(
            f'ES Search took {response.took} ms and returned n={self.results_count} results'
        )

        # group results by index name
        result_groups = {}
        self.results_by_id = {}
        for result in response:
            index = result.meta.index
            result_groups.setdefault(index, []).append(result)
            key = f'{index}_{result.meta.id}'
            self.results_by_id[key] = result

        # build queryset chain for each result group by resolving es results to django models
        qs = chain()
        for index, result_group in result_groups.items():
            document = SEARCHABLE_DOCUMENTS.get(index)
            if not document:
                logging.error(f"Couldn't find document definition for this index = {index}")
                continue

            model = document.django.model
            pks = [result.meta.id for result in result_group]

            queryset = model.objects.filter(pk__in=pks)
            queryset = self.apply_filters(view, queryset, model)
            qs = chain(qs, queryset)

        view.search = self
        return qs, self.results_count

    @staticmethod
    def apply_filters(view, queryset, model):
        for backend in view.pre_resolve_filters:
            queryset = backend().filter_queryset(view.request, queryset, view, model)
        return queryset
