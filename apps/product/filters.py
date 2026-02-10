from django_filters import FilterSet
import django_filters

from apps.product.models import Product


class ProductFilter(FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains',label='name')
    price = django_filters.NumberFilter()
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    market_name = django_filters.CharFilter(field_name='market__name', lookup_expr='icontains')
    min_score = django_filters.NumberFilter(field_name='score', lookup_expr='gte')


    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
        }
