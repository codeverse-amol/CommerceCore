import django_filters

from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):

    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    stock_min = django_filters.NumberFilter(
        field_name="stock",
        lookup_expr="gte"
    )

    stock_max = django_filters.NumberFilter(
        field_name="stock",
        lookup_expr="lte"
    )


    class Meta:
        model = Product
        fields = ["category"]