from rest_framework.pagination import (
    PageNumberPagination as DjangoRestFrameworkPageNumberPagination,
)


class TotalPagesMixin(DjangoRestFrameworkPageNumberPagination):
    """Adds total page count to pagination."""

    def get_paginated_response(self, data: dict):
        """Add total_pages to the response."""
        response = super().get_paginated_response(data=data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response


class PageNumberPagination(TotalPagesMixin):
    """Default pagination class."""


class VariableSizePagination(PageNumberPagination):
    """Paginator for client-specified page size."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LargeSizePagination(VariableSizePagination):

    page_size = 1000
