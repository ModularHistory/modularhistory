# from django.db.utils import ProgrammingError
from django.apps import AppConfig


class SearchConfig(AppConfig):
    """TODO: add docstring."""

    name = 'search'

    # TODO: clean up
    # def ready(self):
    #     from django.contrib.contenttypes.models import ContentType
    #     from images.models import Image
    #     from occurrences.models import Occurrence
    #     from quotes.models import Quote
    #     from sources.models import Source
    #     # from topics.models import Topic
    #
    #     try:
    #         from .models import Search
    #         Search.CONTENT_TYPE_OPTIONS = [
    #             (ContentType.objects.get_for_model(Occurrence).id, 'Occurrences'),
    #             (ContentType.objects.get_for_model(Quote).id, 'Quotes'),
    #             (ContentType.objects.get_for_model(Image).id, 'Images'),
    #             (ContentType.objects.get_for_model(Source).id, 'Sources')
    #         ]
    #         print(f'>>> Set Search content types.')
    #     except ProgrammingError:
    #         pass  # TODO: get from db?
