from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
    ("Extra", {"fields": ("role", "photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
    ("Extra", {"fields": ("role", "photo")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")