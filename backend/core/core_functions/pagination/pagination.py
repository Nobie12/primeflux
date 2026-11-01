from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class that extends DRF's PageNumberPagination."""

    page_size = 100  # Default page size, can be overridden in settings

    page_size_query_param = "page_size"  # Allow clients to set page size with this query parameter
    max_page_size = 300  # Maximum page size to prevent abuse

    def get_paginated_response(self, data):
        """Override the default paginated response to include additional metadata."""
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
