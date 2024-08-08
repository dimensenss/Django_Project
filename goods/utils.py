import django_filters
from django import forms
from django.db.models import Count, Value, F, Sum, Min, Max
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django_filters import CharFilter
from taggit.models import Tag
from dal import autocomplete
from datetime import datetime
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


def get_user_wishes(request):
    if request.user.is_authenticated:
        return Wish.objects.filter(user=request.user,
                                   product__is_published=True).order_by('id').select_related('product').annotate(
            product_slug=F("product__slug"),
        )

    if not request.session.session_key:
        request.session.create()

    return Wish.objects.filter(session_key=request.session.session_key, product__is_published=True).order_by('id').select_related('product').annotate(
        product_slug=F("product__slug"),

    )


def get_product_from_wishes(request):
    if request.user.is_authenticated:
        return Sneakers.objects.filter(is_published=1).annotate(
            sneakers_first_image=F("first_image__image"),
            total_quantity=Sum('variations__quantity')).filter(wish__user=request.user)
    else:
        session_key = request.session.session_key
        return Sneakers.objects.filter(is_published=1).annotate(
            sneakers_first_image=F("first_image__image"),
            total_quantity=Sum('variations__quantity')).filter(wish__session_key=session_key)


def get_product_list_from_wishes(request):
    if request.user.is_authenticated:
        return Sneakers.objects.filter(wish__user=request.user)
    else:
        session_key = request.session.session_key
        return Sneakers.objects.filter(wish__session_key=session_key)


def get_min_max_prices(context):
    aggregate_data = Sneakers.objects.all().filter(is_published=True).aggregate(
        min_price=Min('sell_price'),
        max_price=Max('sell_price'),
    )

    min_price = int(aggregate_data['min_price']) if aggregate_data['min_price'] is not None else 0
    max_price = int(aggregate_data['max_price']) if aggregate_data['max_price'] is not None else 100_000

    context['min_price'] = min_price
    context['max_price'] = max_price


class DataMixin:
    paginate_by = 4

    def get_user_context(self, **kwargs):
        context = kwargs
        if 'request' not in context:
            context['request'] = self.request

        cats = Category.objects.annotate(len=Count('sneakers')).filter(id__gte=1)
        context['cats'] = cats
        get_list_recently_viewed(context)
        get_min_max_prices(context)

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
        fields = {}

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


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs


class SneakersAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SneakersVariations.objects.all()

        if self.q:
            qs = qs.filter(sneakers__title__istartswith=self.q)

        return qs


class BrandsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Brand.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
