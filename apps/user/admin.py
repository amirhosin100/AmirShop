from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm,UserCreationForm
from .models import User, Marketer,OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    fieldsets = (
        (None,{"fields":("phone","password")}),
        ("Personal info",{"fields":("first_name","last_name","email","bio","photo",)}),
        ("Important dates",{"fields":("date_joined","last_login")}),
        ("Permissions",{"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":("phone","password1","password2")
        }),
    )
    list_display = ("phone","first_name","last_name","is_active","is_superuser")
    list_filter = ("is_superuser","is_staff","is_active")
    search_fields = ("phone","first_name","last_name","email")

    ordering = ("phone",)

@admin.register(Marketer)
class MarketerAdmin(admin.ModelAdmin):
    list_display = ('user','national_code')


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone','code']
    search_fields = ['phone']
    readonly_fields = ['created_at','code']
