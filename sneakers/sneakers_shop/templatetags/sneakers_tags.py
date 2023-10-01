from django import template
from sneakers_shop.models import *


register = template.Library()

@register.simple_tag()
def get_menu():
    return [{'title' : 'About', 'url_name': 'about'},
            {'title': 'Contacts', 'url_name' : 'contacts'},]

@register.simple_tag(name='get_cats')
def get_categories():
    return Category.objects.all()

@register.simple_tag(name='get_photos')
def get_photos(post):
    return post.images.all()

@register.simple_tag(name='get_main_photo')
def get_photos(post):
    return post.photo.url

@register.inclusion_tag('sneakers_shop/list_categories.html')
def show_categories(sort = None, cat_selected = None):#доделать
    if sort:
        cats = Category.objects.order_by(sort)
    else:
        cats = Category.objects.all()
    return {'cats':cats, 'cat_selected':cat_selected}

@register.inclusion_tag('includes/paginator.html')
def show_paginator(paginator, page_obj):
    return {"paginator":paginator, 'page_obj':page_obj}

@register.inclusion_tag('includes/slider.html')
def show_slider(post):
    return {"post":post}