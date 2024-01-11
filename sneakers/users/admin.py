from django.contrib import admin

from carts.admin import CartTable
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "username", "email", ]
    search_fields = ["username", "first_name", "last_name", "email", ]
    inlines = [CartTable]
