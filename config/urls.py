"""
URL configuration for AmirShop project.

"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

api_urlpatterns = [
    path(
        'user/',
        include(
            'apps.user.urls.user_registration_urls',
            namespace='user_registration'
        )
    ),

    path('user/market/', include('apps.market.urls.user_urls',namespace='market_user')),

    path('user/product/', include('apps.product.urls.user_urls',namespace='product_user')),

    path('user/cart/', include('apps.cart.urls.user_urls'),name='cart_user'),

    path('owner/market/', include('apps.market.urls.owner_urls',namespace='market_owner')),

    path('owner/product/', include('apps.product.urls.owner_urls',namespace='product_owner')),

    path('market-request/', include('apps.market_request.urls')),

    path("", include('apps.user.urls.user_detail_urls',namespace='user_detail')),

    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(api_urlpatterns)),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
