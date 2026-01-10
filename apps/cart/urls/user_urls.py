from django.urls import path

from apps.cart.views.user_views import (
    CartDetailView,
    CartClearView,
    AddToCartView,
    RemoveCartItemView,
    DecreaseCartItemView,
    SetItemQuantityView,
    CartInfoListView,
    CartInfoDetailView
)

app_name = 'cart_user'

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail'),
    path('clear/', CartClearView.as_view(), name='cart_clear'),
    path('add/<str:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<str:product_id>/', RemoveCartItemView.as_view(), name='remove_cart'),
    path('set/<str:product_id>/', SetItemQuantityView.as_view(), name='set_item_quantity'),
    path('decrease/<str:product_id>/', DecreaseCartItemView.as_view(), name='decrease_item'),

    path('info/list/', CartInfoListView.as_view(), name='cart_info_list'),
    path('info/detail/<str:pk>/', CartInfoDetailView.as_view(), name='cart_info_detail'),
]
