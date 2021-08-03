from django.core import paginator as django_paginator
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination, Paginator
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from core.pagination import TotalPagesMixin


class Page(django_paginator.Page):
    """Page for Elasticsearch."""

    def __init__(self, object_list, number, paginator, facets, count):
        self.facets = facets
        self.count = count
        super().__init__(object_list, number, paginator)


class ElasticPaginator(Paginator):
    """Paginator for Elasticsearch."""

    view: ListAPIView

    def page(self, number):
        """Returns a Page object for the given 1-based page number.

        :param number:
        :return:
        """
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        object_list, count = self.object_list[bottom:top].to_queryset(self.view)
        object_list = self.apply_filters(object_list)

        self.count = count

        if self.count > top and self.count - top <= self.orphans:
            # Fetch the additional orphaned nodes
            orphans = self.object_list[top : self.count].to_queryset(self.view)
            orphans = self.apply_filters(orphans)
            object_list = list(object_list) + list(orphans)
        number = self.validate_number(number)
        __facets = getattr(object_list, 'aggregations', None)
        return self._get_page(object_list, number, self, facets=__facets, count=count)

    def apply_filters(self, object_list):
        for backend in self.view.post_resolve_filters:
            object_list = backend().filter_queryset(self.view.request, object_list, self.view)
        return object_list

    def _get_page(self, *args, **kwargs):
        """Get page.

        Returns an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)


class ElasticPageNumberPagination(TotalPagesMixin, PageNumberPagination):
    """
    Page number pagination.

    A simple page number based style that supports page numbers as
    query parameters.

    Example:
        http://api.example.org/accounts/?page=4
        http://api.example.org/accounts/?page=4&page_size=100
    """

    django_paginator_class = ElasticPaginator
    page_size_query_param = 'page_size'
    orphans_query_param = 'orphans'

    def paginate_queryset(self, queryset, request, view=None):
        """Paginate a queryset.

        Paginate a queryset if required, either returning a page object,
        or `None` if pagination is not configured for this view.

        :param queryset:
        :param request:
        :param view:
        :return:
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        orphans = min(int(request.query_params.get(self.orphans_query_param, 0)), page_size)
        paginator = self.django_paginator_class(queryset, page_size, orphans=orphans)
        paginator.view = view

        page_number = int(request.query_params.get(self.page_query_param, 1))
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except django_paginator.InvalidPage as exc:
            msg = self.invalid_page_message.format(page_number=page_number, message=exc)
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
