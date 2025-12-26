from django.urls import path
from apps.market_request.views import (
    MarketRequestListView,
    MarketRequestCreateView,
    MarketRequestDetailView
)

urlpatterns = [
    path('create/',MarketRequestCreateView.as_view(),name='create'),

    path('list/',MarketRequestListView.as_view(),name='list'),

    path('detail/<str:market_request_id>',MarketRequestDetailView.as_view(),name='detail'),
]