from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from sneakers import settings
from goods.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('goods.urls', namespace='goods')),
    path('user/', include('users.urls', namespace='user')),
    path('cart/', include('carts.urls', namespace='cart')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler404 = PageNotFound
