from django.contrib import admin
from base.base_admin import BaseAdmin,BaseStackedInline
from apps.comment.models import Comment,CommentImage


class CommentImageInline(BaseStackedInline):
    model = CommentImage
    extra = 1


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ['user','content','status']
    search_fields = ['content']
    list_filter = ['status']
    inlines = [CommentImageInline]


