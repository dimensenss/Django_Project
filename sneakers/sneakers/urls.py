from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from sneakers import settings
from sneakers_shop.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sneakers_shop.urls')),#http://127.0.0.1:8000/
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler404 = PageNotFound
