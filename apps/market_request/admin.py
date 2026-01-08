from django.contrib import admin
from apps.market_request.models import MarketRequest
from base.base_admin import BaseAdmin
from apps.user.models import Marketer
from django.contrib import messages
from .tasks import send_mail_to_owner_request


# create an action for saving MarketRequest to Marketer
@admin.action(description="register to marketer")
def register(modeladmin, request, queryset):
    success = True
    for market_request in queryset:
        if not market_request.user.is_authenticated:
            messages.error(request, f"User {market_request.user} dose not exist!")
            success = False
            break

        elif Marketer.objects.filter(user=market_request.user).exists():
            messages.error(request, f"User {market_request.user} already exists!")
            success = False
            break

        elif market_request.status == MarketRequest.StatusChoices.REJECTED:
            messages.error(request, f"User {market_request.user} has rejected!")
            success = False
            break

        else:
            city = market_request.city
            province = market_request.province
            address = market_request.address
            age = market_request.age
            national_code = market_request.national_code
            email = market_request.email
            name = market_request.user.get_full_name()

            Marketer.objects.create(
                user=market_request.user,
                city=city,
                national_code=national_code,
                province=province,
                address=address,
                age=age
            )
            market_request.status = MarketRequest.StatusChoices.PASSED
            market_request.save()

            send_mail_to_owner_request.delay(email,name)
    if success:
        messages.success(request, f"Marketers have been created successfully!")


@admin.action(description="reject requests")
def reject_requests(modeladmin, request, queryset):
    success = True
    for market_request in queryset:

        if Marketer.objects.filter(user=market_request.user).exists():
            messages.error(request, f'You cannot reject this requests for user : {market_request.user}'
                                    f'because this user is a marketer')
            success = False
            break

        elif market_request.status == MarketRequest.StatusChoices.REJECTED:
            messages.error(request, f"User {market_request.user} has rejected!")
            success = False
            break

        else:
            market_request.status = MarketRequest.StatusChoices.REJECTED
            market_request.save()

    if success:
        messages.success(request, f"Requests have been rejected successfully!")


@admin.register(MarketRequest)
class MarketRequestAdmin(BaseAdmin):
    list_display = ("user", "mobile_number", "city", "province", "status")
    search_fields = ("mobile_number", "city", "province", "national_code")
    list_filter = ("city", "province", "status")
    readonly_fields = ['status'] + BaseAdmin.readonly_fields
    actions = (register, reject_requests)
