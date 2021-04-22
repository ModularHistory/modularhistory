"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import time
import random

import django
from elasticsearch_dsl import Search, Q
from elasticsearch import Elasticsearch

from itertools import chain

from .command import command

from apps.search.documents import QuoteDocument, OccurrenceDocument, SourceDocument, EntityDocument, ImageDocument

django.setup()

SEARCHABLE_DOCUMENTS = [OccurrenceDocument, QuoteDocument, SourceDocument, ImageDocument, EntityDocument]

@command
def search(context, query, all: bool = False, start: int = 0, end: int = 20):
    random_document = random.choice(SEARCHABLE_DOCUMENTS)

    print(f"Searching for = {query} in {'all' if all else random_document}")

    query = Q('simple_query_string', query=query)

    # client = Elasticsearch()
    # search = Search(using=client).query(query)

    tic = time.perf_counter_ns()

    if all:
        queryset = chain()
        for document in SEARCHABLE_DOCUMENTS:
            s = document.search().query(query)[start:end]
            queryset = chain(queryset, s.to_queryset())

        queryset = list(queryset)
    else:
        s = random_document.search().query(query)[start:end]
        queryset = list(s.to_queryset())

    toc = (time.perf_counter_ns() - tic)/1000000
    print(f"Search returned n={len(queryset)}, resolved results in {toc} ms")

    if len(queryset) > 0:
        print(f"Random result item = {random.choice(queryset)}")

