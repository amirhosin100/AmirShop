"""
URL configuration for AmirShop project.

"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('user/',include('apps.user.urls.user_registration_urls')),

    path('market-request/',include('apps.market_request.urls')),

    path("", include('apps.user.urls.user_detail_urls')),

]
if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
