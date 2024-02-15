import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django import forms
from django.db.models import Count, Q, Value, Subquery, OuterRef, CharField, F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Concat
from django_filters import CharFilter
from django_filters.widgets import RangeWidget
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

        recently_viewed_qs = Sneakers.objects.filter(
            slug__in=context['request'].session.get("recently_viewed", [])).annotate(
            sneakers_first_image=F("first_image__image"))
        # recently_viewed_qs = sorted(recently_viewed_qs, key=lambda x: context['request'].session[x.slug])

        context['recently_viewed_qs'] = recently_viewed_qs
        return context


class SneakersFilter(django_filters.FilterSet):
    title_search = CharFilter(method='title_content_filter', label='Назва складається з', )

    price__gte = django_filters.NumberFilter(
        field_name='sell_price',
        lookup_expr='gte',
        label='Ціна від:',
    )

    price__lte = django_filters.NumberFilter(
        field_name='sell_price',
        lookup_expr='lte',
        label='Ціна до:',
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('sell_price', 'sell_price'),
        ),
        field_labels={
            'sell_price': 'Від дешевих до дорогих',
            '-sell_price': 'Від дорогих до дешевих',
        },
        empty_label=None,
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__name',
        to_field_name='name',
        label='Теги',
    )

    size = django_filters.CharFilter(
        method='filter_size',
        label='Розмір',
    )

    def title_content_filter(self, queryset, name, value):
        if value.isdigit() and len(value) <= 5:
            return queryset.filter(id=value)

        vector = SearchVector('title', 'content')
        query = SearchQuery(value)
        normalization = Value(2).bitor(Value(4))
        return queryset.annotate(rank=SearchRank(vector, query, normalization=normalization)).filter(
            rank__gt=0).order_by("-rank")

    def size_filter(self, queryset, name, value):
        value = ' '.join(value.split())

        if value:
            sizes = value.split()
            q_objects = Q()
            for size in sizes:
                q_objects |= Q(variations__size=size)

            queryset = queryset.filter(q_objects)

        return queryset.distinct()

    class Meta:
        model = Sneakers
        fields = {
            'tags': ['exact'],
            'price': ['gte', 'lte'],

        }

    def __init__(self, *args, **kwargs):
        super(SneakersFilter, self).__init__(*args, **kwargs)
        # Добавьте класс стилей для фильтра price__gte
        self.filters['price__gte'].field.widget = forms.HiddenInput()
        self.filters['price__lte'].field.widget = forms.HiddenInput()
        self.filters['title_search'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['tags'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['order_by'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['size'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})

