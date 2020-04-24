from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mptt.admin import MPTTModelAdmin

from .models import Inventory, Organization, PPEType, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    model = User
    fieldsets = ((None, {"fields": ("organization",)}),) + UserAdmin.fieldsets
    autocomplete_fields = ("organization",)


@admin.register(Organization)
class OrganizationAdmin(MPTTModelAdmin):
    readonly_fields = ("code",)
    list_display = ("name", "code", "is_provider")
    list_filter = ("is_provider",)
    search_fields = ("name",)


@admin.register(PPEType)
class PPETypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "ppetype",
        "number",
        "item_number",
        "daily_use",
        "projected_daily_use",
        "projected_run_out",
        "timestamp",
    )
    list_filter = (
        "organization",
        "ppetype",
    )
