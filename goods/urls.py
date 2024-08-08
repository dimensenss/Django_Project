from django.urls import path, re_path, include
from django.views.decorators.cache import cache_page
from rest_framework import routers

from .views import *

# /goods

app_name = 'goods'

router = routers.DefaultRouter()
router.register(r'sneakers', TestProductsApiView)

urlpatterns = [
    path('', SneakersHome.as_view(), name='home'),  # http://127.0.0.1:8000/
    path('search/', SneakersSearch.as_view(), name='search'),
    path('about/', about, name='about'),
    path('contacts/', contacts, name='contacts'),
    re_path(r'^category/(?P<cat_slug>[-\w/]+)/$', SneakersCategories.as_view(), name='show_cat'),
    path('product/<slug:product_slug>/', SneakersDetail.as_view(), name='product'),
    path('filtered-reviews', FilterReviewsView.as_view(), name='filtered_reviews'),

    path('add-wish-list/', AddToWishListView.as_view(), name='add_to_wish_list'),
    path('wish-list/', WishListView.as_view(), name='wish_list'),

    path('api/v1/', include(router.urls)),

    path('social/signup/', signup_redirect, name='signup_redirect'),
]
