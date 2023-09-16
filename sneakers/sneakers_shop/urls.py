from django.urls import path, re_path
from .views import *

#/sneakers_shop
urlpatterns = [
    path('', SneakersHome.as_view(), name = 'home'), #http://127.0.0.1:8000/
    path('about/', about, name = 'about'),
    path('shop/', shop, name = 'shop'),
    path('contacts/', contacts, name = 'contacts'),
    path('category/<slug:cat_slug>/', SneakersCategories.as_view(), name = 'show_cat'),
    path('product/<slug:product_slug>/', ShowProduct.as_view(), name = 'product'),
]