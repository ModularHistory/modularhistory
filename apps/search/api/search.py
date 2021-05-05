import logging
from itertools import chain

from elasticsearch_dsl import Search as DSLSearch

from apps.search.documents.source import SourceDocument
from apps.search.documents.entity import EntityDocument
from apps.search.documents.quote import QuoteDocument
from apps.search.documents.occurrence import OccurrenceDocument

SEARCHABLE_DOCUMENTS = [SourceDocument, EntityDocument, QuoteDocument, OccurrenceDocument]


class Search(DSLSearch):

    results_count: int

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
        for result in s:
            result_groups.setdefault(result.meta.index, []).append(result)

        # build queryset chain for each result group by resolving es results to django models
        qs = chain()
        for index, result_group in result_groups.items():
            document = next((document for document in SEARCHABLE_DOCUMENTS if document.index_name() == index), None)
            model = document.django.model
            pks = [result.meta.id for result in result_group]

            queryset = model.objects.filter(pk__in=pks)
            qs = chain(qs, queryset)


        return sorted(qs, key=self.score_order, reverse=True), self.results_count

    def score_order(self, model):
        # TODO: refactor this
        # 1. needs faster hit matching (pre-create hash map with hit.meta.id as a key?)
        # 2. implement other sort options
        # 3. possibly move our meta assigning to somewhere else
        hit = next((hit for hit in self if int(hit.meta.id) == model.pk), None)
        model.meta = hit.meta
        return model.meta.score


