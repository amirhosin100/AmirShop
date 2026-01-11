from django.urls import path
from apps.comment.views.user_views import (
    CommentCreateView,
    CommentImageCreateView
)

app_name = 'comment_user'

urlpatterns = [
    path('create/<str:product_id>/', CommentCreateView.as_view(), name='create'),
    path('image/create/<str:comment_id>/', CommentImageCreateView.as_view(), name='image_create'),
]