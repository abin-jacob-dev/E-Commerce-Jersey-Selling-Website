from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "last_login",
        "is_active",
        "date_joined",
    )
    list_display_links=('email','full_name')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    readonly_fields=('last_login','date_joined','password')
    search_fields=('full_name',)
    ordering = ('-date_joined',)


admin.site.register(Account, UserAdmin)
