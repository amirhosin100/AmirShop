from django.urls import path
from apps.comment.views.owner_views import (
    CommentDetailView,
    CommentListView
)

app_name = 'comment_owner'

urlpatterns = [
    path('list/', CommentListView.as_view(),name='list'),
    path('detail/<str:comment_id>/',CommentDetailView.as_view(),name='detail'),
]
