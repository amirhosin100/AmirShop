from django.contrib import admin
from apps.category.models import Category,SubCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','id']
    search_fields = ['title']
    exclude = []
    readonly_fields = ['id']

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['title','category','id']
    search_fields = ['title']
    exclude = []
    readonly_fields = ['id']

