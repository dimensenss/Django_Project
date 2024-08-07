from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from goods.utils import CategoryAutocomplete, SneakersAutocomplete, BrandsAutocomplete

from sneakers import settings
from goods.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    re_path(
        r'^category-autocomplete/$',
        CategoryAutocomplete.as_view(),
        name='category-autocomplete',
    ),
    re_path(
        r'^sneakers-autocomplete/$',
        SneakersAutocomplete.as_view(),
        name='sneakers-autocomplete',
    ),
    re_path(
        r'^brands-autocomplete/$',
        BrandsAutocomplete.as_view(),
        name='brands-autocomplete',
    ),

    path('', include('goods.urls', namespace='goods')),
    path('user/', include('users.urls', namespace='user')),
    path('cart/', include('carts.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path("", include("allauth.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

else:
    urlpatterns += staticfiles_urlpatterns()

handler404 = PageNotFound
