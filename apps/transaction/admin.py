from django.contrib import admin
from apps.transaction.models import Transaction
from base.base_admin import BaseAdmin


# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    list_display = ["user","first_name","last_name","mobile_number","is_paid"]
    list_filter = ["is_paid"]
    search_fields = ["first_name","last_name","mobile_number"]

