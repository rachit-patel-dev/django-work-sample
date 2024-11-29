from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # Users
    path("", include("core.interface.users.urls", namespace="users")),
]
