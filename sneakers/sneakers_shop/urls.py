from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from .views import *

#/sneakers_shop



urlpatterns = [
    path('', SneakersHome.as_view(), name = 'home'), #http://127.0.0.1:8000/
    path('search/', SneakersHome.as_view(), name = 'search'),
    path('about/', about, name = 'about'),
    path('shop/', shop, name = 'shop'),
    path('contacts/', contacts, name = 'contacts'),
    path('cabinet/', contacts, name = 'cabinet'),
    path('login/', LoginUser.as_view(), name = 'login'),
    path('register/', RegisterUser.as_view(), name = 'register'),
    path('profile/', contacts, name = 'profile'),
    path('logout/', logout_user, name = 'logout'),
    path('category/<slug:cat_slug>/', SneakersCategories.as_view(), name = 'show_cat'),
    path('product/<slug:product_slug>/', ShowProduct.as_view(), name = 'product'),
    path('tag/<str:tag_slug>/', SneakersTags.as_view(), name = 'sneakers_by_tag'),
]