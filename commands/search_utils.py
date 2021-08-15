"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import random
import time
from itertools import chain
from typing import TYPE_CHECKING, Optional

import django
from elasticsearch_dsl import Q

from apps.search.documents.entity import EntityDocument
from apps.search.documents.image import ImageDocument
from apps.search.documents.occurrence import OccurrenceDocument
from apps.search.documents.quote import QuoteDocument
from apps.search.documents.source import SourceDocument
from commands.command import command

if TYPE_CHECKING:
    from invoke.context import Context

    from apps.search.documents.base import Document


django.setup()

SEARCHABLE_DOCUMENTS: list['Document'] = [
    OccurrenceDocument,
    QuoteDocument,
    SourceDocument,
    ImageDocument,
    EntityDocument,
]

DOCUMENT_MAP = {
    'occurrences': OccurrenceDocument,
    'quotes': QuoteDocument,
    'sources': SourceDocument,
    'images': ImageDocument,
    'entities': EntityDocument,
}


@command
def search(
    context: 'Context',
    query: str,
    document: str = 'all',
    print_all: bool = False,
    print_sql: bool = False,
    start: int = 0,
    end: int = 20,
):
    """Perform a search for testing purposes."""
    index: Optional['Document'] = DOCUMENT_MAP.get(document, None)
    if document != 'all' and not index:
        raise ValueError(f'Invalid document name: {document}')
    print(f'Searching for = {query} in {document}...')
    query = Q('simple_query_string', query=query)
    tic = time.perf_counter_ns()
    if print_sql:
        from django.db import connection
    if index:
        s = index.search().query(query)[start:end]
        queryset = list(s.to_queryset())
    else:
        queryset = chain()
        for index in SEARCHABLE_DOCUMENTS:
            s = index.search().query(query)[start:end]
            queryset = chain(queryset, s.to_queryset())
        queryset = list(queryset)
    toc = (time.perf_counter_ns() - tic) / 1000000
    print(f'Search returned n={len(queryset)}, resolved results in {toc} ms')
    if print_sql:
        print(connection.queries)
    if len(queryset) > 0:
        print('Results:')
        if print_all:
            [print(x) for x in queryset]
        else:
            print(f'Random result item = {random.choice(queryset)}')  # noqa: S311
