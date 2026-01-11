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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
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

    path('user/comment/', include('apps.comment.urls.user_urls',namespace='comment_user')),

    path('owner/market/', include('apps.market.urls.owner_urls',namespace='market_owner')),

    path('owner/product/', include('apps.product.urls.owner_urls',namespace='product_owner')),

    path('owner/comment/', include('apps.comment.urls.owner_urls',namespace='comment_owner')),

    path('market-request/', include('apps.market_request.urls',namespace='market_request')),

    path("", include('apps.user.urls.user_detail_urls',namespace='user_detail')),

    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    #jwt
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include(api_urlpatterns)),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
