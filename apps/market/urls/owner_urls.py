from django.urls import path
from apps.market.views.owner_views import (
    MarketOwnerCreateView,
    MarketOwnerUpdateView,
    MarketOwnerDeleteView,
    MarketOwnerListView,
    MarketOwnerDetailView,
)

urlpatterns = [
    path('create/', MarketOwnerCreateView.as_view(), name='create'),
    path('update/<str:market_id>/', MarketOwnerUpdateView.as_view(), name='update'),
    path('delete/<str:market_id>/', MarketOwnerDeleteView.as_view(), name='delete'),
    path('list/', MarketOwnerListView.as_view(), name='list'),
    path('<str:market_id>/', MarketOwnerDetailView.as_view(), name='detail'),
]
