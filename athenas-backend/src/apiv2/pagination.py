from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound

from django.db.models.query import QuerySet


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


class CustomPagination(PageNumberPagination):

    page_size = 30

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request, queryset)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(
            {
                "total": self.page.paginator.count,
                "page": self.page.number,
                "per_page": self.page.paginator.per_page,
                "navigation": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        navigation = {
            "type": "object",
            "properties": {
                "next": {
                    "type": "string",
                    "example": "http://athenas-dev/athenas/api/v2/rh/pvf/requests/?page=2&per_page=5",
                },
                "previous": {
                    "type": "string",
                    "example": "http://athenas-dev/athenas/api/v2/rh/pvf/requests/?per_page=5",
                },
            },
        }
        return {
            "type": "object",
            "properties": {
                "total": {
                    "type": "integer",
                    "example": 123,
                },
                "page": {
                    "type": "integer",
                    "example": 123,
                },
                "per_page": {
                    "type": "integer",
                    "example": 123,
                },
                "navigation": navigation,
                "results": schema,
            },
        }

    def get_page_size(self, request, queryset):
        page_size = request.GET.get("per_page")

        if page_size is None:
            if isinstance(queryset, QuerySet):
                page_size = queryset.count()
            else:
                page_size = len(queryset)

        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size,
                )
            except (KeyError, ValueError):
                pass

        return page_size
