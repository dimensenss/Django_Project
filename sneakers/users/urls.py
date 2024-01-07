from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import *


app_name = 'users'

urlpatterns = [
    path('login/', LoginUser.as_view(), name = 'login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name = 'register'),
    path('profile/', ProfileUser.as_view(), name = 'profile'),
]