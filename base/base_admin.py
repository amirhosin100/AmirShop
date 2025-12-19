from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    fields = []
    exclude = []
