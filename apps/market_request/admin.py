from django.contrib import admin
from apps.market_request.models import MarketRequest
from base.base_admin import BaseAdmin
from apps.user.models import Marketer

# Register your models here.


#create an action for saving MarketRequest to Marketer
@admin.action(description="register to marketer")
def register(modeladmin, request, queryset):
    for market_request in queryset:
        city = market_request.city
        national_code = market_request.national_code
        province = market_request.province
        address = market_request.address
        age = market_request.age
        if market_request.user and not Marketer.objects.filter(user=market_request.user).exists() :
            Marketer.objects.create(
                user=market_request.user,
                city=city,
                national_code=national_code,
                province=province,
                address=address,
                age=age
            )


@admin.register(MarketRequest)
class MarketRequestAdmin(BaseAdmin):
    list_display = ("user","mobile_number","city","province")
    search_fields = ("mobile_number","city","province","national_code")
    list_filter = ("city","province")
    actions = (register,)

