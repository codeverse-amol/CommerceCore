from rest_framework.pagination import PageNumberPagination

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import CursorPagination


class ProductPagination(PageNumberPagination):

    page_size = 5

    page_size_query_param = "page_size"

    max_page_size = 20


class ProductLimitOffsetPagination(LimitOffsetPagination):

    default_limit = 5
    max_limit = 20


class ProductCursorPagination(CursorPagination):

    page_size = 5
    ordering = "-id"
