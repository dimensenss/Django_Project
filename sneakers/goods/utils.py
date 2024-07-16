import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django import forms
from django.db.models import Count, Q, Value, Subquery, OuterRef, CharField, F, Sum
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Concat
from django_filters import CharFilter
from django_filters.widgets import RangeWidget
from taggit.models import Tag

from sneakers.settings import MEDIA_URL
from .models import *


def get_list_recently_viewed(context):
    recently_viewed_data = context['request'].session.get("recently_viewed", [])
    recently_viewed_slugs = [
        product_date_dict['slug'] for product_date_dict in sorted(
            recently_viewed_data,
            key=lambda x: x['viewed_date'],
            reverse=True
        )]

    recently_viewed_qs = Sneakers.objects.filter(slug__in=recently_viewed_slugs).annotate(
        sneakers_first_image=F("first_image__image"),
        total_quantity=Sum('variations__quantity')
    )

    sneakers_dict = {item.slug: item for item in recently_viewed_qs}
    sorted_recently_viewed_qs = [
        sneakers_dict[slug] for slug in recently_viewed_slugs if slug in sneakers_dict
    ]
    context['recently_viewed_qs'] = sorted_recently_viewed_qs


class DataMixin:
    paginate_by = 4

    def get_user_context(self, **kwargs):
        context = kwargs
        if 'request' not in context:
            context['request'] = self.request

        cats = Category.objects.annotate(len=Count('sneakers')).filter(id__gte=1)
        context['cats'] = cats
        get_list_recently_viewed(context)

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
    brand = django_filters.ModelMultipleChoiceFilter(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    size = django_filters.CharFilter(
        label='Розмір',
        method='filter_by_sizes'
    )
    sizes = django_filters.CharFilter(
        label='Розмір',
        method='filter_by_sizes'
    )

    def filter_by_sizes(self, queryset, name, value):
        if value:
            value = value.split()
            queryset = queryset.filter(variations__size__in=value).distinct()
        return queryset

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
        fields = {
        }

    def __init__(self, *args, **kwargs):
        super(SneakersFilter, self).__init__(*args, **kwargs)
        self.filters['title_search'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['tags'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['order_by'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
        self.filters['size'].field.widget = forms.HiddenInput()
        self.filters['sizes'].field.widget = forms.HiddenInput()
        self.filters['price__gte'].field.widget.attrs.update({'class': 'custom-form-control mb-2 price_input'})
        self.filters['price__lte'].field.widget.attrs.update({'class': 'custom-form-control mb-2 price_input'})
        self.filters['tags'].field.widget.attrs.update({'class': 'custom-form-control mb-2'})
