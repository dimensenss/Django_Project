from django import template
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
def show_categories(sort=None, cat_selected=None):  # доделать
    if sort:
        cats = Category.objects.order_by(sort)
    else:
        cats = Category.objects.all()
    return {'cats': cats, 'cat_selected': cat_selected}


@register.inclusion_tag('includes/paginator.html', takes_context=True)
def show_paginator(context, paginator, page_obj):
    request = context['request'].GET.dict()
    return {"paginator": paginator, 'page_obj': page_obj, 'request': request}


@register.inclusion_tag('includes/navbar.html', takes_context=True)
def show_navbar(context, cat_selected, cats, my_filter):
    request = context['request']
    return {"cat_selected": cat_selected, 'menu_items': cats, "filter": my_filter, 'request': request}


@register.inclusion_tag('includes/breadcrumbs.html')
def get_breadcrumbs(category):
    return {
        'category': category
    }


@register.inclusion_tag('includes/slider.html')
def show_slider(post):
    return {"post": post}


@register.inclusion_tag('includes/filter.html', takes_context=True)
def show_filter(context, my_filter):
    request = context['request'].GET.dict()
    return {"filter": my_filter, 'request': request}

@register.simple_tag(name='get_products_by_tag')
def get_products_by_tag(post):
    queryset = Sneakers.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).distinct()
    return DataMixin().get_first_image(queryset)






