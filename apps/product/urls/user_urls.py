from django.urls import path
from apps.product.views.user_views import (
    ProductListView,
    ProductDetailView,
)


urlpatterns = [
    path('list/', ProductListView.as_view(), name='product_list'),
    path('detail/<str:product_id>/', ProductDetailView.as_view(), name='product_detail'),
]