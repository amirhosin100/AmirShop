from django.contrib import admin
from apps.market_request.models import MarketRequest
from base.base_admin import BaseAdmin

# Register your models here.

@admin.register(MarketRequest)
class MarketRequestAdmin(BaseAdmin):
    list_display = ("user","mobile_number","city","province")
    search_fields = ("mobile_number","city","province","national_code")
    list_filter = ("city","province")
