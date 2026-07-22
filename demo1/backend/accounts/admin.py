from django.contrib import admin

from .models import AuthToken, YouthProfile


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "created_at")
    search_fields = ("user__username", "key")


@admin.register(YouthProfile)
class YouthProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "region", "profile_type", "updated_at")
    search_fields = ("user__username", "nickname", "region", "profile_type")
