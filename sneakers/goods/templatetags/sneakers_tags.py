from django import template
from django.db.models import Min, Max, Sum, F


from goods.models import *
from goods.utils import get_user_wishes, get_product_list_from_wishes

register = template.Library()


@register.simple_tag()
def get_menu():
    return [{'title': 'Про нас', 'url_name': 'goods:about'},
            {'title': 'Контакти', 'url_name': 'goods:contacts'}, ]


@register.simple_tag(name='get_photos')
def get_photos(post):
    return post.images.all()


@register.simple_tag(name='get_all_sizes')
def get_all_sizes():
    return SneakersVariations.objects.all().values_list('size', flat=True).distinct()


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

@register.simple_tag(name='user_wishes')
def user_wishes(request):
    return get_user_wishes(request)


@register.simple_tag(name='products_in_wishes_list')
def products_in_wishes_list(request):
    return get_product_list_from_wishes(request)