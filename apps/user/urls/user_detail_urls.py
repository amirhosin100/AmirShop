from django.urls import path
from apps.user.views.user_detail_view import UserDetailView

urlpatterns = [
    path("@<str:phone>/",UserDetailView.as_view(),name="detail"),
]