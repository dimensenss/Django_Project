import django_filters
from django_filters import CharFilter
from django.db.models import Q
from .models import *


class SneakersFilter(django_filters.FilterSet):
    title_search = CharFilter(method='title_content_filter', label='Назва складається з', )
    price__gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Ціна від:',
    )

    price__lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Ціна до:',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('sell_price', 'sell_price'),
        ),
        field_labels={
            'sell_price': 'Ціна',
        }
    )

    def title_content_filter(self, queryset, name, value):
        keywords = [word for word in value.split() if len(word) > 2]
        q_objects = Q()

        for token in keywords:
            q_objects |= Q(title__contains=token)
            q_objects |= Q(content__contains=token)

        return queryset.filter(q_objects)

    class Meta:
        model = Sneakers
        fields = {'price': ['gte', 'lte']}