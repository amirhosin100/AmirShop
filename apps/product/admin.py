from django.contrib import admin
from base.base_admin import BaseAdmin,BaseStackedInline
from .models import *

# Register your models here.

class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 0

class ProductFeatureInline(admin.StackedInline):
    model = ProductFeature
    extra = 0

@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = ["market","name","price","percentage_off","discount_price","score"]
    search_fields = ["name"]
    inlines = [ProductFeatureInline,ProductImageInline]

