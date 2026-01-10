from django.contrib import admin
from base.base_admin import BaseAdmin, BaseStackedInline
from .models import Cart, CartItem,CartInfo


# Register your models here.

class CartItemInline(BaseStackedInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(BaseAdmin):
    list_display = ["user", "amount"]
    inlines = [CartItemInline]
    readonly_fields = BaseAdmin.readonly_fields + ["amount"]


@admin.register(CartInfo)
class CartInfoAdmin(BaseAdmin):
    list_display = ["user", "amount", "status"]
    list_filter = ["status"]
    readonly_fields = BaseAdmin.readonly_fields + ["amount"]
