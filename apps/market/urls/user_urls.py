from django.urls import path
from apps.market.views.user_views import (
    MarketDetailView,
    AllMarketsView
)

urlpatterns = [
    path('list/', AllMarketsView.as_view(), name='list'),
    path('<str:market_id>/', MarketDetailView.as_view(), name='detail'),
]