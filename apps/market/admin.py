from django.contrib import admin
from apps.market.models import Market
from base.base_admin import BaseAdmin


# Register your models here.

@admin.register(Market)
class MarketAdmin(BaseAdmin):
    list_display = ('marketer', 'name','number_phone_1','website','is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

