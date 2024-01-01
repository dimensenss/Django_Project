import django_filters
from django_filters import CharFilter

from .models import *


class SneakersFilter(django_filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains', label='Назва складається з',)
    price__gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Ціна більша за',
    )

    price__lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Ціна меньша за',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('sell_price', 'sell_price'),
        ),
        field_labels={
            'sell_price': 'Ціна',
        }
    )
    class Meta:
        model = Sneakers
        fields = {'price': ['gte', 'lte']}



