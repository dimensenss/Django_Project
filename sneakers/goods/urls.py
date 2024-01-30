from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from .views import *

#/goods

app_name = 'goods'

urlpatterns = [
    path('', SneakersHome.as_view(), name = 'home'), #http://127.0.0.1:8000/
    path('search/', SneakersHome.as_view(), name = 'search'),
    path('about/', about, name = 'about'),
    path('shop/', shop, name = 'shop'),
    path('contacts/', contacts, name = 'contacts'),
    re_path(r'^category/(?P<cat_slug>[-\w/]+)/$', SneakersCategories.as_view(), name='show_cat'),
    path('product/<slug:product_slug>/', show_product, name ='product'),

    path('social/signup/', signup_redirect, name='signup_redirect'),
]