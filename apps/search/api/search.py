import logging
from itertools import chain
from typing import Optional

from elasticsearch_dsl import Search as DSLSearch

from apps.search.documents.source import SourceDocument
from apps.search.documents.entity import EntityDocument
from apps.search.documents.quote import QuoteDocument
from apps.search.documents.occurrence import OccurrenceDocument
from apps.search.documents.image import ImageDocument

SEARCHABLE_DOCUMENTS = {
    OccurrenceDocument.index_name(): OccurrenceDocument,
    SourceDocument.index_name(): SourceDocument,
    EntityDocument.index_name(): EntityDocument,
    QuoteDocument.index_name(): QuoteDocument,
    ImageDocument.index_name(): ImageDocument
}


class Search(DSLSearch):
    results_count: int
    results_by_id: Optional[dict]

    def to_queryset(self):
        """
        This method return a django queryset from the an elasticsearch result.
        It costs a query to the sql db.
        """
        s = self

        # Do not query again if the es result is already cached
        if not hasattr(self, '_response'):
            # We only need the meta fields with the models ids
            s = self.source(excludes=['*'])
            s = s.execute()

        self.results_count = s.hits.total.value

        logging.info(f"ES Search took {s.took} ms and returned n={self.results_count} results")

        # group results by index name
        result_groups = {}
        self.results_by_id = {}
        for result in s:
            index = result.meta.index
            result_groups.setdefault(index, []).append(result)
            key = f"{index}_{result.meta.id}"
            self.results_by_id[key] = result

        # build queryset chain for each result group by resolving es results to django models
        qs = chain()
        for index, result_group in result_groups.items():
            if index not in SEARCHABLE_DOCUMENTS:
                logging.error(f"Couldn't find document definition for this index = {index}")
                continue

            document = SEARCHABLE_DOCUMENTS[index]
            model = document.django.model
            pks = [result.meta.id for result in result_group]

            queryset = model.objects.filter(pk__in=pks)
            qs = chain(qs, queryset)

        qs = sorted(qs, key=self.score_order, reverse=True)
        return qs, self.results_count

    def score_order(self, model):
        # TODO: refactor this
        # 1. find a better way of to assign meta somewhere else

        # hit = next((hit for hit in self if int(hit.meta.id) == model.pk), None)
        document = next((document for document in SEARCHABLE_DOCUMENTS.values() if isinstance(model, document.django.model)), None)
        index = document.index_name()
        key = f"{index}_{model.pk}"
        hit = self.results_by_id[key]
        model.meta = hit.meta
        return model.meta.score
