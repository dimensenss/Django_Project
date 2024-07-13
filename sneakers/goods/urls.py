from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from .views import *

# /goods

app_name = 'goods'

urlpatterns = [
    path('', SneakersHome.as_view(), name='home'),  # http://127.0.0.1:8000/
    path('search/', SneakersSearch.as_view(), name='search'),
    path('about/', about, name='about'),
    path('contacts/', contacts, name='contacts'),
    re_path(r'^category/(?P<cat_slug>[-\w/]+)/$', SneakersCategories.as_view(), name='show_cat'),
    path('product/<slug:product_slug>/', SneakersDetail.as_view(), name='product'),
    path('filtered-reviews', FilterReviewsView.as_view(), name='filtered_reviews'),

    # path('create-review', create_review, name='create_review'),
    # path('update-review', update_review, name='update_review'),
    # path('delete-review', delete_review, name='delete_review'),

    path('social/signup/', signup_redirect, name='signup_redirect'),
]
