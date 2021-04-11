from rest_framework.pagination import (
    PageNumberPagination as DjangoRestFrameworkPageNumberPagination,
)


class PageNumberPagination(DjangoRestFrameworkPageNumberPagination):
    """Pagination including total page count."""

    def get_paginated_response(self, data):
        """Add total_pages to the response."""
        response = super().get_paginated_response(data=data)
        response.data['total_pages'] = self.page.paginator.num_pages
        return response


class LargeResultsPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
