from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import *

app_name = 'carts'

urlpatterns = [
    path('cart_add/', CartAddView.as_view(), name='cart_add'),
    path('cart_change/', CartChangeView.as_view(), name='cart_change'),
    path('cart_remove/', CartDeleteView.as_view(), name='cart_remove'),
]
