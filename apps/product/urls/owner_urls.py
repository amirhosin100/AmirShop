from django.urls import path
from apps.product.views.owner_views import (
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductImageCreateView,
    ProductImageUpdateView,
    ProductImageDeleteView,
    ProductFeatureCreateView,
    ProductFeatureUpdateView,
    ProductFeatureDeleteView,
)


urlpatterns = [
    path('create/<str:market_id>/', ProductCreateView.as_view(), name='product_create'),
    path('update/<str:product_id>/', ProductUpdateView.as_view(), name='product_update'),
    path('delete/<str:product_id>/', ProductDeleteView.as_view(), name='product_delete'),
    path('detail/<str:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('list/', ProductListView.as_view(), name='product_list'),

    path('image/<str:product_id>/', ProductImageCreateView.as_view(), name='create_image'),
    path('image/<str:product_id>/update/<str:image_id>/', ProductImageUpdateView.as_view(), name='update_image'),
    path('image/<str:product_id>/delete/<str:image_id>/', ProductImageDeleteView.as_view(), name='delete_image'),

    path('feature/<str:product_id>/', ProductFeatureCreateView.as_view(), name='create_feature'),
    path('feature/<str:product_id>/update/<str:feature_id>/', ProductFeatureUpdateView.as_view(), name='update_feature'),
    path('feature/<str:product_id>/delete/<str:feature_id>/', ProductFeatureDeleteView.as_view(), name='delete_feature'),

]
