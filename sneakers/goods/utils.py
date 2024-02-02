import django_filters
from django.db.models import Count, Q, Value, Subquery, OuterRef, CharField, F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Concat
from django_filters import CharFilter
from taggit.models import Tag

from sneakers.settings import MEDIA_URL
from .models import *


class DataMixin:
    paginate_by = 4

    def get_user_context(self, **kwargs):

        context = kwargs
        if 'request' not in context:
            context['request'] = self.request

        cats = Category.objects.annotate(len=Count('sneakers')).filter(id__gte=1)  # Исключить катгорию "Нет категории"
        context['cats'] = cats

        recently_viewed_qs = Sneakers.objects.filter(slug__in=context['request'].session.get("recently_viewed", [])).annotate(
            sneakers_first_image=F("first_image__image"))
        # recently_viewed_qs = sorted(recently_viewed_qs, key=lambda x: context['request'].session[x.slug])

        context['recently_viewed_qs'] = recently_viewed_qs
        return context


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
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__name',
        to_field_name='name',
        label='Теги',
    )

    def title_content_filter(self, queryset, name, value):
        if value.isdigit() and len(value) <= 5:
            return queryset.filter(id=value)

        vector = SearchVector('title', 'content')
        query = SearchQuery(value)
        normalization = Value(2).bitor(Value(4))
        return queryset.annotate(rank=SearchRank(vector, query, normalization=normalization)).filter(
            rank__gt=0).order_by("-rank")

    class Meta:
        model = Sneakers
        fields = {'price': ['gte', 'lte'],
                  'tags': ['exact']}
