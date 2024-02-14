from django import template
from django.db.models import Min, Max
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
    return {'cats': cats,}


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
    queryset = Sneakers.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).distinct()
    return queryset



