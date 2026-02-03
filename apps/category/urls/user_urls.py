from django.urls import path
from apps.category.views.user_view import (
    CategoryDetailView,
    CategoryListView
)

app_name = 'category_user'

urlpatterns = [
    path("list/",CategoryListView.as_view(),name="list"),
    path("detail/<str:category_id>/",CategoryDetailView.as_view(),name="detail"),
]