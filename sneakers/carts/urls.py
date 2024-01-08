from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import *


app_name = 'carts'

urlpatterns = [
    path('cart_add/<slug:product_slug>/', cart_add, name = 'cart_add'),
    path('cart_change/<slug:product_slug>/', cart_change, name='cart_change'),
    path('cart_remove/<slug:product_slug>/', cart_delete, name = 'cart_remove'),
]