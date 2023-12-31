

from django import template
from django.utils.http import urlencode

from sneakers_shop.models import *

register = template.Library()


@register.simple_tag()
def get_menu():
    return [{'title': 'Про нас', 'url_name': 'about'},
            {'title': 'Контакти', 'url_name': 'contacts'}, ]


@register.simple_tag(name='get_cats')
def get_categories():
    return Category.objects.all()


@register.simple_tag(name='get_photos')
def get_photos(post):
    return post.images.all()


@register.simple_tag(name='get_main_photo')
def get_photos(post):
    return post.images.first().image


@register.inclusion_tag('sneakers_shop/list_categories.html')
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
    return {"cat_selected": cat_selected, 'cats': cats, "filter": my_filter, 'request': request}


@register.inclusion_tag('includes/slider.html')
def show_slider(post):
    return {"post": post}


@register.inclusion_tag('includes/filter.html', takes_context=True)
def show_filter(context, my_filter):
    request = context['request'].GET.dict()
    return {"filter": my_filter, 'request': request}

# @register.simple_tag(takes_context=True) # метод для добавления параметра в урл запрос
# def change_params(context, **kwargs):
#     query = context['request'].GET.dict()
#     query.update(kwargs)
#     return urlencode(query)
