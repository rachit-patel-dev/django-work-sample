from django.contrib import admin

from core.domain.users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "id", "username", "status", "is_deleted")
    search_fields = ("email", "first_name", "last_name", "username")
    list_filter = ("status", "is_deleted")


admin.site.register(User, UserAdmin)
