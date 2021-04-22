"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import time
import random

import django
from elasticsearch_dsl import Q
from decouple import config
from core.constants.environments import Environments

from .command import command
from django.conf import settings  # noqa: E402

from apps.search.documents import QuoteDocument

django.setup()

@command
def search(context, query):
    print(f"Searching for = {query} in quotes")

    tic = time.perf_counter_ns()

    query = Q('multi_match', query=query)

    search = QuoteDocument.search().query(query)
    searchToc = (time.perf_counter_ns() - tic)/1000000

    tic = time.perf_counter_ns()
    queryset = list(search.to_queryset())
    resolveToc = (time.perf_counter_ns() - tic)/1000000

    print(f"Search returned n={len(queryset)} results in {searchToc} ms, resolved in {resolveToc}ms, total={searchToc+resolveToc} ms")

    if len(queryset) > 0:
        print(f"Random result item = {random.choice(queryset)}")

