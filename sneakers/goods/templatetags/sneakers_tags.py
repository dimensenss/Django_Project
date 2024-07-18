from django import template
from django.db.models import Min, Max, Sum, F
from django.utils.http import urlencode

from goods.models import *
from goods.utils import DataMixin

register = template.Library()


@register.simple_tag()
def get_menu():
    return [{'title': 'Про нас', 'url_name': 'goods:about'},
            {'title': 'Контакти', 'url_name': 'goods:contacts'}, ]


@register.simple_tag(name='get_cats')
def get_categories():
    return Category.objects.all()


@register.simple_tag(name='get_photos')
def get_photos(post):
    return post.images.all()


@register.simple_tag(name='get_all_sizes')
def get_all_sizes():
    return SneakersVariations.objects.all().values_list('size', flat=True).distinct()


@register.simple_tag(name='get_min_max_prices', takes_context=True)
def get_prices(context, queryset):
    aggregate_data = Sneakers.objects.all().filter(is_published=True).aggregate(
        min_price=Min('sell_price'),
        max_price=Max('sell_price'),
    )

    min_price = int(aggregate_data['min_price']) if aggregate_data['min_price'] is not None else None
    max_price = int(aggregate_data['max_price']) if aggregate_data['max_price'] is not None else None

    context['min_price'] = min_price
    context['max_price'] = max_price

    return ''


# @register.simple_tag(name='get_colors')
# def get_colors(post):
#     colors = []
#     if post.variations.exists():
#         for product in post.variations.all().order_by('id'):
#             colors.append(product)
#
#         colors.append(post)
#         return colors


@register.inclusion_tag('goods/list_categories.html')
def show_categories(sort=None):  # доделать
    if sort:
        cats = Category.objects.order_by(sort)
    else:
        cats = Category.objects.all()
    return {'cats': cats, }


@register.inclusion_tag('includes/paginator.html', takes_context=True)
def show_paginator(context, paginator, page_obj):
    request = context['request'].GET.dict()
    return {"paginator": paginator, 'page_obj': page_obj, 'request': request}


@register.inclusion_tag('includes/navbar.html', takes_context=True)
def show_navbar(context, cats):
    request = context['request']
    return {'cats': cats, 'request': request}


@register.inclusion_tag('includes/breadcrumbs.html')
def get_breadcrumbs(category):
    return {
        'category': category
    }


@register.simple_tag(name='get_products_by_tag')
def get_products_by_tag(post):
    queryset = Sneakers.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).annotate(
        sneakers_first_image=F("first_image__image"),
        total_quantity=Sum('variations__quantity')).distinct()
    return queryset


@register.inclusion_tag('includes/horizontal_products_list.html')
def get_horizontal_products_list(products, title):
    return {
        'products': products,
        'title': title
    }

@register.simple_tag(name='get_all_product_ids')
def get_all_product_ids(products):
    return list(products.values_list('id', flat=True))

